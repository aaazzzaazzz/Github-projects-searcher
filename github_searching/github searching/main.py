from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging
from contextlib import asynccontextmanager

from config import settings
from project.models import Base
from project.database import get_db, engine
from services.search_service import SearchService
from services.deepseek_service import deepseek_service
from services.dataease_service import DataEaseService
from data_importer import DataImporter

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("GitHub项目搜索引擎启动中...")
    
    # 确保数据库表存在
    Base.metadata.create_all(bind=engine)
    
    yield
    
    # 关闭时执行
    logger.info("GitHub项目搜索引擎关闭中...")

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="基于DeepSeek API的GitHub项目智能搜索引擎",
    lifespan=lifespan
)

# 挂载静态文件和模板
app.mount("/static", StaticFiles(directory=settings.static_files_dir), name="static")
app.mount("/wordcloud_images", StaticFiles(directory="wordcloud_images"), name="wordcloud_images")
templates = Jinja2Templates(directory=settings.templates_dir)

# 依赖注入
def get_search_service(db: Session = Depends(get_db)) -> SearchService:
    """获取搜索服务实例"""
    return SearchService(db)

# API路由
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """首页"""
    return templates.TemplateResponse("index_simplified.html", {"request": request})

@app.get("/api/search")
async def search_projects(
    q: str = Query(..., description="搜索查询"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    sort_by: str = Query("relevance", description="排序方式"),
    activity_level: Optional[str] = Query(None, description="活跃度级别"),
    search_service: SearchService = Depends(get_search_service)
):
    """
    搜索项目API
    
    Args:
        q: 搜索查询
        page: 页码
        page_size: 每页大小
        sort_by: 排序方式
        search_service: 搜索服务
        
    Returns:
        搜索结果
    """
    try:
        # 使用DeepSeek API解析查询
        search_params = await deepseek_service.generate_search_query(q)
        
        # 对于健康度搜索，使用DeepSeek解析的sort_by
        if "健康度" in q or "高健康度" in q or "项目健康" in q or "代码质量" in q or "维护良好" in q or "健康状况" in q:
            final_sort_by = search_params.get("sort_by", "health")
        else:
            # URL参数优先于DeepSeek解析结果
            final_sort_by = sort_by if sort_by != "relevance" else search_params.get("sort_by", "relevance")
        
        final_activity_level = activity_level if activity_level else search_params.get("activity_level")
        final_health_level = search_params.get("health_level")
        final_stars_level = search_params.get("stars_level")
        final_forks_level = search_params.get("forks_level")
        final_attention_level = search_params.get("attention_level")
        
        # 执行搜索
        results = search_service.search_projects(
            keywords=search_params.get("keywords"),
            languages=search_params.get("languages"),
            event_types=search_params.get("event_types"),
            time_range=search_params.get("time_range"),
            activity_level=final_activity_level,
            health_level=final_health_level,
            stars_level=final_stars_level,
            forks_level=final_forks_level,
            attention_level=final_attention_level,
            sort_by=final_sort_by,
            contributor_type=search_params.get("contributor_type", "all"),
            page=page,
            page_size=page_size
        )
        
        # 生成搜索解释
        if results["results"]:
            explanation = await deepseek_service.generate_search_explanation(q, results["results"])
        else:
            explanation = f"未找到与'{q}'相关的项目，请尝试其他关键词。"
        
        return {
            "success": True,
            "query": q,
            "search_params": search_params,
            "results": results,
            "explanation": explanation
        }
        
    except Exception as e:
        logger.error(f"搜索项目时出错: {e}")
        raise HTTPException(status_code=500, detail="搜索失败，请稍后重试")

@app.get("/api/projects")
async def get_projects(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    sort_by: str = Query("relevance", description="排序方式"),
    search_service: SearchService = Depends(get_search_service)
):
    """
    获取项目列表API
    
    Args:
        page: 页码
        page_size: 每页大小
        sort_by: 排序方式
        search_service: 搜索服务
        
    Returns:
        项目列表
    """
    try:
        results = search_service.search_projects(
            page=page,
            page_size=page_size,
            sort_by=sort_by
        )
        
        return {
            "success": True,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"获取项目列表时出错: {e}")
        raise HTTPException(status_code=500, detail="获取项目列表失败")

@app.get("/api/projects/{project_key:path}")
async def get_project_details(
    project_key: str,
    search_service: SearchService = Depends(get_search_service)
):
    """
    获取项目详细信息API
    
    Args:
        project_key: 项目key
        search_service: 搜索服务
        
    Returns:
        项目详细信息
    """
    try:
        project_details = search_service.get_project_details(project_key)
        
        if not project_details:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        # 生成项目摘要
        # project_details["project"] 是一个字典，需要从中提取metrics_data
        project_dict = project_details["project"]
        metrics_data = project_dict.get("metrics_data")
        
        # 如果metrics_data是字符串，需要解析为字典
        import json
        if isinstance(metrics_data, str):
            try:
                metrics_data = json.loads(metrics_data.replace(':NaN', ':null'))
            except json.JSONDecodeError:
                metrics_data = {}
        
        summary = await deepseek_service.generate_project_summary(
            project_dict,
            [],  # 这里可以传入事件数据（已弃用）
            metrics_data  # 传入metrics_data以获取贡献者和Issue数据
        )
        
        # 推荐相关项目
        related_projects = await deepseek_service.suggest_related_projects(
            project_details["project"],
            db=search_service.db
        )
        
        return {
            "success": True,
            "project_details": project_details,
            "summary": summary,
            "related_projects": related_projects
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取项目详细信息时出错: {e}")
        raise HTTPException(status_code=500, detail="获取项目详情失败")


@app.get("/api/trends")
async def analyze_trends(
    time_period: str = Query("yearly", description="时间周期"),
    db: Session = Depends(get_db)
):
    """
    分析趋势API
    
    Args:
        time_period: 时间周期
        db: 数据库会话
        
    Returns:
        趋势分析结果
    """
    try:
        trends_analysis = await deepseek_service.analyze_trends(db, time_period)
        
        return {
            "success": True,
            "time_period": time_period,
            "analysis": trends_analysis
        }
        
    except Exception as e:
        logger.error(f"分析趋势时出错: {e}")
        raise HTTPException(status_code=500, detail="趋势分析失败")

@app.post("/api/import-data")
async def import_data():
    """
    导入数据API（管理功能）
    
    Returns:
        导入结果
    """
    try:
        # 执行数据导入
        importer = DataImporter()
        importer.run_full_import()
        
        return {
            "success": True,
            "message": "数据导入完成"
        }
        
    except Exception as e:
        logger.error(f"导入数据时出错: {e}")
        raise HTTPException(status_code=500, detail="数据导入失败")

@app.get("/api/health")
async def health_check():
    """
    健康检查API
    
    Returns:
        健康状态
    """
    return {
        "success": True,
        "status": "healthy",
        "version": settings.app_version
    }

# DataEase数据大屏API端点
@app.get("/api/dataease/wordcloud/{metric_type}")
async def get_wordcloud_data(
    metric_type: str,
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
    db: Session = Depends(get_db)
):
    """
    获取词云数据API
    
    Args:
        metric_type: 指标类型 (activity, participants, attention, change_requests,
                       issues_active, new_contributors, openrank, stars, technical_fork)
        limit: 返回数量限制
        db: 数据库会话
        
    Returns:
        词云数据
    """
    try:
        dataease_service = DataEaseService(db)
        wordcloud_data = dataease_service.get_wordcloud_data(metric_type, limit)
        
        return {
            "success": True,
            "metric_type": metric_type,
            "data": wordcloud_data
        }
        
    except Exception as e:
        logger.error(f"获取词云数据时出错: {e}")
        raise HTTPException(status_code=500, detail="获取词云数据失败")

@app.get("/api/dataease/dashboard/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    获取仪表板统计数据API
    
    Args:
        db: 数据库会话
        
    Returns:
        仪表板统计数据
    """
    try:
        dataease_service = DataEaseService(db)
        stats = dataease_service.get_dashboard_stats()
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"获取仪表板统计数据时出错: {e}")
        raise HTTPException(status_code=500, detail="获取仪表板统计数据失败")

@app.get("/api/dataease/project/{project_key:path}")
async def get_project_details_for_dashboard(
    project_key: str,
    db: Session = Depends(get_db)
):
    """
    获取项目详细信息用于仪表板API
    
    Args:
        project_key: 项目键
        db: 数据库会话
        
    Returns:
        项目详细信息
    """
    try:
        dataease_service = DataEaseService(db)
        project_details = dataease_service.get_project_details_for_dashboard(project_key)
        
        if not project_details:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        return {
            "success": True,
            "data": project_details
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取项目详细信息时出错: {e}")
        raise HTTPException(status_code=500, detail="获取项目详细信息失败")

@app.get("/dataease")
async def dataease_dashboard(request: Request):
    """DataEase数据大屏页面"""
    return templates.TemplateResponse("dataease_dashboard.html", {"request": request})

@app.get("/embed-dataease")
async def embed_dataease(request: Request):
    """嵌入DataEase数据大屏页面"""
    return templates.TemplateResponse("embed_dataease_dashboard.html", {"request": request})

# 错误处理
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """404错误处理"""
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": "资源不存在",
            "status_code": 404
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """500错误处理"""
    from fastapi.responses import JSONResponse
    logger.error(f"内部服务器错误: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "内部服务器错误",
            "status_code": 500
        }
    )

# 中间件 - 简化实现
@app.middleware("http")
async def add_cors_header(request: Request, call_next):
    try:
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response
    except Exception as e:
        logger.error(f"中间件错误: {e}")
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "服务器内部错误",
                "status_code": 500
            }
        )

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )
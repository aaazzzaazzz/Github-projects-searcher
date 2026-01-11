#!/usr/bin/env python3
"""
GitHub项目搜索引擎启动脚本
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_requirements():
    """检查依赖是否安装"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import pandas
        import openai
        logger.info("所有依赖包已安装")
        return True
    except ImportError as e:
        logger.error(f"缺少依赖包: {e}")
        logger.info("请运行: pip install -r requirements.txt")
        return False

def check_config():
    """检查配置文件"""
    if not os.path.exists('.env'):
        logger.warning("未找到.env文件，将使用默认配置")
        logger.info("请复制.env.example为.env并配置相应参数")
    else:
        logger.info("配置文件检查完成")

def init_database():
    """初始化数据库"""
    try:
        from project.database import engine, Base
        from project.models import Project, GitHubEvent, Contributor, ProjectActivity
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建完成")
        return True
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        return False

def check_data():
    """检查数据是否存在"""
    try:
        from project.database import SessionLocal
        from project.models import Project
        
        db = SessionLocal()
        project_count = db.query(Project).count()
        db.close()
        
        if project_count == 0:
            logger.warning("数据库中没有项目数据")
            logger.info("请运行数据导入脚本: python data_importer.py")
            return False
        else:
            logger.info(f"数据库中包含 {project_count} 个项目")
            return True
    except Exception as e:
        logger.error(f"检查数据时出错: {e}")
        return False

async def test_api_connection():
    """测试API连接"""
    try:
        from services.deepseek_service import deepseek_service
        
        # 测试DeepSeek API连接
        if hasattr(deepseek_service, 'client') and deepseek_service.client.api_key:
            logger.info("DeepSeek API配置检查完成")
        else:
            logger.warning("DeepSeek API未配置或配置错误")
        
        return True
    except Exception as e:
        logger.error(f"API连接测试失败: {e}")
        return False

def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("GitHub项目搜索引擎启动中...")
    logger.info("=" * 50)
    
    # 检查依赖
    if not check_requirements():
        sys.exit(1)
    
    # 检查配置
    check_config()
    
    # 初始化数据库
    if not init_database():
        sys.exit(1)
    
    # 检查数据
    has_data = check_data()
    
    # 测试API连接
    asyncio.run(test_api_connection())
    
    logger.info("=" * 50)
    logger.info("系统检查完成")
    
    if not has_data:
        logger.info("建议先导入数据: python data_importer.py")
    
    logger.info("启动Web服务器...")
    logger.info("=" * 50)
    
    # 启动FastAPI应用
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("服务器已停止")
    except Exception as e:
        logger.error(f"启动服务器失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
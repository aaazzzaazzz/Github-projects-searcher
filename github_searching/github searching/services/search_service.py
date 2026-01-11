# 触发重新加载 - 第二次
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func, extract
from project.models import Project, GitHubEvent, Contributor, ProjectActivity
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class SearchService:
    """搜索引擎服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def search_projects(self,
                       keywords: Optional[List[str]] = None,
                       languages: Optional[List[str]] = None,
                       event_types: Optional[List[str]] = None,
                       time_range: Optional[Dict[str, str]] = None,
                       activity_level: Optional[str] = None,
                       health_level: Optional[str] = None,
                       stars_level: Optional[str] = None,
                       forks_level: Optional[str] = None,
                       attention_level: Optional[str] = None,
                       sort_by: str = "relevance",
                       contributor_type: str = "all",
                       page: int = 1,
                       page_size: int = 20) -> Dict[str, Any]:
        """
        搜索项目
        
        Args:
        keywords: 关键词列表
        languages: 编程语言列表
        event_types: 事件类型列表
        time_range: 时间范围
        activity_level: 活跃度级别
        health_level: 健康度级别
        stars_level: 星标数级别
        forks_level: 分支数级别
        sort_by: 排序方式
        contributor_type: 贡献者类型
        page: 页码
        page_size: 每页大小
            
        Returns:
            搜索结果字典
        """
        try:
            logger.info(f"搜索参数 - keywords: {keywords}, sort_by: {sort_by}")
            # 处理中文关键词映射
            if keywords:
                processed_keywords = []
                for keyword in keywords:
                    # 检查是否包含中文字符
                    if any('\u4e00' <= char <= '\u9fff' for char in keyword):
                        # 中文关键词映射
                        keyword_lower = keyword.lower()
                        if 'python项目' in keyword_lower:
                            processed_keywords.append('python')
                        elif 'java项目' in keyword_lower:
                            processed_keywords.append('java')
                        elif 'javascript项目' in keyword_lower:
                            processed_keywords.append('javascript')
                        elif 'js项目' in keyword_lower:
                            processed_keywords.append('javascript')
                        elif 'typescript项目' in keyword_lower:
                            processed_keywords.append('typescript')
                        elif 'go项目' in keyword_lower:
                            processed_keywords.append('go')
                        elif 'rust项目' in keyword_lower:
                            processed_keywords.append('rust')
                        elif 'c++项目' in keyword_lower:
                            processed_keywords.extend(['cpp', 'c++'])
                        elif 'c项目' in keyword_lower:
                            processed_keywords.append('c')
                        elif 'php项目' in keyword_lower:
                            processed_keywords.append('php')
                        elif 'ruby项目' in keyword_lower:
                            processed_keywords.append('ruby')
                        elif 'swift项目' in keyword_lower:
                            processed_keywords.append('swift')
                        elif 'kotlin项目' in keyword_lower:
                            processed_keywords.append('kotlin')
                        elif 'scala项目' in keyword_lower:
                            processed_keywords.append('scala')
                        elif 'r项目' in keyword_lower:
                            processed_keywords.append('r')
                        elif 'matlab项目' in keyword_lower:
                            processed_keywords.append('matlab')
                        elif 'vue项目' in keyword_lower:
                            processed_keywords.append('vue')
                        elif 'react项目' in keyword_lower:
                            processed_keywords.append('react')
                        elif 'angular项目' in keyword_lower:
                            processed_keywords.append('angular')
                        elif 'django项目' in keyword_lower:
                            processed_keywords.append('django')
                        elif 'flask项目' in keyword_lower:
                            processed_keywords.append('flask')
                        elif 'spring项目' in keyword_lower:
                            processed_keywords.append('spring')
                        elif 'laravel项目' in keyword_lower:
                            processed_keywords.append('laravel')
                        elif 'web开发' in keyword_lower:
                            processed_keywords.extend(['web', 'development', 'javascript', 'html', 'css', 'frontend'])
                        elif '前端开发' in keyword_lower:
                            processed_keywords.extend(['frontend', 'javascript', 'html', 'css', 'react', 'vue', 'angular'])
                        elif '后端开发' in keyword_lower:
                            processed_keywords.extend(['backend', 'api', 'server', 'nodejs', 'python', 'java', 'go'])
                        elif '全栈开发' in keyword_lower:
                            processed_keywords.extend(['fullstack', 'frontend', 'backend', 'javascript', 'python', 'java', 'react', 'vue'])
                        elif '移动开发' in keyword_lower:
                            processed_keywords.extend(['mobile', 'android', 'ios', 'react-native', 'flutter'])
                        elif '游戏开发' in keyword_lower:
                            processed_keywords.extend(['game', 'unity', 'unreal', 'godot'])
                        elif '高活跃度' in keyword_lower or '非常活跃' in keyword_lower or '特别活跃' in keyword_lower or '很活跃' in keyword_lower or '活跃' in keyword_lower:
                            # 对于高活跃度搜索，不添加具体关键词，让活跃度过滤器处理
                            pass
                        elif '中活跃度' in keyword_lower:
                            # 对于中活跃度搜索，不添加具体关键词，让活跃度过滤器处理
                            pass
                        elif '低活跃度' in keyword_lower or '不活跃' in keyword_lower or '停滞' in keyword_lower or '很少更新' in keyword_lower:
                            # 对于低活跃度搜索，不添加具体关键词，让活跃度过滤器处理
                            pass
                        elif '健康度' in keyword_lower or '健康的项目' in keyword_lower or '代码质量高' in keyword_lower or '维护得很好' in keyword_lower or '稳定' in keyword_lower or '健康状况好' in keyword_lower:
                            # 对于健康度搜索，不添加具体关键词，让排序处理
                            pass
                        elif '高健康度' in keyword_lower:
                            # 对于健康度搜索，不添加具体关键词，让排序处理
                            pass
                        elif '项目健康' in keyword_lower:
                            # 对于健康度搜索，不添加具体关键词，让排序处理
                            pass
                        elif '代码质量' in keyword_lower:
                            # 对于健康度搜索，不添加具体关键词，让排序处理
                            pass
                        elif '维护良好' in keyword_lower:
                            # 对于健康度搜索，不添加具体关键词，让排序处理
                            pass
                        elif '健康状况' in keyword_lower:
                            # 对于健康度搜索，不添加具体关键词，让排序处理
                            pass
                        elif '关注度' in keyword_lower or '很受欢迎' in keyword_lower or '受欢迎' in keyword_lower or '热门' in keyword_lower or '流行' in keyword_lower or '知名度高' in keyword_lower:
                            # 对于高关注度搜索，不添加具体关键词，让排序处理
                            pass
                        elif '高关注度' in keyword_lower:
                            # 对于高关注度搜索，不添加具体关键词，让排序处理
                            pass
                        elif '多关注' in keyword_lower:
                            # 对于高关注度搜索，不添加具体关键词，让排序处理
                            pass
                        elif '关注多' in keyword_lower:
                            # 对于高关注度搜索，不添加具体关键词，让排序处理
                            pass
                        elif '关注高' in keyword_lower:
                            # 对于高关注度搜索，不添加具体关键词，让排序处理
                            pass
                        elif '高关注' in keyword_lower:
                            # 对于高关注度搜索，不添加具体关键词，让排序处理
                            pass
                        elif '低关注度' in keyword_lower or '无人问津' in keyword_lower or '不受欢迎' in keyword_lower or '知名度低' in keyword_lower:
                            # 对于低关注度搜索，不添加具体关键词，让排序处理
                            pass
                        elif '少关注' in keyword_lower:
                            # 对于低关注度搜索，不添加具体关键词，让排序处理
                            pass
                        elif '关注少' in keyword_lower:
                            # 对于低关注度搜索，不添加具体关键词，让排序处理
                            pass
                        elif '低关注' in keyword_lower:
                            # 对于低关注度搜索，不添加具体关键词，让排序处理
                            pass
                        else:
                            # 如果没有匹配，保留原关键词
                            processed_keywords.append(keyword)
                    else:
                        # 英文关键词直接使用
                        processed_keywords.append(keyword)
                
                keywords = processed_keywords
            
            # 构建基础查询
            query = self.db.query(Project)
            
            # 关键词搜索
            if keywords:
                # 特殊处理：如果是健康度搜索或关注度搜索，跳过关键词搜索，让排序处理
                if sort_by in ["health", "health_asc", "attention", "attention_asc"]:
                    # 对于健康度搜索或关注度搜索，跳过关键词搜索
                    logger.info(f"跳过健康度/关注度关键词搜索: {keywords}")
                elif languages:
                    # 如果有语言过滤，跳过关键词搜索，避免过度过滤
                    # 因为语言过滤已经足够精确，不需要再应用关键词过滤
                    logger.info(f"跳过关键词搜索（已有语言过滤）: {keywords}, languages: {languages}")
                else:
                    keyword_conditions = []
                    for keyword in keywords:
                        # 使用SQLite兼容的方式：LIKE + LOWER()实现不区分大小写搜索
                        keyword_lower = keyword.lower()
                        keyword_conditions.append(
                            or_(
                                func.lower(Project.project_name).like(f"%{keyword_lower}%"),
                                func.lower(Project.repo_description).like(f"%{keyword_lower}%"),
                                func.lower(Project.organization).like(f"%{keyword_lower}%")
                            )
                        )
                    query = query.filter(and_(*keyword_conditions))
            
            # 语言过滤
            if languages:
                query = query.filter(Project.repo_language.in_(languages))
            
            # 事件类型过滤（需要关联事件表）
            if event_types:
                query = query.join(GitHubEvent).filter(
                    GitHubEvent.event_type.in_(event_types)
                ).distinct()
            
            # 时间范围过滤
            if time_range:
                start_date_str = time_range.get('start_date')
                end_date_str = time_range.get('end_date')
                start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
                end_date = datetime.fromisoformat(end_date_str) if end_date_str else None
                
                if start_date or end_date:
                    query = query.join(GitHubEvent)
                    if start_date:
                        query = query.filter(GitHubEvent.created_at >= start_date)
                    if end_date:
                        query = query.filter(GitHubEvent.created_at <= end_date)
                    query = query.distinct()
            
            # 排序
            if sort_by == "stars":
                query = query.order_by(desc(Project.repo_stargazers_count))
            elif sort_by == "stars_asc":
                query = query.order_by(asc(Project.repo_stargazers_count))
            elif sort_by == "forks":
                query = query.order_by(desc(Project.repo_forks_count))
            elif sort_by == "forks_asc":
                query = query.order_by(asc(Project.repo_forks_count))
            elif sort_by == "activity":
                # 按活跃度降序排序 - 需要先获取所有项目计算活跃度分数再排序
                # 这里暂时使用时间戳作为排序依据，后面会在结果处理中重新按活跃度分数排序
                query = query.order_by(desc(func.coalesce(Project.repo_pushed_at, Project.repo_updated_at)))
            elif sort_by == "activity_asc":
                # 按活跃度升序排序 - 需要先获取所有项目计算活跃度分数再排序
                # 这里暂时使用时间戳作为排序依据，后面会在结果处理中重新按活跃度分数排序
                query = query.order_by(asc(func.coalesce(Project.repo_pushed_at, Project.repo_updated_at)))
            elif sort_by == "recent":
                query = query.order_by(desc(func.coalesce(Project.repo_updated_at, Project.repo_created_at)))
            elif sort_by == "attention":
                # 按关注度排序 - 需要从attention字段中提取数值
                query = query.order_by(desc(func.coalesce(Project.attention, '0')))
            elif sort_by == "attention_asc":
                # 按关注度升序排序 - 需要从attention字段中提取数值
                query = query.order_by(asc(func.coalesce(Project.attention, '0')))
            elif sort_by == "health":
                # 按健康度降序排序 - 健康度高的项目排在前面
                query = query.order_by(desc(Project.health_score))
            elif sort_by == "health_asc":
                # 按健康度升序排序 - 健康度低的项目排在前面
                query = query.order_by(asc(Project.health_score))
            else:  # relevance
                # 相关性排序：综合考虑星标、分叉和最近活动
                query = query.order_by(
                    desc(Project.repo_stargazers_count),
                    desc(Project.repo_forks_count),
                    desc(func.coalesce(Project.repo_pushed_at, Project.repo_updated_at))
                )
            
            # 如果有活跃度过滤、健康度过滤、星标数过滤、分支数过滤或关注度过滤，需要获取所有项目进行过滤
            if activity_level or health_level or stars_level or forks_level or attention_level or sort_by in ["attention", "attention_asc"]:
                # 获取所有项目（不分页）- 明确设置无限制
                all_projects = query.limit(None).all()
                
                # 获取项目详细统计信息
                results = []
                for project in all_projects:
                    # 获取项目活动统计
                    activity_stats = self._get_project_activity_stats(str(project.project_key), time_range)
                    
                    # 获取贡献者统计
                    contributor_stats = self._get_contributor_stats(str(project.project_key), contributor_type)
                    
                    # 计算活跃度分数
                    activity_score = self._calculate_activity_score(activity_stats)
                    
                    # 尝试从metrics_data中获取更准确的活跃度分数
                    try:
                        metrics_data = getattr(project, 'metrics_data', None)
                        if metrics_data is not None and str(metrics_data).strip():
                            if isinstance(metrics_data, str):
                                metrics_data = json.loads(metrics_data.replace(':NaN', ':null'))
                            else:
                                metrics_data = metrics_data
                            
                            # 从Activity_Metrics中获取活跃度分数
                            if 'Activity_Metrics' in metrics_data:
                                activity_metrics = metrics_data['Activity_Metrics']
                                activity_latest = activity_metrics.get('activity_Latest')
                                if activity_latest is not None and activity_latest != 'null':
                                    activity_score = float(activity_latest)
                    except Exception as e:
                        logger.warning(f"从metrics_data获取活跃度分数时出错: {e}")
                    
                    # 提取健康度分数和关注度分数
                    health_score = self._extract_health_score(project)
                    attention_score = self._extract_attention_score(project)
                    
                    results.append({
                        "id": str(project.id),
                        "project_key": project.project_key,
                        "organization": project.organization,
                        "project_name": project.project_name,
                        "description": project.repo_description,
                        "language": project.repo_language,
                        "stars": project.repo_stargazers_count or 0,
                        "forks": project.repo_forks_count or 0,
                        "size": project.repo_size or 0,
                        "license": project.repo_license,
                        "created_at": project.repo_created_at.isoformat() if project.repo_created_at is not None else None,
                        "updated_at": project.repo_updated_at.isoformat() if project.repo_updated_at is not None else None,
                        "last_pushed": project.repo_pushed_at.isoformat() if project.repo_pushed_at is not None else None,
                        "activity_stats": activity_stats,
                        "contributor_stats": contributor_stats,
                        "activity_score": activity_score,
                        "has_issues": project.repo_has_issues,
                        "has_wiki": project.repo_has_wiki,
                        "has_pages": project.repo_has_pages,
                        "attention": project.attention,
                        "metrics_data": project.metrics_data,
                        "health_score": health_score,
                        "attention_score": attention_score
                    })
                
                # 应用活跃度过滤
                if activity_level:
                    filtered_results = self._filter_by_activity_level(results, activity_level)
                else:
                    filtered_results = results
                
                # 应用星标数过滤
                if stars_level:
                    filtered_results = self._filter_by_stars_level(filtered_results, stars_level)
                
                # 应用分支数过滤
                if forks_level:
                    filtered_results = self._filter_by_forks_level(filtered_results, forks_level)
                
                # 应用健康度过滤
                if health_level:
                    filtered_results = self._filter_by_health_level(filtered_results, health_level)
                
                # 应用关注度过滤
                if attention_level:
                    filtered_results = self._filter_by_attention_level(filtered_results, attention_level)
                    logger.info(f"关注度级别过滤 {attention_level}: {len(results)} -> {len(filtered_results)} 个项目")
                elif sort_by == "attention":
                    filtered_results = self._filter_by_attention_level(filtered_results, "high")
                    logger.info(f"关注度排序(高): {len(results)} -> {len(filtered_results)} 个项目")
                elif sort_by == "attention_asc":
                    filtered_results = self._filter_by_attention_level(filtered_results, "low")
                    logger.info(f"关注度排序(低): {len(results)} -> {len(filtered_results)} 个项目")
                
                total_count = len(filtered_results)
                
                # 分页
                start_idx = (page - 1) * page_size
                end_idx = start_idx + page_size
                results = filtered_results[start_idx:end_idx]
            else:
                # 没有活跃度过滤，正常分页
                
                # 如果是活跃度排序、健康度排序、星标数排序、分支数排序或关注度排序，需要获取所有项目计算分数再排序
                if sort_by in ["activity", "activity_asc", "health", "health_asc", "stars", "stars_asc", "forks", "forks_asc", "attention", "attention_asc"]:
                    # 获取所有项目（不分页）
                    all_projects = query.limit(None).all()
                    
                    # 获取项目详细统计信息
                    results = []
                    for project in all_projects:
                        # 获取项目活动统计
                        activity_stats = self._get_project_activity_stats(str(project.project_key), time_range)
                        
                        # 获取贡献者统计
                        contributor_stats = self._get_contributor_stats(str(project.project_key), contributor_type)
                        
                        # 计算活跃度分数
                        activity_score = self._calculate_activity_score(activity_stats)
                        
                        # 尝试从metrics_data中获取更准确的活跃度分数
                        try:
                            metrics_data = getattr(project, 'metrics_data', None)
                            if metrics_data is not None and str(metrics_data).strip():
                                if isinstance(metrics_data, str):
                                    metrics_data = json.loads(metrics_data.replace(':NaN', ':null'))
                                else:
                                    metrics_data = metrics_data
                                
                                # 从Activity_Metrics中获取活跃度分数
                                if 'Activity_Metrics' in metrics_data:
                                    activity_metrics = metrics_data['Activity_Metrics']
                                    activity_latest = activity_metrics.get('activity_Latest')
                                    if activity_latest is not None and activity_latest != 'null':
                                        old_score = activity_score
                                        activity_score = float(activity_latest)
                                        logger.info(f"更新活跃度分数: {old_score} -> {activity_score} for project {project.project_key}")
                        except Exception as e:
                            logger.warning(f"从metrics_data获取活跃度分数时出错: {e}")
                        
                        # 提取健康度和关注度数值
                        health_score = self._extract_health_score(project)
                        attention_score = self._extract_attention_score(project)
                        
                        results.append({
                            "id": str(project.id),
                            "project_key": project.project_key,
                            "organization": project.organization,
                            "project_name": project.project_name,
                            "description": project.repo_description,
                            "language": project.repo_language,
                            "stars": project.repo_stargazers_count or 0,
                            "forks": project.repo_forks_count or 0,
                            "size": project.repo_size or 0,
                            "license": project.repo_license,
                            "created_at": project.repo_created_at.isoformat() if project.repo_created_at is not None else None,
                            "updated_at": project.repo_updated_at.isoformat() if project.repo_updated_at is not None else None,
                            "last_pushed": project.repo_pushed_at.isoformat() if project.repo_pushed_at is not None else None,
                            "activity_stats": activity_stats,
                            "contributor_stats": contributor_stats,
                            "activity_score": activity_score,
                            "has_issues": project.repo_has_issues,
                            "has_wiki": project.repo_has_wiki,
                            "has_pages": project.repo_has_pages,
                            "attention": project.attention,
                            "metrics_data": project.metrics_data,
                            "health_score": health_score,
                            "attention_score": attention_score
                        })
                    
                    # 按活跃度分数、健康度分数、星标数、分支数或关注度排序
                    if sort_by == "activity":
                        results.sort(key=lambda x: x["activity_score"], reverse=True)
                    elif sort_by == "activity_asc":
                        results.sort(key=lambda x: x["activity_score"])
                    elif sort_by == "health":
                        results.sort(key=lambda x: x["health_score"], reverse=True)
                        # 对于健康度排序，不应用健康度过滤，显示所有项目
                        pass
                    elif sort_by == "health_asc":
                        results.sort(key=lambda x: x["health_score"])
                        # 对于健康度升序排序，不应用健康度过滤，显示所有项目
                        pass
                    
                    # 应用星标数过滤
                    if stars_level:
                        results = self._filter_by_stars_level(results, stars_level)
                    
                    # 应用分支数过滤
                    if forks_level:
                        results = self._filter_by_forks_level(results, forks_level)
                    elif sort_by == "stars":
                        results.sort(key=lambda x: x["stars"], reverse=True)
                    elif sort_by == "stars_asc":
                        results.sort(key=lambda x: x["stars"])
                    elif sort_by == "forks":
                        results.sort(key=lambda x: x["forks"], reverse=True)
                    elif sort_by == "forks_asc":
                        results.sort(key=lambda x: x["forks"])
                    elif sort_by == "attention":
                        results.sort(key=lambda x: x["attention_score"], reverse=True)
                    elif sort_by == "attention_asc":
                        results.sort(key=lambda x: x["attention_score"])
                    
                    total_count = len(results)
                    
                    # 分页
                    start_idx = (page - 1) * page_size
                    end_idx = start_idx + page_size
                    results = results[start_idx:end_idx]
                else:
                    # 获取总数量
                    total_count = query.count()
                    
                    # 分页
                    offset = (page - 1) * page_size
                    projects = query.offset(offset).limit(page_size).all()
                    
                    # 获取项目详细统计信息
                    results = []
                    for project in projects:
                        # 获取项目活动统计
                        activity_stats = self._get_project_activity_stats(str(project.project_key), time_range)
                        
                        # 获取贡献者统计
                        contributor_stats = self._get_contributor_stats(str(project.project_key), contributor_type)
                        
                        # 计算活跃度分数
                        activity_score = self._calculate_activity_score(activity_stats)
                        
                        # 尝试从metrics_data中获取更准确的活跃度分数
                        try:
                            metrics_data = getattr(project, 'metrics_data', None)
                            if metrics_data is not None and str(metrics_data).strip():
                                if isinstance(metrics_data, str):
                                    metrics_data = json.loads(metrics_data.replace(':NaN', ':null'))
                                else:
                                    metrics_data = metrics_data
                                
                                # 从Activity_Metrics中获取活跃度分数
                                if 'Activity_Metrics' in metrics_data:
                                    activity_metrics = metrics_data['Activity_Metrics']
                                    activity_latest = activity_metrics.get('activity_Latest')
                                    if activity_latest is not None and activity_latest != 'null':
                                        old_score = activity_score
                                        activity_score = float(activity_latest)
                                        logger.info(f"更新活跃度分数: {old_score} -> {activity_score} for project {project.project_key}")
                        except Exception as e:
                            logger.warning(f"从metrics_data获取活跃度分数时出错: {e}")
                        
                        # 提取健康度和关注度数值
                        health_score = self._extract_health_score(project)
                        attention_score = self._extract_attention_score(project)
                        
                        results.append({
                            "id": str(project.id),
                            "project_key": project.project_key,
                            "organization": project.organization,
                            "project_name": project.project_name,
                            "description": project.repo_description,
                            "language": project.repo_language,
                            "stars": project.repo_stargazers_count or 0,
                            "forks": project.repo_forks_count or 0,
                            "size": project.repo_size or 0,
                            "license": project.repo_license,
                            "created_at": project.repo_created_at.isoformat() if project.repo_created_at is not None else None,
                            "updated_at": project.repo_updated_at.isoformat() if project.repo_updated_at is not None else None,
                            "last_pushed": project.repo_pushed_at.isoformat() if project.repo_pushed_at is not None else None,
                            "activity_stats": activity_stats,
                            "contributor_stats": contributor_stats,
                            "activity_score": activity_score,
                            "has_issues": project.repo_has_issues,
                            "has_wiki": project.repo_has_wiki,
                            "has_pages": project.repo_has_pages,
                            "attention": project.attention,
                            "metrics_data": project.metrics_data,
                            "health_score": health_score,
                            "attention_score": attention_score
                        })
            
            return {
                "results": results,
                "total_count": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_count + page_size - 1) // page_size
            }
            
        except Exception as e:
            logger.error(f"搜索项目时出错: {e}")
            return {
                "results": [],
                "total_count": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0
            }
    
    def get_project_details(self, project_key: str) -> Optional[Dict[str, Any]]:
        """
        获取项目详细信息
        
        Args:
            project_key: 项目key
            
        Returns:
            项目详细信息字典
        """
        try:
            # 添加调试日志
            logger.info(f"查询项目详情，project_key: {project_key}")
            
            project = self.db.query(Project).filter(Project.project_key == project_key).first()
            if not project:
                logger.warning(f"未找到项目: {project_key}")
                return None
            
            logger.info(f"找到项目: {project.project_key}")
            logger.info(f"项目类型: {type(project)}")
            
            # 获取最近事件
            recent_events = self.db.query(GitHubEvent).filter(
                GitHubEvent.project_key == project_key
            ).order_by(desc(GitHubEvent.created_at)).limit(20).all()
            
            # 获取项目活动趋势
            activity_trend = self._get_activity_trend(project_key)
            
            # 获取顶级贡献者
            top_contributors = self._get_top_contributors(project_key)
            
            # 获取项目活动统计
            activity_stats = self._get_project_activity_stats(project_key)
            
            # 计算活跃度分数
            activity_score = self._calculate_activity_score(activity_stats)
            logger.info(f"初始活跃度分数: {activity_score} for project {project_key}")
            
            # 尝试从metrics_data中获取更准确的活跃度分数
            try:
                metrics_data = getattr(project, 'metrics_data', None)
                if metrics_data is not None and str(metrics_data).strip():
                    if isinstance(metrics_data, str):
                        metrics_data = json.loads(metrics_data.replace(':NaN', ':null'))
                    else:
                        metrics_data = metrics_data
                    
                    # 从Activity_Metrics中获取活跃度分数
                    if 'Activity_Metrics' in metrics_data:
                        activity_metrics = metrics_data['Activity_Metrics']
                        activity_latest = activity_metrics.get('activity_Latest')
                        if activity_latest is not None and activity_latest != 'null':
                            old_score = activity_score
                            activity_score = float(activity_latest)
                            logger.info(f"更新活跃度分数: {old_score} -> {activity_score} for project {project.project_key}")
                            print(f"DEBUG: 更新活跃度分数: {old_score} -> {activity_score} for project {project.project_key}")
            except Exception as e:
                logger.warning(f"从metrics_data获取活跃度分数时出错: {e}")
            
            # 获取贡献者统计
            contributor_stats = self._get_contributor_stats(str(project.project_key))
            
            # 从metrics_data中提取四个特定指标
            contributor_metrics_data = {}
            try:
                metrics_data = getattr(project, 'metrics_data', None)
                if metrics_data is not None and str(metrics_data).strip():
                    if isinstance(metrics_data, str):
                        metrics_data = json.loads(metrics_data.replace(':NaN', ':null'))
                    else:
                        metrics_data = metrics_data
                    
                    # 从Contributor_Metrics中获取四个特定指标
                    if 'Contributor_Metrics' in metrics_data:
                        contributor_metrics = metrics_data['Contributor_Metrics']
                        
                        # 提取四个特定指标，处理NaN值
                        def safe_float(value):
                            if value is None or value == 'null':
                                return 0.0
                            try:
                                float_val = float(value)
                                return 0.0 if (isinstance(float_val, float) and (float_val != float_val)) else float_val
                            except (ValueError, TypeError):
                                return 0.0
                        
                        contributor_metrics_data = {
                            "new_contributors_latest": safe_float(contributor_metrics.get('new_contributors_Latest', 0)),
                            "new_contributors_average": safe_float(contributor_metrics.get('new_contributors_Average', 0)),
                            "inactive_contributors_latest": safe_float(contributor_metrics.get('inactive_contributors_Latest', 0)),
                            "inactive_contributors_average": safe_float(contributor_metrics.get('inactive_contributors_Average', 0))
                        }
                        
                        logger.info(f"从metrics_data提取贡献者指标: {contributor_metrics_data}")
            except Exception as e:
                logger.warning(f"从metrics_data提取贡献者指标时出错: {e}")
            
            # 不再使用top_contributors，设置为空列表
            metrics_contributors = []
            
            # 从metrics_data中提取Issue指标
            issue_metrics_data = {}
            try:
                metrics_data = getattr(project, 'metrics_data', None)
                if metrics_data is not None and str(metrics_data).strip():
                    if isinstance(metrics_data, str):
                        metrics_data = json.loads(metrics_data.replace(':NaN', ':null'))
                    else:
                        metrics_data = metrics_data
                    
                    # 从Issue_Metrics中获取Issue指标
                    if 'Issue_Metrics' in metrics_data:
                        issue_metrics = metrics_data['Issue_Metrics']
                        
                        # 安全转换函数
                        def safe_float(value):
                            if value is None or value == 'null':
                                return 0.0
                            try:
                                float_val = float(value)
                                return 0.0 if (isinstance(float_val, float) and (float_val != float_val)) else float_val
                            except (ValueError, TypeError):
                                return 0.0
                        
                        # 提取Issue指标
                        issue_metrics_data = {
                            "issues_new_latest": safe_float(issue_metrics.get('issues_new_Latest', 0)),
                            "issues_new_average": safe_float(issue_metrics.get('issues_new_Average', 0)),
                            "issues_closed_latest": safe_float(issue_metrics.get('issues_closed_Latest', 0)),
                            "issues_closed_average": safe_float(issue_metrics.get('issues_closed_Average', 0)),
                            "issue_comments_latest": int(issue_metrics.get('issue_comments_Latest', 0)) if issue_metrics.get('issue_comments_Latest') else 0,
                            "issue_comments_average": safe_float(issue_metrics.get('issue_comments_Average', 0)),
                            "issues_and_change_request_active_latest": int(issue_metrics.get('issues_and_change_request_active_Latest', 0)) if issue_metrics.get('issues_and_change_request_active_Latest') else 0,
                            "issues_and_change_request_active_average": safe_float(issue_metrics.get('issues_and_change_request_active_Average', 0))
                        }
                        
                        logger.info(f"从metrics_data提取Issue指标: {issue_metrics_data}")
            except Exception as e:
                logger.warning(f"从metrics_data提取Issue指标时出错: {e}")
            
            return {
                "project": {
                    "id": str(project.id),
                    "project_key": str(project.project_key),
                    "organization": str(project.organization),
                    "project_name": str(project.project_name),
                    "description": project.repo_description,
                    "language": project.repo_language,
                    "stars": project.repo_stargazers_count or 0,
                    "forks": project.repo_forks_count or 0,
                    "size": project.repo_size or 0,
                    "license": project.repo_license,
                    "default_branch": project.repo_default_branch,
                    "created_at": project.repo_created_at.isoformat() if project.repo_created_at is not None else None,
                    "updated_at": project.repo_updated_at.isoformat() if project.repo_updated_at is not None else None,
                    "last_pushed": project.repo_pushed_at.isoformat() if project.repo_pushed_at is not None else None,
                    "has_issues": project.repo_has_issues,
                    "has_projects": project.repo_has_projects,
                    "has_downloads": project.repo_has_downloads,
                    "has_wiki": project.repo_has_wiki,
                    "has_pages": project.repo_has_pages,
                    "attention": project.attention,
                    "metrics_data": project.metrics_data,
                    "activity_score": float(activity_score) if activity_score is not None else 0.0,
                    "contributor_stats": contributor_stats
                },
                "recent_events": [
                    {
                        "id": str(event.id),
                        "type": event.event_type,
                        "action": event.action,
                        "actor_login": event.actor_login,
                        "created_at": event.created_at.isoformat() if event.created_at is not None else None,
                        "issue_title": event.issue_title,
                        "pull_commits": event.pull_commits,
                        "pull_additions": event.pull_additions,
                        "pull_deletions": event.pull_deletions
                    }
                    for event in recent_events
                ],
                "activity_trend": activity_trend,
                "top_contributors": metrics_contributors,
                "activity_stats": activity_stats,
                "contributor_stats": contributor_stats,
                "contributor_metrics": contributor_metrics_data,
                "issue_metrics": issue_metrics_data,
                "activity_score": activity_score
            }
            
        except Exception as e:
            logger.error(f"获取项目详细信息时出错: {e}")
            return None
    
    def get_trending_projects(self, time_period: str = "monthly", limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取趋势项目
        
        Args:
            time_period: 时间周期 (monthly, quarterly, yearly)
            limit: 返回数量限制
            
        Returns:
            趋势项目列表
        """
        try:
            # 根据时间周期计算日期范围
            now = datetime.now()
            if time_period == "monthly":
                start_date = now.replace(day=1)
            elif time_period == "quarterly":
                current_quarter = (now.month - 1) // 3 + 1
                start_month = (current_quarter - 1) * 3 + 1
                start_date = now.replace(month=start_month, day=1)
            else:  # yearly
                start_date = now.replace(month=1, day=1)
            
            # 查询最近活跃的项目
            trending_projects = self.db.query(
                Project,
                func.count(GitHubEvent.id).label('recent_events'),
                func.count(func.distinct(GitHubEvent.actor_login)).label('unique_contributors')
            ).join(GitHubEvent).filter(
                GitHubEvent.created_at >= start_date
            ).group_by(
                Project.id
            ).order_by(
                desc('recent_events'),
                desc('unique_contributors')
            ).limit(limit).all()
            
            results = []
            for project, event_count, contributor_count in trending_projects:
                results.append({
                    "project_key": project.project_key,
                    "organization": project.organization,
                    "project_name": project.project_name,
                    "description": project.repo_description,
                    "language": project.repo_language,
                    "stars": project.repo_stargazers_count or 0,
                    "forks": project.repo_forks_count or 0,
                    "recent_events": event_count,
                    "unique_contributors": contributor_count,
                    "trend_score": self._calculate_trend_score(event_count, contributor_count)
                })
            
            return results
            
        except Exception as e:
            logger.error(f"获取趋势项目时出错: {e}")
            return []
    
    def get_language_stats(self) -> List[Dict[str, Any]]:
        """
        获取编程语言统计
        
        Returns:
            语言统计列表
        """
        try:
            language_stats = self.db.query(
                Project.repo_language,
                func.count(Project.id).label('project_count'),
                func.sum(Project.repo_stargazers_count).label('total_stars'),
                func.sum(Project.repo_forks_count).label('total_forks')
            ).filter(
                Project.repo_language.isnot(None)
            ).group_by(
                Project.repo_language
            ).order_by(
                desc('project_count')
            ).all()
            
            results = []
            for language, count, stars, forks in language_stats:
                results.append({
                    "language": language,
                    "project_count": count,
                    "total_stars": stars or 0,
                    "total_forks": forks or 0,
                    "avg_stars": (stars or 0) / count if count > 0 else 0,
                    "avg_forks": (forks or 0) / count if count > 0 else 0
                })
            
            return results
            
        except Exception as e:
            logger.error(f"获取语言统计时出错: {e}")
            return []
    
    def _get_project_activity_stats(self, project_key: str, time_range: Optional[Dict[str, str]] = None) -> Dict[str, int]:
        """获取项目活动统计"""
        try:
            # 首先尝试从metrics_data获取贡献者数据
            project = self.db.query(Project).filter(Project.project_key == project_key).first()
            if project and hasattr(project, 'metrics_data') and project.metrics_data is not None and str(project.metrics_data).strip():
                try:
                    if isinstance(project.metrics_data, str):
                        metrics_data = json.loads(project.metrics_data.replace(':NaN', ':null'))
                    else:
                        metrics_data = project.metrics_data
                    
                    # 从Contributor_Metrics获取数据
                    if 'Contributor_Metrics' in metrics_data:
                        contributor_metrics = metrics_data['Contributor_Metrics']
                        new_contributors = contributor_metrics.get('new_contributors_Latest', 0)
                        inactive_contributors = contributor_metrics.get('inactive_contributors_Latest', 0)
                        
                        # 计算总贡献者数量，处理NaN值
                        try:
                            new_contributors = 0 if (isinstance(new_contributors, float) and (new_contributors != new_contributors)) else new_contributors
                            inactive_contributors = 0 if (isinstance(inactive_contributors, float) and (inactive_contributors != inactive_contributors)) else inactive_contributors
                            total_contributors = new_contributors + inactive_contributors
                        except Exception:
                            total_contributors = 0
                            new_contributors = 0
                            inactive_contributors = 0
                        
                        # 从Activity_Metrics获取活动数据
                        total_events = 0
                        if 'Activity_Metrics' in metrics_data:
                            activity_metrics = metrics_data['Activity_Metrics']
                            # 尝试获取各种活动指标
                            for key in ['code_change_count_Latest', 'issue_opened_Latest', 'pull_request_opened_Latest', 'release_count_Latest']:
                                if key in activity_metrics and activity_metrics[key] is not None:
                                    try:
                                        value = activity_metrics[key]
                                        if isinstance(value, (int, float)) and not isinstance(value, bool):
                                            total_events += int(value)
                                    except (ValueError, TypeError):
                                        continue
                        
                        return {
                            "total_events": total_events,
                            "issues_events": 0,  # 这些数据在metrics_data中可能没有详细分类
                            "pull_request_events": 0,
                            "push_events": 0,
                            "fork_events": 0,
                            "release_events": 0,
                            "unique_contributors": int(total_contributors) if not (isinstance(total_contributors, float) and (total_contributors != total_contributors)) else 0,
                            "new_contributors": int(new_contributors) if not (isinstance(new_contributors, float) and (new_contributors != new_contributors)) else 0,
                            "inactive_contributors": int(inactive_contributors) if not (isinstance(inactive_contributors, float) and (inactive_contributors != inactive_contributors)) else 0
                        }
                except Exception as e:
                    logger.warning(f"从metrics_data解析贡献者数据时出错: {e}")
            
            # 如果metrics_data不可用，回退到github_events表
            query = self.db.query(GitHubEvent).filter_by(project_key=project_key)
            
            if time_range:
                start_date_str = time_range.get('start_date')
                end_date_str = time_range.get('end_date')
                
                if start_date_str:
                    start_date = datetime.fromisoformat(start_date_str)
                    query = query.filter(GitHubEvent.created_at >= start_date)
                if end_date_str:
                    end_date = datetime.fromisoformat(end_date_str)
                    query = query.filter(GitHubEvent.created_at <= end_date)
            
            events = query.all()
            
            stats = {
                "total_events": len(events),
                "issues_events": len([e for e in events if str(e.event_type) == "IssuesEvent"]),
                "pull_request_events": len([e for e in events if str(e.event_type) == "PullRequestEvent"]),
                "push_events": len([e for e in events if str(e.event_type) == "PushEvent"]),
                "fork_events": len([e for e in events if str(e.event_type) == "ForkEvent"]),
                "release_events": len([e for e in events if str(e.event_type) == "ReleaseEvent"]),
                "unique_contributors": len(set([str(e.actor_login) for e in events if e.actor_login is not None]))
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取项目活动统计时出错: {e}")
            return {"total_events": 0}
    
    def _get_contributor_stats(self, project_key: str, contributor_type: str = "all") -> Dict[str, Any]:
        """获取贡献者统计"""
        try:
            query = self.db.query(GitHubEvent).filter_by(project_key=project_key)
            
            # 过滤贡献者类型
            if contributor_type == "human":
                query = query.filter(~func.lower(GitHubEvent.actor_login).like('%[bot]%'))
            elif contributor_type == "bot":
                query = query.filter(func.lower(GitHubEvent.actor_login).like('%[bot]%'))
            
            events = query.all()
            
            contributor_events = {}
            for event in events:
                if event.actor_login is not None:
                    login = str(event.actor_login)
                    if login not in contributor_events:
                        contributor_events[login] = 0
                    contributor_events[login] += 1
            
            # 排序并获取统计信息
            sorted_contributors = sorted(contributor_events.items(), key=lambda x: x[1], reverse=True)
            
            # 准备顶级贡献者对象
            top_contributor = None
            if sorted_contributors:
                top_contributor = {
                    "name": sorted_contributors[0][0],
                    "contributions": sorted_contributors[0][1]
                }
            
            stats = {
                "total_contributors": len(contributor_events),
                "top_contributor": top_contributor,
                "median_contributions": 0,
                "total_events": len(events)
            }
            
            if sorted_contributors:
                contributions = [count for _, count in sorted_contributors]
                median_idx = len(contributions) // 2
                stats["median_contributions"] = contributions[median_idx]
            
            return stats
            
        except Exception as e:
            logger.error(f"获取贡献者统计时出错: {e}")
            return {"total_contributors": 0}
    
    def _calculate_activity_score(self, activity_stats: Dict[str, int]) -> float:
        """计算活跃度分数"""
        try:
            total_events = activity_stats.get("total_events", 0)
            unique_contributors = activity_stats.get("unique_contributors", 0)
            
            # 改进的活跃度分数计算 - 更合理的权重和缩放
            # 排除DeleteEvent，因为它不代表积极的活动
            positive_events = (
                activity_stats.get("issues_events", 0) +
                activity_stats.get("pull_request_events", 0) +
                activity_stats.get("push_events", 0) +
                activity_stats.get("fork_events", 0) +
                activity_stats.get("release_events", 0)
            )
            
            # 基于积极事件和贡献者数量计算活跃度
            score = (positive_events * 2.0) + (unique_contributors * 5.0)
            return round(score, 2)
            
        except Exception:
            return 0.0
    
    def _filter_by_activity_level(self, results: List[Dict], activity_level: str) -> List[Dict]:
        """根据活跃度级别过滤结果"""
        try:
            # 获取所有活跃度分数用于动态计算阈值
            if not results:
                return results
                
            scores = [r["activity_score"] for r in results if r["activity_score"] is not None]
            if not scores:
                return results
                
            max_score = max(scores)
            min_score = min(scores)
            
            # 动态计算阈值：基于实际数据分布
            high_threshold = max_score * 0.7      # 前30%为高活跃度
            medium_threshold = max_score * 0.3   # 30%-70%为中等活跃度
            low_threshold = max_score * 0.1      # 后10%为低活跃度
            
            logger.info(f"活跃度阈值 - High: >{high_threshold:.2f}, Medium: {medium_threshold:.2f}-{high_threshold:.2f}, Low: ≤{medium_threshold:.2f}")
            
            if activity_level == "high":
                filtered = [r for r in results if r["activity_score"] > high_threshold]
                logger.info(f"High活跃度过滤: {len(results)} -> {len(filtered)} 个项目")
                return filtered
            elif activity_level == "medium":
                filtered = [r for r in results if medium_threshold < r["activity_score"] <= high_threshold]
                logger.info(f"Medium活跃度过滤: {len(results)} -> {len(filtered)} 个项目")
                return filtered
            elif activity_level == "low":
                filtered = [r for r in results if r["activity_score"] <= medium_threshold]
                logger.info(f"Low活跃度过滤: {len(results)} -> {len(filtered)} 个项目")
                return filtered
            else:
                return results
                
        except Exception as e:
            logger.error(f"活跃度过滤时出错: {e}")
            return results
    
    def _filter_by_health_level(self, results: List[Dict], health_level: str) -> List[Dict]:
        """根据健康度级别过滤结果"""
        try:
            # 获取所有健康度分数用于动态计算阈值
            if not results:
                return results
                
            scores = [r["health_score"] for r in results if r["health_score"] is not None]
            if not scores:
                return results
                
            max_score = max(scores)
            min_score = min(scores)
            
            # 动态计算阈值：基于实际数据分布
            high_threshold = max_score * 0.7      # 前30%为高健康度
            medium_threshold = max_score * 0.3   # 30%-70%为中等健康度
            low_threshold = max_score * 0.1      # 后10%为低健康度
            
            logger.info(f"健康度阈值 - High: >{high_threshold:.2f}, Medium: {medium_threshold:.2f}-{high_threshold:.2f}, Low: ≤{medium_threshold:.2f}")
            
            if health_level == "high":
                filtered = [r for r in results if r["health_score"] > high_threshold]
                logger.info(f"High健康度过滤: {len(results)} -> {len(filtered)} 个项目")
                return filtered
            elif health_level == "medium":
                filtered = [r for r in results if medium_threshold < r["health_score"] <= high_threshold]
                logger.info(f"Medium健康度过滤: {len(results)} -> {len(filtered)} 个项目")
                return filtered
            elif health_level == "low":
                filtered = [r for r in results if r["health_score"] <= medium_threshold]
                logger.info(f"Low健康度过滤: {len(results)} -> {len(filtered)} 个项目")
                return filtered
            else:
                return results
                
        except Exception as e:
            logger.error(f"健康度过滤时出错: {e}")
            return results
    
    def _filter_by_stars_level(self, results: List[Dict], stars_level: str) -> List[Dict]:
        """根据星标数级别过滤结果"""
        try:
            # 获取所有星标数用于动态计算阈值
            if not results:
                return results
            
            stars_counts = [r["stars"] for r in results if r["stars"] is not None]
            if not stars_counts:
                return results
            
            max_stars = max(stars_counts)
            min_stars = min(stars_counts)
            
            # 使用预定义的阈值（基于之前分析的结果）
            low_threshold = 56    # < 56 为低星标数
            high_threshold = 402  # > 402 为高星标数
            
            logger.info(f"星标数阈值 - High: >{high_threshold}, Medium: {low_threshold}-{high_threshold}, Low: ≤{low_threshold}")
            
            if stars_level == "high":
                filtered = [r for r in results if r["stars"] > high_threshold]
                logger.info(f"High星标数过滤: {len(results)} -> {len(filtered)} 个项目")
                return filtered
            elif stars_level == "medium":
                filtered = [r for r in results if low_threshold < r["stars"] <= high_threshold]
                logger.info(f"Medium星标数过滤: {len(results)} -> {len(filtered)} 个项目")
                return filtered
            elif stars_level == "low":
                filtered = [r for r in results if r["stars"] <= low_threshold]
                logger.info(f"Low星标数过滤: {len(results)} -> {len(filtered)} 个项目")
                return filtered
            else:
                return results
                
        except Exception as e:
            logger.error(f"星标数过滤时出错: {e}")
            return results
    
    def _filter_by_forks_level(self, results: List[Dict], forks_level: str) -> List[Dict]:
        """根据分支数级别过滤结果"""
        try:
            # 获取所有分支数用于动态计算阈值
            if not results:
                return results
            
            forks_counts = [r["forks"] for r in results if r["forks"] is not None]
            if not forks_counts:
                return results
            
            max_forks = max(forks_counts)
            min_forks = min(forks_counts)
            
            # 使用预定义的阈值（基于之前分析的结果）
            low_threshold = 33    # < 33 为低分支数
            high_threshold = 142  # > 142 为高分支数
            
            logger.info(f"分支数阈值 - High: >{high_threshold}, Medium: {low_threshold}-{high_threshold}, Low: ≤{low_threshold}")
            
            if forks_level == "high":
                filtered = [r for r in results if r["forks"] > high_threshold]
                logger.info(f"High分支数过滤: {len(results)} -> {len(filtered)} 个项目")
                return filtered
            elif forks_level == "medium":
                filtered = [r for r in results if low_threshold < r["forks"] <= high_threshold]
                logger.info(f"Medium分支数过滤: {len(results)} -> {len(filtered)} 个项目")
                return filtered
            elif forks_level == "low":
                filtered = [r for r in results if r["forks"] <= low_threshold]
                logger.info(f"Low分支数过滤: {len(results)} -> {len(filtered)} 个项目")
                return filtered
            else:
                return results
                
        except Exception as e:
            logger.error(f"分支数过滤时出错: {e}")
            return results
    
    def _filter_by_attention_level(self, results: List[Dict], attention_level: str) -> List[Dict]:
        """根据关注度级别过滤结果"""
        try:
            # 获取所有关注度分数用于动态计算阈值
            if not results:
                return results
            
            # 提取关注度分数
            attention_scores = []
            for r in results:
                if "attention_score" in r and r["attention_score"] is not None:
                    attention_scores.append(r["attention_score"])
            
            if not attention_scores:
                logger.warning(f"没有找到有效的关注度分数，返回所有结果")
                return results
            
            # 排序以计算百分位数
            attention_scores_sorted = sorted(attention_scores)
            total_count = len(attention_scores_sorted)
            
            # 使用百分位数设置阈值
            # 高关注度：前20%的项目
            # 中关注度：20%-80%的项目
            # 低关注度：后20%的项目
            high_index = int(total_count * 0.8)  # 80%位置，高关注度是前20%
            medium_low_index = int(total_count * 0.2)  # 20%位置
            
            # 确保索引在有效范围内
            high_index = min(high_index, total_count - 1)
            medium_low_index = min(medium_low_index, total_count - 1)
            
            high_threshold = attention_scores_sorted[high_index]
            medium_threshold = attention_scores_sorted[medium_low_index]
            
            logger.info(f"关注度分数范围: {attention_scores_sorted[0]:.2f} - {attention_scores_sorted[-1]:.2f}")
            logger.info(f"关注度阈值 - High: >{high_threshold:.2f}, Medium: {medium_threshold:.2f}-{high_threshold:.2f}, Low: ≤{medium_threshold:.2f}")
            
            if attention_level == "high":
                filtered = [r for r in results if r.get("attention_score", 0) > high_threshold]
                logger.info(f"High关注度过滤: {len(results)} -> {len(filtered)} 个项目")
                return filtered
            elif attention_level == "medium":
                filtered = [r for r in results if medium_threshold < r.get("attention_score", 0) <= high_threshold]
                logger.info(f"Medium关注度过滤: {len(results)} -> {len(filtered)} 个项目")
                return filtered
            elif attention_level == "low":
                filtered = [r for r in results if r.get("attention_score", 0) <= medium_threshold]
                logger.info(f"Low关注度过滤: {len(results)} -> {len(filtered)} 个项目")
                return filtered
            else:
                return results
                
        except Exception as e:
            logger.error(f"关注度过滤时出错: {e}")
            return results
    
    def _get_activity_trend(self, project_key: str) -> List[Dict[str, Any]]:
        """获取项目活动趋势"""
        try:
            activity_data = self.db.query(ProjectActivity).filter_by(
                project_key=project_key
            ).order_by(
                ProjectActivity.year, ProjectActivity.month
            ).all()
            
            trend = []
            for activity in activity_data:
                trend.append({
                    "year": activity.year,
                    "month": activity.month,
                    "total_events": activity.total_events,
                    "unique_contributors": activity.unique_contributors
                })
            
            return trend
            
        except Exception as e:
            logger.error(f"获取活动趋势时出错: {e}")
            return []
    
    def _get_top_contributors(self, project_key: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取顶级贡献者"""
        try:
            contributor_stats = self.db.query(
                GitHubEvent.actor_login,
                func.count(GitHubEvent.id).label('event_count'),
                func.min(GitHubEvent.created_at).label('first_event'),
                func.max(GitHubEvent.created_at).label('last_event')
            ).filter(
                GitHubEvent.project_key == project_key
            ).filter(
                GitHubEvent.actor_login.isnot(None)
            ).group_by(
                GitHubEvent.actor_login
            ).order_by(
                desc('event_count')
            ).limit(limit).all()
            
            contributors = []
            for login, count, first_event, last_event in contributor_stats:
                contributors.append({
                    "login": login,
                    "event_count": count,
                    "first_event": first_event.isoformat() if first_event is not None else None,
                    "last_event": last_event.isoformat() if last_event is not None else None
                })
            
            return contributors
            
        except Exception as e:
            logger.error(f"获取顶级贡献者时出错: {e}")
            return []
    
    def _calculate_trend_score(self, event_count: int, contributor_count: int) -> float:
        """计算趋势分数"""
        try:
            # 简单的趋势分数计算
            score = (event_count * 0.7) + (contributor_count * 0.3)
            return round(score, 2)
            
        except Exception:
            return 0.0
    
    def _extract_health_score(self, project) -> float:
        """从metrics_data中提取健康度分数"""
        try:
            metrics_data = getattr(project, 'metrics_data', None)
            if metrics_data is None or not str(metrics_data).strip():
                return 0.0
            
            # 解析JSON数据
            if isinstance(metrics_data, str):
                metrics_data = json.loads(metrics_data.replace(':NaN', ':null'))
            else:
                metrics_data = metrics_data
            
            # 从Project_Health_Metrics中获取健康度指标
            if 'Project_Health_Metrics' in metrics_data:
                health_metrics = metrics_data['Project_Health_Metrics']
                
                # 综合健康度分数：结合bus_factor和openrank
                bus_factor = float(health_metrics.get('bus_factor_Latest', 0))
                openrank = float(health_metrics.get('openrank_Latest', 0))
                technical_fork = float(health_metrics.get('technical_fork_Latest', 0))
                
                # 计算综合健康度分数
                health_score = (bus_factor * 0.4) + (openrank * 0.4) + (technical_fork * 0.2)
                return round(health_score, 2)
            
            return 0.0
            
        except Exception as e:
            logger.warning(f"提取健康度分数时出错: {e}")
            return 0.0
    
    def _extract_attention_score(self, project) -> float:
        """从attention字段中提取关注度分数"""
        try:
            attention_data = getattr(project, 'attention', None)
            if attention_data is None or not str(attention_data).strip():
                logger.warning(f"项目 {project.project_key} 的attention字段为空")
                return 0.0
            
            # 解析JSON数据
            if isinstance(attention_data, str):
                attention_data = json.loads(attention_data.replace(':NaN', ':null'))
            else:
                attention_data = attention_data
            
            # 获取最新关注度值
            attention_latest = float(attention_data.get('attention_Latest', 0))
            score = round(attention_latest, 2)
            logger.info(f"项目 {project.project_key} 的关注度分数: {score}")
            return score
            
        except Exception as e:
            logger.warning(f"提取关注度分数时出错: {e}")
            return 0.0
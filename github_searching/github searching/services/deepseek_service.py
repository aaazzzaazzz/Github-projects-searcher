import openai
import json
import logging
from typing import List, Dict, Any, Optional, Union
from config import settings
from sqlalchemy.orm import Session
from project.models import Project, GitHubEvent, Contributor, ProjectActivity

logger = logging.getLogger(__name__)

class DeepSeekService:
    """DeepSeek API服务类"""
    
    def __init__(self):
        """初始化DeepSeek服务"""
        self.client = openai.OpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_api_base
        )
        self.model = settings.deepseek_model
    
    async def generate_search_query(self, user_query: str) -> Dict[str, Any]:
        """
        将用户自然语言查询转换为结构化搜索查询
        
        Args:
            user_query: 用户的自然语言查询
            
        Returns:
            结构化的搜索查询字典
        """
        try:
            # 检查是否包含中文字符
            has_chinese = any('\u4e00' <= char <= '\u9fff' for char in user_query)
            
            if has_chinese:
                # 对于中文查询，使用简化的提示，避免语言过滤
                prompt = f"""
                你是一个GitHub项目搜索引擎的查询分析器。请将用户的中文自然语言查询转换为结构化的搜索查询。

                用户查询: "{user_query}"

                重要：由于数据库中的语言字段不完整，请将查询主要转换为关键词搜索，而不是语言过滤。

                请分析查询并返回JSON格式的搜索参数，包含以下字段：
                - keywords: 关键词列表（重要：请提取英文关键词，如果是编程语言相关，请提取对应的英文名称）
                - languages: [] （重要：请始终设为空数组）
                - event_types: 事件类型列表 (如: IssuesEvent, PullRequestEvent, PushEvent等)
                - time_range: 时间范围 (start_date, end_date)
                - activity_level: 活跃度级别 (high, medium, low)
                - health_level: 健康度级别 (high, medium, low)
                - stars_level: 星标数级别 (high, medium, low)
                - forks_level: 分支数级别 (high, medium, low)
                - sort_by: 排序方式 (stars, forks, activity, recent, health)
                - contributor_type: 贡献者类型 (human, bot, all)

                特殊规则：
                - 如果查询包含"Python项目"，请提取关键词为["python"]
                - 如果查询包含"Java项目"，请提取关键词为["java"]
                - 如果查询包含"JavaScript项目"，请提取关键词为["javascript"]
                - 如果查询包含其他编程语言，请提取对应的英文名称
                - 如果查询包含"高活跃度"、"高活跃项目"、"活跃度高的项目"、"最活跃的项目"等词汇，请设置activity_level为"high"
                - 如果查询包含"中活跃度"、"中等活跃项目"、"活跃度中等的项目"等词汇，请设置activity_level为"medium"
                - 如果查询包含"低活跃度"、"低活跃项目"、"活跃度较低的项目"等词汇，请设置activity_level为"low"并设置sort_by为"activity_asc"
                - 如果查询包含"活跃项目"、"热门项目"、"流行项目"、"活跃度"等词汇，请设置sort_by为"activity"并设置activity_level为null
                - 如果查询包含"高星标数"、"多星标"、"stars多"、"星标多"、"星标高"、"高星标"等词汇，请设置stars_level为"high"并设置sort_by为"stars"
                - 如果查询包含"中星标数"、"中等星标"、"星标中等"等词汇，请设置stars_level为"medium"并设置sort_by为"stars"
                - 如果查询包含"低星标数"、"少星标"、"星标少"、"低星标"等词汇，请设置stars_level为"low"并设置sort_by为"stars_asc"
                - 如果查询包含"星标数"、"星标"、"stars"等词汇，请设置sort_by为"stars"并设置stars_level为null
                - 如果查询包含"高分支数"、"多分支"、"分支多"、"分支高"、"高分支"等词汇，请设置forks_level为"high"并设置sort_by为"forks"
                - 如果查询包含"中分支数"、"中等分支"、"分支中等"等词汇，请设置forks_level为"medium"并设置sort_by为"forks"
                - 如果查询包含"低分支数"、"少分支"、"分支少"、"低分支"等词汇，请设置forks_level为"low"并设置sort_by为"forks_asc"
                - 如果查询包含"分支数"、"分支"、"forks"等词汇，请设置sort_by为"forks"并设置forks_level为null
                - 如果查询包含"高健康度"、"高健康项目"、"健康状况良好"、"代码质量高"等词汇，请设置sort_by为"health"并设置health_level为"high"
                - 如果查询包含"低健康度"、"低健康项目"、"健康状况差"、"代码质量差"、"维护不良"等词汇，请设置sort_by为"health_asc"并设置health_level为"low"
                - 如果查询包含"中健康度"、"中等健康项目"、"健康状况中等"等词汇，请设置sort_by为"health"并设置health_level为"medium"
                - 如果查询包含"健康度"、"项目健康"、"代码质量"、"维护良好"、"健康状况"等词汇，请设置sort_by为"health"并设置health_level为null
                - 如果查询包含"高关注度"、"多关注"、"关注多"、"关注高"、"高关注"等词汇，请设置attention_level为"high"并设置sort_by为"attention"
                - 如果查询包含"中关注度"、"中等关注度"、"关注度中等"等词汇，请设置attention_level为"medium"并设置sort_by为"attention"
                - 如果查询包含"低关注度"、"少关注"、"关注少"、"低关注"等词汇，请设置attention_level为"low"并设置sort_by为"attention_asc"
                - 如果查询包含"关注度"、"关注"、"attention"等词汇，请设置sort_by为"attention"并设置attention_level为null
                - 如果查询明确要求查找特定活跃度级别的项目，请优先满足活跃度要求

                示例输出格式:
                {{
                    "keywords": ["python"],
                    "languages": [],
                    "event_types": [],
                    "time_range": null,
                    "activity_level": null,
                    "health_level": null,
                    "stars_level": null,
                    "forks_level": null,
                    "sort_by": "relevance",
                    "contributor_type": "all"
                }}

                如果查询中不包含某些信息，请将对应字段设为null或空列表。
                """
            else:
                # 英文查询使用原有逻辑
                prompt = f"""
                你是一个GitHub项目搜索引擎的查询分析器。请将用户的自然语言查询转换为结构化的搜索查询。

                用户查询: "{user_query}"

                请分析查询并返回JSON格式的搜索参数，包含以下字段：
                - keywords: 关键词列表
                - languages: 编程语言列表
                - event_types: 事件类型列表 (如: IssuesEvent, PullRequestEvent, PushEvent等)
                - time_range: 时间范围 (start_date, end_date)
                - activity_level: 活跃度级别 (high, medium, low)
                - health_level: 健康度级别 (high, medium, low)
                - stars_level: 星标数级别 (high, medium, low)
                - forks_level: 分支数级别 (high, medium, low)
                - sort_by: 排序方式 (stars, forks, activity, recent, health)
                - contributor_type: 贡献者类型 (human, bot, all)

                示例输出格式:
                {{
                    "keywords": ["machine learning", "AI"],
                    "languages": ["Python", "JavaScript"],
                    "event_types": ["IssuesEvent", "PullRequestEvent"],
                    "time_range": {{
                        "start_date": "2020-01-01",
                        "end_date": "2023-03-31"
                    }},
                    "activity_level": null,
                    "health_level": null,
                    "stars_level": null,
                    "forks_level": null,
                    "sort_by": "stars",
                    "contributor_type": "all"
                }}

                如果查询中不包含某些信息，请将对应字段设为null或空列表。
                """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的GitHub项目搜索查询分析器。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            if content is not None:
                content = content.strip()
            else:
                content = ""
            
            # 清理Markdown格式的JSON
            if content.startswith('```json'):
                content = content[7:]  # 移除```json
            if content.startswith('```'):
                content = content[3:]   # 移除```
            if content.endswith('```'):
                content = content[:-3]   # 移除```
            content = content.strip()
            
            # 尝试解析JSON
            try:
                search_params = json.loads(content)
                logger.info(f"DeepSeek解析结果: {search_params}")
                
                # 对于中文查询的特殊处理
                if any('\u4e00' <= char <= '\u9fff' for char in user_query):
                    # 检查关键词是否包含中文字符
                    keywords = search_params.get('keywords', [])
                    has_chinese_keywords = any(any('\u4e00' <= char <= '\u9fff' for char in kw) for kw in keywords)
                    
                    # 如果关键词包含中文或为空，进行特殊处理
                    if has_chinese_keywords or len(keywords) == 0:
                        logger.warning(f"中文查询解析结果包含中文或为空，进行特殊处理: {keywords}")
                        
                        # 编程语言映射
                        lang_mapping = {
                            'python项目': ['python'],
                            'java项目': ['java'],
                            'javascript项目': ['javascript'],
                            'js项目': ['javascript'],
                            'typescript项目': ['typescript'],
                            'go项目': ['go'],
                            'golang项目': ['go'],
                            'rust项目': ['rust'],
                            'c++项目': ['cpp', 'c++'],
                            'c项目': ['c'],
                            'php项目': ['php'],
                            'ruby项目': ['ruby'],
                            'swift项目': ['swift'],
                            'kotlin项目': ['kotlin'],
                            'scala项目': ['scala'],
                            'r项目': ['r'],
                            'matlab项目': ['matlab'],
                            'vue项目': ['vue'],
                            'react项目': ['react'],
                            'angular项目': ['angular'],
                            'django项目': ['django'],
                            'flask项目': ['flask'],
                            'spring项目': ['spring'],
                            'laravel项目': ['laravel'],
                            'node项目': ['nodejs', 'node'],
                            'python': ['python'],
                            'java': ['java'],
                            'javascript': ['javascript'],
                            'typescript': ['typescript'],
                            'go': ['go'],
                            'rust': ['rust'],
                            'c++': ['cpp', 'c++'],
                            'c': ['c'],
                            'php': ['php'],
                            'ruby': ['ruby'],
                            'swift': ['swift'],
                            'kotlin': ['kotlin'],
                            'scala': ['scala'],
                            'r': ['r'],
                            'matlab': ['matlab'],
                            'vue': ['vue'],
                            'react': ['react'],
                            'angular': ['angular'],
                            'django': ['django'],
                            'flask': ['flask'],
                            'spring': ['spring'],
                            'laravel': ['laravel'],
                            'nodejs': ['nodejs', 'node']
                        }
                        
                        # 活跃度映射
                        activity_mapping = {
                            '高活跃度': 'high',
                            '高活跃项目': 'high',
                            '活跃度高': 'high',
                            '最活跃的项目': 'high',
                            '活跃度高的项目': 'high',
                            '超活跃': 'high',
                            '非常活跃': 'high',
                            '中活跃度': 'medium',
                            '中等活跃项目': 'medium',
                            '活跃度中等': 'medium',
                            '活跃度中等的项目': 'medium',
                            '普通活跃': 'medium',
                            '低活跃度': 'low',
                            '低活跃项目': 'low',
                            '活跃度低': 'low',
                            '活跃度较低的项目': 'low',
                            '不活跃': 'low'
                        }
                        
                        # 健康度映射
                        health_mapping = {
                            '高健康度': 'high',
                            '高健康项目': 'high',
                            '健康状况良好': 'high',
                            '代码质量高': 'high',
                            '维护良好': 'high',
                            '健康度高': 'high',
                            '中健康度': 'medium',
                            '中等健康项目': 'medium',
                            '健康状况中等': 'medium',
                            '健康度中等': 'medium',
                            '低健康度': 'low',
                            '低健康项目': 'low',
                            '健康状况差': 'low',
                            '代码质量差': 'low',
                            '维护不良': 'low',
                            '健康度低': 'low'
                        }
                        
                        # 星标数映射
                        stars_mapping = {
                            '高星标数': 'high',
                            '多星标': 'high',
                            'stars多': 'high',
                            '星标多': 'high',
                            '星标高': 'high',
                            '高星标': 'high',
                            '星标数高': 'high',
                            '中星标数': 'medium',
                            '中等星标': 'medium',
                            '星标中等': 'medium',
                            '星标数中等': 'medium',
                            '低星标数': 'low',
                            '少星标': 'low',
                            '星标少': 'low',
                            '低星标': 'low',
                            '星标数低': 'low'
                        }
                        
                        # 分支数映射
                        forks_mapping = {
                            '高分支数': 'high',
                            '多分支': 'high',
                            '分支多': 'high',
                            '分支高': 'high',
                            '高分支': 'high',
                            '分支数高': 'high',
                            '中分支数': 'medium',
                            '中等分支': 'medium',
                            '分支中等': 'medium',
                            '分支数中等': 'medium',
                            '低分支数': 'low',
                            '少分支': 'low',
                            '分支少': 'low',
                            '低分支': 'low',
                            '分支数低': 'low'
                        }
                        
                        # 关注度映射
                        attention_mapping = {
                            '高关注度': 'high',
                            '多关注': 'high',
                            '关注多': 'high',
                            '关注高': 'high',
                            '高关注': 'high',
                            '关注度高': 'high',
                            '中关注度': 'medium',
                            '中等关注度': 'medium',
                            '关注度中等': 'medium',
                            '低关注度': 'low',
                            '少关注': 'low',
                            '关注少': 'low',
                            '低关注': 'low',
                            '关注度低': 'low'
                        }
                        
                        # 通用关键词映射 - 只设置排序方式，不设置级别过滤
                        general_mapping = {
                            '活跃度': 'activity',
                            '健康度': 'health',
                            '星标数': 'stars',
                            '分支数': 'forks',
                            '关注度': 'attention'
                        }
                         
                        # 查找匹配的编程语言
                        query_lower = user_query.lower()
                        mapped_keywords = []
                        for chinese_term, english_keywords in lang_mapping.items():
                            if chinese_term in query_lower:
                                mapped_keywords.extend(english_keywords)
                                break
                         
                        # 首先检查具体的级别映射
                        has_level_mapping = False
                        
                        # 查找匹配的活跃度 - 修复匹配逻辑
                        mapped_activity = None
                        for chinese_term, activity_level in activity_mapping.items():
                            if chinese_term in query_lower:  # 修复：使用包含匹配而不是精确匹配
                                mapped_activity = activity_level
                                has_level_mapping = True
                                break
                        
                        # 如果找到活跃度映射，设置活跃度级别和排序方式
                        if mapped_activity:
                            logger.info(f"使用映射活跃度: {mapped_activity}")
                            search_params['activity_level'] = mapped_activity
                            search_params['sort_by'] = 'activity'
                        
                        # 查找匹配的健康度
                        mapped_health = None
                        for chinese_term, health_level in health_mapping.items():
                            if chinese_term in query_lower:
                                mapped_health = health_level
                                has_level_mapping = True
                                break
                        
                        # 如果找到健康度映射，设置健康度级别和排序方式
                        if mapped_health:
                            logger.info(f"使用映射健康度: {mapped_health}")
                            search_params['health_level'] = mapped_health
                            search_params['sort_by'] = 'health'
                        
                        # 查找匹配的星标数
                        mapped_stars = None
                        for chinese_term, stars_level in stars_mapping.items():
                            if chinese_term in query_lower:
                                mapped_stars = stars_level
                                has_level_mapping = True
                                break
                        
                        # 如果找到星标数映射，设置星标数级别和排序方式
                        if mapped_stars:
                            logger.info(f"使用映射星标数: {mapped_stars}")
                            search_params['stars_level'] = mapped_stars
                            search_params['sort_by'] = 'stars'
                        
                        # 查找匹配的分支数
                        mapped_forks = None
                        for chinese_term, forks_level in forks_mapping.items():
                            if chinese_term in query_lower:
                                mapped_forks = forks_level
                                has_level_mapping = True
                                break
                        
                        # 如果找到分支数映射，设置分支数级别和排序方式
                        if mapped_forks:
                            logger.info(f"使用映射分支数: {mapped_forks}")
                            search_params['forks_level'] = mapped_forks
                            search_params['sort_by'] = 'forks'
                        
                        # 查找匹配的关注度
                        mapped_attention = None
                        for chinese_term, attention_level in attention_mapping.items():
                            if chinese_term in query_lower:
                                mapped_attention = attention_level
                                has_level_mapping = True
                                break
                        
                        # 如果找到关注度映射，设置关注度级别和排序方式
                        if mapped_attention:
                            logger.info(f"使用映射关注度: {mapped_attention}")
                            search_params['attention_level'] = mapped_attention
                            search_params['sort_by'] = 'attention'
                        
                        # 如果没有找到级别映射，则检查通用关键词映射
                        if not has_level_mapping:
                            general_match = None
                            for chinese_term, sort_type in general_mapping.items():
                                if chinese_term in query_lower:
                                    general_match = sort_type
                                    break
                            
                            # 如果找到通用关键词匹配，只设置排序方式，不设置级别过滤
                            if general_match:
                                logger.info(f"使用通用关键词映射，设置排序为: {general_match}")
                                search_params['sort_by'] = general_match
                                # 确保级别过滤为null
                                search_params['activity_level'] = None
                                search_params['health_level'] = None
                                search_params['stars_level'] = None
                                search_params['forks_level'] = None
                                search_params['attention_level'] = None
                        
                        # 如果找到映射，使用映射的关键词
                        if mapped_keywords:
                            logger.info(f"使用映射关键词: {mapped_keywords}")
                            search_params['keywords'] = mapped_keywords
                       
                        # 强制设置语言为空，避免语言过滤
                        search_params['languages'] = []
                    
                return search_params
            except json.JSONDecodeError:
                # 如果JSON解析失败，返回基础查询
                logger.warning(f"JSON解析失败，使用基础查询: {user_query}")
                return {
                    "keywords": [user_query],
                    "languages": [],
                    "event_types": [],
                    "time_range": None,
                    "activity_level": None,
                    "health_level": None,
                    "stars_level": None,
                    "forks_level": None,
                    "sort_by": "relevance",
                    "contributor_type": "all"
                }
                
        except Exception as e:
            logger.error(f"生成搜索查询时出错: {e}")
            return {
                "keywords": [user_query],
                "languages": [],
                "event_types": [],
                "time_range": None,
                "activity_level": None,
                "health_level": None,
                "stars_level": None,
                "forks_level": None,
                "sort_by": "relevance",
                "contributor_type": "all"
            }
    
    async def generate_project_summary(self, project: Any, events: Optional[List[Any]] = None, metrics_data: Optional[Dict[str, Any]] = None) -> str:
        """
        生成项目摘要
        
        Args:
            project: 项目对象或字典
            events: 项目事件列表（已弃用，保留兼容性）
            metrics_data: 项目指标数据（从metrics_data字段提取）
            
        Returns:
            项目摘要文本
        """
        try:
            # 处理项目数据，支持对象和字典
            if isinstance(project, dict):
                project_key = project.get('project_key', 'Unknown')
                repo_description = project.get('description', '无描述')
                repo_language = project.get('language', '未知')
                repo_stargazers_count = project.get('stars', 0)
                repo_forks_count = project.get('forks', 0)
            else:
                project_key = project.project_key
                repo_description = project.repo_description or "无描述"
                repo_language = project.repo_language or "未知"
                repo_stargazers_count = project.repo_stargazers_count or 0
                repo_forks_count = project.repo_forks_count or 0
             
            # 从metrics_data中提取指标数据
            issue_metrics = {}
            contributor_metrics = {}
            
            if metrics_data:
                # 提取Issue指标
                if 'Issue_Metrics' in metrics_data:
                    issue_metrics = metrics_data['Issue_Metrics']
                
                # 提取贡献者指标
                if 'Contributor_Metrics' in metrics_data:
                    contributor_metrics = metrics_data['Contributor_Metrics']
             
            # 使用metrics_data中的数据，而不是events
            issues_new_latest = issue_metrics.get('issues_new_Latest', 0)
            issues_closed_latest = issue_metrics.get('issues_closed_Latest', 0)
            issue_comments_latest = issue_metrics.get('issue_comments_Latest', 0)
            issues_active_latest = issue_metrics.get('issues_and_change_request_active_Latest', 0)
            
            new_contributors_latest = contributor_metrics.get('new_contributors_Latest', 0)
            inactive_contributors_latest = contributor_metrics.get('inactive_contributors_Latest', 0)
             
            prompt = f"""
            请为以下GitHub项目生成一个简洁的项目摘要：
 
            项目名称: {project_key}
            描述: {repo_description}
            编程语言: {repo_language}
            星标数: {repo_stargazers_count}
            分叉数: {repo_forks_count}
 
            Issue指标 (最新):
            - 新建Issues: {issues_new_latest}
            - 关闭Issues: {issues_closed_latest}
            - Issue评论: {issue_comments_latest}
            - 活跃Issues: {issues_active_latest}
 
            贡献者指标 (最新):
            - 新增贡献者: {new_contributors_latest}
            - 非活跃贡献者: {inactive_contributors_latest}
 
            请生成一个100-150字的项目摘要，突出项目的特点、活跃度和社区参与情况。
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的GitHub项目分析师。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            if content is not None:
                return content.strip()
            else:
                return ""
            
        except Exception as e:
            logger.error(f"生成项目摘要时出错: {e}")
            if isinstance(project, dict):
                return f"{project.get('project_key', 'Unknown')} - {project.get('description', '无描述')}"
            else:
                return f"{project.project_key} - {project.repo_description or '无描述'}"
    
    async def generate_search_explanation(self, query: str, results: List[Dict]) -> str:
        """
        生成搜索结果解释
        
        Args:
            query: 用户查询
            results: 搜索结果列表
           
        Returns:
            搜索结果解释文本
        """
        try:
            # 分析查询特点
            query_lower = query.lower()
            
            # 判断搜索类型
            search_type = "常规搜索"
            if any(word in query_lower for word in ["高活跃度", "活跃度高", "活跃项目", "热门项目"]):
                search_type = "高活跃度项目搜索"
            elif any(word in query_lower for word in ["高健康度", "健康度高", "健康状况良好", "代码质量高"]):
                search_type = "高健康度项目搜索"
            elif any(word in query_lower for word in ["高关注度", "关注度高", "多关注", "关注多"]):
                search_type = "高关注度项目搜索"
            elif any(word in query_lower for word in ["星标数", "高星标", "多星标", "stars多"]):
                search_type = "高星标数项目搜索"
            elif any(word in query_lower for word in ["分支数", "高分支", "多分支", "分支多"]):
                search_type = "高分支数项目搜索"
            elif any('\u4e00' <= char <= '\u9fff' for char in query):
                # 检查是否包含中文
                if len([c for c in query if '\u4e00' <= c <= '\u9fff']) > len(query) * 0.5:
                    search_type = "中文关键词搜索"
            
            # 获取结果统计
            total_results = len(results)
            languages = list(set([r.get('language', 'Unknown') for r in results[:10] if r.get('language')]))
            top_projects = [r.get('project_key', 'Unknown') for r in results[:3]]
            
            prompt = f"""
            用户搜索查询: "{query}"
            搜索类型: {search_type}
            找到结果数: {total_results}
            主要编程语言: {', '.join(languages[:5])}
            顶级项目: {', '.join(top_projects)}

            请为用户生成一个简洁的搜索特点说明，只阐述当前搜索内容的特点，不要提及搜索结果数量和关联编程语言，不要推荐任何服务或关键词。
            请说明：
            1. 当前搜索的类型和特点
            2. 搜索结果的主要特征
            3. 结果中项目的共同特点

            重要：不要包含任何推荐、建议、引导性语言，如"推荐"、"建议"、"可以尝试"、"您可能还"、"试试搜索"等词汇。
            请用简洁、客观的语气回应，控制在120-150字，只描述不推荐。
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的搜索分析助手，只分析搜索内容特点，不做任何推荐。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
           
            content = response.choices[0].message.content
            if content is not None:
                return content.strip()
            else:
                return ""
           
        except Exception as e:
            logger.error(f"生成搜索解释时出错: {e}")
            return f"搜索完成，找到 {len(results)} 个相关项目。"
    
    async def suggest_related_projects(self, project: Any, db: Optional[Session] = None, limit: int = 5) -> List[str]:
        """
        推荐相关项目
        
        Args:
            project: 当前项目（对象或字典）
            db: 数据库会话
            limit: 推荐数量限制
            
        Returns:
            推荐的项目key列表
        """
        try:
            # 处理项目数据，支持对象和字典
            if isinstance(project, dict):
                project_key = project.get('project_key', 'Unknown')
                repo_description = project.get('description', '无描述')
                repo_language = project.get('language', '未知')
                repo_license = project.get('license', '未知')
            else:
                project_key = project.project_key
                repo_description = project.repo_description or "无描述"
                repo_language = project.repo_language or "未知"
                repo_license = project.repo_license or "未知"
            
            # 如果提供了数据库会话，先获取数据库中实际存在的项目
            existing_projects = []
            if db:
                try:
                    # 获取数据库中所有项目的project_key
                    db_projects = db.query(Project.project_key).all()
                    existing_projects = [p.project_key for p in db_projects]
                    logger.info(f"数据库中共有 {len(existing_projects)} 个项目")
                except Exception as db_error:
                    logger.warning(f"获取数据库项目列表时出错: {db_error}")
            
            prompt = f"""
            基于以下GitHub项目，请推荐5个相关的项目：

            当前项目:
            - 名称: {project_key}
            - 描述: {repo_description}
            - 编程语言: {repo_language}
            - 标签: {repo_license}

            请推荐相关的项目，考虑：
            1. 相同编程语言的项目
            2. 相似功能或领域的项目
            3. 相似规模的项目

            只返回项目名称列表，每行一个，不需要解释。
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个GitHub项目推荐专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            content = response.choices[0].message.content
            if content is not None:
                content = content.strip()
            else:
                content = ""
            suggested_projects = [line.strip() for line in content.split('\n') if line.strip()]
            
            # 如果有数据库项目列表，只返回数据库中存在的项目
            if existing_projects:
                filtered_projects = []
                for suggested in suggested_projects:
                    # 检查推荐的项目是否在数据库中存在
                    if suggested in existing_projects:
                        filtered_projects.append(suggested)
                        logger.info(f"推荐项目 {suggested} 存在于数据库中")
                    else:
                        logger.warning(f"推荐项目 {suggested} 不存在于数据库中，跳过")
                
                # 如果过滤后项目不足，从数据库中随机选择一些项目补充
                if len(filtered_projects) < limit:
                    logger.info(f"推荐项目不足，从数据库中补充项目")
                    
                    # 获取当前项目的信息，用于推荐相似项目
                    current_language = repo_language.lower() if repo_language else ""
                    current_org = project_key.split('/')[0] if '/' in project_key else ""
                    
                    # 从数据库中查找相似的项目
                    similar_projects = []
                    for existing_project in existing_projects:
                        if existing_project == project_key:  # 跳过当前项目
                            continue
                        
                        # 简单的相似性检查：相同语言或相同组织
                        if current_language and current_language in existing_project.lower():
                            similar_projects.append(existing_project)
                        elif current_org and existing_project.startswith(current_org + '/'):
                            similar_projects.append(existing_project)
                    
                    # 如果相似项目还是不足，随机选择一些项目
                    if len(similar_projects) < (limit - len(filtered_projects)):
                        remaining_projects = [p for p in existing_projects
                                            if p != project_key and p not in filtered_projects and p not in similar_projects]
                        similar_projects.extend(remaining_projects[:limit - len(filtered_projects) - len(similar_projects)])
                    
                    # 添加补充项目到推荐列表
                    for similar_project in similar_projects[:limit - len(filtered_projects)]:
                        if similar_project not in filtered_projects:
                            filtered_projects.append(similar_project)
                            logger.info(f"补充推荐项目 {similar_project}")
                
                return filtered_projects[:limit]
            else:
                # 如果没有数据库连接，返回原始推荐（可能包含不存在的项目）
                return suggested_projects[:limit]
            
        except Exception as e:
            logger.error(f"推荐相关项目时出错: {e}")
            return []
    
    async def analyze_trends(self, db: Session, time_period: str = "yearly") -> Dict[str, Any]:
        """
        分析项目趋势
        
        Args:
            db: 数据库会话
            time_period: 时间周期 (monthly, quarterly, yearly)
            
        Returns:
            趋势分析结果
        """
        try:
            # 从数据库获取趋势数据
            if time_period == "yearly":
                activity_data = db.query(ProjectActivity).filter(
                    ProjectActivity.month == 1  # 只取每年1月的数据
                ).order_by(ProjectActivity.year, ProjectActivity.project_key).all()
            elif time_period == "quarterly":
                activity_data = db.query(ProjectActivity).filter(
                    ProjectActivity.month.in_([1, 4, 7, 10])  # 每季度第一个月
                ).order_by(ProjectActivity.year, ProjectActivity.month, ProjectActivity.project_key).all()
            else:  # monthly
                activity_data = db.query(ProjectActivity).order_by(
                    ProjectActivity.year, ProjectActivity.month, ProjectActivity.project_key
                ).all()
            
            # 准备数据摘要
            data_summary = []
            for activity in activity_data[:50]:  # 限制数据量
                data_summary.append({
                    "project": activity.project_key,
                    "year": activity.year,
                    "month": activity.month,
                    "events": activity.total_events,
                    "contributors": activity.unique_contributors
                })
            
            prompt = f"""
            基于以下GitHub项目活动数据，请分析趋势并提供洞察：

            时间周期: {time_period}
            数据样本: {len(data_summary)} 条记录

            请分析：
            1. 整体活动趋势
            2. 最活跃的项目
            3. 贡献者增长趋势
            4. 技术栈变化趋势

            请提供简洁的趋势分析报告，控制在200字以内。

            数据样本:
            {json.dumps(data_summary[:10], ensure_ascii=False)}
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个数据分析师，专门分析GitHub项目趋势。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=400
            )
            
            content = response.choices[0].message.content
            if content is not None:
                analysis = content.strip()
            else:
                analysis = ""
            
            return {
                "analysis": analysis,
                "data_count": len(activity_data),
                "time_period": time_period
            }
            
        except Exception as e:
            logger.error(f"分析趋势时出错: {e}")
            return {
                "analysis": "趋势分析暂时不可用，请稍后重试。",
                "data_count": 0,
                "time_period": time_period
            }

# 创建全局服务实例
deepseek_service = DeepSeekService()
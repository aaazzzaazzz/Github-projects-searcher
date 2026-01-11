#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DataEase数据大屏服务
为DataEase提供数据接口，支持词云图和各种统计图表
"""

import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_, case
from datetime import datetime, timedelta
import logging

from project.models import Project, GitHubEvent, Contributor, ProjectActivity

logger = logging.getLogger(__name__)

class DataEaseService:
    """DataEase数据服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_wordcloud_data(self, metric_type: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取词云数据
        
        Args:
            metric_type: 指标类型 (activity, participants, attention, change_requests, 
                        issues_active, new_contributors, openrank, stars, technical_fork)
            limit: 返回数量限制
            
        Returns:
            词云数据列表，格式：[{"name": "项目名", "value": 数值}, ...]
        """
        try:
            if metric_type == "activity":
                return self._get_activity_wordcloud(limit)
            elif metric_type == "participants":
                return self._get_participants_wordcloud(limit)
            elif metric_type == "attention":
                return self._get_attention_wordcloud(limit)
            elif metric_type == "change_requests":
                return self._get_change_requests_wordcloud(limit)
            elif metric_type == "issues_active":
                return self._get_issues_active_wordcloud(limit)
            elif metric_type == "new_contributors":
                return self._get_new_contributors_wordcloud(limit)
            elif metric_type == "openrank":
                return self._get_openrank_wordcloud(limit)
            elif metric_type == "stars":
                return self._get_stars_wordcloud(limit)
            elif metric_type == "technical_fork":
                return self._get_technical_fork_wordcloud(limit)
            else:
                return []
        except Exception as e:
            logger.error(f"获取词云数据时出错: {e}")
            return []
    
    def _get_activity_wordcloud(self, limit: int) -> List[Dict[str, Any]]:
        """获取活跃度词云数据"""
        # 基于项目活跃度事件总数
        result = self.db.query(
            Project.project_name,
            func.count(GitHubEvent.id).label('activity_count')
        ).join(
            GitHubEvent, Project.project_key == GitHubEvent.project_key
        ).group_by(
            Project.project_name
        ).order_by(
            desc('activity_count')
        ).limit(limit).all()
        
        return [{"name": row.project_name, "value": row.activity_count} for row in result]
    
    def _get_participants_wordcloud(self, limit: int) -> List[Dict[str, Any]]:
        """获取参与者词云数据"""
        # 基于项目独特贡献者数量
        result = self.db.query(
            Project.project_name,
            func.count(func.distinct(GitHubEvent.actor_login)).label('participant_count')
        ).join(
            GitHubEvent, Project.project_key == GitHubEvent.project_key
        ).group_by(
            Project.project_name
        ).order_by(
            desc('participant_count')
        ).limit(limit).all()
        
        return [{"name": row.project_name, "value": row.participant_count} for row in result]
    
    def _get_attention_wordcloud(self, limit: int) -> List[Dict[str, Any]]:
        """获取关注度词云数据"""
        # 基于星标数
        result = self.db.query(
            Project.project_name,
            Project.repo_stargazers_count.label('attention_count')
        ).filter(
            Project.repo_stargazers_count.isnot(None)
        ).order_by(
            desc(Project.repo_stargazers_count)
        ).limit(limit).all()
        
        return [{"name": row.project_name, "value": row.attention_count or 0} for row in result]
    
    def _get_change_requests_wordcloud(self, limit: int) -> List[Dict[str, Any]]:
        """获取变更请求词云数据"""
        # 基于Pull Request数量
        result = self.db.query(
            Project.project_name,
            func.count(GitHubEvent.id).label('pr_count')
        ).join(
            GitHubEvent, Project.project_key == GitHubEvent.project_key
        ).filter(
            GitHubEvent.event_type == 'PullRequestEvent'
        ).group_by(
            Project.project_name
        ).order_by(
            desc('pr_count')
        ).limit(limit).all()
        
        return [{"name": row.project_name, "value": row.pr_count} for row in result]
    
    def _get_issues_active_wordcloud(self, limit: int) -> List[Dict[str, Any]]:
        """获取活跃Issue词云数据"""
        # 基于Issue事件数量
        result = self.db.query(
            Project.project_name,
            func.count(GitHubEvent.id).label('issue_count')
        ).join(
            GitHubEvent, Project.project_key == GitHubEvent.project_key
        ).filter(
            GitHubEvent.event_type == 'IssuesEvent'
        ).group_by(
            Project.project_name
        ).order_by(
            desc('issue_count')
        ).limit(limit).all()
        
        return [{"name": row.project_name, "value": row.issue_count} for row in result]
    
    def _get_new_contributors_wordcloud(self, limit: int) -> List[Dict[str, Any]]:
        """获取新贡献者词云数据"""
        # 基于新贡献者数量
        result = self.db.query(
            Project.project_name,
            func.count(func.distinct(GitHubEvent.actor_login)).label('new_contributor_count')
        ).join(
            GitHubEvent, Project.project_key == GitHubEvent.project_key
        ).filter(
            GitHubEvent.created_at >= datetime.now() - timedelta(days=365)
        ).group_by(
            Project.project_name
        ).order_by(
            desc('new_contributor_count')
        ).limit(limit).all()
        
        return [{"name": row.project_name, "value": row.new_contributor_count} for row in result]
    
    def _get_openrank_wordcloud(self, limit: int) -> List[Dict[str, Any]]:
        """获取OpenRank词云数据（基于健康度分数）"""
        result = self.db.query(
            Project.project_name,
            Project.health_score.label('openrank')
        ).filter(
            Project.health_score.isnot(None)
        ).order_by(
            desc(Project.health_score)
        ).limit(limit).all()
        
        return [{"name": row.project_name, "value": int(row.openrank * 100) if row.openrank else 0} for row in result]
    
    def _get_stars_wordcloud(self, limit: int) -> List[Dict[str, Any]]:
        """获取星标词云数据"""
        result = self.db.query(
            Project.project_name,
            Project.repo_stargazers_count.label('stars_count')
        ).filter(
            Project.repo_stargazers_count.isnot(None)
        ).order_by(
            desc(Project.repo_stargazers_count)
        ).limit(limit).all()
        
        return [{"name": row.project_name, "value": row.stars_count or 0} for row in result]
    
    def _get_technical_fork_wordcloud(self, limit: int) -> List[Dict[str, Any]]:
        """获取技术分叉词云数据"""
        result = self.db.query(
            Project.project_name,
            Project.repo_forks_count.label('fork_count')
        ).filter(
            Project.repo_forks_count.isnot(None)
        ).order_by(
            desc(Project.repo_forks_count)
        ).limit(limit).all()
        
        return [{"name": row.project_name, "value": row.fork_count or 0} for row in result]
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        获取仪表板统计数据
        
        Returns:
            包含各种统计数据的字典
        """
        try:
            # 基础统计
            total_projects = self.db.query(func.count(Project.id)).scalar()
            total_events = self.db.query(func.count(GitHubEvent.id)).scalar()
            total_contributors = self.db.query(func.count(Contributor.id)).scalar()
            
            # 语言分布
            language_stats = self.db.query(
                Project.repo_language,
                func.count(Project.id).label('count')
            ).filter(
                Project.repo_language.isnot(None)
            ).group_by(
                Project.repo_language
            ).order_by(
                desc('count')
            ).limit(10).all()
            
            # 活跃度趋势（最近12个月）
            twelve_months_ago = datetime.now() - timedelta(days=365)
            activity_trend = self.db.query(
                func.date_trunc('month', GitHubEvent.created_at).label('month'),
                func.count(GitHubEvent.id).label('count')
            ).filter(
                GitHubEvent.created_at >= twelve_months_ago
            ).group_by(
                func.date_trunc('month', GitHubEvent.created_at)
            ).order_by(
                'month'
            ).all()
            
            # 健康度分布
            health_distribution = self.db.query(
                case(
                    (Project.health_score >= 0.8, "高健康度"),
                    (Project.health_score >= 0.6, "中等健康度"),
                    else_="低健康度"
                ).label('health_level'),
                func.count(Project.id).label('count')
            ).filter(
                Project.health_score.isnot(None)
            ).group_by('health_level').all()
            
            return {
                "total_projects": total_projects,
                "total_events": total_events,
                "total_contributors": total_contributors,
                "language_distribution": [
                    {"language": row.repo_language, "count": row.count} 
                    for row in language_stats
                ],
                "activity_trend": [
                    {"month": row.month.strftime("%Y-%m"), "count": row.count}
                    for row in activity_trend
                ],
                "health_distribution": [
                    {"level": row.health_level, "count": row.count}
                    for row in health_distribution
                ]
            }
            
        except Exception as e:
            logger.error(f"获取仪表板统计数据时出错: {e}")
            return {}
    
    def get_project_details_for_dashboard(self, project_key: str) -> Optional[Dict[str, Any]]:
        """
        获取项目详细信息用于仪表板
        
        Args:
            project_key: 项目键
            
        Returns:
            项目详细信息字典
        """
        try:
            project = self.db.query(Project).filter(
                Project.project_key == project_key
            ).first()
            
            if not project:
                return None
            
            # 获取事件统计
            event_stats = self.db.query(
                GitHubEvent.event_type,
                func.count(GitHubEvent.id).label('count')
            ).filter(
                GitHubEvent.project_key == project_key
            ).group_by(
                GitHubEvent.event_type
            ).all()
            
            # 获取贡献者统计
            contributor_stats = self.db.query(
                func.count(func.distinct(GitHubEvent.actor_login)).label('unique_contributors')
            ).filter(
                GitHubEvent.project_key == project_key
            ).scalar()
            
            # 获取活跃度趋势
            activity_trend = self.db.query(
                func.date_trunc('month', GitHubEvent.created_at).label('month'),
                func.count(GitHubEvent.id).label('count')
            ).filter(
                and_(
                    GitHubEvent.project_key == project_key,
                    GitHubEvent.created_at >= datetime.now() - timedelta(days=365)
                )
            ).group_by(
                func.date_trunc('month', GitHubEvent.created_at)
            ).order_by(
                'month'
            ).all()
            
            return {
                "project": {
                    "name": project.project_name,
                    "organization": project.organization,
                    "description": project.repo_description,
                    "language": project.repo_language,
                    "stars": project.repo_stargazers_count,
                    "forks": project.repo_forks_count,
                    "health_score": project.health_score,
                    "created_at": project.repo_created_at.isoformat() if project.repo_created_at is not None else None,
                    "updated_at": project.repo_updated_at.isoformat() if project.repo_updated_at is not None else None
                },
                "event_stats": [
                    {"event_type": row.event_type, "count": row.count}
                    for row in event_stats
                ],
                "contributor_stats": {
                    "unique_contributors": contributor_stats or 0
                },
                "activity_trend": [
                    {"month": row.month.strftime("%Y-%m"), "count": row.count}
                    for row in activity_trend
                ]
            }
            
        except Exception as e:
            logger.error(f"获取项目详细信息时出错: {e}")
            return None

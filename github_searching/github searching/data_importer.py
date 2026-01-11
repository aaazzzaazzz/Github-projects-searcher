import pandas as pd
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from project.models import Base, Project, GitHubEvent, Contributor, ProjectActivity
import uuid
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataImporter:
    def __init__(self, database_url="sqlite:///github_search.db"):
        """
        初始化数据导入器
        
        Args:
            database_url: 数据库连接URL
        """
        self.engine = sqlalchemy.create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
        
        # 创建所有表
        Base.metadata.create_all(self.engine)
        logger.info("数据库表创建完成")
    
    def import_projects_basic_info(self, excel_file="top_300_metrics_full.xlsx"):
        """导入项目基本信息"""
        logger.info(f"开始导入项目基本信息: {excel_file}")
        
        try:
            df = pd.read_excel(excel_file)
            session = self.Session()
            
            imported_count = 0
            for _, row in df.iterrows():
                # 检查项目是否已存在
                existing_project = session.query(Project).filter_by(
                    project_key=row['Project_Key']
                ).first()
                
                if not existing_project:
                    project = Project(
                        organization=row['Organization'],
                        project_name=row['Project'],
                        project_key=row['Project_Key']
                    )
                    session.add(project)
                    imported_count += 1
            
            session.commit()
            session.close()
            logger.info(f"成功导入 {imported_count} 个项目基本信息")
            
        except Exception as e:
            logger.error(f"导入项目基本信息时出错: {e}")
            if 'session' in locals():
                session.rollback()
                session.close()
    
    def import_all_metrics(self, excel_file="top_300_metrics_full.xlsx"):
        """导入所有工作表的指标数据"""
        logger.info(f"开始导入所有指标数据: {excel_file}")
        
        try:
            # 获取所有工作表名称
            xl = pd.ExcelFile(excel_file)
            session = self.Session()
            
            updated_count = 0
            
            # 遍历所有工作表
            for sheet_name in xl.sheet_names:
                logger.info(f"正在处理工作表: {sheet_name}")
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                for _, row in df.iterrows():
                    project_key = row.get('Project_Key') if 'Project_Key' in df.columns else None
                    
                    if not project_key:
                        continue
                        
                    project = session.query(Project).filter_by(project_key=project_key).first()
                    
                    if project:
                        # 为每个工作表创建数据字典
                        sheet_data = {}
                        for col in df.columns:
                            if col not in ['Organization', 'Project', 'Project_Key']:
                                sheet_data[col] = row.get(col)
                        
                        # 将工作表数据存储为JSON字符串
                        import json
                        current_metrics = {}
                        if project.metrics_data:
                            try:
                                current_metrics = json.loads(project.metrics_data) if isinstance(project.metrics_data, str) else project.metrics_data
                            except:
                                current_metrics = {}
                        
                        current_metrics[sheet_name] = sheet_data
                        project.metrics_data = json.dumps(current_metrics)
                        
                        updated_count += 1
            
            session.commit()
            session.close()
            logger.info(f"成功更新 {updated_count} 个项目的所有指标数据")
            
        except Exception as e:
            logger.error(f"导入所有指标数据时出错: {e}")
            if 'session' in locals():
                session.rollback()
                session.close()
    
    def import_activity_metrics(self, excel_file="top_300_metrics_full.xlsx"):
        """导入项目活跃度指标数据，包括attention数据"""
        logger.info(f"开始导入项目活跃度指标数据: {excel_file}")
        
        try:
            # 读取Activity_Metrics工作表
            df = pd.read_excel(excel_file, sheet_name='Activity_Metrics')
            session = self.Session()
            
            updated_count = 0
            for _, row in df.iterrows():
                project = session.query(Project).filter_by(
                    project_key=row.get('Project_Key')
                ).first()
                
                if project:
                    # 更新attention相关字段
                    attention_data = {
                        'attention_Latest': row.get('attention_Latest'),
                        'attention_Data_Points': row.get('attention_Data_Points'),
                        'attention_Average': row.get('attention_Average'),
                        'attention_Min': row.get('attention_Min'),
                        'attention_Max': row.get('attention_Max')
                    }
                    
                    # 将attention数据存储为JSON字符串
                    import json
                    project.attention = json.dumps(attention_data)
                    
                    updated_count += 1
            
            session.commit()
            session.close()
            logger.info(f"成功更新 {updated_count} 个项目的attention数据")
            
        except Exception as e:
            logger.error(f"导入项目活跃度指标数据时出错: {e}")
            if 'session' in locals():
                session.rollback()
                session.close()
    
    def import_github_events(self, excel_file="top300_20_23_robust_all_fixed.xlsx"):
        """导入GitHub事件数据"""
        logger.info(f"开始导入GitHub事件数据: {excel_file}")
        
        try:
            # 分块读取大文件
            chunk_size = 1000
            total_imported = 0
            
            # 由于pandas版本问题，直接读取整个文件
            df = pd.read_excel(excel_file)
            session = self.Session()
            chunk_imported = 0
            
            for _, row in df.iterrows():
                session = self.Session()
                chunk_imported = 0
                
                for _, row in df.iterrows():
                    try:
                        # 处理日期时间字段
                        created_at = self._parse_datetime(row.get('created_at'))
                        issue_created_at = self._parse_datetime(row.get('issue_created_at'))
                        issue_updated_at = self._parse_datetime(row.get('issue_updated_at'))
                        issue_closed_at = self._parse_datetime(row.get('issue_closed_at'))
                        pull_merged_at = self._parse_datetime(row.get('pull_merged_at'))
                        release_created_at = self._parse_datetime(row.get('release_created_at'))
                        release_published_at = self._parse_datetime(row.get('release_published_at'))
                        
                        event = GitHubEvent(
                            github_event_id=row.get('id'),
                            event_type=row.get('type'),
                            action=row.get('action'),
                            created_at=created_at,
                            actor_id=row.get('actor_id'),
                            actor_login=row.get('actor_login'),
                            repo_id=row.get('repo_id'),
                            repo_name=row.get('repo_name'),
                            project_key=row.get('repo_name'),  # 使用repo_name作为project_key
                            org_id=row.get('org_id'),
                            org_login=row.get('org_login'),
                            
                            # Issue信息
                            issue_id=row.get('issue_id'),
                            issue_number=row.get('issue_number'),
                            issue_title=row.get('issue_title'),
                            issue_body=row.get('body'),
                            issue_author_id=row.get('issue_author_id'),
                            issue_author_login=row.get('issue_author_login'),
                            issue_author_type=row.get('issue_author_type'),
                            issue_author_association=row.get('issue_author_association'),
                            issue_created_at=issue_created_at,
                            issue_updated_at=issue_updated_at,
                            issue_closed_at=issue_closed_at,
                            issue_comments=row.get('issue_comments'),
                            
                            # Pull Request信息
                            pull_commits=row.get('pull_commits'),
                            pull_additions=row.get('pull_additions'),
                            pull_deletions=row.get('pull_deletions'),
                            pull_changed_files=row.get('pull_changed_files'),
                            pull_merged=row.get('pull_merged'),
                            pull_merged_at=pull_merged_at,
                            pull_merged_by_login=row.get('pull_merged_by_login'),
                            pull_review_comments=row.get('pull_review_comments'),
                            
                            # Push信息
                            push_size=row.get('push_size'),
                            push_distinct_size=row.get('push_distinct_size'),
                            push_ref=row.get('push_ref'),
                            push_head=row.get('push_head'),
                            
                            # Release信息
                            release_id=row.get('release_id'),
                            release_tag_name=row.get('release_tag_name'),
                            release_name=row.get('release_name'),
                            release_draft=row.get('release_draft'),
                            release_prerelease=row.get('release_prerelease'),
                            release_created_at=release_created_at,
                            release_published_at=release_published_at,
                            release_body=row.get('release_body')
                        )
                        
                        session.add(event)
                        chunk_imported += 1
                        
                    except Exception as e:
                        logger.warning(f"导入事件时出错 (ID: {row.get('id')}): {e}")
                        continue
                
            session.commit()
            session.close()
            total_imported = chunk_imported
            logger.info(f"已导入 {total_imported} 条事件记录")
            
            logger.info(f"GitHub事件数据导入完成，总计导入 {total_imported} 条记录")
            
        except Exception as e:
            logger.error(f"导入GitHub事件数据时出错: {e}")
            if 'session' in locals():
                session.rollback()
                session.close()
    
    def update_project_details(self, excel_file="top300_20_23_robust_all_fixed.xlsx"):
        """更新项目详细信息"""
        logger.info(f"开始更新项目详细信息: {excel_file}")
        
        try:
            df = pd.read_excel(excel_file)
            session = self.Session()
           
            # 按项目名称分组，只处理每个项目一次
            # 先获取每个项目的第一行（非空值）
            df_unique = df.dropna(subset=['repo_name']).drop_duplicates('repo_name', keep='first')
            
            updated_count = 0
            for _, row in df_unique.iterrows():
                project = session.query(Project).filter_by(
                    project_key=row.get('repo_name')
                ).first()
                
                if project:
                    # 更新项目详细信息
                    project.repo_description = row.get('repo_description')
                    project.repo_size = self._safe_int(row.get('repo_size'))
                    project.repo_stargazers_count = self._safe_int(row.get('repo_stargazers_count'))
                    project.repo_forks_count = self._safe_int(row.get('repo_forks_count'))
                    project.repo_language = row.get('repo_language')
                    project.repo_license = row.get('repo_license')
                    project.repo_default_branch = row.get('repo_default_branch')
                    project.repo_created_at = self._parse_datetime(row.get('created_at'))
                    project.repo_updated_at = self._parse_datetime(row.get('repo_updated_at'))
                    project.repo_pushed_at = self._parse_datetime(row.get('repo_pushed_at'))
                    project.repo_has_issues = self._safe_bool(row.get('repo_has_issues'))
                    project.repo_has_projects = self._safe_bool(row.get('repo_has_projects'))
                    project.repo_has_downloads = self._safe_bool(row.get('repo_has_downloads'))
                    project.repo_has_wiki = self._safe_bool(row.get('repo_has_wiki'))
                    project.repo_has_pages = self._safe_bool(row.get('repo_has_pages'))
                    
                    # 更新attention字段（如果存在）
                    if 'attention' in row and pd.notna(row.get('attention')):
                        project.attention = str(row.get('attention'))
                    
                    updated_count += 1
            
            session.commit()
            session.close()
            logger.info(f"成功更新 {updated_count} 个项目的详细信息")
            
        except Exception as e:
            logger.error(f"更新项目详细信息时出错: {e}")
            if 'session' in locals():
                session.rollback()
                session.close()
    
    def generate_contributor_stats(self):
        """生成贡献者统计信息"""
        logger.info("开始生成贡献者统计信息")
        
        try:
            session = self.Session()
            
            # 获取所有贡献者及其事件统计
            contributor_stats = session.query(
                GitHubEvent.actor_login,
                GitHubEvent.actor_id,
                sqlalchemy.func.count(GitHubEvent.id).label('total_events'),
                sqlalchemy.func.min(GitHubEvent.created_at).label('first_event'),
                sqlalchemy.func.max(GitHubEvent.created_at).label('last_event'),
                sqlalchemy.func.count(sqlalchemy.distinct(GitHubEvent.repo_name)).label('projects_count')
            ).group_by(GitHubEvent.actor_login, GitHubEvent.actor_id).all()
            
            for stat in contributor_stats:
                # 检查贡献者是否已存在
                existing_contributor = session.query(Contributor).filter_by(
                    contributor_login=stat.actor_login
                ).first()
                
                if not existing_contributor and stat.actor_login:
                    contributor = Contributor(
                        contributor_login=stat.actor_login,
                        contributor_id=stat.actor_id,
                        total_events=stat.total_events,
                        first_event_at=stat.first_event,
                        last_event_at=stat.last_event,
                        projects_contributed=stat.projects_count
                    )
                    session.add(contributor)
            
            session.commit()
            session.close()
            logger.info(f"贡献者统计信息生成完成，共处理 {len(contributor_stats)} 个贡献者")
            
        except Exception as e:
            logger.error(f"生成贡献者统计信息时出错: {e}")
            if 'session' in locals():
                session.rollback()
                session.close()
    
    def generate_activity_stats(self):
        """生成项目活跃度统计信息"""
        logger.info("开始生成项目活跃度统计信息")
        
        try:
            session = self.Session()
            
            # 按项目和月份统计事件
            activity_stats = session.query(
                GitHubEvent.project_key,
                sqlalchemy.extract('year', GitHubEvent.created_at).label('year'),
                sqlalchemy.extract('month', GitHubEvent.created_at).label('month'),
                sqlalchemy.func.count(GitHubEvent.id).label('total_events'),
                sqlalchemy.func.count(sqlalchemy.distinct(GitHubEvent.actor_login)).label('unique_contributors')
            ).filter(
                GitHubEvent.project_key.isnot(None),
                GitHubEvent.created_at.isnot(None)
            ).group_by(
                GitHubEvent.project_key,
                sqlalchemy.extract('year', GitHubEvent.created_at),
                sqlalchemy.extract('month', GitHubEvent.created_at)
            ).all()
            
            logger.info(f"找到 {len(activity_stats)} 条活动统计记录")
            
            for stat in activity_stats:
                # 检查活跃度记录是否已存在
                existing_activity = session.query(ProjectActivity).filter_by(
                    project_key=stat.project_key,
                    year=stat.year,
                    month=stat.month
                ).first()
                
                if not existing_activity:
                    activity = ProjectActivity(
                        project_key=stat.project_key,
                        year=stat.year,
                        month=stat.month,
                        total_events=stat.total_events,
                        unique_contributors=stat.unique_contributors
                    )
                    session.add(activity)
            
            session.commit()
            session.close()
            logger.info(f"项目活跃度统计信息生成完成，共处理 {len(activity_stats)} 条记录")
            
        except Exception as e:
            logger.error(f"生成项目活跃度统计信息时出错: {e}")
            if 'session' in locals():
                session.rollback()
                session.close()
    
    def _parse_datetime(self, datetime_value):
        """解析日期时间值"""
        if pd.isna(datetime_value):
            return None
        
        if isinstance(datetime_value, datetime):
            return datetime_value
        
        if isinstance(datetime_value, str):
            try:
                # 首先尝试pandas的自动解析，这对Excel中的日期字符串最有效
                try:
                    parsed_date = pd.to_datetime(datetime_value)
                    return parsed_date.to_pydatetime()
                except Exception:
                    pass
                
                # 尝试ISO格式（带Z）
                if 'T' in datetime_value and datetime_value.endswith('Z'):
                    return datetime.fromisoformat(datetime_value.replace('Z', '+00:00'))
                # 尝试ISO格式（不带Z）
                elif 'T' in datetime_value:
                    return datetime.fromisoformat(datetime_value)
                # 尝试Excel日期格式（如 2021-11-07 12:57:17）
                elif ' ' in datetime_value and ':' in datetime_value:
                    # 直接解析完整的日期时间字符串
                    return datetime.strptime(datetime_value, '%Y-%m-%d %H:%M:%S')
                # 尝试简单日期格式
                elif '-' in datetime_value and len(datetime_value) == 10:
                    return datetime.strptime(datetime_value, '%Y-%m-%d')
                else:
                    # 如果都失败了，记录警告并返回None
                    logger.warning(f"无法解析日期格式: {datetime_value}")
                    return None
            except Exception as e:
                logger.warning(f"日期解析失败 '{datetime_value}': {e}")
                return None
        
        # 如果是数字（Excel日期序列号）
        if isinstance(datetime_value, (int, float)):
            try:
                return pd.to_datetime(datetime_value, unit='D', origin='1899-12-30').to_pydatetime()
            except Exception as e:
                logger.warning(f"Excel日期解析失败 '{datetime_value}': {e}")
                return None
        
        return datetime_value
    
    def _safe_int(self, value):
        """安全转换为整数"""
        try:
            if pd.isna(value) or value is None:
                return 0
            return int(value)
        except:
            return 0
    
    def _safe_bool(self, value):
        """安全转换为布尔值"""
        try:
            if pd.isna(value) or value is None:
                return False
            return bool(value)
        except:
            return False
    
    def run_full_import(self):
        """执行完整的数据导入流程"""
        logger.info("开始执行完整数据导入流程")
        
        # 1. 导入项目基本信息
        self.import_projects_basic_info()
        
        # 2. 导入GitHub事件数据
        self.import_github_events()
        
        # 3. 更新项目详细信息
        self.update_project_details()
        
        # 4. 导入所有工作表的指标数据（包括attention）
        self.import_all_metrics()
        
        # 5. 导入项目活跃度指标数据（包括attention）
        self.import_activity_metrics()
        
        # 6. 生成贡献者统计信息
        self.generate_contributor_stats()
        
        # 7. 生成项目活跃度统计信息
        self.generate_activity_stats()
        
        logger.info("完整数据导入流程执行完成")

if __name__ == "__main__":
    # 创建数据导入器并执行导入
    importer = DataImporter()
    importer.run_full_import()
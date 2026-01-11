from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from project.database import Base
import uuid

class Project(Base):
    """GitHub项目基本信息表"""
    __tablename__ = 'projects'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization = Column(String(255), nullable=False, index=True)  # 组织名
    project_name = Column(String(255), nullable=False, index=True)  # 项目名
    project_key = Column(String(255), unique=True, nullable=False, index=True)  # 完整项目路径
    
    # 仓库基本信息
    repo_description = Column(Text)
    repo_size = Column(Integer)
    repo_stargazers_count = Column(Integer, index=True)
    repo_forks_count = Column(Integer)
    repo_language = Column(String(100), index=True)
    repo_license = Column(String(100))
    repo_default_branch = Column(String(100))
    repo_created_at = Column(DateTime)
    repo_updated_at = Column(DateTime)
    repo_pushed_at = Column(DateTime)
    
    # 仓库特性
    repo_has_issues = Column(Boolean, default=False)
    repo_has_projects = Column(Boolean, default=False)
    repo_has_downloads = Column(Boolean, default=False)
    repo_has_wiki = Column(Boolean, default=False)
    repo_has_pages = Column(Boolean, default=False)
    
    # 项目关注度指标
    attention = Column(Text)  # 存储attention相关指标的JSON字符串
    metrics_data = Column(Text)  # 存储所有工作表指标的JSON字符串
    health_score = Column(Float, default=0.0)  # 项目健康度分数
    
    # 关联关系
    events = relationship("GitHubEvent", back_populates="project")
    
    def __repr__(self):
        return f"<Project(organization='{self.organization}', project='{self.project_name}')>"

class GitHubEvent(Base):
    """GitHub事件日志表"""
    __tablename__ = 'github_events'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    github_event_id = Column(Integer, unique=True, nullable=False, index=True)  # GitHub原始事件ID
    
    # 事件基本信息
    event_type = Column(String(100), nullable=False, index=True)  # 事件类型
    action = Column(String(100), index=True)  # 事件动作
    created_at = Column(DateTime, nullable=False, index=True)  # 事件创建时间
    
    # 参与者信息
    actor_id = Column(Integer, index=True)
    actor_login = Column(String(255), index=True)
    
    # 仓库信息
    repo_id = Column(Integer, index=True)
    repo_name = Column(String(255), index=True)
    project_key = Column(String(255), ForeignKey('projects.project_key'), index=True)
    
    # 组织信息
    org_id = Column(Integer)
    org_login = Column(String(255))
    
    # Issue相关信息
    issue_id = Column(Integer)
    issue_number = Column(Integer)
    issue_title = Column(Text)
    issue_body = Column(Text)
    issue_author_id = Column(Integer)
    issue_author_login = Column(String(255))
    issue_author_type = Column(String(50))
    issue_author_association = Column(String(50))
    issue_created_at = Column(DateTime)
    issue_updated_at = Column(DateTime)
    issue_closed_at = Column(DateTime)
    issue_comments = Column(Integer)
    
    # Pull Request相关信息
    pull_commits = Column(Integer)
    pull_additions = Column(Integer)
    pull_deletions = Column(Integer)
    pull_changed_files = Column(Integer)
    pull_merged = Column(Boolean)
    pull_merged_at = Column(DateTime)
    pull_merged_by_login = Column(String(255))
    pull_review_comments = Column(Integer)
    
    # Push相关信息
    push_size = Column(Integer)
    push_distinct_size = Column(Integer)
    push_ref = Column(String(255))
    push_head = Column(String(255))
    
    # Release相关信息
    release_id = Column(Integer)
    release_tag_name = Column(String(255))
    release_name = Column(String(255))
    release_draft = Column(Boolean)
    release_prerelease = Column(Boolean)
    release_created_at = Column(DateTime)
    release_published_at = Column(DateTime)
    release_body = Column(Text)
    
    # 关联关系
    project = relationship("Project", back_populates="events")
    
    def __repr__(self):
        return f"<GitHubEvent(type='{self.event_type}', repo='{self.repo_name}', created_at='{self.created_at}')>"

class Contributor(Base):
    """贡献者统计表"""
    __tablename__ = 'contributors'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    contributor_login = Column(String(255), unique=True, nullable=False, index=True)
    contributor_id = Column(Integer, index=True)
    contributor_type = Column(String(50))
    
    # 贡献统计
    total_events = Column(Integer, default=0)
    issue_events = Column(Integer, default=0)
    pull_request_events = Column(Integer, default=0)
    push_events = Column(Integer, default=0)
    fork_events = Column(Integer, default=0)
    
    # 时间范围
    first_event_at = Column(DateTime)
    last_event_at = Column(DateTime)
    
    # 参与的项目
    projects_contributed = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<Contributor(login='{self.contributor_login}', total_events={self.total_events})>"

class ProjectActivity(Base):
    """项目活跃度统计表"""
    __tablename__ = 'project_activity'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_key = Column(String(255), ForeignKey('projects.project_key'), index=True)
    year = Column(Integer, index=True)
    month = Column(Integer, index=True)
    
    # 活跃度统计
    total_events = Column(Integer, default=0)
    issue_events = Column(Integer, default=0)
    pull_request_events = Column(Integer, default=0)
    push_events = Column(Integer, default=0)
    fork_events = Column(Integer, default=0)
    release_events = Column(Integer, default=0)
    
    # 贡献者统计
    unique_contributors = Column(Integer, default=0)
    new_contributors = Column(Integer, default=0)
    
    # 关联关系
    project = relationship("Project")
    
    def __repr__(self):
        return f"<ProjectActivity(project='{self.project_key}', year={self.year}, month={self.month}, events={self.total_events})>"

# 创建索引的辅助函数
def create_indexes(engine):
    """创建数据库索引以提高查询性能"""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_projects_org_lang ON projects(organization, repo_language);",
        "CREATE INDEX IF NOT EXISTS idx_events_type_created ON github_events(event_type, created_at);",
        "CREATE INDEX IF NOT EXISTS idx_events_repo_created ON github_events(repo_name, created_at);",
        "CREATE INDEX IF NOT EXISTS idx_events_actor_created ON github_events(actor_login, created_at);",
        "CREATE INDEX IF NOT EXISTS idx_activity_project_month ON project_activity(project_key, year, month);",
        "CREATE INDEX IF NOT EXISTS idx_contributor_events ON contributors(total_events DESC);",
    ]
    
    for index_sql in indexes:
        try:
            engine.execute(index_sql)
        except Exception as e:
            print(f"创建索引时出错: {e}")
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基本配置
    app_name: str = "GitHub项目搜索引擎"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # 数据库配置
    database_url: str = "sqlite:///github_search.db"
    
    # DeepSeek API配置
    deepseek_api_key: str = ""
    deepseek_api_base: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-chat"
    
    # 搜索配置
    search_results_limit: int = 20
    max_search_results: int = 100
    
    # 缓存配置
    cache_ttl: int = 3600  # 缓存时间（秒）
    
    # 前端配置
    static_files_dir: str = "static"
    templates_dir: str = "templates"
    
    # CORS配置
    allowed_origins: list = ["*"]
    
    # 分页配置
    default_page_size: int = 20
    max_page_size: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# 创建全局配置实例
settings = Settings()
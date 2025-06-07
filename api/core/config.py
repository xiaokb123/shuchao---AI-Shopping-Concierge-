from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache
from dotenv import load_dotenv
import os

# 显式加载 .env 文件
load_dotenv()


class Settings(BaseSettings):
    # 基础配置
    PROJECT_NAME: str = "数潮"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # 安全配置
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # 数据库配置
    DATABASE_URL: str
    DB_USER: str
    DB_PASSWORD: str
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    # Redis配置
    REDIS_URL: str
    REDIS_MAX_CONNECTIONS: int = 10

    # AI配置
    OPENAI_API_KEY: Optional[str] = None
    AI_MODEL_PATH: Optional[str] = None

    # 爬虫配置
    CRAWLER_INTERVAL: int = 3600  # 1小时
    MAX_CRAWL_PAGES: int = 100

    # 缓存配置
    CACHE_TYPE: str = "redis"
    CACHE_REDIS_URL: str
    CACHE_DEFAULT_TIMEOUT: int = 300

    # 监控配置
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_PORT: int = 9090

    # 邮件配置
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str

    # AWS配置
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "ap-northeast-1"

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"  # 允许额外的字段


@lru_cache()
def get_settings():
    settings = Settings()
    print("Settings initialized:", settings.dict())
    return settings


settings = get_settings()
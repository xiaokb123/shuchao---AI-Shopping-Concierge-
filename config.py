import os
from datetime import timedelta
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """基础配置类"""
    # 基础配置
    PROJECT_NAME = os.getenv('PROJECT_NAME', '数潮')
    VERSION = os.getenv('VERSION', '1.0.0')
    
    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        pass
        
    # 安全配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-please-change')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-key-please-change')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # CSRF配置
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.getenv('WTF_CSRF_SECRET_KEY', 'csrf-key-please-change')
    WTF_CSRF_TIME_LIMIT = 3600  # CSRF令牌有效期（秒）
    WTF_CSRF_SSL_STRICT = True  # 在HTTPS下强制使用CSRF
    WTF_CSRF_CHECK_DEFAULT = True  # 默认检查所有POST请求
    
    # CSRF排除的路由
    WTF_CSRF_EXEMPT_LIST = [
        '/api/webhook/',  # 第三方webhook回调
        '/api/public/'    # 公开API
    ]
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = int(os.getenv('SQLALCHEMY_POOL_SIZE', 5))
    SQLALCHEMY_MAX_OVERFLOW = int(os.getenv('SQLALCHEMY_MAX_OVERFLOW', 10))
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True  # 自动提交配置
    SQLALCHEMY_ECHO = True  # 显示SQL查询日志
    
    # Redis配置
    REDIS_URL = os.getenv('REDIS_URL')
    
    # 缓存配置
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'redis')
    CACHE_REDIS_URL = os.getenv('CACHE_REDIS_URL')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))
    
    # AI配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    AI_MODEL = os.getenv('AI_MODEL', 'gpt-3.5-turbo')
    AI_MAX_TOKENS = int(os.getenv('AI_MAX_TOKENS', 2000))
    AI_TEMPERATURE = float(os.getenv('AI_TEMPERATURE', 0.7))
    
    # 邮件配置
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    
    # 文件上传配置
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'png,jpg,jpeg,gif').split(','))
    
    # 爬虫配置
    CRAWLER_INTERVAL = int(os.getenv('CRAWLER_INTERVAL', 3600))
    CRAWLER_MAX_PAGES = int(os.getenv('CRAWLER_MAX_PAGES', 100))
    CRAWLER_TIMEOUT = int(os.getenv('CRAWLER_TIMEOUT', 30))
    CRAWLER_USER_AGENT = os.getenv('CRAWLER_USER_AGENT')
    
    # 监控配置
    SENTRY_DSN = os.getenv('SENTRY_DSN')
    PROMETHEUS_PORT = int(os.getenv('PROMETHEUS_PORT', 9090))

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False
    
    # 开发环境特定配置
    TEMPLATES_AUTO_RELOAD = True
    EXPLAIN_TEMPLATE_LOADING = True
    SEND_FILE_MAX_AGE_DEFAULT = 0
    
    # 静态文件配置
    STATIC_FOLDER = 'static'
    STATIC_URL_PATH = '/static'

class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = False
    TESTING = True
    
    # 测试环境特定配置
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # 使用内存数据库
    WTF_CSRF_ENABLED = False  # 禁用CSRF保护
    MAIL_SUPPRESS_SEND = True  # 禁止发送邮件

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    
    # 生产环境特定配置
    PREFERRED_URL_SCHEME = 'https'  # 使用HTTPS
    SESSION_COOKIE_SECURE = True  # 安全Cookie
    REMEMBER_COOKIE_SECURE = True  # 记住我Cookie安全
    SESSION_COOKIE_HTTPONLY = True  # HttpOnly Cookie

# 配置映射
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 
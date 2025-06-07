from flask import request, abort, current_app
from functools import wraps
import jwt
from datetime import datetime, timedelta
from api.models import User
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import bleach
from flask_wtf.csrf import CSRFProtect, generate_csrf

# CSRF保护
csrf = CSRFProtect()

# 实现速率限制
limiter = Limiter(key_func=get_remote_address)

def setup_security(app):
    """初始化所有安全相关的组件"""
    # 初始化CSRF保护
    csrf.init_app(app)
    
    # 初始化速率限制器
    limiter.init_app(app)
    
    # 设置安全相关的配置
    app.config['CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # CSRF令牌有效期（秒）
    
    # 添加csrf_token到所有模板的上下文
    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf())
    
    return app

def validate_api_key(api_key):
    """验证API密钥"""
    valid_api_key = current_app.config.get('API_KEY')
    return api_key == valid_api_key

def require_api_key(f):
    """API密钥验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or not validate_api_key(api_key):
            abort(401)
        return f(*args, **kwargs)
    return decorated

def generate_jwt_token(user_id):
    """生成JWT令牌"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow()
    }
    return jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )

@limiter.limit("5 per minute")
def rate_limited_route():
    return "Rate limited response"

# XSS防护
def sanitize_input(data):
    """清理用户输入"""
    return bleach.clean(data)
from functools import wraps
from flask_caching import Cache
from flask import current_app

cache = Cache()

def init_cache(app):
    """初始化缓存"""
    cache_config = {
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_HOST': app.config['REDIS_HOST'],
        'CACHE_REDIS_PORT': app.config['REDIS_PORT'],
        'CACHE_DEFAULT_TIMEOUT': 300
    }
    cache.init_app(app, config=cache_config)

def cache_key_prefix():
    """生成缓存键前缀"""
    return f"{current_app.config['CACHE_KEY_PREFIX']}:"

def cached(timeout=300, key_prefix='view/%s'):
    """缓存装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = key_prefix % request.path
            rv = cache.get(cache_key)
            if rv is not None:
                return rv
            rv = f(*args, **kwargs)
            cache.set(cache_key, rv, timeout=timeout)
            return rv
        return decorated_function
    return decorator
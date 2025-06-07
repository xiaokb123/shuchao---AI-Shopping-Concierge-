from functools import wraps
import hashlib
import pickle
from redis import Redis
import json

class AdvancedCache:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.default_timeout = 300
    
    def cached_with_version(self, timeout=None):
        """带版本控制的缓存装饰器"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                cache_key = self._generate_cache_key(f, args, kwargs)
                version_key = f"{cache_key}:version"
                
                # 获取当前版本
                current_version = self.redis.get(version_key) or b'1'
                full_key = f"{cache_key}:{current_version.decode()}"
                
                # 尝试获取缓存
                cached_value = self.redis.get(full_key)
                if cached_value:
                    return pickle.loads(cached_value)
                
                # 执行函数
                value = f(*args, **kwargs)
                
                # 缓存结果
                self.redis.setex(
                    full_key,
                    timeout or self.default_timeout,
                    pickle.dumps(value)
                )
                
                return value
            return decorated_function
        return decorator
    
    def invalidate_by_pattern(self, pattern):
        """按模式失效缓存"""
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)
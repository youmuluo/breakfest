import time
from functools import lru_cache, wraps

class Cache:
    """简单的内存缓存实现"""
    def __init__(self):
        self.cache = {}
        self.expiry = {}
    
    def get(self, key):
        """获取缓存值"""
        if key not in self.cache:
            return None
        
        # 检查是否过期
        if key in self.expiry and time.time() > self.expiry[key]:
            del self.cache[key]
            del self.expiry[key]
            return None
        
        return self.cache[key]
    
    def set(self, key, value, ttl=3600):
        """设置缓存值，ttl为过期时间（秒）"""
        self.cache[key] = value
        if ttl > 0:
            self.expiry[key] = time.time() + ttl
    
    def delete(self, key):
        """删除缓存值"""
        if key in self.cache:
            del self.cache[key]
        if key in self.expiry:
            del self.expiry[key]
    
    def clear(self):
        """清空所有缓存"""
        self.cache.clear()
        self.expiry.clear()

# 创建全局缓存实例
cache = Cache()

def cached(ttl=3600):
    """缓存装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            key_parts = [func.__name__]
            for arg in args:
                if isinstance(arg, (int, str, float, bool)):
                    key_parts.append(str(arg))
            for k, v in sorted(kwargs.items()):
                if isinstance(v, (int, str, float, bool)):
                    key_parts.append(f"{k}={v}")
            cache_key = "_".join(key_parts)
            
            # 尝试从缓存获取
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 缓存结果
            cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

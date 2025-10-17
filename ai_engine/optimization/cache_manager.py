import redis
import json
import pickle
import hashlib
from functools import wraps
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Advanced caching system for performance optimization
    """
    
    def __init__(self):
        self.default_timeout = 3600  # 1 hour
    
    def generate_cache_key(self, prefix, data):
        """Generate unique cache key from data"""
        data_str = json.dumps(data, sort_keys=True)
        data_hash = hashlib.md5(data_str.encode()).hexdigest()
        return f"{prefix}:{data_hash}"
    
    def cache_result(self, timeout=None):
        """Decorator to cache function results"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key from function name and arguments
                cache_key = self.generate_cache_key(
                    func.__name__,
                    {'args': args, 'kwargs': kwargs}
                )
                
                # Try to get from cache
                cached_result = cache.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for {cache_key}")
                    return cached_result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                cache.set(cache_key, result, timeout or self.default_timeout)
                logger.debug(f"Cache set for {cache_key}")
                
                return result
            return wrapper
        return decorator
    
    def cache_analysis_result(self, filing_data, analysis_result):
        """Cache fraud analysis results"""
        cache_key = self.generate_cache_key('fraud_analysis', filing_data)
        cache.set(cache_key, analysis_result, 86400)  # 24 hours
        return cache_key
    
    def get_cached_analysis(self, filing_data):
        """Get cached fraud analysis"""
        cache_key = self.generate_cache_key('fraud_analysis', filing_data)
        return cache.get(cache_key)
    
    def cache_chat_response(self, query, context, response):
        """Cache chatbot responses"""
        cache_key = self.generate_cache_key('chat_response', {
            'query': query,
            'context': context
        })
        cache.set(cache_key, response, 1800)  # 30 minutes
        return cache_key
    
    def get_cached_chat_response(self, query, context):
        """Get cached chatbot response"""
        cache_key = self.generate_cache_key('chat_response', {
            'query': query,
            'context': context
        })
        return cache.get(cache_key)

# Global cache manager instance
cache_manager = CacheManager()
"""
Redis-based caching utilities for OmniDoc
"""
import json
import os
from typing import Any, Optional, Dict
import redis
from functools import wraps

# Get Redis URL from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Redis client (with connection pooling)
try:
    # For Upstash Redis, we need SSL support
    test_url = REDIS_URL
    
    if "upstash.io" in REDIS_URL:
        # Upstash requires SSL, convert redis:// to rediss://
        if not REDIS_URL.startswith("rediss://"):
            test_url = REDIS_URL.replace("redis://", "rediss://", 1)
    
    # rediss:// automatically enables SSL, no need to pass ssl parameter
    redis_client = redis.from_url(
        test_url,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5
    )
    redis_client.ping()  # Test connection
    REDIS_AVAILABLE = True
except Exception as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Redis connection failed: {type(e).__name__}: {str(e)}")
    REDIS_AVAILABLE = False
    redis_client = None


def get_cache_key(prefix: str, *args, **kwargs) -> str:
    """Generate a cache key from prefix and arguments"""
    key_parts = [prefix]
    if args:
        key_parts.extend(str(arg) for arg in args)
    if kwargs:
        key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
    return ":".join(key_parts)


def cache_result(ttl: int = 3600, key_prefix: str = "cache"):
    """
    Decorator to cache function results in Redis
    Supports both sync and async functions
    
    Args:
        ttl: Time to live in seconds (default: 1 hour)
        key_prefix: Prefix for cache keys
    """
    def decorator(func):
        import asyncio
        is_async = asyncio.iscoroutinefunction(func)
        
        if is_async:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                if not REDIS_AVAILABLE:
                    return await func(*args, **kwargs)
                
                cache_key = get_cache_key(key_prefix, func.__name__, *args, **kwargs)
                
                # Try to get from cache
                try:
                    cached = redis_client.get(cache_key)
                    if cached:
                        return json.loads(cached)
                except Exception:
                    pass
                
                # Call function and cache result
                result = await func(*args, **kwargs)
                
                # Store in cache
                try:
                    redis_client.setex(
                        cache_key,
                        ttl,
                        json.dumps(result, default=str)
                    )
                except Exception:
                    pass
                
                return result
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                if not REDIS_AVAILABLE:
                    return func(*args, **kwargs)
                
                cache_key = get_cache_key(key_prefix, func.__name__, *args, **kwargs)
                
                # Try to get from cache
                try:
                    cached = redis_client.get(cache_key)
                    if cached:
                        return json.loads(cached)
                except Exception:
                    pass
                
                # Call function and cache result
                result = func(*args, **kwargs)
                
                # Store in cache
                try:
                    redis_client.setex(
                        cache_key,
                        ttl,
                        json.dumps(result, default=str)
                    )
                except Exception:
                    pass
                
                return result
            return sync_wrapper
    return decorator


def get_cached(key: str) -> Optional[Any]:
    """Get a value from cache"""
    if not REDIS_AVAILABLE:
        return None
    
    try:
        cached = redis_client.get(key)
        if cached:
            return json.loads(cached)
    except Exception:
        pass
    
    return None


def set_cached(key: str, value: Any, ttl: int = 3600) -> bool:
    """Set a value in cache"""
    if not REDIS_AVAILABLE:
        return False
    
    try:
        redis_client.setex(key, ttl, json.dumps(value, default=str))
        return True
    except Exception:
        return False


def invalidate_cache(pattern: str) -> int:
    """Invalidate cache keys matching a pattern"""
    if not REDIS_AVAILABLE:
        return 0
    
    try:
        keys = redis_client.keys(pattern)
        if keys:
            return redis_client.delete(*keys)
        return 0
    except Exception:
        return 0


def cache_document_templates(ttl: int = 86400) -> callable:
    """Cache document templates (cache for 24 hours by default)"""
    return cache_result(ttl=ttl, key_prefix="doc_templates")


def cache_project_results(project_id: str, ttl: int = 3600) -> callable:
    """Cache project results (cache for 1 hour by default)"""
    return cache_result(ttl=ttl, key_prefix=f"project:{project_id}")


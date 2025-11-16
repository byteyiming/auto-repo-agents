"""
Celery application configuration for background task processing.

This module configures the Celery distributed task queue for handling
long-running document generation tasks asynchronously.

Configuration:
- Broker: Redis (for task queue)
- Backend: Redis (for task results)
- Serialization: JSON (for compatibility)
- Timezone: UTC

Task Limits:
- Maximum task duration: 1 hour (hard limit)
- Soft timeout: 55 minutes (allows graceful shutdown)
- Worker restart: After 10 tasks (prevents memory leaks)

Security:
- Tasks run in isolated worker processes
- No direct database access from web server
- Task results stored in Redis (can be configured for persistence)

Monitoring:
- Task state tracking enabled
- Task start/end times logged
- Failed tasks logged with full stack traces

Backward Compatibility:
- JSON serialization ensures compatibility across Python versions
- Task names are versioned in task definitions
"""
import os
from celery import Celery
import redis
import ssl  # 导入 ssl 模块

# Get Redis URL from environment or use default
# Environment variable allows configuration without code changes
REDIS_URL = os.getenv("REDIS_URL", "rediss://default:AXVjAAIncDJlNDY0OGUwNzdkMjc0M2U5OGE2Yzg4ZGUzYWU3YWVlZXAyMzAwNTE@right-loon-30051.upstash.io:6379")


def check_redis_available() -> bool:
    """
    Check if Redis is available for Celery broker/backend.
    
    Returns:
        True if Redis is available, False otherwise
    """
    try:
        # For Upstash Redis, we need SSL support
        # Check if URL contains upstash.io (requires SSL)
        test_url = REDIS_URL
        is_ssl = False

        if "upstash.io" in REDIS_URL or REDIS_URL.startswith("rediss://"):
            is_ssl = True
            # Upstash requires SSL, convert redis:// to rediss://
            if not test_url.startswith("rediss://"):
                test_url = test_url.replace("redis://", "rediss://", 1)
        
        # *** 修复 ***
        # 如果使用 rediss:// 并且缺少参数，则添加 ssl_cert_reqs=CERT_NONE
        # 这是 Celery/Redis 客户端进行 SSL 连接所必需的
        if is_ssl and "ssl_cert_reqs" not in test_url:
            separator = "?" if "?" not in test_url else "&"
            test_url += f"{separator}ssl_cert_reqs=CERT_NONE"

        # 尝试使用修改后的 URL 连接 Redis
        r = redis.from_url(
            test_url,
            socket_connect_timeout=5,
            socket_timeout=5,
            decode_responses=False  # Celery needs bytes
        )
        r.ping()
        return True
    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Redis connection failed: {type(e).__name__}: {str(e)}")
        return False


# Check Redis availability at module load time
REDIS_AVAILABLE = check_redis_available()

# Prepare Redis URL for Celery (may need SSL for Upstash)
celery_redis_url = REDIS_URL
is_ssl = False

if "upstash.io" in REDIS_URL or REDIS_URL.startswith("rediss://"):
    is_ssl = True
    if not celery_redis_url.startswith("rediss://"):
        # Upstash requires SSL, convert redis:// to rediss://
        celery_redis_url = celery_redis_url.replace("redis://", "rediss://", 1)

# *** 修复 ***
# 如果使用 SSL (rediss://)，Celery 后端会引发 ValueError，除非
# 提供了 ssl_cert_reqs。我们将其添加到 URL 查询字符串中。
# 对于我们信任的托管服务（如 Upstash），使用 CERT_NONE 是常见的做法。
if is_ssl and "ssl_cert_reqs" not in celery_redis_url:
    separator = "?" if "?" not in celery_redis_url else "&"
    celery_redis_url += f"{separator}ssl_cert_reqs=CERT_NONE"

# Create Celery app with application name
celery_app = Celery(
    "omnidoc",
    broker=celery_redis_url,  # Message broker for task queue
    backend=celery_redis_url,  # Result backend for task results
    include=["src.tasks.generation_tasks"],  # Task modules to include
)

# Celery configuration for production use
# SSL configuration for Upstash Redis (required for rediss://)
broker_transport_options = {}
if "upstash.io" in REDIS_URL or celery_redis_url.startswith("rediss://"):
    # *** 修复 ***
    # 使用 CERT_NONE 来匹配 URL 参数。
    # 使用 CERT_REQUIRED 并将 ssl_ca_certs=None 设为
    # 是矛盾的。
    broker_transport_options = {
        "ssl_cert_reqs": ssl.CERT_NONE,
        # "ssl_ca_certs": None, # 不再需要，因为 CERT_NONE 不会验证 CA
    }

celery_app.conf.update(
    # Serialization settings (JSON for compatibility)
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # Timezone settings
    timezone="UTC",
    enable_utc=True,
    
    # Task tracking for monitoring
    task_track_started=True,
    
    # Time limits (prevent runaway tasks)
    task_time_limit=3600,  # 1 hour max per task (hard limit)
    task_soft_time_limit=3300,  # 55 minutes soft limit (allows cleanup)
    
    # Worker settings (prevent memory leaks)
    worker_prefetch_multiplier=1,  # Process one task at a time (better for long tasks)
    worker_max_tasks_per_child=10,  # Restart worker after 10 tasks to prevent memory leaks
    
    # SSL configuration for Redis broker (Upstash requires SSL)
    broker_transport_options=broker_transport_options,
    result_backend_transport_options=broker_transport_options,
)
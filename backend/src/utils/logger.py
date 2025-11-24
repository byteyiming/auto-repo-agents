"""
Enhanced Logging Configuration Module
Supports JSON format, performance monitoring, and environment-based configuration

Features:
- JSON format for production (log analysis tools)
- Text format for development (easier to read)
- Performance monitoring decorator
- Environment-aware configuration (DEV/PROD)
- Categorized log files (API, business logic, agents, tasks, errors, etc.)
"""
import logging
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable
from functools import wraps
from enum import Enum

# Import configuration
from src.config.settings import get_settings

# Global error handler cache to avoid duplicates
_error_handlers: dict[str, logging.Handler] = {}


class LogCategory(str, Enum):
    """Log file categories for organized logging"""
    API = "api"                    # HTTP requests/responses, API errors
    BUSINESS = "business"         # Business logic, coordination, workflow
    AGENTS = "agents"             # Agent activities (generation, improvement, quality)
    TASKS = "tasks"               # Celery background tasks
    WEBSOCKET = "websocket"       # WebSocket connections and events
    ERROR = "error"               # All errors across the system
    PERFORMANCE = "performance"   # Performance metrics, slow operations
    DATABASE = "database"         # Database operations
    LLM = "llm"                   # LLM API calls and responses
    GENERAL = "general"           # General application logs


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)
        
        # Add performance metrics if present
        if hasattr(record, 'execution_time'):
            log_data["execution_time_seconds"] = record.execution_time
        if hasattr(record, 'memory_usage_mb'):
            log_data["memory_usage_mb"] = record.memory_usage_mb
        
        return json.dumps(log_data, ensure_ascii=False)


def get_log_category(name: str) -> LogCategory:
    """
    Determine log category based on module name
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        LogCategory enum value
    """
    name_lower = name.lower()
    
    # API and web routes
    if any(x in name_lower for x in ['web.routers', 'web.app', 'web.health', 'web.monitoring']):
        return LogCategory.API
    
    # Business logic and coordination
    if any(x in name_lower for x in ['coordination', 'coordinator', 'workflow']):
        return LogCategory.BUSINESS
    
    # Agents
    if 'agents' in name_lower:
        return LogCategory.AGENTS
    
    # Background tasks
    if any(x in name_lower for x in ['tasks', 'celery', 'generation_tasks']):
        return LogCategory.TASKS
    
    # WebSocket
    if 'websocket' in name_lower:
        return LogCategory.WEBSOCKET
    
    # Database
    if any(x in name_lower for x in ['context', 'context_manager', 'database']):
        return LogCategory.DATABASE
    
    # LLM providers
    if any(x in name_lower for x in ['llm', 'provider', 'gemini', 'openai', 'ollama']):
        return LogCategory.LLM
    
    # Default to general
    return LogCategory.GENERAL


def setup_logger(
    name: str,
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    log_dir: Optional[str] = None,
    log_format: Optional[str] = None,
    category: Optional[LogCategory] = None,
    force_reconfigure: bool = False
) -> logging.Logger:
    """
    Setup and configure a logger with both file and console handlers
    
    Args:
        name: Logger name (usually __name__)
        log_level: Logging level (default: from settings)
        log_file: Optional log file name (default: auto-generated)
        log_dir: Directory for log files (default: from settings)
        log_format: 'json' or 'text' (default: from settings)
        force_reconfigure: Force reconfiguration even if handlers exist
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if logger already configured (unless forced)
    if logger.handlers and not force_reconfigure:
        return logger
    
    # Clear existing handlers if forcing reconfigure
    if force_reconfigure and logger.handlers:
        logger.handlers.clear()
    
    # Get settings from environment
    settings = get_settings()
    
    # Use provided values or fall back to settings
    level_str = log_level or settings.log_level
    level = getattr(logging, level_str.upper(), logging.INFO)
    logger.setLevel(level)
    
    log_format_type = log_format or settings.log_format
    log_dir_path = log_dir or settings.log_dir
    
    # Determine category
    log_category = category or get_log_category(name)
    
    # Create formatters based on format type
    if log_format_type.lower() == 'json':
        detailed_formatter = JSONFormatter()
        console_formatter = JSONFormatter()  # JSON in console for prod
    else:
        # Text format (for DEV)
        detailed_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
    
    # Console handler (always enabled)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (always enabled for local development)
    # Use regular FileHandler for Celery worker (RotatingFileHandler causes seek errors)
    # Use RotatingFileHandler for non-Celery processes
    is_celery_worker = os.getenv("CELERY_WORKER", "").lower() in ("true", "1") or "celery" in sys.argv[0] if len(sys.argv) > 0 else False
    
    if log_dir_path:
        log_path = Path(log_dir_path)
        log_path.mkdir(parents=True, exist_ok=True)
        
        # Generate log file name based on category
        if not log_file:
            timestamp = datetime.now().strftime('%Y%m%d')
            env_suffix = settings.environment.value
            # Use category-based naming instead of module-based
            log_file = f"{log_category.value}_{env_suffix}_{timestamp}.log"
        
        file_path = log_path / log_file
        
        # Use regular FileHandler for Celery worker (avoids seek errors)
        # Use RotatingFileHandler for other processes (better for long-running apps)
        if is_celery_worker:
            # Celery worker: use simple FileHandler
            file_handler = logging.FileHandler(file_path, encoding='utf-8', mode='a')
        else:
            # Non-Celery: use RotatingFileHandler to prevent log files from growing too large
            try:
                from logging.handlers import RotatingFileHandler
                # Max 10MB per file, keep 5 backup files
                file_handler = RotatingFileHandler(
                    file_path, 
                    maxBytes=10*1024*1024,  # 10MB
                    backupCount=5,
                    encoding='utf-8'
                )
            except ImportError:
                # Fallback to regular FileHandler if RotatingFileHandler unavailable
                file_handler = logging.FileHandler(file_path, encoding='utf-8')
        
        file_handler.setLevel(logging.DEBUG)  # File logs are more detailed
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
        
        # Add shared error log handler (all ERROR and CRITICAL go to error log)
        # Use a single shared handler per environment/day to avoid duplicates
        error_log_key = f"error_{settings.environment.value}_{datetime.now().strftime('%Y%m%d')}"
        
        if error_log_key not in _error_handlers:
            error_log_file = f"{error_log_key}.log"
            error_file_path = log_path / error_log_file
            
            if is_celery_worker:
                error_handler = logging.FileHandler(error_file_path, encoding='utf-8', mode='a')
            else:
                try:
                    from logging.handlers import RotatingFileHandler
                    error_handler = RotatingFileHandler(
                        error_file_path,
                        maxBytes=10*1024*1024,  # 10MB
                        backupCount=5,
                        encoding='utf-8'
                    )
                except ImportError:
                    error_handler = logging.FileHandler(error_file_path, encoding='utf-8')
            
            error_handler.setLevel(logging.ERROR)  # Only ERROR and CRITICAL
            error_handler.setFormatter(detailed_formatter)
            _error_handlers[error_log_key] = error_handler
        
        # Add the shared error handler to this logger
        logger.addHandler(_error_handlers[error_log_key])
    
    return logger


def get_logger(name: str, category: Optional[LogCategory] = None) -> logging.Logger:
    """
    Get or create a logger instance with environment-aware configuration
    
    Args:
        name: Logger name (usually __name__)
        category: Optional log category override (auto-detected if not provided)
    
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    # Configure if not already configured
    if not logger.handlers:
        setup_logger(name, category=category)
    
    return logger


def log_performance(func: Callable) -> Callable:
    """
    Decorator to log function execution time and performance metrics
    
    Usage:
        @log_performance
        def my_function():
            ...
    
    The decorator will log:
    - Execution time
    - Function name
    - Arguments (if settings.enable_profiling is True)
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        settings = get_settings()
        
        if not settings.enable_performance_logging:
            return func(*args, **kwargs)
        
        logger = get_logger(func.__module__)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Log performance metrics
            extra = {
                'execution_time': execution_time,
                'function': func.__name__,
                'module': func.__module__
            }
            
            # Add arguments if profiling is enabled
            if settings.enable_profiling:
                extra['args'] = str(args)[:200]  # Limit length
                extra['kwargs'] = str(kwargs)[:200]
            
            # Log based on execution time
            if execution_time > 1.0:
                logger.warning(
                    f"Slow execution: {func.__name__} took {execution_time:.2f}s",
                    extra={'extra_fields': extra}
                )
            else:
                logger.debug(
                    f"Performance: {func.__name__} took {execution_time:.3f}s",
                    extra={'extra_fields': extra}
                )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"Error in {func.__name__} after {execution_time:.2f}s: {str(e)}",
                exc_info=True,
                extra={'extra_fields': {
                    'execution_time': execution_time,
                    'function': func.__name__
                }}
            )
            raise
    
    return wrapper


def log_with_context(logger: logging.Logger, level: int = logging.INFO):
    """
    Context manager for logging with automatic timing
    
    Usage:
        with log_with_context(logger):
            # your code here
            pass
    
    Automatically logs entry/exit with timing
    """
    class LogContext:
        def __init__(self, logger: logging.Logger, level: int):
            self.logger = logger
            self.level = level
            self.start_time = None
            self.context_name = None
        
        def __enter__(self):
            self.start_time = time.time()
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            execution_time = time.time() - self.start_time
            
            if exc_type:
                self.logger.error(
                    f"Context failed after {execution_time:.2f}s",
                    exc_info=(exc_type, exc_val, exc_tb),
                    extra={'extra_fields': {'execution_time': execution_time}}
                )
            else:
                self.logger.log(
                    self.level,
                    f"Context completed in {execution_time:.3f}s",
                    extra={'extra_fields': {'execution_time': execution_time}}
                )
            
            return False  # Don't suppress exceptions
    
    return LogContext(logger, level)

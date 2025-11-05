"""
Example: Using Environment Configuration and Enhanced Logging

This script demonstrates:
1. Setting environment (DEV/PROD)
2. Using JSON vs Text logging
3. Performance monitoring
"""
from src.config import set_environment, Environment, get_settings, is_dev, is_prod
from src.utils.logger import get_logger
from src.utils.performance import track_performance, PerformanceMonitor

# Example 1: Set environment
print("=" * 60)
print("Example 1: Setting Environment")
print("=" * 60)

# Set to DEV mode
set_environment(Environment.DEV)
settings = get_settings()
print(f"Environment: {settings.environment.value}")
print(f"Log Format: {settings.log_format}")
print(f"Log Level: {settings.log_level}")
print(f"Performance Logging: {settings.enable_performance_logging}")
print()

# Set to PROD mode
set_environment(Environment.PROD)
settings = get_settings()
print(f"Environment: {settings.environment.value}")
print(f"Log Format: {settings.log_format}")
print(f"Log Level: {settings.log_level}")
print(f"Performance Logging: {settings.enable_performance_logging}")
print()

# Example 2: Logging in different formats
print("=" * 60)
print("Example 2: Logging Format Differences")
print("=" * 60)

# DEV mode - Text format
set_environment(Environment.DEV)
logger = get_logger(__name__)
logger.info("This is an info message in DEV mode (text format)")
logger.debug("This is a debug message (only in DEV)")
logger.warning("This is a warning message")
print()

# PROD mode - JSON format
set_environment(Environment.PROD)
logger = get_logger(__name__)
logger.info("This is an info message in PROD mode (JSON format)")
logger.warning("This is a warning message in JSON")
print()

# Example 3: Performance Monitoring
print("=" * 60)
print("Example 3: Performance Monitoring")
print("=" * 60)

set_environment(Environment.DEV)

@track_performance(min_time_ms=50, log_level='INFO', include_args=True)
def slow_function(delay=0.1):
    """Simulate a slow operation"""
    import time
    time.sleep(delay)
    return "Done"

# Fast function (< 50ms) - won't log
result1 = slow_function(0.01)
print(f"Result: {result1}")
print()

# Slow function (> 50ms) - will log
result2 = slow_function(0.2)
print(f"Result: {result2}")
print()

# Example 4: Context Manager for Performance
print("=" * 60)
print("Example 4: Performance Context Manager")
print("=" * 60)

with PerformanceMonitor("document_generation", logger):
    import time
    time.sleep(0.1)  # Simulate work
    logger.info("Generating documents...")
print()

# Example 5: Conditional Logic Based on Environment
print("=" * 60)
print("Example 5: Environment-Based Logic")
print("=" * 60)

if is_dev():
    print("Running development-specific code")
    logger.debug("Debug information only available in DEV")
elif is_prod():
    print("Running production-specific code")
    logger.info("Production mode - debug logs disabled")

print()
print("=" * 60)
print("Examples completed!")
print("=" * 60)


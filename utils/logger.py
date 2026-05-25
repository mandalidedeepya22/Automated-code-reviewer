"""
Logging configuration module for the AI Code Reviewer.
Provides centralized logging setup with file and console handlers.
"""

import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime


def setup_logger(
    name: str,
    log_file: str = None,
    level: str = "INFO",
    max_bytes: int = 10485760,
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up a logger with both file and console handlers.
    
    Args:
        name: Name of the logger
        log_file: Path to log file (default: logs/{name}.log)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup log files to keep
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if log_file specified or default)
    if log_file is None:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"{name}.log"
    
    # Ensure log directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(exist_ok=True)
    
    # Rotating file handler
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: Name of the logger
        
    Returns:
        Logger instance
    """
    return setup_logger(name)


# Create module-specific loggers
app_logger = setup_logger("app")
db_logger = setup_logger("database")
parser_logger = setup_logger("code_parser")
analyzer_logger = setup_logger("static_analyzer")
security_logger = setup_logger("security_checker")
ai_logger = setup_logger("ai_reviewer")
github_logger = setup_logger("github_fetcher")
report_logger = setup_logger("report_generator")


def log_function_call(logger: logging.Logger):
    """
    Decorator to log function calls with arguments and return values.
    
    Usage:
        @log_function_call(logger)
        def my_function(arg1, arg2):
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug(f"Calling {func.__name__} with args: {args}, kwargs: {kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"{func.__name__} returned: {result}")
                return result
            except Exception as e:
                logger.error(f"{func.__name__} raised {type(e).__name__}: {e}")
                raise
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    return decorator


def log_execution_time(logger: logging.Logger, threshold: float = 1.0):
    """
    Decorator to log function execution time.
    
    Args:
        logger: Logger instance
        threshold: Log warning if execution exceeds this many seconds
        
    Usage:
        @log_execution_time(logger, threshold=0.5)
        def slow_function():
            pass
    """
    import time
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed_time = time.time() - start_time
                if elapsed_time > threshold:
                    logger.warning(
                        f"{func.__name__} took {elapsed_time:.2f}s (threshold: {threshold}s)"
                    )
                else:
                    logger.debug(f"{func.__name__} completed in {elapsed_time:.3f}s")
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    return decorator
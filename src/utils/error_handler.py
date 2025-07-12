"""
Centralized error handling and logging system for web crawler
"""

import logging
import traceback
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, Callable
from functools import wraps


class ErrorLevel(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CrawlerError(Exception):
    """Base exception for crawler errors"""
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN"
        self.details = details or {}
        self.timestamp = datetime.now()


class NetworkError(CrawlerError):
    """Network-related errors"""
    pass


class ParseError(CrawlerError):
    """Content parsing errors"""
    pass


class ValidationError(CrawlerError):
    """Input validation errors"""
    pass


class RateLimitError(CrawlerError):
    """Rate limiting errors"""
    pass


class AntiDetectionError(CrawlerError):
    """Anti-detection related errors"""
    pass


class ErrorHandler:
    """Centralized error handling and logging"""
    
    def __init__(self, log_level: str = "INFO", log_file: str = None):
        self.logger = self._setup_logger(log_level, log_file)
        self.error_counts = {}
        self.recovery_strategies = {}
        
        # Register default recovery strategies
        self._register_default_strategies()
    
    def _setup_logger(self, log_level: str, log_file: str = None) -> logging.Logger:
        """Setup structured logging"""
        logger = logging.getLogger("crawler")
        logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None, 
                    level: ErrorLevel = ErrorLevel.MEDIUM) -> bool:
        """
        Handle error with logging and recovery
        
        Args:
            error: Exception to handle
            context: Additional context information
            level: Error severity level
            
        Returns:
            True if error was handled and can continue, False if should abort
        """
        context = context or {}
        error_type = type(error).__name__
        
        # Increment error count
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Log the error
        self._log_error(error, context, level)
        
        # Try recovery strategy
        if error_type in self.recovery_strategies:
            try:
                return self.recovery_strategies[error_type](error, context)
            except Exception as recovery_error:
                self.logger.error(f"Recovery strategy failed: {recovery_error}")
        
        # Default handling based on error level
        if level in [ErrorLevel.CRITICAL]:
            return False  # Abort
        
        return True  # Continue
    
    def _log_error(self, error: Exception, context: Dict[str, Any], level: ErrorLevel):
        """Log error with context"""
        error_info = {
            'error_type': type(error).__name__,
            'message': str(error),
            'level': level.value,
            'context': context,
            'traceback': traceback.format_exc() if level in [ErrorLevel.HIGH, ErrorLevel.CRITICAL] else None
        }
        
        if isinstance(error, CrawlerError):
            error_info.update({
                'error_code': error.error_code,
                'details': error.details,
                'timestamp': error.timestamp.isoformat()
            })
        
        # Log based on severity
        if level == ErrorLevel.CRITICAL:
            self.logger.critical(f"CRITICAL ERROR: {error_info}")
        elif level == ErrorLevel.HIGH:
            self.logger.error(f"HIGH ERROR: {error_info}")
        elif level == ErrorLevel.MEDIUM:
            self.logger.warning(f"MEDIUM ERROR: {error_info}")
        else:
            self.logger.info(f"LOW ERROR: {error_info}")
    
    def register_recovery_strategy(self, error_type: str, strategy: Callable):
        """Register recovery strategy for specific error type"""
        self.recovery_strategies[error_type] = strategy
    
    def _register_default_strategies(self):
        """Register default recovery strategies"""
        
        def handle_network_error(error: NetworkError, context: Dict[str, Any]) -> bool:
            """Handle network errors with retry logic"""
            retry_count = context.get('retry_count', 0)
            max_retries = context.get('max_retries', 3)
            
            if retry_count < max_retries:
                self.logger.info(f"Network error, will retry ({retry_count + 1}/{max_retries})")
                return True
            
            self.logger.error("Max retries exceeded for network error")
            return False
        
        def handle_rate_limit_error(error: RateLimitError, context: Dict[str, Any]) -> bool:
            """Handle rate limit errors with backoff"""
            self.logger.warning("Rate limit hit, will backoff")
            # The backoff logic should be handled in the calling code
            return True
        
        def handle_parse_error(error: ParseError, context: Dict[str, Any]) -> bool:
            """Handle parsing errors gracefully"""
            self.logger.warning(f"Parsing failed, skipping item: {error.message}")
            return True  # Continue with next item
        
        def handle_validation_error(error: ValidationError, context: Dict[str, Any]) -> bool:
            """Handle validation errors"""
            self.logger.warning(f"Validation failed: {error.message}")
            return False  # Don't continue with invalid data
        
        self.register_recovery_strategy('NetworkError', handle_network_error)
        self.register_recovery_strategy('RateLimitError', handle_rate_limit_error)
        self.register_recovery_strategy('ParseError', handle_parse_error)
        self.register_recovery_strategy('ValidationError', handle_validation_error)
    
    def get_error_stats(self) -> Dict[str, int]:
        """Get error statistics"""
        return self.error_counts.copy()
    
    def reset_stats(self):
        """Reset error statistics"""
        self.error_counts.clear()


def error_handler_decorator(handler: ErrorHandler, level: ErrorLevel = ErrorLevel.MEDIUM, 
                          reraise: bool = False):
    """
    Decorator for automatic error handling
    
    Args:
        handler: ErrorHandler instance
        level: Error level for logging
        reraise: Whether to reraise the exception after handling
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                context = {
                    'function': func.__name__,
                    'args': str(args)[:200],  # Limit length
                    'kwargs': str(kwargs)[:200]
                }
                
                should_continue = handler.handle_error(e, context, level)
                
                if reraise and not should_continue:
                    raise
                    
                return None
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = {
                    'function': func.__name__,
                    'args': str(args)[:200],
                    'kwargs': str(kwargs)[:200]
                }
                
                should_continue = handler.handle_error(e, context, level)
                
                if reraise and not should_continue:
                    raise
                    
                return None
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def safe_execute(func: Callable, default_return=None, error_handler: ErrorHandler = None,
                level: ErrorLevel = ErrorLevel.LOW) -> Any:
    """
    Safely execute a function with error handling
    
    Args:
        func: Function to execute
        default_return: Default return value on error
        error_handler: ErrorHandler instance
        level: Error level
        
    Returns:
        Function result or default_return on error
    """
    try:
        return func()
    except Exception as e:
        if error_handler:
            error_handler.handle_error(e, {'function': func.__name__}, level)
        return default_return
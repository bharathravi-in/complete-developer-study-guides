#!/usr/bin/env python3
"""
Logging Decorator - Production-Ready Implementation

Features:
- Configurable log levels
- Execution timing
- Exception logging
- Input/output logging
"""

import functools
import logging
import time
from typing import Callable, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def create_logger(name: str = None) -> logging.Logger:
    """Create a configured logger"""
    return logging.getLogger(name or __name__)


def log_call(
    logger: Optional[logging.Logger] = None,
    level: int = logging.INFO,
    log_args: bool = True,
    log_result: bool = True,
    log_time: bool = True,
    sensitive_args: Optional[list] = None
):
    """
    Configurable logging decorator.
    
    Args:
        logger: Logger instance (creates default if None)
        level: Logging level
        log_args: Whether to log function arguments
        log_result: Whether to log return value
        log_time: Whether to log execution time
        sensitive_args: List of argument names to mask
    """
    if logger is None:
        logger = create_logger()
    
    sensitive_args = sensitive_args or []
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            
            # Build args string for logging
            if log_args:
                # Get argument names
                import inspect
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                
                # Mask sensitive arguments
                safe_args = {}
                for key, value in bound_args.arguments.items():
                    if key in sensitive_args:
                        safe_args[key] = "****"
                    else:
                        safe_args[key] = repr(value)[:50]  # Truncate long values
                
                args_str = ", ".join(f"{k}={v}" for k, v in safe_args.items())
                logger.log(level, f"Calling {func_name}({args_str})")
            else:
                logger.log(level, f"Calling {func_name}()")
            
            # Execute function
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                elapsed = time.perf_counter() - start_time
                
                # Log result
                if log_result:
                    result_str = repr(result)[:100]  # Truncate
                    logger.log(level, f"{func_name} returned: {result_str}")
                
                # Log time
                if log_time:
                    logger.log(level, f"{func_name} completed in {elapsed*1000:.2f}ms")
                
                return result
                
            except Exception as e:
                elapsed = time.perf_counter() - start_time
                logger.exception(f"{func_name} raised {type(e).__name__}: {e}")
                logger.error(f"{func_name} failed after {elapsed*1000:.2f}ms")
                raise
        
        return wrapper
    return decorator


# ============================================
# USAGE EXAMPLES
# ============================================

# Create a custom logger
app_logger = create_logger("my_app")


@log_call(logger=app_logger)
def simple_function(x: int, y: int) -> int:
    """Simple addition"""
    return x + y


@log_call(logger=app_logger, sensitive_args=["password"])
def login(username: str, password: str) -> dict:
    """Simulated login with sensitive data masking"""
    time.sleep(0.1)  # Simulate network call
    if username == "admin" and password == "secret":
        return {"token": "abc123", "user": username}
    raise ValueError("Invalid credentials")


@log_call(logger=app_logger, log_result=False)
def get_large_data() -> list:
    """Function returning large data (result not logged)"""
    return list(range(10000))


@log_call(level=logging.DEBUG)
def debug_function(data: dict) -> dict:
    """Function logged at debug level"""
    return {k: v * 2 for k, v in data.items()}


# ============================================
# ALTERNATIVE: Decorator Class
# ============================================

class LogCall:
    """Class-based logging decorator"""
    
    def __init__(
        self,
        func: Callable = None,
        *,
        logger: logging.Logger = None,
        level: int = logging.INFO
    ):
        self.logger = logger or create_logger()
        self.level = level
        self.func = func
        
        if func is not None:
            functools.update_wrapper(self, func)
    
    def __call__(self, *args, **kwargs):
        if self.func is None:
            # Called with arguments: @LogCall(logger=...)
            func = args[0]
            return LogCall(func, logger=self.logger, level=self.level)
        
        # Normal call
        self.logger.log(self.level, f"Calling {self.func.__name__}")
        try:
            result = self.func(*args, **kwargs)
            self.logger.log(self.level, f"{self.func.__name__} completed")
            return result
        except Exception as e:
            self.logger.exception(f"{self.func.__name__} failed")
            raise
    
    def __get__(self, obj, objtype=None):
        """Support for instance methods"""
        if obj is None:
            return self
        return functools.partial(self, obj)


# ============================================
# DEMO
# ============================================

def main():
    print("=" * 60)
    print("LOGGING DECORATOR DEMO")
    print("=" * 60)
    
    print("\n1. Simple function call:")
    result = simple_function(10, 20)
    print(f"   Result: {result}")
    
    print("\n2. Function with sensitive args:")
    try:
        token = login("admin", "secret")
        print(f"   Login successful!")
    except ValueError as e:
        print(f"   Login failed: {e}")
    
    print("\n3. Large data (result not logged):")
    data = get_large_data()
    print(f"   Got {len(data)} items")
    
    print("\n4. Debug level function:")
    result = debug_function({"a": 1, "b": 2})
    print(f"   Result: {result}")
    
    print("\n5. Function that raises exception:")
    try:
        login("user", "wrong")
    except ValueError:
        print("   Exception was logged!")


if __name__ == "__main__":
    main()

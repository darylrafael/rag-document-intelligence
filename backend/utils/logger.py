import logging
import time
import sys
import asyncio
from functools import wraps
from typing import Callable, Any

def setup_logger(name: str) -> logging.Logger:
    """Configures and returns a structured logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

pipeline_logger = setup_logger("pipeline")

def log_pipeline_stage(stage_name: str):
    """
    Decorator to log execution time of a pipeline stage.
    Expects the wrapped function to return a tuple or dict containing 
    input_count and output_count if applicable, or we can just log the time.
    For simplicity, we'll log the time here and let the function log specifics.
    """
    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                start_time = time.perf_counter()
                try:
                    result = await func(*args, **kwargs)
                    duration_ms = (time.perf_counter() - start_time) * 1000
                    pipeline_logger.info(
                        f"Stage: {stage_name} | Status: SUCCESS | Duration: {duration_ms:.2f}ms"
                    )
                    return result
                except Exception as e:
                    duration_ms = (time.perf_counter() - start_time) * 1000
                    pipeline_logger.error(
                        f"Stage: {stage_name} | Status: ERROR | Duration: {duration_ms:.2f}ms | Error: {str(e)}"
                    )
                    raise
            return async_wrapper
        else:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                start_time = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    duration_ms = (time.perf_counter() - start_time) * 1000
                    pipeline_logger.info(
                        f"Stage: {stage_name} | Status: SUCCESS | Duration: {duration_ms:.2f}ms"
                    )
                    return result
                except Exception as e:
                    duration_ms = (time.perf_counter() - start_time) * 1000
                    pipeline_logger.error(
                        f"Stage: {stage_name} | Status: ERROR | Duration: {duration_ms:.2f}ms | Error: {str(e)}"
                    )
                    raise
            return wrapper
    return decorator

def log_stage_metrics(stage_name: str, duration_ms: float, input_count: int, output_count: int):
    """Utility to explicitly log pipeline metrics."""
    pipeline_logger.info(
        f"Stage: {stage_name} | Duration: {duration_ms:.2f}ms | "
        f"Input Count: {input_count} | Output Count: {output_count}"
    )

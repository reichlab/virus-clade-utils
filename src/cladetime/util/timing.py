"""Code to support the timing of functions."""

import functools
import time

import structlog

logger = structlog.get_logger()


def time_function(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        logger.info(f"{repr(func.__name__)} complete", elapsed_seconds=round(run_time, ndigits=2))
        return value

    return wrapper

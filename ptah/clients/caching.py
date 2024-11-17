"""
Cache-related utilities.
"""

from functools import wraps
from typing import Callable, TypeVar

from cachelib import BaseCache

from ptah.clients._injector import get

# https://stackoverflow.com/a/50185096
T = TypeVar("T", bound=Callable)


def cache_ignore_inputs(func: T) -> T:
    """
    Cache the output of a function based on module and function name, ignoring input values. Useful
    for operations that "retrieve state" from the outside world.
    """
    cache_key = f"{func.__module__}.{func.__name__}"

    @wraps(func)
    def inner(*args, **kwargs):
        _cache = get(BaseCache)
        if _cache.has(cache_key):
            return _cache.get(cache_key)
        rv = func(*args, **kwargs)
        _cache.set(cache_key, rv)
        return rv

    return inner  # type: ignore

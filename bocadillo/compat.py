"""Compatibility utilities (version-dependant, sync/async, etc.)."""
import re
import sys
from asyncio import iscoroutinefunction
from typing import Callable, Coroutine

from starlette.concurrency import run_in_threadpool

from .exceptions import ShouldBeAsync

try:
    from contextlib import asynccontextmanager
except ImportError:  # pragma: no cover
    assert sys.version_info[:2] == (3, 6)
    from async_generator import asynccontextmanager

_camel_regex = re.compile(r"(.)([A-Z][a-z]+)")
_snake_regex = re.compile(r"([a-z0-9])([A-Z])")


# NOTE: this helper is only provided for users; we do not use it anywhere
# else in the code base.
async def call_async(func: Callable, *args, sync=False, **kwargs) -> Coroutine:
    """Call a function in an async manner.

    If the function is synchronous (or the `sync` hint flag is set),
    it is run in the asyncio thread pool.
    """
    if sync or not iscoroutinefunction(func):
        return await run_in_threadpool(func, *args, **kwargs)
    return await func(*args, **kwargs)


def camel_to_snake(name: str) -> str:
    """Convert a CamelCase name to its snake_case version."""
    s1 = _camel_regex.sub(r"\1_\2", name)
    return _snake_regex.sub(r"\1_\2", s1).lower()


def check_async(func: Callable):
    """Check that a callable is asynchronous.

    Parameters
    ----------
    func : callable
        A function or class instance.

    Raises
    ------
    ShouldBeAsync :
        If `func` (or its `__call__()` method) is not a coroutine function.
    """
    if iscoroutinefunction(func):
        return
    elif hasattr(func, "__call__") and iscoroutinefunction(func.__call__):
        # Func may be a callable class instance
        return
    raise ShouldBeAsync(func)

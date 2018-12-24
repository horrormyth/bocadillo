"""Bocadillo middleware definition."""
from typing import Coroutine, Callable

from .compat import check_async
from .request import Request
from .response import Response

Dispatcher = Callable[[Request], Coroutine]


class MiddlewareMeta(type):
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        for attr in "before_dispatch", "dispatch", "after_dispatch":
            method = getattr(cls, attr, None)
            if method is not None:
                check_async(method)
        return cls


class Middleware(metaclass=MiddlewareMeta):
    """Base class for middleware classes."""

    def __init__(self, dispatch: Dispatcher, **kwargs):
        self.dispatch = dispatch
        self.kwargs = kwargs

    async def __call__(self, req: Request) -> Response:
        res: Response = None

        if hasattr(self, "before_dispatch"):
            res = await self.before_dispatch(req)

        res = res or await self.dispatch(req)

        if hasattr(self, "after_dispatch"):
            res = await self.after_dispatch(req, res) or res

        return res


# TODO: remove in v0.8
RoutingMiddleware = Middleware

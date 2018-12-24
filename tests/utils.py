import os
from contextlib import contextmanager
from typing import Any

from bocadillo import API


class RouteBuilder:
    """Builder of simple testing routes."""

    def __init__(self, api: API = None):
        self._api = api

    @property
    def api(self):
        return self._api

    def function_based(self, pattern: str, *args, res: dict = None, **kwargs):
        if res is None:
            res = {}

        @self._api.route(pattern, *args, **kwargs)
        async def view(request, response):
            for key, value in res.items():
                setattr(response, key, value)

    def class_based(self, pattern: str, *args, **kwargs):
        @self._api.route(pattern, *args, **kwargs)
        class View:
            pass


@contextmanager
def function_hooks(before_value: Any = True, after_value: Any = True):
    flags = {"before": False, "after": False}

    def before(req, res, params, value=before_value):
        nonlocal flags
        assert not flags["after"]
        flags["before"] = value

    def after(req, res, params, value=after_value):
        nonlocal flags
        assert flags["before"]
        flags["after"] = value

    yield before, after

    assert flags["before"] == before_value
    assert flags["after"] == after_value


@contextmanager
def async_function_hooks(before_value: Any = True, after_value: Any = True):
    flags = {"before": False, "after": False}

    async def before(req, res, params, value=before_value):
        nonlocal flags
        assert not flags["after"]
        flags["before"] = value

    async def after(req, res, params, value=after_value):
        nonlocal flags
        assert flags["before"]
        flags["after"] = value

    yield before, after

    assert flags["before"] == before_value
    assert flags["after"] == after_value


@contextmanager
def class_hooks():
    flags = {"before": False, "after": False}

    class SetFlag:
        def __init__(self, flag, value):
            self.flag = flag
            self.value = value

        async def __call__(self, req, res, params):
            nonlocal flags
            flags[self.flag] = self.value

    yield SetFlag("before", True), SetFlag("after", True)

    assert flags["before"]
    assert flags["after"]


@contextmanager
def env(var: str, value: str):
    initial = os.environ.get(var, None)
    os.environ[var] = value
    try:
        yield
    finally:
        os.environ.pop(var)
        if initial is not None:
            os.environ[var] = initial

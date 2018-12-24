from asyncio import sleep
from contextlib import contextmanager

import pytest

from bocadillo import API, Middleware
from bocadillo.exceptions import HTTPError, ShouldBeAsync


@contextmanager
def build_middleware(expect_kwargs=None, sync=False):
    called = {"before": False, "after": False}
    kwargs = None

    class SetCalled(Middleware):
        def __init__(self, dispatch, **kw):
            nonlocal kwargs
            kwargs = kw
            super().__init__(dispatch, **kw)

        if sync:

            def before_dispatch(self, req):
                nonlocal called
                called["before"] = True

            def after_dispatch(self, req, res):
                nonlocal called
                called["after"] = True

        else:

            async def before_dispatch(self, req):
                nonlocal called
                await sleep(0.01)
                called["before"] = True

            async def after_dispatch(self, req, res):
                nonlocal called
                await sleep(0.01)
                called["after"] = True

    yield SetCalled

    assert called["before"] is True
    assert called["after"] is True
    if expect_kwargs is not None:
        assert kwargs == expect_kwargs


def test_if_middleware_is_added_then_it_is_called(api: API):
    with build_middleware() as middleware:
        api.add_middleware(middleware)

        @api.route("/")
        async def index(req, res):
            pass

        api.client.get("/")


def test_can_pass_extra_kwargs(api: API):
    kwargs = {"foo": "bar"}
    with build_middleware(expect_kwargs=kwargs) as middleware:
        api.add_middleware(middleware, **kwargs)

        @api.route("/")
        async def index(req, res):
            pass

        api.client.get("/")


def test_callbacks_are_called_if_method_not_allowed(api: API):
    with build_middleware() as middleware:
        api.add_middleware(middleware)

        @api.route("/", methods=["get"])
        async def index(req, res):
            pass

        response = api.client.put("/")
        assert response.status_code == 405


def test_before_dispatch_must_be_async():
    with pytest.raises(ShouldBeAsync):

        class MyMiddleware(Middleware):
            def before_dispatch(self, req):
                pass


def test_after_dispatch_must_be_async():
    with pytest.raises(ShouldBeAsync):

        class MyMiddleware(Middleware):
            def after_dispatch(self, req, res):
                pass


@pytest.mark.parametrize("when", ["before", "after"])
def test_errors_raised_in_callback_return_500_error(api: API, when):
    class CustomError(Exception):
        pass

    @api.error_handler(CustomError)
    async def handle_error(req, res, exception):
        res.text = "muted!"

    class MiddlewareWithErrors(Middleware):
        async def before_dispatch(self, req):
            if when == "before":
                raise CustomError

        async def after_dispatch(self, req, res):
            if when == "after":
                raise CustomError

    api.add_middleware(MiddlewareWithErrors)

    @api.route("/")
    async def index(req, res):
        pass

    response = api.client.get("/")
    assert response.status_code == 500
    assert response.text == "muted!"


def test_middleware_uses_registered_http_error_handler(api: API):
    @api.error_handler(HTTPError)
    async def custom(req, res, exc: HTTPError):
        res.status_code = exc.status_code
        res.text = "Foo"

    class NopeMiddleware(Middleware):
        async def before_dispatch(self, req):
            raise HTTPError(401)

    api.add_middleware(NopeMiddleware)

    @api.route("/")
    async def index(req, res):
        pass

    response = api.client.get("/")
    assert response.status_code == 401
    assert response.text == "Foo"

import pytest

from bocadillo import API
from bocadillo.routing import RouteDeclarationError
from tests.utils import RouteBuilder


def test_index_returns_404_by_default(api: API):
    assert api.client.get("/").status_code == 404


def test_if_route_not_registered_then_404(api: API):
    assert api.client.get("/test").status_code == 404


def test_if_route_registered_then_not_404(api: API):
    @api.route("/")
    async def test(req, res):
        pass

    assert api.client.get("/").status_code != 404


def test_default_status_code_is_200_on_routes(builder: RouteBuilder):
    builder.function_based("/")
    assert builder.api.client.get("/").status_code == 200


def test_route_must_start_with_slash(builder: RouteBuilder):
    with pytest.raises(RouteDeclarationError):
        builder.function_based("foo")


def test_route_must_expect_request_and_response(api: API):
    with pytest.raises(RouteDeclarationError):

        @api.route("/foo/{bar}")
        def foo(bar):
            pass

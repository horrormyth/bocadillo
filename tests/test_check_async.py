import pytest

from bocadillo.compat import check_async
from bocadillo.exceptions import ShouldBeAsync


def test_if_is_async_then_ok():
    async def foo():
        pass

    check_async(foo)


def test_if_async_callable_class_instance_then_ok():
    class Foo:
        async def __call__(self):
            pass

    check_async(Foo)


def test_if_sync_then_fail():
    def foo():
        pass

    with pytest.raises(ShouldBeAsync):
        check_async(foo)


def test_if_is_sync_callable_class_instance_then_fail():
    class Foo:
        def __call__(self):
            pass

    with pytest.raises(ShouldBeAsync):
        check_async(Foo)

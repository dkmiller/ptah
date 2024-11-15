import random
from uuid import uuid4

from ptah.clients.caching import cache_ignore_inputs


def test_caching_return_integers():
    @cache_ignore_inputs
    def _random():
        return random.randint(0, 1000000000)

    assert _random() == _random()


def test_caching_return_strings():
    @cache_ignore_inputs
    def _random():
        return str(uuid4())

    assert _random() == _random()


_caching_called = False


def test_caching_when_return_none():
    @cache_ignore_inputs
    def func():
        global _caching_called
        assert not _caching_called
        _caching_called = True
        return None

    assert func() is None
    assert func() is None

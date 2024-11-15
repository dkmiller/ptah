from time import perf_counter, sleep

import pytest

from ptah.clients import get
from ptah.clients.process import Process


@pytest.mark.parametrize(
    "input,encoded",
    [
        ("", "IiI="),
        ("a b", "ImEgYiI="),
        ("a ! :: b", "ImEgISA6OiBiIg=="),
    ],
)
def test_encode(input, encoded):
    assert get(Process).encode(input) == encoded


@pytest.mark.parametrize(
    "input,decoded",
    [
        (
            "IiI=",
            "",
        ),
        ("ImEgYiI=", "a b"),
        ("ImEgISA6OiBiIg==", "a ! :: b"),
    ],
)
def test_decode(input, decoded):
    assert get(Process).decode(input) == decoded


def test_run():
    process = get(Process)
    start = perf_counter()

    process.run(["sleep", ".5"])

    end = perf_counter()

    assert end - start > 0.4
    assert end - start < 0.6


def test_spawn_then_terminate():
    process = get(Process)
    args = ["sleep", "10"]
    start = perf_counter()

    process.spawn(args)
    sleep(0.5)
    process.terminate(args)

    end = perf_counter()

    assert end - start > 0.4
    assert end - start < 0.6

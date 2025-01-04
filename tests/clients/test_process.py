from time import perf_counter, sleep

import pytest

from ptah.clients import get
from ptah.clients.process import Process
from ptah.models import OperatingSystem


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

    assert end - start > 0.3
    assert end - start < 0.7


# TODO: can we remove this?
@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
def test_spawn_then_terminate():
    process = get(Process)
    args = ["sleep", "10"]
    start = perf_counter()

    process.spawn(args)
    duration = 0.5
    sleep(duration)

    process.terminate(args)

    end = perf_counter()

    # Python is strangely slow to boot inside macOS test runners.
    threshold = 0.3 if get(OperatingSystem) == OperatingSystem.MACOS else 0.1

    # https://stackoverflow.com/a/39623614
    assert duration == pytest.approx(end - start, threshold)

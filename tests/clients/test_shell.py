import random
import sys
from uuid import uuid4

import pytest

from ptah.clients import get
from ptah.clients.shell import Shell


def test_run_success():
    shell = get(Shell)
    value = str(uuid4())
    result = shell.run(["echo", value])
    assert result == value


def test_run_failure():
    shell = get(Shell)
    # https://unix.stackexchange.com/a/418786
    exit_code = random.randint(1, 255)
    with pytest.raises(SystemExit) as exc_info:
        shell.run([sys.executable, "-c", f"import sys; sys.exit({exit_code})"])
    assert exc_info.value.args[0] == exit_code

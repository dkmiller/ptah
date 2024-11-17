from unittest.mock import MagicMock

import pytest

from ptah.clients import Helmfile, get
from ptah.models import OperatingSystem


@pytest.mark.skipif(get(OperatingSystem) == OperatingSystem.LINUX, reason="unsupported")
def test_install():
    helmfile = get(Helmfile)
    helmfile.shell = MagicMock()

    helmfile.install()

    helmfile.shell.run.assert_called_once()

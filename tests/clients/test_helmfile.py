from unittest.mock import MagicMock

from ptah.clients import Helmfile, get


def test_install():
    helmfile = get(Helmfile)
    helmfile.shell = MagicMock()

    helmfile.install()

    helmfile.shell.run.assert_called()
    # .assert_called_once()

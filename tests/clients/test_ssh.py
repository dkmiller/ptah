from unittest.mock import MagicMock, patch

from ptah.clients import Ssh, get


@patch(f"{Ssh.__module__}.os")
def test_ssh_run(os):
    ssh = get(Ssh)
    ssh.shell = MagicMock(return_value="pod-name")

    ssh.run("some-app-name")

    ssh.shell.assert_called_once_with(
        "kubectl",
        "get",
        "pods",
        "--selector=app=some-app-name",
        "-o",
        "jsonpath={.items[0].metadata.name}",
    )

    os.system.assert_called_once_with("kubectl exec -it pod-name -- /bin/bash")

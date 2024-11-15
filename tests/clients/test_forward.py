import random
from pathlib import Path

from ptah.clients import Forward, get


def test_commands(tmp_cwd):
    deployments = Path(__file__).parent / "deployments.json"
    port = random.randint(49152, 65535)
    path = tmp_cwd / "ptah.yml"
    path.write_text(f"""
kind:
  name: some-name
api_server:
  port: {port}        
    """)

    forward = get(Forward)
    forward.shell = lambda *args: deployments.read_text()  # type: ignore

    assert forward.commands() == [
        ["kubectl", "proxy", "--port", str(port)],
        ["kubectl", "port-forward", "deployment/kubernetes-dashboard", "8443:8443"],
    ]

from ptah.clients import Filesystem, get


def test_package_root_contains_clients():
    filesystem = get(Filesystem)
    clients = filesystem.package_root() / "clients"
    assert clients.is_dir()

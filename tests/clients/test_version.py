import re

from ptah.clients import Version, get


def test_version_has_expected_pattern():
    version = get(Version).version()
    assert re.match(r"\d+\.\d+\.\d+", version)

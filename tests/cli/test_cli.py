from click import BaseCommand


def test_cli_click_object():
    from ptah.cli import ptah

    assert isinstance(ptah, BaseCommand)

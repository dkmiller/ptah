from dataclasses import dataclass

from ptah.clients import Yaml, get


def test_yaml_load(tmp_path):
    yaml = get(Yaml)

    @dataclass
    class Inner:
        value: str

    @dataclass
    class Outer:
        inner: Inner
        other_value: float

    path = tmp_path / "foo.yml"

    path.write_text("""
inner:
    value: value_1
other_value: 1.234
""")

    value = yaml.load(path, Outer)
    assert value == Outer(Inner("value_1"), 1.234)


def test_yaml_dumps():
    @dataclass
    class Inner:
        value: str

    @dataclass
    class Outer:
        inner: Inner
        other_value: int

    outer = Outer(Inner(value="value_a"), other_value=42)
    assert (
        get(Yaml).dumps(outer)
        == """inner:
  value: value_a
other_value: 42
"""
    )

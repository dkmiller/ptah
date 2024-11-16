from typing import Any

from jsonpath_ng.ext import parse


class Jsonpath:
    """
    Wrap JSONPath parsing (https://jsonpath.com/).
    """

    def find(self, path: str, datum: Any) -> list:
        parsed = parse(path)
        return [m.value for m in parsed.find(datum)]

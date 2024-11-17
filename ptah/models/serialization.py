from enum import Enum


class Serialization(str, Enum):
    json = "json"
    yaml = "yaml"

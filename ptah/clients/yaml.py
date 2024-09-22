from pathlib import Path
from typing import Type, TypeVar

from omegaconf import OmegaConf

T = TypeVar("T")


class Yaml:
    pass

    def load(self, path: Path, interface: Type[T]) -> T:
        schema = OmegaConf.structured(interface)
        conf = OmegaConf.load(path)
        merged = OmegaConf.merge(schema, conf)
        return OmegaConf.to_object(merged)  # type: ignore

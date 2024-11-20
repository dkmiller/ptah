from dataclasses import dataclass
from pathlib import Path


@dataclass
class DockerImage:
    """
    Local definition of Docker image.
    """

    location: Path
    name: str
    tag: str

    @property
    def uri(self):
        return f"{self.name}:{self.tag}"

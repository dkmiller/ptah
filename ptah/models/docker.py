from dataclasses import dataclass
from pathlib import Path


@dataclass
class DockerCopyStatement:
    source: str
    target: str


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
        # Future: ptah.local/{project}/{name}:tag
        return f"{self.name}:{self.tag}"

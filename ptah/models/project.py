from dataclasses import dataclass, field

from ptah.models.kind import KindCluster


@dataclass
class ApiServer:
    port: int = 8001


@dataclass
class Project:
    """
    Strongly typed Ptah project configuration, captured in a `ptah.yml` file.
    """

    kind: KindCluster
    api_server: ApiServer = field(default_factory=ApiServer)

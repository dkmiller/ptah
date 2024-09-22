from dataclasses import dataclass

from ptah.models.kind import KindCluster


@dataclass
class Project:
    """
    Strongly typed Ptah project configuration, captured in a `ptah.yml` file.
    """

    kind: KindCluster

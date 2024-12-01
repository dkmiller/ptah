from dataclasses import dataclass


@dataclass
class KindCluster:
    """
    [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/#creating-a-cluster)
    cluster configuration.
    """

    name: str | None = None
    """
    Name of Kind cluster. If not specified here, must exist in the Kind config file.
    """
    config: str | None = None
    """
    Path (relative to project root) of
    [Kind config file](https://kind.sigs.k8s.io/docs/user/configuration/).
    """

    def __post_init__(self):
        if not (self.name or self.config):
            raise ValueError("Either name or configuration path must be defined")

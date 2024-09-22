from dataclasses import dataclass


@dataclass
class KindCluster:
    """
    [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/#creating-a-cluster)
    cluster configuration.
    """

    name: str

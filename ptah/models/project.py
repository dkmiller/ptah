from dataclasses import dataclass, field

from ptah.models.kind import KindCluster


@dataclass
class ApiServer:
    port: int = 8001


@dataclass
class Ui:
    service: str = "kubernetes-dashboard"
    user: str = "dashboard-admin"


@dataclass
class Project:
    """
    Strongly typed Ptah project configuration, captured in a `ptah.yml` file.
    """

    kind: KindCluster
    api_server: ApiServer = field(default_factory=ApiServer)
    ui: Ui = field(default_factory=Ui)

    dockerfiles: str = r"(?i)(?P<name>\w+)[/\\][\w\.]*Dockerfile"
    """
    Regular expression used to identify Dockerfiles. If containing a group named `name`, that will
    be used to determine image names.
    """

    manifests: str = r"^(?!helmfile).*\.yaml"
    """
    Regex to look for candidate K8 manifest files.
    """

    build_output: str = ".build"
    """
    Relative (to project root) or absolute path for where the built manifests should go (this is
    where kubectl apply will be called).
    """

    tag_algorithm: str = "md5"
    """
    Dirhash algorithm used to determine Docker image tags.
    """

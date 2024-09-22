from pathlib import Path

from ptah.models import PROJECT_FILE


class Filesystem:
    def package_root(self) -> Path:
        """
        Fully qualified absolute path to the root of the package.
        """
        return Path(__file__).parents[1].resolve().absolute()

    def project_path(self) -> Path:
        for candidate in [Path.cwd()] + list(Path.cwd().parents):
            rv = candidate / PROJECT_FILE
            if rv.is_file():
                return rv
        raise RuntimeError(
            f"Could not find project file {PROJECT_FILE} in current location or parent(s)"
        )

    def pyproject(self) -> Path:
        return self.package_root().parent / "pyproject.toml"

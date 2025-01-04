import shutil
import tempfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from injector import inject

from ptah.clients.panic import Panic, PtahPanic
from ptah.models import PROJECT_FILE


@inject
@dataclass
class Filesystem:
    panic: Panic

    def cache_location(self) -> Path:
        try:
            root = self.project_root()
        except PtahPanic:
            root = Path.cwd()
        return root / ".ptah"

    def delete(self, path: Path) -> None:
        """
        Attempt to recursively delete the provided path, failing silently and safely.
        """
        try:
            shutil.rmtree(path)
        except FileNotFoundError:
            pass

    def download(self, url: str) -> Path:
        """
        Download the provided URL to a temporary location which is returned.
        """
        root = tempfile.mkdtemp()
        filename = urlparse(url).path.split("/")[-1]
        rv = Path(root) / filename
        rv.touch()

        # https://stackoverflow.com/a/7244263
        with urllib.request.urlopen(url) as source, rv.open("rb+") as dest:
            shutil.copyfileobj(source, dest)

        return rv

    def package_root(self) -> Path:
        """
        Fully qualified absolute path to the root of the package.
        """
        return Path(__file__).parents[1].resolve().absolute()

    def project_path(self, location: Optional[Path] = None) -> Path:
        location = location or Path.cwd()
        for candidate in [location] + list(location.parents):
            rv = candidate / PROJECT_FILE
            if rv.is_file():
                return rv.absolute()
        self.panic(f"No file {PROJECT_FILE} in current location or parent(s)")

    def project_root(self, location: Optional[Path] = None) -> Path:
        return self.project_path(location).parent

    def pyproject(self) -> Path:
        return self.package_root().parent / "pyproject.toml"

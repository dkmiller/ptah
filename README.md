# Ptah

[![PyPI - Version](https://img.shields.io/pypi/v/ptah-cli)](https://pypi.org/project/ptah-cli/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Documentation Status](https://readthedocs.org/projects/ptah/badge/?version=latest)](https://ptah.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/github/dkmiller/ptah/graph/badge.svg?token=Ohy0M4ZGhl)](https://codecov.io/github/dkmiller/ptah)

Kubernetes development toolkit, with a focus on rapid iteration and local
hosting.

## Development

To install the Ptah CLI from source, either pip install directly:

```bash
pip install -e ".[dev,doc]"
```

or, if you do not have a compatible version of Python,
[install Miniforge](https://github.com/conda-forge/miniforge) then create the `ptah` environment
[from the file](https://stackoverflow.com/a/59686678) in this repo.

```bash
conda env create -f conda.yml
```

Run automatic formatting / lint fixes via

```bash
ruff check --fix . && ruff format . && isort . && pyright
```

Alternatively, leverage our [pre-commit](https://pre-commit.com/) configuration:

```bash
pre-commit install
```

Try to add documentation for any new feature you build. When possible it should follow
[Diátaxis](https://diataxis.fr/). You may host a local copy of the docs by running

```bash
mkdocs serve
```

The lengthy series of tests in [test_cli_end_to_end.py](./tests/cli/test_cli_end_to_end.py) are
skipped by default. To force them to run, use the command:

```bash
pytest -m e2e
```

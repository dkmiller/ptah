"""
Kubernetes development toolkit, with a focus on rapid iteration and local
hosting.

Under construction: more coming soon!
"""

from ptah.clients import Version, get

__version__ = get(Version).version()

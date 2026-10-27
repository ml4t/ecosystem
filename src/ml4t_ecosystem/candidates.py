"""Build environments and artifact identity for explicit release candidates."""

from __future__ import annotations

import os
import zipfile
from email.parser import Parser
from pathlib import Path

from packaging.version import Version


def candidate_build_environment(version: str | None) -> dict[str, str]:
    """Keep existing builds unchanged unless an explicit candidate is requested."""
    environment = dict(os.environ)
    if version:
        environment["SETUPTOOLS_SCM_PRETEND_VERSION"] = str(Version(version))
    return environment


def wheel_candidate_version(wheel: Path, expected: str | None = None) -> str:
    """Read actual artifact identity and reject a backend ignoring the request."""
    with zipfile.ZipFile(wheel) as archive:
        paths = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
        if len(paths) != 1:
            raise ValueError("candidate wheel has no unique METADATA file")
        metadata = Parser().parsestr(archive.read(paths[0]).decode("utf-8"))
    version = metadata.get("Version")
    if not version:
        raise ValueError("candidate wheel metadata has no Version")
    if expected and Version(version) != Version(expected):
        raise ValueError(f"built candidate version {version} does not match requested {expected}")
    return version

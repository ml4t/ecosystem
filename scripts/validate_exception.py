"""Validate one qualification exception for a reusable workflow caller."""

from __future__ import annotations

import argparse
import subprocess
import tempfile
import zipfile
from datetime import UTC, datetime
from email.parser import Parser
from pathlib import Path

from ml4t_ecosystem.config import load_config
from ml4t_ecosystem.exceptions import validate_exception


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--exception-id", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--package-root", type=Path, required=True)
    return parser.parse_args()


def build_candidate_version(package_root: Path) -> str:
    """Build the candidate wheel and return its declared version."""
    root = package_root.resolve()
    if not (root / "pyproject.toml").is_file():
        raise ValueError(f"package root has no pyproject.toml: {root}")
    with tempfile.TemporaryDirectory(prefix="ml4t-exception-candidate-") as temporary:
        output = Path(temporary)
        subprocess.run(
            [
                "uv",
                "build",
                "--wheel",
                "--out-dir",
                str(output),
                "--no-create-gitignore",
                str(root),
            ],
            check=True,
        )
        wheels = list(output.glob("*.whl"))
        if len(wheels) != 1:
            raise ValueError(f"candidate build produced {len(wheels)} wheels instead of one")
        with zipfile.ZipFile(wheels[0]) as archive:
            metadata_paths = [
                name for name in archive.namelist() if name.endswith(".dist-info/METADATA")
            ]
            if len(metadata_paths) != 1:
                raise ValueError("candidate wheel has no unique METADATA file")
            metadata = Parser().parsestr(archive.read(metadata_paths[0]).decode("utf-8"))
    version = metadata.get("Version")
    if not version:
        raise ValueError("candidate wheel metadata has no Version")
    return version


def main() -> None:
    """Validate the configured exception and print its bounded scope."""
    args = parse_args()
    config = load_config(args.config)
    library = next(
        (
            item
            for item in config.libraries
            if f"{config.owner}/{item.repository}" == args.repository
        ),
        None,
    )
    if library is None:
        raise ValueError(f"repository {args.repository} is not a managed library")
    package_version = build_candidate_version(args.package_root)
    exception = validate_exception(
        config,
        exception_id=args.exception_id,
        library_key=library.key,
        repository=args.repository,
        package_version=package_version,
        on_date=datetime.now(UTC).date(),
    )
    print(
        f"Approved exception {exception.id} covers {library.key} {package_version} through "
        f"{exception.expires_on.isoformat()}: {exception.issue}"
    )


if __name__ == "__main__":
    main()

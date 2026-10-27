"""Validate one qualification exception for a reusable workflow caller."""

from __future__ import annotations

import argparse
import os
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from ml4t_ecosystem.candidates import candidate_build_environment, wheel_candidate_version
from ml4t_ecosystem.config import load_config
from ml4t_ecosystem.exceptions import validate_exception


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--exception-id", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--candidate-version", default=os.environ.get("ML4T_CANDIDATE_VERSION"))
    return parser.parse_args()


def build_candidate_version(package_root: Path, candidate_version: str | None = None) -> str:
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
            env=candidate_build_environment(candidate_version),
        )
        wheels = list(output.glob("*.whl"))
        if len(wheels) != 1:
            raise ValueError(f"candidate build produced {len(wheels)} wheels instead of one")
        return wheel_candidate_version(wheels[0], candidate_version)


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
    package_version = build_candidate_version(args.package_root, args.candidate_version)
    exception = validate_exception(
        config,
        exception_id=args.exception_id,
        library_key=library.key,
        repository=args.repository,
        package_version=package_version,
        on_date=datetime.now(UTC).date(),
    )
    if exception.review_triggers:
        scope = "review triggers " + ", ".join(exception.review_triggers)
    else:
        assert exception.expires_on is not None
        scope = f"expiration {exception.expires_on.isoformat()}"
    print(
        f"Approved exception {exception.id} covers {library.key} {package_version}; "
        f"{scope}: {exception.issue}"
    )


if __name__ == "__main__":
    main()

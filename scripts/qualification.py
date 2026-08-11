#!/usr/bin/env python3
"""Run the shared library qualification commands in the current repository."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def run(command: list[str], *, env: dict[str, str] | None = None) -> None:
    """Run a qualification command and fail immediately on errors."""
    print("+", " ".join(command), flush=True)
    subprocess.run(command, check=True, env=env)


def venv_python(directory: Path) -> Path:
    """Return the platform-specific virtual-environment interpreter."""
    if os.name == "nt":
        return directory / "Scripts/python.exe"
    return directory / "bin/python"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", required=True)
    parser.add_argument("--import-package", required=True)
    parser.add_argument("--prerelease", action="store_true")
    return parser.parse_args()


def main() -> int:
    """Qualify the library in the current working directory."""
    args = parse_args()
    prerelease_args = ["--prerelease", "allow"] if args.prerelease else []
    run(["uv", "python", "install", args.python, *prerelease_args])
    run(["uv", "sync", "--dev", "--python", args.python, *prerelease_args])
    if not args.prerelease:
        run(["uv", "run", "--python", args.python, "ruff", "check", "src", "tests"])
        run(["uv", "run", "--python", args.python, "ruff", "format", "--check", "src", "tests"])
        run(["uv", "run", "--python", args.python, "ty", "check", "src", "tests"])
    run(["uv", "run", "--python", args.python, "pytest", "tests", "-q"])
    run(["uv", "build"])

    wheels = sorted(Path("dist").glob("*.whl"), key=lambda path: path.stat().st_mtime)
    if not wheels:
        raise RuntimeError("uv build did not produce a wheel")
    with tempfile.TemporaryDirectory(prefix="ml4t-qualification-") as temporary:
        environment = Path(temporary)
        run(["uv", "venv", "--python", args.python, str(environment), *prerelease_args])
        interpreter = venv_python(environment)
        run(
            [
                "uv",
                "pip",
                "install",
                "--python",
                str(interpreter),
                str(wheels[-1]),
                *prerelease_args,
            ]
        )
        run(
            [
                str(interpreter),
                "-c",
                f"import {args.import_package}; print({args.import_package}.__name__)",
            ]
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())

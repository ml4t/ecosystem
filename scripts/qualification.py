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


def dependency_prerelease_args(enabled: bool) -> list[str]:
    """Return prerelease selection flags for dependency resolution commands."""
    return ["--prerelease", "allow"] if enabled else []


def python_install_command(version: str, *, preinstalled: bool = False) -> list[str] | None:
    """Build a managed-Python install command unless CI supplied the interpreter."""
    if preinstalled:
        return None
    return ["uv", "python", "install", version]


def venv_command(version: str, directory: Path) -> list[str]:
    """Build a virtual-environment command without dependency-only flags."""
    return ["uv", "venv", "--python", version, str(directory)]


def sync_command(version: str, *, prerelease: bool) -> list[str]:
    """Build the dependency installation command for one qualification lane."""
    command = ["uv", "sync", "--python", version]
    if prerelease:
        return [
            *command,
            "--no-dev",
            "--group",
            "test",
            *dependency_prerelease_args(True),
        ]
    return [*command, "--dev"]


def uv_run_command(version: str, *command: str) -> list[str]:
    """Run from the environment installed by the explicit sync step."""
    return ["uv", "run", "--no-sync", "--python", version, *command]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", required=True)
    parser.add_argument("--import-package", required=True)
    parser.add_argument("--prerelease", action="store_true")
    parser.add_argument("--preinstalled-python", action="store_true")
    return parser.parse_args()


def main() -> int:
    """Qualify the library in the current working directory."""
    args = parse_args()
    prerelease_args = dependency_prerelease_args(args.prerelease)
    install = python_install_command(args.python, preinstalled=args.preinstalled_python)
    if install is not None:
        run(install)
    run(sync_command(args.python, prerelease=args.prerelease))
    if not args.prerelease:
        run(uv_run_command(args.python, "ruff", "check", "src", "tests"))
        run(uv_run_command(args.python, "ruff", "format", "--check", "src", "tests"))
        run(uv_run_command(args.python, "ty", "check", "src", "tests"))
    run(uv_run_command(args.python, "pytest", "tests", "-q"))
    run(["uv", "build"])

    wheels = sorted(Path("dist").glob("*.whl"), key=lambda path: path.stat().st_mtime)
    if not wheels:
        raise RuntimeError("uv build did not produce a wheel")
    with tempfile.TemporaryDirectory(prefix="ml4t-qualification-") as temporary:
        environment = Path(temporary)
        run(venv_command(args.python, environment))
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

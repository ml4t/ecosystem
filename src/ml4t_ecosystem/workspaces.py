"""Local release-checkout and development-sidecar compliance checks."""

from __future__ import annotations

import subprocess
from collections.abc import Sequence
from pathlib import Path

from ml4t_ecosystem.agent_orientation import orientation_issues
from ml4t_ecosystem.models import CheckResult, EcosystemConfig, Library, WorkspaceReport

CLAUDE_IMPORT = "@AGENTS.md\n"
SIDECAR_DIRECTORIES = (
    "issues",
    ".workspace/work",
    ".workspace/transitions",
    ".workspace/memory",
)
SIDECAR_FILES = (
    "AGENTS.md",
    "CLAUDE.md",
    ".workspace/memory/MEMORY_INDEX.md",
)


def _result(code: str, passed: bool, message: str) -> CheckResult:
    return CheckResult(code=code, status="pass" if passed else "fail", message=message)


def _git(path: Path, arguments: Sequence[str]) -> tuple[int, str]:
    completed = subprocess.run(
        ["git", "-C", str(path), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )
    return completed.returncode, completed.stdout.strip()


def _has_exact_claude_import(path: Path) -> bool:
    try:
        return path.read_text(encoding="utf-8") == CLAUDE_IMPORT
    except OSError:
        return False


def audit_workspace(root: Path, library: Library) -> WorkspaceReport:
    """Audit one local release checkout and its private development sidecar."""
    release = root / library.local_checkout
    report = WorkspaceReport(library=library, root=str(root))

    report.checks.append(
        _result(
            "release.exists",
            release.is_dir(),
            f"Release checkout {library.local_checkout} exists",
        )
    )
    report.checks.append(
        _result(
            "release.agent-orientation",
            not (
                agent_issues := orientation_issues(
                    _read_text(release / "AGENTS.md"), library.import_package
                )
            ),
            (
                "Release checkout AGENTS.md provides public orientation"
                if not agent_issues
                else "Release checkout AGENTS.md is incomplete: " + "; ".join(agent_issues)
            ),
        )
    )

    if library.development_workspace is None:
        report.checks.append(
            _result(
                "sidecar.not-required",
                True,
                "Library inventory does not require a development sidecar",
            )
        )
        return report

    sidecar = root / library.development_workspace

    sidecar_exists = sidecar.is_dir()
    report.checks.append(
        _result(
            "sidecar.exists",
            sidecar_exists,
            f"Development sidecar {library.development_workspace} exists",
        )
    )
    for relative in SIDECAR_FILES:
        path = sidecar / relative
        passed = _has_exact_claude_import(path) if relative == "CLAUDE.md" else path.is_file()
        code_path = relative.replace("/", ".").lstrip(".")
        report.checks.append(
            _result(
                f"sidecar.file.{code_path}",
                passed,
                (
                    "Development sidecar CLAUDE.md contains only @AGENTS.md"
                    if relative == "CLAUDE.md"
                    else f"Development sidecar file {relative} exists"
                ),
            )
        )
    for relative in SIDECAR_DIRECTORIES:
        code_path = relative.replace("/", ".").lstrip(".")
        report.checks.append(
            _result(
                f"sidecar.directory.{code_path}",
                (sidecar / relative).is_dir(),
                f"Development sidecar directory {relative} exists",
            )
        )

    repository_code, repository_value = _git(sidecar, ("rev-parse", "--is-inside-work-tree"))
    is_repository = sidecar_exists and repository_code == 0 and repository_value == "true"
    report.checks.append(
        _result("sidecar.git-repository", is_repository, "Development sidecar is a Git repository")
    )

    origin_code, origin_value = _git(sidecar, ("remote", "get-url", "origin"))
    report.checks.append(
        _result(
            "sidecar.origin",
            is_repository and origin_code == 0 and bool(origin_value),
            "Development sidecar has an origin remote",
        )
    )

    status_code, status_value = _git(sidecar, ("status", "--porcelain"))
    report.checks.append(
        _result(
            "sidecar.clean",
            is_repository and status_code == 0 and not status_value,
            "Development sidecar has no uncommitted or untracked work",
        )
    )

    sync_code, sync_value = _git(
        sidecar, ("rev-list", "--left-right", "--count", "@{upstream}...HEAD")
    )
    report.checks.append(
        _result(
            "sidecar.synchronized",
            is_repository and sync_code == 0 and sync_value.split() == ["0", "0"],
            "Development sidecar matches its configured upstream",
        )
    )
    return report


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def audit_workspaces(root: Path, config: EcosystemConfig) -> list[WorkspaceReport]:
    """Audit every configured local release checkout and sidecar."""
    return [audit_workspace(root, library) for library in config.libraries]

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from ml4t_ecosystem.audit import REQUIRED_FILES, audit_all, audit_library
from ml4t_ecosystem.clients import EvidenceError
from ml4t_ecosystem.config import load_config


class FakePyPI:
    def __init__(self, *, stable: bool = True, compatible: bool = True, version: str | None = None):
        self.stable = stable
        self.compatible = compatible
        self.version = version

    def package(self, distribution: str) -> dict[str, Any]:
        return {
            "version": self.version or ("0.1.0" if self.stable else "0.1.0b1"),
            "classifiers": [
                "Development Status :: 5 - Production/Stable"
                if self.stable
                else "Development Status :: 4 - Beta"
            ],
            "requires_python": ">=3.12" if self.compatible else ">=3.12,<3.15",
        }


class FakeGitHub:
    def __init__(self, *, complete: bool = True):
        self.complete = complete

    def repository(self, owner: str, repository: str) -> dict[str, Any]:
        return {"default_branch": "main"}

    def branch_commit(self, owner: str, repository: str, branch: str) -> str:
        return "a" * 40

    def content(self, owner: str, repository: str, path: str) -> str | None:
        if not self.complete and path == "SECURITY.md":
            return None
        if path == ".github/workflows/ecosystem.yml":
            exception = {
                "data": "python-315-polars",
                "engineer": "python-315-polars",
                "diagnostic": "python-315-scipy",
            }.get(repository)
            return (
                "concurrency:\n"
                "  cancel-in-progress: true\n"
                "uses: ml4t/ecosystem/.github/workflows/qualify-library.yml@"
                f"{'a' * 40}\n" + (f"prerelease-exception: {exception}\n" if exception else "")
            )
        if path == ".github/workflows/release.yml":
            return f"uses: ml4t/ecosystem/.github/workflows/qualify-library.yml@{'a' * 40}\n"
        if path == ".github/workflows/docs.yml":
            return "run: uv run mkdocs build --strict\n"
        if path == "mkdocs.yml":
            return "site_url: https://www.ml4trading.io/docs/data/\n"
        if path == "pyproject.toml":
            return "[dependency-groups]\ntest = []\n"
        return "present\n" if path in REQUIRED_FILES else None

    def labels(self, owner: str, repository: str) -> set[str]:
        from ml4t_ecosystem.audit import REQUIRED_LABELS

        return set(REQUIRED_LABELS) if self.complete else set()

    def private_vulnerability_reporting(self, owner: str, repository: str) -> bool | None:
        return True


class FailingPyPI(FakePyPI):
    def package(self, distribution: str) -> dict[str, Any]:
        raise EvidenceError("PyPI unavailable")


class FailingGitHub(FakeGitHub):
    def repository(self, owner: str, repository: str) -> dict[str, Any]:
        raise EvidenceError("GitHub unavailable")


class HiddenSecurityGitHub(FakeGitHub):
    def private_vulnerability_reporting(self, owner: str, repository: str) -> bool | None:
        return None


def config():
    return load_config(Path("config/libraries.toml"))


def test_audit_library_passes_complete_evidence() -> None:
    ecosystem = config()
    report = audit_library(
        ecosystem,
        ecosystem.library("data"),
        FakeGitHub(),  # type: ignore[arg-type]
        FakePyPI(),  # type: ignore[arg-type]
        observed_at=datetime(2026, 8, 11, tzinfo=UTC),
    )

    assert report.passed
    assert report.published_version == "0.1.0"
    assert report.source_commit == "a" * 40


def test_audit_library_fails_beta_upper_bound_and_missing_repository_files() -> None:
    ecosystem = config()
    report = audit_library(
        ecosystem,
        ecosystem.library("backtest"),
        FakeGitHub(complete=False),  # type: ignore[arg-type]
        FakePyPI(stable=False, compatible=False),  # type: ignore[arg-type]
    )

    failed = {check.code for check in report.checks if check.status == "fail"}
    assert "pypi.stable-version" in failed
    assert "pypi.stable-classifier" in failed
    assert "pypi.prerelease-install" in failed
    assert "repository.file.SECURITY.md" in failed
    assert "github.shared-labels" in failed


def test_audit_accepts_active_version_scoped_prerelease_exception() -> None:
    ecosystem = config()
    report = audit_library(
        ecosystem,
        ecosystem.library("data"),
        FakeGitHub(),  # type: ignore[arg-type]
        FakePyPI(compatible=False, version="0.1.2"),  # type: ignore[arg-type]
        observed_at=datetime(2026, 8, 11, tzinfo=UTC),
    )

    check = next(check for check in report.checks if check.code == "pypi.prerelease-install")
    assert check.status == "pass"
    assert "python-315-polars" in check.message


def test_audit_rejects_expired_prerelease_exception() -> None:
    ecosystem = config()
    report = audit_library(
        ecosystem,
        ecosystem.library("data"),
        FakeGitHub(),  # type: ignore[arg-type]
        FakePyPI(compatible=False, version="0.1.2"),  # type: ignore[arg-type]
        observed_at=datetime(2026, 10, 1, tzinfo=UTC),
    )

    check = next(check for check in report.checks if check.code == "pypi.prerelease-install")
    assert check.status == "fail"
    assert "expired" in check.message


def test_audit_rejects_missing_workflow_exception_declaration() -> None:
    class MissingExceptionGitHub(FakeGitHub):
        def content(self, owner: str, repository: str, path: str) -> str | None:
            content = super().content(owner, repository, path)
            if path == ".github/workflows/ecosystem.yml" and content is not None:
                return content.replace("prerelease-exception: python-315-polars\n", "")
            return content

    ecosystem = config()
    report = audit_library(
        ecosystem,
        ecosystem.library("data"),
        MissingExceptionGitHub(),
        FakePyPI(compatible=False, version="0.1.2"),
        observed_at=datetime(2026, 8, 11, tzinfo=UTC),
    )

    check = next(check for check in report.checks if check.code == "workflow.prerelease-exception")
    assert check.status == "fail"


def test_audit_preserves_source_failures_as_unknown() -> None:
    ecosystem = config()
    report = audit_library(
        ecosystem,
        ecosystem.library("data"),
        FailingGitHub(),  # type: ignore[arg-type]
        FailingPyPI(),  # type: ignore[arg-type]
    )

    assert {check.status for check in report.checks} == {"unknown"}
    assert not report.passed


def test_audit_all_uses_one_observation_time() -> None:
    ecosystem = config()
    reports = audit_all(
        ecosystem,
        FakeGitHub(),  # type: ignore[arg-type]
        FakePyPI(),  # type: ignore[arg-type]
        observed_at=datetime(2026, 8, 11, tzinfo=UTC),
    )

    assert len(reports) == 7
    assert len({report.observed_at for report in reports}) == 1


def test_audit_marks_hidden_security_state_unknown() -> None:
    ecosystem = config()
    report = audit_library(
        ecosystem,
        ecosystem.library("data"),
        HiddenSecurityGitHub(),
        FakePyPI(),
    )

    security = next(check for check in report.checks if check.code == "security.private-reporting")
    assert security.status == "unknown"


def test_audit_rejects_mutable_workflow_references_and_uncancelled_runs() -> None:
    class MutableWorkflowGitHub(FakeGitHub):
        def content(self, owner: str, repository: str, path: str) -> str | None:
            if path in {".github/workflows/ecosystem.yml", ".github/workflows/release.yml"}:
                return "uses: ml4t/ecosystem/.github/workflows/qualify-library.yml@main\n"
            return super().content(owner, repository, path)

    ecosystem = config()
    report = audit_library(
        ecosystem,
        ecosystem.library("data"),
        MutableWorkflowGitHub(),
        FakePyPI(),
    )

    failed = {check.code for check in report.checks if check.status == "fail"}
    assert failed == {
        "release.central-qualification",
        "workflow.central-qualification",
        "workflow.prerelease-exception",
        "workflow.superseded-cancellation",
    }


def test_audit_requires_an_isolated_test_dependency_group() -> None:
    class MissingTestGroupGitHub(FakeGitHub):
        def content(self, owner: str, repository: str, path: str) -> str | None:
            if path == "pyproject.toml":
                return "[dependency-groups]\ndev = []\n"
            return super().content(owner, repository, path)

    ecosystem = config()
    report = audit_library(
        ecosystem,
        ecosystem.library("data"),
        MissingTestGroupGitHub(),
        FakePyPI(),
    )

    check = next(
        check for check in report.checks if check.code == "repository.test-dependency-group"
    )
    assert check.status == "fail"


@pytest.mark.parametrize("version", ["invalid", "0.1.0b1"])
def test_invalid_or_prerelease_pypi_version_fails(version: str) -> None:
    class VersionPyPI(FakePyPI):
        def package(self, distribution: str) -> dict[str, Any]:
            result = super().package(distribution)
            result["version"] = version
            return result

    ecosystem = config()
    report = audit_library(
        ecosystem,
        ecosystem.library("data"),
        FakeGitHub(),
        VersionPyPI(),
    )

    check = next(check for check in report.checks if check.code == "pypi.stable-version")
    assert check.status == "fail"

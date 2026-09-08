from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from ml4t_ecosystem.audit import REQUIRED_FILES, audit_all, audit_library
from ml4t_ecosystem.clients import EvidenceError
from ml4t_ecosystem.config import load_config

SHA = "a" * 40
DESCRIPTION = "Market data acquisition, validation, storage, and access for quantitative trading"
KEYWORDS = [
    "finance",
    "quantitative-finance",
    "algorithmic-trading",
    "market-data",
    "storage",
]


def config():
    return load_config(Path("config/libraries.toml"))


def project_urls(repository: str) -> dict[str, str]:
    base = f"https://github.com/ml4t/{repository}"
    return {
        "Homepage": "https://www.ml4trading.io/",
        "Documentation": f"https://www.ml4trading.io/docs/{repository}/",
        "Repository": base,
        "Issues": f"{base}/issues",
        "Changelog": f"{base}/releases",
    }


class FakePyPI:
    def __init__(
        self,
        *,
        stable: bool = True,
        compatible: bool = True,
        version: str | None = None,
        complete_artifacts: bool = True,
    ):
        self.stable = stable
        self.compatible = compatible
        self.version = version
        self.complete_artifacts = complete_artifacts

    def package(self, distribution: str) -> dict[str, Any]:
        version = self.version or ("0.1.0" if self.stable else "0.1.0b1")
        repository = distribution.removeprefix("ml4t-")
        ecosystem = config()
        classifiers = list(ecosystem.policy.required_classifiers)
        if not self.stable:
            classifiers.remove("Development Status :: 5 - Production/Stable")
            classifiers.append("Development Status :: 4 - Beta")
        artifacts = [
            {
                "filename": f"{distribution.replace('-', '_')}-{version}-py3-none-any.whl",
                "packagetype": "bdist_wheel",
                "digests": {"sha256": "wheel-digest"},
            },
            {
                "filename": f"{distribution.replace('-', '_')}-{version}.tar.gz",
                "packagetype": "sdist",
                "digests": {"sha256": "sdist-digest"},
            },
        ]
        if not self.complete_artifacts:
            artifacts.pop()
        return {
            "version": version,
            "summary": DESCRIPTION,
            "author": "Stefan Jansen",
            "author_email": "stefan@applied-ai.com",
            "maintainer": "Stefan Jansen",
            "maintainer_email": "pm@ml4trading.io",
            "keywords": ",".join(KEYWORDS),
            "classifiers": classifiers,
            "project_urls": project_urls(repository),
            "requires_python": ">=3.12" if self.compatible else ">=3.12,<3.15",
            "_release_files": artifacts,
        }


class FakeGitHub:
    def __init__(self, *, complete: bool = True):
        self.complete = complete

    def repository(self, owner: str, repository: str) -> dict[str, Any]:
        return {
            "default_branch": "main",
            "visibility": "public",
            "description": DESCRIPTION,
            "homepage": f"https://www.ml4trading.io/docs/{repository}/",
            "topics": [
                "ml4t",
                "python",
                "quantitative-finance",
                "algorithmic-trading",
                repository,
                "trading-library",
            ],
        }

    def branch_commit(self, owner: str, repository: str, branch: str) -> str:
        return SHA

    def tag_commit(self, owner: str, repository: str, tag: str) -> str | None:
        return SHA

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
                "permissions:\n  contents: read\n"
                "concurrency:\n  cancel-in-progress: true\n"
                "uses: ml4t/ecosystem/.github/workflows/qualify-library.yml@"
                f"{SHA}\n" + (f"prerelease-exception: {exception}\n" if exception else "")
            )
        if path == ".github/workflows/release.yml":
            return (
                "permissions:\n  contents: read\n  id-token: write\n"
                f"uses: ml4t/ecosystem/.github/workflows/qualify-library.yml@{SHA}\n"
                f"- uses: pypa/gh-action-pypi-publish@{SHA}\n"
                "run: sha256sum dist/* > artifact-manifest.txt\n"
                "env:\n  CANDIDATE_COMMIT: ${{ github.sha }}\n"
            )
        if path == ".github/workflows/docs.yml":
            return (
                "permissions:\n  contents: read\n"
                f"- uses: actions/checkout@{SHA}\n"
                "run: uv run mkdocs build --strict\n"
            )
        if path == ".github/workflows/ci.yml":
            return (
                "on:\n  pull_request:\n  push:\n    branches: [main]\n"
                "permissions:\n  contents: read\n"
                f"- uses: actions/checkout@{SHA}\n"
                "run: uv run ruff check .\n"
                "run: uv run ruff format --check .\n"
                "run: uv run ty check\n"
                "run: uv run pytest\n"
                "run: uv build\n"
                "run: uv run mkdocs build --strict\n"
            )
        if path == "mkdocs.yml":
            return f"site_url: https://www.ml4trading.io/docs/{repository}/\n"
        if path == "pyproject.toml":
            urls = project_urls(repository)
            classifiers = "\n".join(
                f'    "{classifier}",' for classifier in config().policy.required_classifiers
            )
            keywords = ", ".join(f'"{keyword}"' for keyword in KEYWORDS)
            return (
                "[project]\n"
                f'name = "ml4t-{repository}"\n'
                f'description = "{DESCRIPTION}"\n'
                'requires-python = ">=3.12"\n'
                'authors = [{ name = "Stefan Jansen", email = "stefan@applied-ai.com" }]\n'
                'maintainers = [{ name = "Stefan Jansen", email = "pm@ml4trading.io" }]\n'
                f"keywords = [{keywords}]\n"
                f"classifiers = [\n{classifiers}\n]\n"
                "[project.urls]\n"
                + "\n".join(f'{label} = "{url}"' for label, url in urls.items())
                + "\n[dependency-groups]\ntest = []\n"
            )
        if path == "README.md":
            urls = project_urls(repository)
            return (
                f"# ml4t-{repository}\n\n{DESCRIPTION}.\n\n"
                "## Requirements and support\n\nPython 3.12, 3.13, and 3.14.\n\n"
                f"Install `ml4t-{repository}`.\n\n"
                f"```python\nimport ml4t.{repository}\n```\n\n"
                f"[Documentation]({urls['Documentation']})\n"
                f"[Issues]({urls['Issues']})\n"
                f"[Releases]({urls['Changelog']})\n"
                "[License](LICENSE)\n\nDevelopment: ruff, ty, pytest.\n"
            )
        if path == "CLAUDE.md":
            return "@AGENTS.md\n"
        return "present\n" if path in REQUIRED_FILES else None

    def labels(self, owner: str, repository: str) -> set[str]:
        from ml4t_ecosystem.audit import REQUIRED_LABELS

        return set(REQUIRED_LABELS) if self.complete else set()

    def private_vulnerability_reporting(self, owner: str, repository: str) -> bool | None:
        return True


class FakeDocumentation:
    def __init__(self, *, version: str = "0.1.0", commit: str = SHA):
        self.version = version
        self.commit = commit

    def page(self, url: str) -> str:
        library = url.rstrip("/").rsplit("/", 1)[-1]
        return (
            "<html><head>"
            f'<meta name="ml4t-library" content="{library}">'
            f'<meta name="ml4t-version" content="{self.version}">'
            f'<meta name="ml4t-commit" content="{self.commit}">'
            "</head></html>"
        )


class FailingPyPI(FakePyPI):
    def package(self, distribution: str) -> dict[str, Any]:
        raise EvidenceError("PyPI unavailable")


class FailingGitHub(FakeGitHub):
    def repository(self, owner: str, repository: str) -> dict[str, Any]:
        raise EvidenceError("GitHub unavailable")


class FailingDocumentation(FakeDocumentation):
    def page(self, url: str) -> str:
        raise EvidenceError("Documentation unavailable")


class HiddenSecurityGitHub(FakeGitHub):
    def private_vulnerability_reporting(self, owner: str, repository: str) -> bool | None:
        return None


def test_audit_library_passes_complete_evidence() -> None:
    ecosystem = config()
    report = audit_library(
        ecosystem,
        ecosystem.library("data"),
        FakeGitHub(),
        FakePyPI(),
        FakeDocumentation(),
        observed_at=datetime(2026, 8, 11, tzinfo=UTC),
    )

    assert report.passed
    assert report.published_version == "0.1.0"
    assert report.source_commit == SHA
    assert report.release_commit == SHA
    assert report.documentation_commit == SHA
    assert all(check.evidence for check in report.checks)


def test_audit_library_fails_beta_upper_bound_and_missing_repository_files() -> None:
    ecosystem = config()
    report = audit_library(
        ecosystem,
        ecosystem.library("backtest"),
        FakeGitHub(complete=False),
        FakePyPI(stable=False, compatible=False),
        FakeDocumentation(version="0.1.0b1"),
    )

    failed = {check.code for check in report.checks if check.status == "fail"}
    assert "pypi.stable-version" in failed
    assert "pypi.classifiers" in failed
    assert "pypi.prerelease-install" in failed
    assert "repository.file.SECURITY.md" in failed
    assert "github.shared-labels" in failed


def test_audit_accepts_active_version_scoped_prerelease_exception() -> None:
    ecosystem = config()
    report = audit_library(
        ecosystem,
        ecosystem.library("data"),
        FakeGitHub(),
        FakePyPI(compatible=False, version="0.1.2"),
        FakeDocumentation(version="0.1.2"),
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
        FakeGitHub(),
        FakePyPI(compatible=False, version="0.1.2"),
        FakeDocumentation(version="0.1.2"),
        observed_at=datetime(2026, 10, 1, tzinfo=UTC),
    )

    check = next(check for check in report.checks if check.code == "pypi.prerelease-install")
    assert check.status == "fail"
    assert "expired" in check.message


def test_audit_rejects_metadata_readme_and_instruction_drift() -> None:
    class DriftGitHub(FakeGitHub):
        def repository(self, owner: str, repository: str) -> dict[str, Any]:
            result = super().repository(owner, repository)
            result.update(description="State-of-the-art package", homepage="https://example.com")
            result["topics"] = []
            return result

        def content(self, owner: str, repository: str, path: str) -> str | None:
            if path == "pyproject.toml":
                return (
                    "[project]\n"
                    'name = "ml4t-data"\n'
                    'description = "State-of-the-art package"\n'
                    'authors = [{ name = "Template Team", email = "info@example.invalid" }]\n'
                )
            if path == "README.md":
                return "# Placeholder\n"
            if path == "CLAUDE.md":
                return "Duplicated instructions\n"
            return super().content(owner, repository, path)

    ecosystem = config()
    report = audit_library(
        ecosystem,
        ecosystem.library("data"),
        DriftGitHub(),
        FakePyPI(),
        FakeDocumentation(),
    )
    failed = {check.code for check in report.checks if check.status == "fail"}

    assert {
        "github.description",
        "github.homepage",
        "github.topics",
        "repository.public-identity",
        "source.identity",
        "source.description",
        "readme.installation",
        "readme.quick-start",
        "repository.claude-import",
    }.issubset(failed)


def test_repository_collection_is_atomic_on_source_failure() -> None:
    class MidCollectionFailure(FakeGitHub):
        def content(self, owner: str, repository: str, path: str) -> str | None:
            if path == "README.md":
                raise EvidenceError("content unavailable")
            return super().content(owner, repository, path)

    ecosystem = config()
    report = audit_library(
        ecosystem,
        ecosystem.library("data"),
        MidCollectionFailure(),
        FakePyPI(),
        FakeDocumentation(),
    )

    github_checks = [check for check in report.checks if check.code.startswith("github.")]
    repository_checks = [check for check in report.checks if check.code.startswith("repository.")]
    assert [check.code for check in github_checks] == ["github.evidence"]
    assert repository_checks == []
    assert not report.passed


def test_missing_sources_remain_unknown_and_cannot_pass() -> None:
    ecosystem = config()
    report = audit_library(
        ecosystem,
        ecosystem.library("data"),
        FailingGitHub(),
        FailingPyPI(),
        FailingDocumentation(),
    )

    assert {check.status for check in report.checks} == {"unknown"}
    assert {check.code for check in report.checks} == {
        "github.evidence",
        "pypi.evidence",
        "docs.evidence",
    }
    assert not report.passed


def test_audit_all_uses_one_observation_time() -> None:
    ecosystem = config()
    reports = audit_all(
        ecosystem,
        FakeGitHub(),
        FakePyPI(),
        FakeDocumentation(),
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
        FakeDocumentation(),
    )

    security = next(check for check in report.checks if check.code == "security.private-reporting")
    assert security.status == "unknown"
    assert not report.passed


def test_audit_rejects_mutable_workflow_references_and_uncancelled_runs() -> None:
    class MutableWorkflowGitHub(FakeGitHub):
        def content(self, owner: str, repository: str, path: str) -> str | None:
            if path in {".github/workflows/ecosystem.yml", ".github/workflows/release.yml"}:
                return (
                    "permissions:\n  contents: read\n"
                    "uses: ml4t/ecosystem/.github/workflows/qualify-library.yml@main\n"
                )
            return super().content(owner, repository, path)

    ecosystem = config()
    report = audit_library(
        ecosystem,
        ecosystem.library("data"),
        MutableWorkflowGitHub(),
        FakePyPI(),
        FakeDocumentation(),
    )

    failed = {check.code for check in report.checks if check.status == "fail"}
    assert {
        "release.central-qualification",
        "workflow.central-qualification",
        "workflow.immutable-actions",
        "workflow.prerelease-exception",
        "workflow.superseded-cancellation",
    }.issubset(failed)


def test_audit_requires_isolated_tests_and_artifact_identity() -> None:
    class MissingTestGroupGitHub(FakeGitHub):
        def content(self, owner: str, repository: str, path: str) -> str | None:
            content = super().content(owner, repository, path)
            if path == "pyproject.toml" and content is not None:
                return content.replace("[dependency-groups]\ntest = []\n", "")
            return content

    ecosystem = config()
    report = audit_library(
        ecosystem,
        ecosystem.library("data"),
        MissingTestGroupGitHub(),
        FakePyPI(complete_artifacts=False),
        FakeDocumentation(),
    )

    failed = {check.code for check in report.checks if check.status == "fail"}
    assert "repository.test-dependency-group" in failed
    assert "pypi.artifact-digests" in failed


def test_audit_rejects_stale_documentation_identity() -> None:
    ecosystem = config()
    report = audit_library(
        ecosystem,
        ecosystem.library("data"),
        FakeGitHub(),
        FakePyPI(),
        FakeDocumentation(version="0.0.9", commit="b" * 40),
    )

    failed = {check.code for check in report.checks if check.status == "fail"}
    assert {"docs.deployed-version", "docs.deployed-commit"}.issubset(failed)


@pytest.mark.parametrize("version", ["invalid", "0.1.0b1"])
def test_invalid_or_prerelease_pypi_version_fails(version: str) -> None:
    ecosystem = config()
    report = audit_library(
        ecosystem,
        ecosystem.library("data"),
        FakeGitHub(),
        FakePyPI(version=version),
        FakeDocumentation(version=version),
    )

    check = next(check for check in report.checks if check.code == "pypi.stable-version")
    assert check.status == "fail"

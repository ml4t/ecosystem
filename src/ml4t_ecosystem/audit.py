"""Evidence-backed release metadata and repository compliance checks."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any

from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import InvalidVersion, Version

from ml4t_ecosystem.clients import AuditGitHub, EvidenceError, PyPIEvidence
from ml4t_ecosystem.models import CheckResult, EcosystemConfig, Library, LibraryReport

REQUIRED_FILES = (
    "LICENSE",
    "README.md",
    "SECURITY.md",
    ".github/ISSUE_TEMPLATE/bug.yml",
    ".github/ISSUE_TEMPLATE/feature.yml",
    ".github/ISSUE_TEMPLATE/documentation.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/workflows/ecosystem.yml",
    "mkdocs.yml",
)
REQUIRED_LABELS = {
    "type: bug",
    "type: feature",
    "type: documentation",
    "priority: critical",
    "priority: high",
    "priority: normal",
    "priority: low",
    "status: needs-triage",
    "status: pending-review",
    "status: accepted",
    "status: blocked",
    "compatibility: breaking",
    "compatibility: affected",
    "compatibility: none",
    "ecosystem",
}
CENTRAL_QUALIFICATION = re.compile(
    r"^\s*uses:\s*ml4t/ecosystem/\.github/workflows/qualify-library\.yml@[0-9a-f]{40}"
    r"(?:\s*#.*)?$",
    re.MULTILINE,
)


def _result(code: str, passed: bool, message: str, evidence: str | None = None) -> CheckResult:
    return CheckResult(
        code=code, status="pass" if passed else "fail", message=message, evidence=evidence
    )


def _unknown(code: str, message: str, evidence: str | None = None) -> CheckResult:
    return CheckResult(code=code, status="unknown", message=message, evidence=evidence)


def _uses_pinned_central_qualification(workflow: str) -> bool:
    return CENTRAL_QUALIFICATION.search(workflow) is not None


def _allows_prerelease(requires_python: str | None, prerelease: str) -> bool:
    if not requires_python:
        return False
    try:
        specifier = SpecifierSet(requires_python)
        candidate = Version(f"{prerelease}.0b1")
    except (InvalidSpecifier, InvalidVersion):
        return False
    return specifier.contains(candidate, prereleases=True)


def _check_pypi(
    report: LibraryReport,
    info: dict[str, Any],
    prerelease_python: str,
) -> None:
    version_text = info.get("version")
    report.published_version = version_text if isinstance(version_text, str) else None
    try:
        stable_version = isinstance(version_text, str) and not Version(version_text).is_prerelease
    except InvalidVersion:
        stable_version = False
    report.checks.append(
        _result("pypi.stable-version", stable_version, f"Published version is {version_text!r}")
    )

    classifiers = info.get("classifiers")
    classifier_values = classifiers if isinstance(classifiers, list) else []
    stable_classifier = "Development Status :: 5 - Production/Stable" in classifier_values
    report.checks.append(
        _result(
            "pypi.stable-classifier",
            stable_classifier,
            (
                "Published metadata identifies the package as Production/Stable"
                if stable_classifier
                else "Published metadata does not identify the package as Production/Stable"
            ),
        )
    )

    requires_python = info.get("requires_python")
    requires_text = requires_python if isinstance(requires_python, str) else None
    prerelease_allowed = _allows_prerelease(requires_text, prerelease_python)
    report.checks.append(
        _result(
            "pypi.prerelease-install",
            prerelease_allowed,
            (
                f"Requires-Python {requires_text!r} allows Python {prerelease_python} beta"
                if prerelease_allowed
                else f"Requires-Python {requires_text!r} blocks Python {prerelease_python} beta"
            ),
        )
    )


def _check_repository(
    report: LibraryReport,
    owner: str,
    library: Library,
    github: AuditGitHub,
) -> None:
    metadata = github.repository(owner, library.repository)
    default_branch = metadata.get("default_branch")
    if isinstance(default_branch, str):
        report.source_commit = github.branch_commit(owner, library.repository, default_branch)
    report.checks.append(
        _result(
            "github.default-branch",
            default_branch == "main",
            f"Default branch is {default_branch!r}",
        )
    )

    contents: dict[str, str | None] = {}
    for path in REQUIRED_FILES:
        contents[path] = github.content(owner, library.repository, path)
        report.checks.append(
            _result(
                f"repository.file.{path}",
                contents[path] is not None,
                (
                    f"Required file {path} exists"
                    if contents[path] is not None
                    else f"Required file {path} is missing"
                ),
            )
        )

    ecosystem_workflow = contents[".github/workflows/ecosystem.yml"] or ""
    report.checks.append(
        _result(
            "workflow.central-qualification",
            _uses_pinned_central_qualification(ecosystem_workflow),
            "Repository calls an immutable central qualification workflow revision",
        )
    )
    cancels_superseded = (
        "concurrency:" in ecosystem_workflow and "cancel-in-progress: true" in ecosystem_workflow
    )
    report.checks.append(
        _result(
            "workflow.superseded-cancellation",
            cancels_superseded,
            "Repository cancels superseded qualification runs",
        )
    )

    mkdocs = contents["mkdocs.yml"] or ""
    canonical_url = library.docs_url.rstrip("/") in mkdocs
    report.checks.append(
        _result(
            "docs.canonical-url",
            canonical_url,
            (
                f"MkDocs declares canonical route {library.docs_url}"
                if canonical_url
                else f"MkDocs does not declare canonical route {library.docs_url}"
            ),
        )
    )

    docs_workflow = github.content(owner, library.repository, ".github/workflows/docs.yml")
    release_workflow = github.content(owner, library.repository, ".github/workflows/release.yml")
    strict_docs = "mkdocs build --strict" in (docs_workflow or "") or "mkdocs build --strict" in (
        release_workflow or ""
    )
    report.checks.append(
        _result("docs.strict-build", strict_docs, "CI or release runs MkDocs in strict mode")
    )
    release_qualified = _uses_pinned_central_qualification(release_workflow or "")
    report.checks.append(
        _result(
            "release.central-qualification",
            release_qualified,
            "Release workflow depends on an immutable central qualification revision",
        )
    )

    labels = github.labels(owner, library.repository)
    missing_labels = sorted(REQUIRED_LABELS - labels)
    report.checks.append(
        _result(
            "github.shared-labels",
            not missing_labels,
            "Shared labels are present"
            if not missing_labels
            else f"Missing labels: {missing_labels}",
        )
    )

    vulnerability_reporting = github.private_vulnerability_reporting(owner, library.repository)
    if vulnerability_reporting is None:
        report.checks.append(
            _unknown(
                "security.private-reporting",
                "Private vulnerability reporting state is not visible to the current credential",
            )
        )
    else:
        report.checks.append(
            _result(
                "security.private-reporting",
                vulnerability_reporting,
                (
                    "Private vulnerability reporting is enabled"
                    if vulnerability_reporting
                    else "Private vulnerability reporting is disabled"
                ),
            )
        )


def audit_library(
    config: EcosystemConfig,
    library: Library,
    github: AuditGitHub,
    pypi: PyPIEvidence,
    *,
    observed_at: datetime | None = None,
) -> LibraryReport:
    """Audit one library, preserving source failures as unknown evidence."""
    observed = (observed_at or datetime.now(UTC)).isoformat()
    report = LibraryReport(library=library, observed_at=observed)
    try:
        info = pypi.package(library.distribution)
        _check_pypi(report, info, config.policy.prerelease_python)
    except EvidenceError as error:
        report.checks.append(_unknown("pypi.evidence", str(error)))

    try:
        _check_repository(report, config.owner, library, github)
    except EvidenceError as error:
        report.checks.append(_unknown("github.evidence", str(error)))
    return report


def audit_all(
    config: EcosystemConfig,
    github: AuditGitHub,
    pypi: PyPIEvidence,
    *,
    observed_at: datetime | None = None,
) -> list[LibraryReport]:
    """Audit every configured library at one observation time."""
    timestamp = observed_at or datetime.now(UTC)
    return [
        audit_library(config, library, github, pypi, observed_at=timestamp)
        for library in config.libraries
    ]

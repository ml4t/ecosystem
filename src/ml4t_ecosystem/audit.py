"""Evidence-backed release metadata and repository compliance checks."""

from __future__ import annotations

import re
import tomllib
from contextlib import suppress
from dataclasses import dataclass
from datetime import UTC, datetime
from html.parser import HTMLParser
from typing import Any

from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import InvalidVersion, Version

from ml4t_ecosystem.agent_orientation import orientation_issues
from ml4t_ecosystem.clients import (
    AuditGitHub,
    DocumentationEvidence,
    EvidenceError,
    PyPIEvidence,
)
from ml4t_ecosystem.models import CheckResult, EcosystemConfig, Library, LibraryReport

REQUIRED_FILES = (
    "LICENSE",
    "README.md",
    "SECURITY.md",
    "AGENTS.md",
    ".github/ISSUE_TEMPLATE/bug.yml",
    ".github/ISSUE_TEMPLATE/feature.yml",
    ".github/ISSUE_TEMPLATE/documentation.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/workflows/ci.yml",
    ".github/workflows/ecosystem.yml",
    ".github/workflows/docs.yml",
    ".github/workflows/release.yml",
    "mkdocs.yml",
    "pyproject.toml",
)
WORKFLOW_PREFIX = ".github/workflows/"
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
PRERELEASE_EXCEPTION = re.compile(r"^\s*prerelease-exception:\s*([^\s#]+)", re.MULTILINE)
ACTION_REFERENCE = re.compile(r"^\s*(?:-\s*)?uses:\s*([^\s#]+)", re.MULTILINE)
UNSUPPORTED_CLAIM = re.compile(
    r"\b(?:state[- ]of[- ]the[- ]art|high[- ]performance|comprehensive|best[- ]in[- ]class)\b",
    re.IGNORECASE,
)
EMAIL_ADDRESS = re.compile(r"[A-Z0-9._%+-]+@([A-Z0-9.-]+\.[A-Z]{2,})\b", re.IGNORECASE)
COPYRIGHT_HOLDER = re.compile(r"^\s*copyright\s+(?:\(c\)|©|\d{4})", re.IGNORECASE)


@dataclass(frozen=True)
class RepositoryEvidence:
    """Repository evidence collected before any GitHub result is emitted."""

    metadata: dict[str, Any]
    source_commit: str
    release_commit: str | None
    contents: dict[str, str | None]
    labels: set[str]
    vulnerability_reporting: bool | None


class _MetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.values: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "meta":
            return
        values = dict(attrs)
        name = values.get("name")
        content = values.get("content")
        if name in {"ml4t-library", "ml4t-version", "ml4t-commit"} and content is not None:
            self.values[name] = content


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


def _keywords(value: object) -> set[str]:
    if isinstance(value, list):
        return {item.strip() for item in value if isinstance(item, str) and item.strip()}
    if isinstance(value, str):
        return {item.strip() for item in value.split(",") if item.strip()}
    return set()


def _person_matches(value: object, name: str, email: str) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 1
        and isinstance(value[0], dict)
        and value[0].get("name") == name
        and value[0].get("email") == email
    )


def _description_passes(description: object, config: EcosystemConfig) -> bool:
    return (
        isinstance(description, str)
        and config.policy.description_minimum_characters
        <= len(description)
        <= config.policy.description_maximum_characters
        and "\n" not in description
        and not UNSUPPORTED_CLAIM.search(description)
    )


def _expected_project_urls(config: EcosystemConfig, library: Library) -> dict[str, str]:
    repository = f"https://github.com/{config.owner}/{library.repository}"
    return {
        "Homepage": config.policy.homepage_url,
        "Documentation": library.docs_url,
        "Repository": repository,
        "Issues": f"{repository}/issues",
    }


def _project_urls_pass(value: object, config: EcosystemConfig, library: Library) -> bool:
    if not isinstance(value, dict):
        return False
    if not set(config.policy.required_project_urls).issubset(value):
        return False
    expected = _expected_project_urls(config, library)
    if any(value.get(label) != url for label, url in expected.items()):
        return False
    repository = expected["Repository"]
    return value.get("Changelog") in {
        f"{repository}/releases",
        f"{repository}/blob/main/CHANGELOG.md",
    }


def _release_files_pass(info: dict[str, Any], version: str | None) -> bool:
    files = info.get("_release_files")
    if not isinstance(files, list) or not isinstance(version, str):
        return False
    types: set[str] = set()
    for item in files:
        if not isinstance(item, dict):
            return False
        package_type = item.get("packagetype")
        filename = item.get("filename")
        digests = item.get("digests")
        if not isinstance(package_type, str) or not isinstance(filename, str):
            return False
        if version not in filename or not isinstance(digests, dict) or not digests.get("sha256"):
            return False
        types.add(package_type)
    return {"bdist_wheel", "sdist"}.issubset(types)


def _check_pypi(
    report: LibraryReport,
    info: dict[str, Any],
    config: EcosystemConfig,
    library: Library,
    observed_at: datetime,
) -> None:
    evidence = f"https://pypi.org/pypi/{library.distribution}/json"
    version_text = info.get("version")
    report.published_version = version_text if isinstance(version_text, str) else None
    try:
        stable_version = isinstance(version_text, str) and not Version(version_text).is_prerelease
    except InvalidVersion:
        stable_version = False
    report.checks.append(
        _result(
            "pypi.stable-version",
            stable_version,
            f"Published version is {version_text!r}",
            evidence,
        )
    )

    classifiers = info.get("classifiers")
    classifier_values = set(classifiers) if isinstance(classifiers, list) else set()
    missing_classifiers = sorted(set(config.policy.required_classifiers) - classifier_values)
    report.checks.append(
        _result(
            "pypi.classifiers",
            not missing_classifiers,
            "Published classifiers satisfy policy"
            if not missing_classifiers
            else f"Published metadata is missing classifiers: {missing_classifiers}",
            evidence,
        )
    )

    identity_matches = (
        info.get("author") == config.policy.author_name
        and info.get("author_email") == config.policy.author_email
        and info.get("maintainer") == config.policy.maintainer_name
        and info.get("maintainer_email") == config.policy.maintainer_email
    )
    report.checks.append(
        _result(
            "pypi.identity",
            identity_matches,
            "Published author and maintainer identities match policy",
            evidence,
        )
    )

    keyword_values = _keywords(info.get("keywords"))
    missing_keywords = sorted(set(config.policy.required_keywords) - keyword_values)
    keyword_passes = len(keyword_values) >= config.policy.minimum_keywords and not missing_keywords
    report.checks.append(
        _result(
            "pypi.keywords",
            keyword_passes,
            "Published keywords satisfy policy"
            if keyword_passes
            else f"Published keywords are incomplete; missing common terms: {missing_keywords}",
            evidence,
        )
    )
    report.checks.append(
        _result(
            "pypi.description",
            _description_passes(info.get("summary"), config),
            "Published description is factual and within configured limits",
            evidence,
        )
    )
    report.checks.append(
        _result(
            "pypi.project-urls",
            _project_urls_pass(info.get("project_urls"), config, library),
            "Published project URLs match canonical destinations",
            evidence,
        )
    )
    report.checks.append(
        _result(
            "pypi.artifact-digests",
            _release_files_pass(info, report.published_version),
            "Published source and wheel artifacts have versioned SHA-256 digests",
            evidence,
        )
    )

    requires_python = info.get("requires_python")
    requires_text = requires_python if isinstance(requires_python, str) else None
    prerelease_python = config.policy.prerelease_python
    prerelease_allowed = _allows_prerelease(requires_text, prerelease_python)
    exception_message: str | None = None
    exception_evidence: str | None = None
    if not prerelease_allowed and library.prerelease_exception is not None:
        exception = config.exception(library.prerelease_exception)
        exception_evidence = exception.issue
        if not exception.is_active(observed_at.date()):
            exception_message = (
                f"Exception {exception.id} expired on {exception.expires_on.isoformat()}"
            )
        elif not isinstance(version_text, str) or not exception.covers_version(version_text):
            exception_message = (
                f"Exception {exception.id} does not cover published version {version_text!r}"
            )
        else:
            prerelease_allowed = True
            exception_message = (
                f"Requires-Python {requires_text!r} is covered by active exception "
                f"{exception.id} through {exception.expires_on.isoformat()}"
            )
    report.checks.append(
        _result(
            "pypi.prerelease-install",
            prerelease_allowed,
            (
                exception_message
                if exception_message is not None
                else f"Requires-Python {requires_text!r} allows Python {prerelease_python} beta"
                if prerelease_allowed
                else f"Requires-Python {requires_text!r} blocks Python {prerelease_python} beta"
            ),
            exception_evidence or evidence,
        )
    )


def _collect_repository(
    owner: str,
    library: Library,
    github: AuditGitHub,
    published_version: str | None,
    required_workflow_files: tuple[str, ...],
) -> RepositoryEvidence:
    metadata = github.repository(owner, library.repository)
    default_branch = metadata.get("default_branch")
    if not isinstance(default_branch, str):
        raise EvidenceError("GitHub repository response has no default branch")
    source_commit = github.branch_commit(owner, library.repository, default_branch)
    base_files = [path for path in REQUIRED_FILES if not path.startswith(WORKFLOW_PREFIX)]
    required_files = (
        *base_files,
        *(f"{WORKFLOW_PREFIX}{name}" for name in required_workflow_files),
    )
    contents = {path: github.content(owner, library.repository, path) for path in required_files}
    return RepositoryEvidence(
        metadata=metadata,
        source_commit=source_commit,
        release_commit=(
            github.tag_commit(owner, library.repository, f"v{published_version}")
            if published_version is not None
            else None
        ),
        contents=contents,
        labels=github.labels(owner, library.repository),
        vulnerability_reporting=github.private_vulnerability_reporting(owner, library.repository),
    )


def _actions_are_pinned(workflows: list[str]) -> bool:
    references = [
        reference for workflow in workflows for reference in ACTION_REFERENCE.findall(workflow)
    ]
    external = [reference for reference in references if not reference.startswith("./")]
    return bool(external) and all(re.search(r"@[0-9a-f]{40}$", reference) for reference in external)


def _check_source_metadata(
    report: LibraryReport,
    config: EcosystemConfig,
    library: Library,
    contents: dict[str, str | None],
    pypi_info: dict[str, Any] | None,
) -> None:
    evidence = f"https://github.com/{config.owner}/{library.repository}/blob/main/pyproject.toml"
    pyproject_text = contents.get("pyproject.toml") or ""
    try:
        pyproject = tomllib.loads(pyproject_text)
    except tomllib.TOMLDecodeError:
        report.checks.append(
            _result("source.pyproject", False, "pyproject.toml is not valid TOML", evidence)
        )
        return
    project = pyproject.get("project")
    if not isinstance(project, dict):
        report.checks.append(
            _result("source.pyproject", False, "pyproject.toml has no project table", evidence)
        )
        return

    report.checks.append(
        _result(
            "source.identity",
            _person_matches(
                project.get("authors"), config.policy.author_name, config.policy.author_email
            )
            and _person_matches(
                project.get("maintainers"),
                config.policy.maintainer_name,
                config.policy.maintainer_email,
            ),
            "Source author and maintainer identities match policy",
            evidence,
        )
    )
    description = project.get("description")
    report.checks.append(
        _result(
            "source.description",
            _description_passes(description, config),
            "Source description is factual and within configured limits",
            evidence,
        )
    )
    keyword_values = _keywords(project.get("keywords"))
    missing_keywords = sorted(set(config.policy.required_keywords) - keyword_values)
    keyword_passes = len(keyword_values) >= config.policy.minimum_keywords and not missing_keywords
    report.checks.append(
        _result(
            "source.keywords",
            keyword_passes,
            "Source keywords satisfy policy"
            if keyword_passes
            else f"Source keywords are incomplete; missing common terms: {missing_keywords}",
            evidence,
        )
    )
    classifiers = project.get("classifiers")
    classifier_values = set(classifiers) if isinstance(classifiers, list) else set()
    missing_classifiers = sorted(set(config.policy.required_classifiers) - classifier_values)
    report.checks.append(
        _result(
            "source.classifiers",
            not missing_classifiers,
            "Source classifiers satisfy policy"
            if not missing_classifiers
            else f"Source metadata is missing classifiers: {missing_classifiers}",
            evidence,
        )
    )
    report.checks.append(
        _result(
            "source.project-urls",
            _project_urls_pass(project.get("urls"), config, library),
            "Source project URLs match canonical destinations",
            evidence,
        )
    )
    if pypi_info is None:
        report.checks.append(
            _unknown(
                "metadata.source-pypi",
                "PyPI metadata was not collected, so source equality is unknown",
                evidence,
            )
        )
    else:
        fields_match = (
            description == pypi_info.get("summary")
            and project.get("requires-python") == pypi_info.get("requires_python")
            and keyword_values == _keywords(pypi_info.get("keywords"))
            and classifier_values == set(pypi_info.get("classifiers", []))
            and project.get("urls") == pypi_info.get("project_urls")
        )
        report.checks.append(
            _result(
                "metadata.source-pypi",
                fields_match,
                "Source and latest PyPI metadata match",
                evidence,
            )
        )


def _check_readme(
    report: LibraryReport, config: EcosystemConfig, library: Library, readme: str
) -> None:
    evidence = f"https://github.com/{config.owner}/{library.repository}/blob/main/README.md"
    repository = f"https://github.com/{config.owner}/{library.repository}"
    report.checks.append(
        _result(
            "readme.installation",
            library.distribution in readme
            and all(version in readme for version in config.policy.stable_python),
            "README names the distribution and every supported Python version",
            evidence,
        )
    )
    report.checks.append(
        _result(
            "readme.quick-start",
            "```python" in readme and library.import_package in readme,
            "README contains a Python quick start using the public package",
            evidence,
        )
    )
    required_links = (library.docs_url, f"{repository}/issues", "LICENSE")
    release_notes_linked = f"{repository}/releases" in readme or "CHANGELOG.md" in readme
    report.checks.append(
        _result(
            "readme.links",
            all(link in readme for link in required_links) and release_notes_linked,
            "README links documentation, issues, license, and release notes",
            evidence,
        )
    )
    report.checks.append(
        _result(
            "readme.development-gates",
            all(command in readme for command in ("ruff", "ty", "pytest")),
            "README names the repository lint, type, and test gates",
            evidence,
        )
    )
    report.checks.append(
        _result(
            "readme.support-boundaries",
            any(term in readme.lower() for term in ("compatibility", "requirements", "support")),
            "README identifies requirements, compatibility, or support boundaries",
            evidence,
        )
    )


def _check_repository(
    report: LibraryReport,
    config: EcosystemConfig,
    library: Library,
    repository: RepositoryEvidence,
    pypi_info: dict[str, Any] | None,
) -> None:
    owner = config.owner
    repository_url = f"https://github.com/{owner}/{library.repository}"
    metadata = repository.metadata
    report.source_commit = repository.source_commit
    report.release_commit = repository.release_commit
    default_branch = metadata.get("default_branch")
    report.checks.append(
        _result(
            "github.default-branch",
            default_branch == "main",
            f"Default branch is {default_branch!r}",
            repository_url,
        )
    )
    report.checks.append(
        _result(
            "github.visibility",
            metadata.get("visibility") == "public",
            f"Repository visibility is {metadata.get('visibility')!r}",
            repository_url,
        )
    )
    report.checks.append(
        _result(
            "github.release-commit",
            repository.release_commit is not None,
            (
                f"Published version resolves to commit {repository.release_commit}"
                if repository.release_commit is not None
                else "Published version has no matching v-prefixed Git tag"
            ),
            repository_url,
        )
    )

    for path in repository.contents:
        content = repository.contents[path]
        code_path = path.replace("/", ".").lstrip(".")
        report.checks.append(
            _result(
                f"repository.file.{code_path}",
                content is not None,
                f"Required file {path} {'exists' if content is not None else 'is missing'}",
                f"{repository_url}/blob/main/{path}",
            )
        )

    description = metadata.get("description")
    source_description: object = None
    with suppress(AttributeError, tomllib.TOMLDecodeError):
        source_description = (
            tomllib.loads(repository.contents["pyproject.toml"] or "")
            .get("project", {})
            .get("description")
        )
    report.checks.append(
        _result(
            "github.description",
            _description_passes(description, config) and description == source_description,
            "GitHub and source descriptions match and satisfy policy",
            repository_url,
        )
    )
    report.checks.append(
        _result(
            "github.homepage",
            metadata.get("homepage") == library.docs_url,
            f"GitHub homepage is the canonical documentation route {library.docs_url}",
            repository_url,
        )
    )
    topics = metadata.get("topics")
    topic_values = set(topics) if isinstance(topics, list) else set()
    missing_topics = sorted(set(config.policy.required_github_topics) - topic_values)
    report.checks.append(
        _result(
            "github.topics",
            not missing_topics
            and len(topic_values) >= len(config.policy.required_github_topics) + 2,
            "GitHub topics include common and library-specific terms"
            if not missing_topics
            else f"GitHub topics are missing: {missing_topics}",
            repository_url,
        )
    )

    public_text = "\n".join(content or "" for content in repository.contents.values())
    email_domains = {match.lower() for match in EMAIL_ADDRESS.findall(public_text)}
    allowed_domains = {
        config.policy.author_email.rsplit("@", 1)[-1].lower(),
        config.policy.maintainer_email.rsplit("@", 1)[-1].lower(),
    }
    copyright_lines = [line for line in public_text.splitlines() if COPYRIGHT_HOLDER.search(line)]
    public_identity_passes = email_domains <= allowed_domains and all(
        config.policy.author_name in line or "ML4T" in line for line in copyright_lines
    )
    report.checks.append(
        _result(
            "repository.public-identity",
            public_identity_passes,
            "Required public files use only canonical contact domains and copyright identities",
            repository_url,
        )
    )

    _check_source_metadata(report, config, library, repository.contents, pypi_info)
    _check_readme(report, config, library, repository.contents["README.md"] or "")

    agent_issues = orientation_issues(
        repository.contents["AGENTS.md"] or "", library.import_package
    )
    report.checks.append(
        _result(
            "repository.agent-orientation",
            not agent_issues,
            (
                "AGENTS.md provides public repository orientation"
                if not agent_issues
                else "AGENTS.md is incomplete: " + "; ".join(agent_issues)
            ),
            f"{repository_url}/blob/main/AGENTS.md",
        )
    )

    ecosystem_workflow = repository.contents[".github/workflows/ecosystem.yml"] or ""
    report.checks.append(
        _result(
            "workflow.central-qualification",
            _uses_pinned_central_qualification(ecosystem_workflow),
            "Repository calls an immutable central qualification workflow revision",
            f"{repository_url}/blob/main/.github/workflows/ecosystem.yml",
        )
    )
    exception_match = PRERELEASE_EXCEPTION.search(ecosystem_workflow)
    declared_exception = exception_match.group(1) if exception_match else None
    expected_exception = library.prerelease_exception
    report.checks.append(
        _result(
            "workflow.prerelease-exception",
            declared_exception == expected_exception,
            (
                f"Workflow declares expected prerelease exception {expected_exception}"
                if expected_exception is not None and declared_exception == expected_exception
                else "Workflow correctly requires prerelease qualification"
                if expected_exception is None and declared_exception is None
                else (
                    f"Workflow prerelease exception {declared_exception!r} does not match "
                    f"configured exception {expected_exception!r}"
                )
            ),
            f"{repository_url}/blob/main/.github/workflows/ecosystem.yml",
        )
    )

    pyproject_text = repository.contents["pyproject.toml"] or ""
    try:
        pyproject = tomllib.loads(pyproject_text)
        test_group = pyproject.get("dependency-groups", {}).get("test")
        has_test_group = isinstance(test_group, list)
    except tomllib.TOMLDecodeError:
        has_test_group = False
    report.checks.append(
        _result(
            "repository.test-dependency-group",
            has_test_group,
            "Repository declares the isolated prerelease test dependency group",
            f"{repository_url}/blob/main/pyproject.toml",
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
            f"{repository_url}/blob/main/.github/workflows/ecosystem.yml",
        )
    )

    mkdocs = repository.contents["mkdocs.yml"] or ""
    canonical_url = library.docs_url.rstrip("/") in mkdocs
    report.checks.append(
        _result(
            "docs.canonical-url",
            canonical_url,
            f"MkDocs declares canonical route {library.docs_url}",
            f"{repository_url}/blob/main/mkdocs.yml",
        )
    )

    ci_workflow = repository.contents[".github/workflows/ci.yml"] or ""
    docs_workflow = repository.contents[".github/workflows/docs.yml"] or ""
    release_workflow = repository.contents[".github/workflows/release.yml"] or ""
    workflows = [ci_workflow, ecosystem_workflow, docs_workflow, release_workflow]
    report.checks.append(
        _result(
            "workflow.immutable-actions",
            _actions_are_pinned(workflows),
            "All external workflow references use full commit SHAs",
            f"{repository_url}/tree/main/.github/workflows",
        )
    )
    report.checks.append(
        _result(
            "workflow.minimum-permissions",
            all(
                "permissions:" in workflow and "contents: read" in workflow
                for workflow in workflows
            ),
            "Each workflow declares read-only contents permission by default",
            f"{repository_url}/tree/main/.github/workflows",
        )
    )
    ci_terms = (
        "pull_request:",
        "branches: [main]",
        "ruff check",
        "ruff format --check",
        "ty check",
        "pytest",
        "uv build",
        "mkdocs build --strict",
    )
    report.checks.append(
        _result(
            "workflow.ci-gates",
            all(term in ci_workflow for term in ci_terms),
            "CI runs the common pull-request and main quality gates",
            f"{repository_url}/blob/main/.github/workflows/ci.yml",
        )
    )
    strict_docs = "mkdocs build --strict" in docs_workflow
    report.checks.append(
        _result(
            "docs.strict-build",
            strict_docs,
            "Documentation CI runs MkDocs in strict mode",
            f"{repository_url}/blob/main/.github/workflows/docs.yml",
        )
    )
    release_qualified = _uses_pinned_central_qualification(release_workflow)
    report.checks.append(
        _result(
            "release.central-qualification",
            release_qualified,
            "Release workflow depends on an immutable central qualification revision",
            f"{repository_url}/blob/main/.github/workflows/release.yml",
        )
    )
    trusted_publishing = (
        "id-token: write" in release_workflow
        and "pypa/gh-action-pypi-publish" in release_workflow
        and "password:" not in release_workflow
    )
    report.checks.append(
        _result(
            "release.trusted-publishing",
            trusted_publishing,
            "Release uses scoped PyPI trusted publishing without an upload password",
            f"{repository_url}/blob/main/.github/workflows/release.yml",
        )
    )
    manifest_terms = ("sha256", "manifest", "github.sha")
    report.checks.append(
        _result(
            "release.artifact-manifest",
            all(term in release_workflow.lower() for term in manifest_terms),
            "Release binds artifact digests and manifest to the candidate commit",
            f"{repository_url}/blob/main/.github/workflows/release.yml",
        )
    )

    missing_labels = sorted(REQUIRED_LABELS - repository.labels)
    report.checks.append(
        _result(
            "github.shared-labels",
            not missing_labels,
            "Shared labels are present"
            if not missing_labels
            else f"Missing labels: {missing_labels}",
            f"{repository_url}/labels",
        )
    )

    vulnerability_reporting = repository.vulnerability_reporting
    if vulnerability_reporting is None:
        report.checks.append(
            _unknown(
                "security.private-reporting",
                "Private vulnerability reporting state is not visible to the current credential",
                f"{repository_url}/security",
            )
        )
    else:
        report.checks.append(
            _result(
                "security.private-reporting",
                vulnerability_reporting,
                "Private vulnerability reporting is enabled"
                if vulnerability_reporting
                else "Private vulnerability reporting is disabled",
                f"{repository_url}/security",
            )
        )


def _check_documentation(
    report: LibraryReport, library: Library, html: str, pypi_collected: bool
) -> None:
    parser = _MetadataParser()
    parser.feed(html)
    documented_library = parser.values.get("ml4t-library")
    documented_version = parser.values.get("ml4t-version")
    documented_commit = parser.values.get("ml4t-commit")
    report.documentation_version = documented_version
    report.documentation_commit = documented_commit
    report.checks.append(
        _result(
            "docs.deployed-library",
            documented_library == library.key,
            f"Deployed documentation identifies library {documented_library!r}",
            library.docs_url,
        )
    )
    if pypi_collected:
        report.checks.append(
            _result(
                "docs.deployed-version",
                documented_version == report.published_version,
                f"Deployed documentation version is {documented_version!r}",
                library.docs_url,
            )
        )
    else:
        report.checks.append(
            _unknown(
                "docs.deployed-version",
                "PyPI evidence was not collected, so documentation freshness is unknown",
                library.docs_url,
            )
        )
    report.checks.append(
        _result(
            "docs.deployed-commit",
            documented_commit == report.release_commit,
            f"Deployed documentation commit is {documented_commit!r}",
            library.docs_url,
        )
    )


def audit_library(
    config: EcosystemConfig,
    library: Library,
    github: AuditGitHub,
    pypi: PyPIEvidence,
    documentation: DocumentationEvidence,
    *,
    observed_at: datetime | None = None,
) -> LibraryReport:
    """Audit one library, preserving source failures as unknown evidence."""
    observation = observed_at or datetime.now(UTC)
    report = LibraryReport(library=library, observed_at=observation.isoformat())

    pypi_info: dict[str, Any] | None = None
    try:
        pypi_info = pypi.package(library.distribution)
    except EvidenceError as error:
        report.checks.append(
            _unknown(
                "pypi.evidence",
                str(error),
                f"https://pypi.org/pypi/{library.distribution}/json",
            )
        )

    repository: RepositoryEvidence | None = None
    try:
        repository = _collect_repository(
            config.owner,
            library,
            github,
            (
                pypi_info.get("version")
                if pypi_info is not None and isinstance(pypi_info.get("version"), str)
                else None
            ),
            config.policy.required_workflow_files,
        )
    except EvidenceError as error:
        report.checks.append(
            _unknown(
                "github.evidence",
                str(error),
                f"https://github.com/{config.owner}/{library.repository}",
            )
        )

    documentation_html: str | None = None
    try:
        documentation_html = documentation.page(library.docs_url)
    except EvidenceError as error:
        report.checks.append(_unknown("docs.evidence", str(error), library.docs_url))

    if pypi_info is not None:
        _check_pypi(report, pypi_info, config, library, observation)
    if repository is not None:
        _check_repository(report, config, library, repository, pypi_info)
    if documentation_html is not None:
        _check_documentation(report, library, documentation_html, pypi_info is not None)
    return report


def audit_all(
    config: EcosystemConfig,
    github: AuditGitHub,
    pypi: PyPIEvidence,
    documentation: DocumentationEvidence,
    *,
    observed_at: datetime | None = None,
) -> list[LibraryReport]:
    """Audit every configured library at one observation time."""
    timestamp = observed_at or datetime.now(UTC)
    return [
        audit_library(config, library, github, pypi, documentation, observed_at=timestamp)
        for library in config.libraries
    ]

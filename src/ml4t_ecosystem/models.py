"""Typed ecosystem configuration and result models."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Literal

from packaging.specifiers import SpecifierSet

CheckStatus = Literal["pass", "fail", "unknown"]


@dataclass(frozen=True)
class Library:
    """One managed ML4T library."""

    key: str
    repository: str
    distribution: str
    import_package: str
    docs_url: str
    local_checkout: str
    development_workspace: str
    prerelease_exception: str | None = None


@dataclass(frozen=True)
class QualificationException:
    """One approved, time-limited release qualification exception."""

    id: str
    criterion: str
    libraries: tuple[str, ...]
    affected_versions: str
    rationale: str
    evidence: tuple[str, ...]
    user_impact: str
    mitigation: str
    approver: str
    expires_on: date
    issue: str

    def is_active(self, on_date: date) -> bool:
        """Return whether the exception remains valid on a date."""
        return on_date <= self.expires_on

    def covers_version(self, version: str) -> bool:
        """Return whether a published version is inside the approved scope."""
        return SpecifierSet(self.affected_versions).contains(version, prereleases=True)


@dataclass(frozen=True)
class Policy:
    """Shared compatibility and response policy."""

    minimum_python: str
    stable_python: tuple[str, ...]
    prerelease_python: str
    operating_systems: tuple[str, ...]
    classification_target_minutes: int
    response_target_business_days: int
    maintainer_logins: tuple[str, ...]


@dataclass(frozen=True)
class EcosystemConfig:
    """Validated ecosystem inventory."""

    schema_version: int
    owner: str
    policy: Policy
    libraries: tuple[Library, ...]
    exceptions: tuple[QualificationException, ...]

    def library(self, key: str) -> Library:
        """Return a configured library by key."""
        for library in self.libraries:
            if library.key == key:
                return library
        raise KeyError(f"Unknown library: {key}")

    def exception(self, exception_id: str) -> QualificationException:
        """Return a configured qualification exception by id."""
        for exception in self.exceptions:
            if exception.id == exception_id:
                return exception
        raise KeyError(f"Unknown exception: {exception_id}")


@dataclass(frozen=True)
class CheckResult:
    """One evidence-backed compliance result."""

    code: str
    status: CheckStatus
    message: str
    evidence: str | None = None

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-compatible representation."""
        return asdict(self)


@dataclass
class LibraryReport:
    """Collected evidence and checks for one library."""

    library: Library
    observed_at: str
    source_commit: str | None = None
    published_version: str | None = None
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """Return whether all checks passed."""
        return bool(self.checks) and all(check.status == "pass" for check in self.checks)

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-compatible representation."""
        return {
            "library": asdict(self.library),
            "observed_at": self.observed_at,
            "source_commit": self.source_commit,
            "published_version": self.published_version,
            "passed": self.passed,
            "checks": [check.to_dict() for check in self.checks],
        }

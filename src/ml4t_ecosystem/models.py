"""Typed ecosystem configuration and result models."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

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


@dataclass(frozen=True)
class Policy:
    """Shared compatibility and response policy."""

    minimum_python: str
    stable_python: tuple[str, ...]
    prerelease_python: str
    operating_systems: tuple[str, ...]
    classification_target_minutes: int
    response_target_business_days: int


@dataclass(frozen=True)
class EcosystemConfig:
    """Validated ecosystem inventory."""

    schema_version: int
    owner: str
    policy: Policy
    libraries: tuple[Library, ...]

    def library(self, key: str) -> Library:
        """Return a configured library by key."""
        for library in self.libraries:
            if library.key == key:
                return library
        raise KeyError(f"Unknown library: {key}")


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

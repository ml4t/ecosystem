"""Load and validate ecosystem configuration."""

from __future__ import annotations

import tomllib
from datetime import date
from pathlib import Path
from typing import Any

from packaging.specifiers import InvalidSpecifier, SpecifierSet

from ml4t_ecosystem.models import EcosystemConfig, Library, Policy, QualificationException

EXPECTED_LIBRARY_KEYS = {
    "data",
    "engineer",
    "backtest",
    "specs",
    "live",
    "diagnostic",
    "models",
}


def _required_str(mapping: dict[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _string_tuple(mapping: dict[str, Any], key: str) -> tuple[str, ...]:
    value = mapping.get(key)
    if not isinstance(value, list) or not value or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{key} must be a non-empty string list")
    return tuple(value)


def _optional_str(mapping: dict[str, Any], key: str) -> str | None:
    value = mapping.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string when provided")
    return value


def _required_date(mapping: dict[str, Any], key: str) -> date:
    value = mapping.get(key)
    if not isinstance(value, date):
        raise ValueError(f"{key} must be a TOML date")
    return value


def load_config(path: Path) -> EcosystemConfig:
    """Load and validate a library inventory TOML file."""
    with path.open("rb") as handle:
        raw = tomllib.load(handle)

    if raw.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    owner = _required_str(raw, "owner")

    raw_policy = raw.get("policy")
    if not isinstance(raw_policy, dict):
        raise ValueError("policy must be a table")
    classification = raw_policy.get("classification_target_minutes")
    response = raw_policy.get("response_target_business_days")
    if not isinstance(classification, int) or classification <= 0:
        raise ValueError("classification_target_minutes must be a positive integer")
    if not isinstance(response, int) or response <= 0:
        raise ValueError("response_target_business_days must be a positive integer")
    policy = Policy(
        minimum_python=_required_str(raw_policy, "minimum_python"),
        stable_python=_string_tuple(raw_policy, "stable_python"),
        prerelease_python=_required_str(raw_policy, "prerelease_python"),
        operating_systems=_string_tuple(raw_policy, "operating_systems"),
        classification_target_minutes=classification,
        response_target_business_days=response,
        maintainer_logins=_string_tuple(raw_policy, "maintainer_logins"),
    )

    raw_libraries = raw.get("libraries")
    if not isinstance(raw_libraries, list):
        raise ValueError("libraries must be an array of tables")
    libraries: list[Library] = []
    for raw_library in raw_libraries:
        if not isinstance(raw_library, dict):
            raise ValueError("each library must be a table")
        libraries.append(
            Library(
                key=_required_str(raw_library, "key"),
                repository=_required_str(raw_library, "repository"),
                distribution=_required_str(raw_library, "distribution"),
                import_package=_required_str(raw_library, "import_package"),
                docs_url=_required_str(raw_library, "docs_url"),
                local_checkout=_required_str(raw_library, "local_checkout"),
                development_workspace=_required_str(raw_library, "development_workspace"),
                prerelease_exception=_optional_str(raw_library, "prerelease_exception"),
            )
        )

    keys = [library.key for library in libraries]
    if len(keys) != len(set(keys)):
        raise ValueError("library keys must be unique")
    if set(keys) != EXPECTED_LIBRARY_KEYS:
        missing = sorted(EXPECTED_LIBRARY_KEYS - set(keys))
        extra = sorted(set(keys) - EXPECTED_LIBRARY_KEYS)
        raise ValueError(f"library inventory mismatch: missing={missing}, extra={extra}")
    repositories = [library.repository for library in libraries]
    if len(repositories) != len(set(repositories)):
        raise ValueError("library repositories must be unique")

    raw_exceptions = raw.get("exceptions", [])
    if not isinstance(raw_exceptions, list):
        raise ValueError("exceptions must be an array of tables")
    exceptions: list[QualificationException] = []
    for raw_exception in raw_exceptions:
        if not isinstance(raw_exception, dict):
            raise ValueError("each exception must be a table")
        affected_versions = _required_str(raw_exception, "affected_versions")
        try:
            SpecifierSet(affected_versions)
        except InvalidSpecifier as error:
            raise ValueError(f"affected_versions must be a valid specifier: {error}") from error
        exceptions.append(
            QualificationException(
                id=_required_str(raw_exception, "id"),
                criterion=_required_str(raw_exception, "criterion"),
                libraries=_string_tuple(raw_exception, "libraries"),
                affected_versions=affected_versions,
                rationale=_required_str(raw_exception, "rationale"),
                evidence=_string_tuple(raw_exception, "evidence"),
                user_impact=_required_str(raw_exception, "user_impact"),
                mitigation=_required_str(raw_exception, "mitigation"),
                approver=_required_str(raw_exception, "approver"),
                expires_on=_required_date(raw_exception, "expires_on"),
                issue=_required_str(raw_exception, "issue"),
            )
        )

    exception_ids = [exception.id for exception in exceptions]
    if len(exception_ids) != len(set(exception_ids)):
        raise ValueError("exception ids must be unique")
    known_keys = set(keys)
    expected_criterion = f"python-{policy.prerelease_python}-prerelease"
    for exception in exceptions:
        if exception.criterion != expected_criterion:
            raise ValueError(f"exception {exception.id} criterion must be {expected_criterion!r}")
        unknown = sorted(set(exception.libraries) - known_keys)
        if unknown:
            raise ValueError(f"exception {exception.id} has unknown libraries: {unknown}")

    exceptions_by_id = {exception.id: exception for exception in exceptions}
    for library in libraries:
        if library.prerelease_exception is None:
            continue
        exception = exceptions_by_id.get(library.prerelease_exception)
        if exception is None:
            raise ValueError(
                f"library {library.key} references unknown prerelease exception "
                f"{library.prerelease_exception}"
            )
        if library.key not in exception.libraries:
            raise ValueError(
                f"exception {exception.id} does not include configured library {library.key}"
            )

    referenced = {
        library.prerelease_exception
        for library in libraries
        if library.prerelease_exception is not None
    }
    unreferenced = sorted(set(exception_ids) - referenced)
    if unreferenced:
        raise ValueError(f"unreferenced exceptions: {unreferenced}")

    return EcosystemConfig(
        schema_version=1,
        owner=owner,
        policy=policy,
        libraries=tuple(libraries),
        exceptions=tuple(exceptions),
    )

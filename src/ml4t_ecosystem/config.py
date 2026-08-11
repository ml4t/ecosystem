"""Load and validate ecosystem configuration."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

from ml4t_ecosystem.models import EcosystemConfig, Library, Policy

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

    return EcosystemConfig(
        schema_version=1,
        owner=owner,
        policy=policy,
        libraries=tuple(libraries),
    )

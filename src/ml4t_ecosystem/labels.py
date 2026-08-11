"""Load and synchronize the shared GitHub label vocabulary."""

from __future__ import annotations

import subprocess
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Label:
    """One required GitHub label."""

    name: str
    color: str
    description: str


def load_labels(path: Path) -> tuple[Label, ...]:
    """Load and validate shared labels."""
    with path.open("rb") as handle:
        raw = tomllib.load(handle)
    if raw.get("schema_version") != 1:
        raise ValueError("label schema_version must be 1")
    values = raw.get("labels")
    if not isinstance(values, list):
        raise ValueError("labels must be an array of tables")
    labels: list[Label] = []
    for value in values:
        if not isinstance(value, dict):
            raise ValueError("each label must be a table")
        name = _string(value, "name")
        color = _string(value, "color")
        description = _string(value, "description")
        if len(color) != 6 or any(character not in "0123456789abcdefABCDEF" for character in color):
            raise ValueError(f"invalid label color for {name}: {color}")
        labels.append(Label(name, color.lower(), description))
    names = [label.name for label in labels]
    if len(names) != len(set(names)):
        raise ValueError("label names must be unique")
    return tuple(labels)


def _string(value: dict[str, Any], key: str) -> str:
    result = value.get(key)
    if not isinstance(result, str) or not result:
        raise ValueError(f"label {key} must be a non-empty string")
    return result


def sync_labels(repository: str, labels: tuple[Label, ...]) -> None:
    """Create or update labels through the authenticated GitHub CLI."""
    for label in labels:
        subprocess.run(
            [
                "gh",
                "label",
                "create",
                label.name,
                "--repo",
                repository,
                "--color",
                label.color,
                "--description",
                label.description,
                "--force",
            ],
            check=True,
        )

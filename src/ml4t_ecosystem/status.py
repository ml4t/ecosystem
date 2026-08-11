"""Render and atomically publish qualification status."""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Mapping
from pathlib import Path

from ml4t_ecosystem.models import LibraryReport


def render_json(reports: list[LibraryReport]) -> str:
    """Render reports as deterministic JSON."""
    payload = {
        "schema_version": 1,
        "passed": bool(reports) and all(report.passed for report in reports),
        "reports": [report.to_dict() for report in reports],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def render_markdown(reports: list[LibraryReport]) -> str:
    """Render a concise human-readable qualification summary."""
    lines = [
        "# Current qualification status",
        "",
        "This file is generated from PyPI and GitHub evidence. Do not edit it by hand.",
        "",
        "| Library | Version | Commit evidence | Result | Failed or unknown checks |",
        "|---|---:|---|---|---|",
    ]
    for report in reports:
        failures = [check.code for check in report.checks if check.status != "pass"]
        lines.append(
            "| {key} | {version} | {commit} | {result} | {failures} |".format(
                key=report.library.key,
                version=report.published_version or "unknown",
                commit=report.source_commit or "unknown",
                result="PASS" if report.passed else "FAIL",
                failures=", ".join(failures) if failures else "none",
            )
        )
    lines.extend(["", f"Observed at: {reports[0].observed_at if reports else 'unknown'}", ""])
    return "\n".join(lines)


def atomic_write_many(files: Mapping[Path, str]) -> None:
    """Write a set of text files and restore all originals on replacement failure."""
    if not files:
        return
    parents = {path.parent.resolve() for path in files}
    if len(parents) != 1:
        raise ValueError("all atomic outputs must share one directory")
    parent = next(iter(parents))
    parent.mkdir(parents=True, exist_ok=True)
    originals = {path: path.read_bytes() if path.exists() else None for path in files}
    staged: dict[Path, Path] = {}
    try:
        for destination, content in files.items():
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=parent, delete=False
            ) as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
                staged[destination] = Path(handle.name)
        replaced: list[Path] = []
        try:
            for destination, temporary in staged.items():
                os.replace(temporary, destination)
                replaced.append(destination)
        except OSError:
            for destination in reversed(replaced):
                original = originals[destination]
                if original is None:
                    destination.unlink(missing_ok=True)
                else:
                    destination.write_bytes(original)
            raise
    finally:
        for temporary in staged.values():
            temporary.unlink(missing_ok=True)


def write_current_status(reports: list[LibraryReport], output_directory: Path) -> None:
    """Publish JSON and Markdown current status as one logical operation."""
    atomic_write_many(
        {
            output_directory / "current.json": render_json(reports),
            output_directory / "current.md": render_markdown(reports),
        }
    )

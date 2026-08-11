"""Synchronize canonical GitHub collaboration files into a library checkout."""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

TEMPLATE_FILES = (
    ".github/ISSUE_TEMPLATE/bug.yml",
    ".github/ISSUE_TEMPLATE/feature.yml",
    ".github/ISSUE_TEMPLATE/documentation.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/PULL_REQUEST_TEMPLATE.md",
)


def sync_templates(source_root: Path, target_root: Path, repository: str) -> None:
    """Copy validated templates without leaving a partial target update."""
    rendered: dict[Path, str] = {}
    for relative_name in TEMPLATE_FILES:
        source = source_root / relative_name
        if not source.is_file():
            raise ValueError(f"missing canonical template: {relative_name}")
        content = (
            source.read_text(encoding="utf-8")
            .replace("{{repository}}", repository)
            .replace("ml4t/ecosystem", repository)
        )
        if "{{" in content or "}}" in content:
            raise ValueError(f"unresolved template variable in {relative_name}")
        rendered[target_root / relative_name] = content

    backup_directory = Path(tempfile.mkdtemp(prefix="ml4t-template-backup-"))
    originals: dict[Path, Path | None] = {}
    try:
        for destination in rendered:
            if destination.exists():
                backup = backup_directory / str(len(originals))
                shutil.copy2(destination, backup)
                originals[destination] = backup
            else:
                originals[destination] = None
        written: list[Path] = []
        try:
            for destination, content in rendered.items():
                destination.parent.mkdir(parents=True, exist_ok=True)
                temporary = destination.with_name(f".{destination.name}.tmp")
                temporary.write_text(content, encoding="utf-8")
                os.replace(temporary, destination)
                written.append(destination)
        except OSError:
            for destination in reversed(written):
                backup = originals[destination]
                if backup is None:
                    destination.unlink(missing_ok=True)
                else:
                    shutil.copy2(backup, destination)
            raise
    finally:
        shutil.rmtree(backup_directory)

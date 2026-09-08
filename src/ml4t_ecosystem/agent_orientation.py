"""Validation for public repository agent orientation."""

from __future__ import annotations

import re

MINIMUM_ORIENTATION_WORDS = 75


def orientation_issues(text: str, import_package: str) -> tuple[str, ...]:
    """Return concrete reasons a public AGENTS.md does not orient an external agent."""
    issues: list[str] = []
    words = re.findall(r"[A-Za-z0-9_][A-Za-z0-9_.-]*", text)
    if len(words) < MINIMUM_ORIENTATION_WORDS:
        issues.append(f"contains fewer than {MINIMUM_ORIENTATION_WORDS} words")
    if re.search(r"^##\s+\S", text, flags=re.MULTILINE) is None:
        issues.append("has no navigable sections")
    if import_package not in text:
        issues.append(f"does not name the public import {import_package}")
    if "src/" not in text:
        issues.append("does not identify the source tree")
    if f"from {import_package}" not in text and "uv run" not in text:
        issues.append("contains neither a public import example nor a quality command")
    if re.search(r"^\s*@\.workspace/", text, flags=re.MULTILINE):
        issues.append("imports private workspace state")
    return tuple(issues)

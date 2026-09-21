"""Validation for public repository agent orientation."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

MINIMUM_ORIENTATION_WORDS = 75
MINIMUM_NESTED_WORDS = 30
MAXIMUM_ROOT_LINES = 200
MAXIMUM_NESTED_LINES = 120

PRIVATE_STATE = re.compile(
    r"(?:@?\.(?:workspace|claude|codex)(?:/|\b)|(?:^|\s)(?:/home/|~/)|@AGENTS\.md)",
    flags=re.MULTILINE,
)
TOOL_MECHANISM = re.compile(r"\b(?:Claude|Codex)\b", flags=re.IGNORECASE)
VOLATILE_COUNT = re.compile(
    r"\b\d[\d,]*(?:\s+|-)(?:lines?|tests?|files?|modules?)\b",
    flags=re.IGNORECASE,
)


def _words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9_][A-Za-z0-9_.-]*", text)


def _title_tokens(value: str) -> set[str]:
    tokens = re.findall(r"[a-z0-9]+", value.lower())
    return {token[:-1] if len(token) > 3 and token.endswith("s") else token for token in tokens}


def _shared_issues(text: str) -> list[str]:
    issues: list[str] = []
    if PRIVATE_STATE.search(text):
        issues.append("references private or machine-local agent state")
    if TOOL_MECHANISM.search(text):
        issues.append("describes agent-tool mechanics instead of the library")
    if VOLATILE_COUNT.search(text):
        issues.append("contains a volatile file, line, module, or test count")
    return issues


def orientation_issues(text: str, import_package: str) -> tuple[str, ...]:
    """Return concrete reasons a public AGENTS.md does not orient an external agent."""
    issues = _shared_issues(text)
    if len(_words(text)) < MINIMUM_ORIENTATION_WORDS:
        issues.append(f"contains fewer than {MINIMUM_ORIENTATION_WORDS} words")
    if len(text.splitlines()) > MAXIMUM_ROOT_LINES:
        issues.append(f"contains more than {MAXIMUM_ROOT_LINES} lines")
    if re.search(r"^##\s+\S", text, flags=re.MULTILINE) is None:
        issues.append("has no navigable sections")
    if import_package not in text:
        issues.append(f"does not name the public import {import_package}")
    if "src/" not in text:
        issues.append("does not identify the source tree")
    if f"from {import_package}" not in text and "uv run" not in text:
        issues.append("contains neither a public import example nor a quality command")
    missing_commands = [command for command in ("ruff", "ty", "pytest") if command not in text]
    if missing_commands:
        issues.append("does not name required quality commands: " + ", ".join(missing_commands))
    return tuple(issues)


def discover_agent_guides(root: Path) -> tuple[Path, ...]:
    """Return tracked agent guides, falling back to filesystem discovery outside Git."""
    completed = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--", "AGENTS.md", ":(glob)**/AGENTS.md"],
        check=False,
        capture_output=True,
    )
    if completed.returncode == 0:
        relative_paths = [Path(value.decode()) for value in completed.stdout.split(b"\0") if value]
        return tuple(sorted(relative_paths))
    return tuple(sorted(path.relative_to(root) for path in root.rglob("AGENTS.md")))


def nested_orientation_issues(root: Path) -> tuple[str, ...]:
    """Return path-qualified issues for tracked nested AGENTS.md files."""
    findings: list[str] = []
    seen_content: dict[str, Path] = {}
    root_guide = root / "AGENTS.md"
    if root_guide.is_file():
        seen_content[" ".join(_words(root_guide.read_text(encoding="utf-8").lower()))] = Path(
            "AGENTS.md"
        )
    for relative in discover_agent_guides(root):
        if relative == Path("AGENTS.md"):
            continue
        text = (root / relative).read_text(encoding="utf-8")
        issues = _shared_issues(text)
        if len(_words(text)) < MINIMUM_NESTED_WORDS:
            issues.append(f"contains fewer than {MINIMUM_NESTED_WORDS} words")
        if len(text.splitlines()) > MAXIMUM_NESTED_LINES:
            issues.append(f"contains more than {MAXIMUM_NESTED_LINES} lines")
        if re.search(r"^##\s+\S", text, flags=re.MULTILINE) is None:
            issues.append("has no navigable sections")
        directory_name = relative.parent.name
        heading = next(
            (
                line.removeprefix("#").strip().lower()
                for line in text.splitlines()
                if line.startswith("#")
            ),
            "",
        )
        if not _title_tokens(directory_name) <= _title_tokens(heading):
            issues.append(f"does not identify its directory {relative.parent.name!r} in the title")
        normalized = " ".join(_words(text.lower()))
        if duplicate := seen_content.get(normalized):
            issues.append(f"duplicates {duplicate.as_posix()}")
        else:
            seen_content[normalized] = relative
        findings.extend(f"{relative.as_posix()}: {issue}" for issue in issues)
    return tuple(findings)

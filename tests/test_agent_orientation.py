import subprocess
from pathlib import Path

from ml4t_ecosystem.agent_orientation import (
    discover_agent_guides,
    nested_orientation_issues,
    orientation_issues,
)

ROOT_GUIDE = """# ml4t-data contributor guide

Market data acquisition and storage for quantitative research.

## Repository map

The `src/ml4t/data/` tree contains providers, storage adapters, and data managers. Tests live in
`tests/`, examples in `examples/`, and user documentation in `docs/`. Provider modules acquire and
normalize source data; storage modules persist validated tables; managers coordinate those layers.

## Public surface

```python
from ml4t.data import DataManager
```

Use public package exports before importing implementation modules. Keep credentials outside the
repository and use synthetic fixtures for offline tests.

## Verification

Run `uv run ruff check .`, `uv run ruff format --check .`, `uv run ty check`, and
`uv run pytest` after changes. Consult a nested guide when its directory has narrower constraints.
"""


def _git(path: Path, *arguments: str) -> None:
    subprocess.run(["git", "-C", str(path), *arguments], check=True, capture_output=True)


def test_root_orientation_rejects_private_volatile_and_incomplete_content() -> None:
    text = ROOT_GUIDE.replace("uv run ty check", "Codex uses @AGENTS.md for 42 tests")

    issues = orientation_issues(text, "ml4t.data")

    assert "references private or machine-local agent state" in issues
    assert "describes agent-tool mechanics instead of the library" in issues
    assert "contains a volatile file, line, module, or test count" in issues
    assert "does not name required quality commands: ty" in issues


def test_discovery_uses_tracked_guides_and_does_not_require_nested_files(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text(ROOT_GUIDE, encoding="utf-8")
    (tmp_path / "untracked").mkdir()
    (tmp_path / "untracked/AGENTS.md").write_text("placeholder\n", encoding="utf-8")
    _git(tmp_path, "init", "--initial-branch=main")
    _git(tmp_path, "add", "AGENTS.md")

    assert discover_agent_guides(tmp_path) == (Path("AGENTS.md"),)
    assert nested_orientation_issues(tmp_path) == ()


def test_nested_guides_are_directory_specific_and_stable(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text(ROOT_GUIDE, encoding="utf-8")
    nested = tmp_path / "src/ml4t/data/providers/AGENTS.md"
    nested.parent.mkdir(parents=True)
    nested.write_text(
        """# providers subsystem

Provider adapters normalize upstream responses behind the shared provider contract.

## Change rules

Keep imports credential-free and preserve the common schema. Use recorded or synthetic responses in
default tests. Live requests belong in the marked provider-contract lane. Reuse the shared retry and
rate-limit helpers instead of adding adapter-specific variants.
""",
        encoding="utf-8",
    )
    _git(tmp_path, "init", "--initial-branch=main")
    _git(tmp_path, "add", "AGENTS.md", "src/ml4t/data/providers/AGENTS.md")

    assert nested_orientation_issues(tmp_path) == ()

    nested.write_text(ROOT_GUIDE, encoding="utf-8")
    assert any("duplicates AGENTS.md" in finding for finding in nested_orientation_issues(tmp_path))

    nested.write_text(
        """# implementation notes

This directory has 42 files. Codex reads @AGENTS.md and ~/.workspace/private.md.

## Current status

The provider work is complete. Keep this file because discovery expects one in every directory.
""",
        encoding="utf-8",
    )

    findings = nested_orientation_issues(tmp_path)
    assert any("volatile" in finding for finding in findings)
    assert any("agent-tool mechanics" in finding for finding in findings)
    assert any("private or machine-local" in finding for finding in findings)
    assert any("does not identify its directory 'providers'" in finding for finding in findings)

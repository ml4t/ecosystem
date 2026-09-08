import subprocess
from pathlib import Path

from ml4t_ecosystem.config import load_config
from ml4t_ecosystem.models import Library
from ml4t_ecosystem.workspaces import CLAUDE_IMPORT, audit_workspace


def _git(path: Path, *arguments: str) -> None:
    subprocess.run(["git", "-C", str(path), *arguments], check=True, capture_output=True)


def _write(path: Path, content: str = "present\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _complete_workspace(tmp_path: Path) -> tuple[Path, Library]:
    config = load_config(Path("config/libraries.toml"))
    library = config.library("data")
    release = tmp_path / library.local_checkout
    assert library.development_workspace is not None
    sidecar = tmp_path / library.development_workspace
    release.mkdir()
    _write(
        release / "AGENTS.md",
        """# ml4t-data

Market data acquisition and storage for quantitative research.

## Structure

The `src/ml4t/data/` tree contains providers, storage adapters, and data managers. Tests live in
`tests/`, examples in `examples/`, and user documentation in `docs/`. Provider modules acquire and
normalize source data; storage modules persist validated tables; managers coordinate those layers.

## Public entry point

```python
from ml4t.data import DataManager
```

Use the public package exports before importing implementation modules. Run `uv run pytest`,
`uv run ruff check .`, and `uv run ty check` after changes. Consult the nested agent guides before
changing provider-specific behavior, because authentication and rate-limit constraints vary by
source. Keep credentials outside the repository and use synthetic fixtures in tests.
""",
    )
    for relative in ("AGENTS.md", ".workspace/memory/MEMORY_INDEX.md"):
        _write(sidecar / relative)
    _write(sidecar / "CLAUDE.md", CLAUDE_IMPORT)
    for relative in ("issues", ".workspace/work", ".workspace/transitions"):
        (sidecar / relative).mkdir(parents=True)

    remote = tmp_path / "remote.git"
    remote.mkdir()
    _git(remote, "init", "--bare", "--initial-branch=main")
    _git(sidecar, "init", "--initial-branch=main")
    _git(sidecar, "config", "user.name", "Test")
    _git(sidecar, "config", "user.email", "test@example.com")
    _git(sidecar, "add", ".")
    _git(sidecar, "commit", "-m", "initial")
    _git(sidecar, "remote", "add", "origin", str(remote))
    _git(sidecar, "push", "-u", "origin", "main")
    return tmp_path, library


def test_complete_workspace_passes(tmp_path: Path) -> None:
    root, library = _complete_workspace(tmp_path)

    report = audit_workspace(root, library)

    assert report.passed
    assert all(check.status == "pass" for check in report.checks)


def test_workspace_reports_missing_paths_and_invalid_import(tmp_path: Path) -> None:
    config = load_config(Path("config/libraries.toml"))
    library = config.library("data")
    release = tmp_path / library.local_checkout
    release.mkdir()
    _write(release / "AGENTS.md", "Placeholder\n")

    report = audit_workspace(tmp_path, library)
    failed = {check.code for check in report.checks if check.status == "fail"}

    assert "release.agent-orientation" in failed
    assert "sidecar.exists" in failed
    assert "sidecar.directory.issues" in failed
    assert "sidecar.file.workspace.memory.MEMORY_INDEX.md" in failed
    assert "sidecar.origin" in failed
    assert "sidecar.synchronized" in failed


def test_workspace_without_sidecar_checks_only_release_orientation(tmp_path: Path) -> None:
    config = load_config(Path("config/libraries.toml"))
    library = config.library("specs")
    release = tmp_path / library.local_checkout
    release.mkdir()
    _write(
        release / "AGENTS.md",
        """# ml4t-specs

Runtime-neutral contracts shared by ML4T libraries.

## Structure

The `src/ml4t/specs/` tree contains lifecycle, market-data, artifact, and execution contracts.
Tests in `tests/` verify serialization and validation behavior, while `docs/` explains public
semantics. Keep these contracts independent of any engine implementation so backtest and live
runtimes can consume the same values.

## Public entry point

```python
from ml4t.specs import FeedSpec, LifecycleContract
```

Run `uv run pytest`, `uv run ruff check src tests`, and `uv run ty check` after a contract change.
Treat field names and serialized values as compatibility-sensitive public API. Add migration
guidance when a compatible default cannot preserve existing payloads.
""",
    )

    report = audit_workspace(tmp_path, library)

    assert report.passed
    assert [check.code for check in report.checks] == [
        "release.exists",
        "release.agent-orientation",
        "sidecar.not-required",
    ]


def test_workspace_reports_dirty_or_unsynchronized_sidecar(tmp_path: Path) -> None:
    root, library = _complete_workspace(tmp_path)
    assert library.development_workspace is not None
    sidecar = root / library.development_workspace
    _write(sidecar / "untracked.txt")

    dirty = audit_workspace(root, library)
    clean_check = next(check for check in dirty.checks if check.code == "sidecar.clean")
    assert clean_check.status == "fail"

    (sidecar / "untracked.txt").unlink()
    _write(sidecar / "AGENTS.md", "changed\n")
    _git(sidecar, "add", "AGENTS.md")
    _git(sidecar, "commit", "-m", "ahead")
    ahead = audit_workspace(root, library)
    sync_check = next(check for check in ahead.checks if check.code == "sidecar.synchronized")
    assert sync_check.status == "fail"

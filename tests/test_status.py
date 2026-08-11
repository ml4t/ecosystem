from datetime import UTC, datetime
from pathlib import Path

import pytest

from ml4t_ecosystem.models import CheckResult, Library, LibraryReport
from ml4t_ecosystem.status import (
    atomic_write_many,
    render_json,
    render_markdown,
    write_current_status,
)


def report(*, passed: bool = True) -> LibraryReport:
    value = LibraryReport(
        library=Library(
            key="data",
            repository="data",
            distribution="ml4t-data",
            import_package="ml4t.data",
            docs_url="https://www.ml4trading.io/docs/data/",
            local_checkout="ml4t-data",
            development_workspace="ml4t-data-dev",
        ),
        observed_at=datetime(2026, 8, 11, tzinfo=UTC).isoformat(),
        source_commit="abc123",
        published_version="0.1.2",
    )
    value.checks.append(CheckResult("test", "pass" if passed else "fail", "result", "evidence"))
    return value


def test_render_status() -> None:
    json_text = render_json([report()])
    markdown = render_markdown([report(passed=False)])

    assert '"passed": true' in json_text
    assert "| data | 0.1.2 | abc123 | FAIL | test |" in markdown


def test_write_current_status(tmp_path: Path) -> None:
    write_current_status([report()], tmp_path)

    assert (tmp_path / "current.json").is_file()
    assert "Current qualification status" in (tmp_path / "current.md").read_text()


def test_atomic_write_requires_one_directory(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="share one directory"):
        atomic_write_many({tmp_path / "a/x": "x", tmp_path / "b/y": "y"})


def test_atomic_write_restores_replaced_files(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    import ml4t_ecosystem.status as status_module

    first = tmp_path / "first"
    second = tmp_path / "second"
    first.write_text("old first", encoding="utf-8")
    second.write_text("old second", encoding="utf-8")
    real_replace = status_module.os.replace
    calls = 0

    def fail_second(source: Path, destination: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("replacement failed")
        real_replace(source, destination)

    monkeypatch.setattr(status_module.os, "replace", fail_second)

    with pytest.raises(OSError, match="replacement failed"):
        atomic_write_many({first: "new first", second: "new second"})

    assert first.read_text(encoding="utf-8") == "old first"
    assert second.read_text(encoding="utf-8") == "old second"

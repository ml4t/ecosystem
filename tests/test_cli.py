import json
from pathlib import Path

import pytest

from ml4t_ecosystem.cli import main
from ml4t_ecosystem.models import CheckResult, Library, LibraryReport
from ml4t_ecosystem.monitor import MonitorFinding


def test_validate_config(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["validate-config"]) == 0
    assert "Validated 7 libraries" in capsys.readouterr().out


def test_snapshot_requires_current_status(tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="does not exist"):
        main(["snapshot", "--status-dir", str(tmp_path)])


def test_snapshot_validates_and_copies(tmp_path: Path) -> None:
    reports = [{"observed_at": "2026-08-11T00:00:00+00:00"} for _ in range(7)]
    (tmp_path / "current.json").write_text(
        json.dumps({"schema_version": 1, "reports": reports}), encoding="utf-8"
    )

    assert main(["snapshot", "--status-dir", str(tmp_path)]) == 0
    assert len(list((tmp_path / "snapshots").glob("*.json"))) == 1


def test_sync_templates_command(tmp_path: Path) -> None:
    assert main(["sync-templates", str(tmp_path), "--repository", "ml4t/data"]) == 0
    assert (tmp_path / ".github/ISSUE_TEMPLATE/bug.yml").is_file()


def sample_report(*, passed: bool) -> LibraryReport:
    report = LibraryReport(
        library=Library(
            "data",
            "data",
            "ml4t-data",
            "ml4t.data",
            "https://www.ml4trading.io/docs/data/",
            "ml4t-data",
            "ml4t-data-dev",
        ),
        observed_at="2026-08-11T00:00:00+00:00",
    )
    report.checks.append(CheckResult("check", "pass" if passed else "fail", "message"))
    return report


def test_collect_command(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    class Client:
        def __init__(self, *args, **kwargs):
            pass

        def close(self) -> None:
            pass

    monkeypatch.setattr("ml4t_ecosystem.cli.GitHubClient", Client)
    monkeypatch.setattr("ml4t_ecosystem.cli.PyPIClient", Client)
    monkeypatch.setattr(
        "ml4t_ecosystem.cli.audit_all", lambda config, github, pypi: [sample_report(passed=False)]
    )

    assert main(["collect", "--output", str(tmp_path)]) == 1
    assert main(["collect", "--output", str(tmp_path), "--allow-failures"]) == 0
    assert (tmp_path / "current.json").is_file()


def test_monitor_command(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    class Client:
        def __init__(self, *args, **kwargs):
            pass

        def close(self) -> None:
            pass

    finding = MonitorFinding("data", 1, "issue", "overdue", "message", "url")
    monkeypatch.setattr("ml4t_ecosystem.cli.GitHubClient", Client)
    monkeypatch.setattr("ml4t_ecosystem.cli.monitor_all", lambda config, github: [finding])
    output = tmp_path / "monitor.json"

    assert main(["monitor", "--output", str(output)]) == 1
    assert json.loads(output.read_text(encoding="utf-8"))["findings"][0]["library"] == "data"


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"schema_version": 1, "reports": []},
        {
            "schema_version": 1,
            "reports": [
                {"observed_at": "one"},
                {"observed_at": "two"},
                *[{"observed_at": "one"} for _ in range(5)],
            ],
        },
    ],
)
def test_snapshot_rejects_invalid_current_status(
    tmp_path: Path, payload: dict[str, object]
) -> None:
    (tmp_path / "current.json").write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(SystemExit):
        main(["snapshot", "--status-dir", str(tmp_path)])


def test_sync_labels_command(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(
        "ml4t_ecosystem.cli.sync_labels",
        lambda repository, labels: calls.append(repository),
    )

    assert main(["sync-labels", "ml4t/data"]) == 0
    assert calls == ["ml4t/data"]

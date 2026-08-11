from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ml4t_ecosystem.clients import EvidenceError
from ml4t_ecosystem.config import load_config
from ml4t_ecosystem.monitor import business_days_between, monitor_all, monitor_library


class FakeGitHub:
    def __init__(self, items: list[dict[str, Any]], comments: list[dict[str, Any]] | None = None):
        self.items = items
        self.comments = comments or []

    def open_issues(self, owner: str, repository: str) -> list[dict[str, Any]]:
        return self.items

    def issue_comments(self, owner: str, repository: str, number: int) -> list[dict[str, Any]]:
        return self.comments

    def pull_reviews(self, owner: str, repository: str, number: int) -> list[dict[str, Any]]:
        return []


class FailingGitHub(FakeGitHub):
    def open_issues(self, owner: str, repository: str) -> list[dict[str, Any]]:
        raise EvidenceError("unavailable")


class FailingCommentsGitHub(FakeGitHub):
    def issue_comments(self, owner: str, repository: str, number: int) -> list[dict[str, Any]]:
        raise EvidenceError("comments unavailable")


def item(*, labels: list[str], body: str = "", pull: bool = False) -> dict[str, Any]:
    value: dict[str, Any] = {
        "number": 7,
        "created_at": "2026-08-03T12:00:00Z",
        "html_url": "https://github.com/ml4t/data/issues/7",
        "body": body,
        "labels": [{"name": label} for label in labels],
    }
    if pull:
        value["pull_request"] = {}
    return value


def test_business_days_between_excludes_weekend() -> None:
    assert business_days_between(datetime(2026, 8, 7).date(), datetime(2026, 8, 10).date()) == 1


def test_monitor_reports_classification_and_response_failures() -> None:
    config = load_config(Path("config/libraries.toml"))
    findings = monitor_library(
        config,
        config.library("data"),
        FakeGitHub([item(labels=[])]),  # type: ignore[arg-type]
        now=datetime(2026, 8, 11, 12, tzinfo=UTC),
    )

    assert {finding.code for finding in findings} == {
        "monitor.classification-overdue",
        "monitor.response-overdue",
    }


def test_maintainer_response_satisfies_response_target() -> None:
    config = load_config(Path("config/libraries.toml"))
    labels = [
        "type: bug",
        "priority: normal",
        "status: accepted",
        "compatibility: affected",
    ]
    findings = monitor_library(
        config,
        config.library("data"),
        FakeGitHub([item(labels=labels)], [{"author_association": "MEMBER"}]),  # type: ignore[arg-type]
        now=datetime(2026, 8, 11, 12, tzinfo=UTC),
    )

    assert findings == []


def test_dated_pending_review_satisfies_response_target() -> None:
    config = load_config(Path("config/libraries.toml"))
    labels = [
        "type: bug",
        "priority: normal",
        "status: pending-review",
        "compatibility: affected",
    ]
    findings = monitor_library(
        config,
        config.library("data"),
        FakeGitHub([item(labels=labels, body="Next review: 2026-08-15")]),  # type: ignore[arg-type]
        now=datetime(2026, 8, 11, 12, tzinfo=UTC),
    )

    assert findings == []


def test_monitor_all_preserves_evidence_failure() -> None:
    config = load_config(Path("config/libraries.toml"))
    findings = monitor_all(config, FailingGitHub([]))  # type: ignore[arg-type]

    assert len(findings) == 7
    assert {finding.code for finding in findings} == {"monitor.evidence"}


def test_monitor_reports_missing_timestamp() -> None:
    config = load_config(Path("config/libraries.toml"))
    findings = monitor_library(
        config,
        config.library("data"),
        FakeGitHub([{"number": 3, "html_url": "url"}]),
    )

    assert [finding.code for finding in findings] == ["monitor.timestamp"]


def test_young_item_does_not_require_classification_or_response() -> None:
    config = load_config(Path("config/libraries.toml"))
    young = item(labels=[])
    young["created_at"] = "2026-08-11T11:30:00Z"

    findings = monitor_library(
        config,
        config.library("data"),
        FakeGitHub([young]),
        now=datetime(2026, 8, 11, 12, tzinfo=UTC),
    )

    assert findings == []


def test_pull_review_and_comment_evidence_paths() -> None:
    config = load_config(Path("config/libraries.toml"))
    labels = [
        "type: bug",
        "priority: normal",
        "status: accepted",
        "compatibility: affected",
    ]

    class ReviewedPullGitHub(FakeGitHub):
        def pull_reviews(self, owner: str, repository: str, number: int) -> list[dict[str, Any]]:
            return [{"author_association": "COLLABORATOR"}]

    findings = monitor_library(
        config,
        config.library("data"),
        ReviewedPullGitHub([item(labels=labels, pull=True)]),
        now=datetime(2026, 8, 11, 12, tzinfo=UTC),
    )
    assert findings == []

    failed = monitor_library(
        config,
        config.library("data"),
        FailingCommentsGitHub([item(labels=labels)]),
        now=datetime(2026, 8, 11, 12, tzinfo=UTC),
    )
    assert [finding.code for finding in failed] == ["monitor.evidence"]

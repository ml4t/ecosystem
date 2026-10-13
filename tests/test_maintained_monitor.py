import json
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest

from ml4t_ecosystem.cli import main
from ml4t_ecosystem.clients import EvidenceError, GitHubClient
from ml4t_ecosystem.config import load_config
from ml4t_ecosystem.maintenance import (
    MaintainedRepository,
    collect_queues,
    load_maintained_repositories,
)

CAPTURE = json.loads(Path("tests/fixtures/monitor-github.json").read_text())


def test_open_queue_does_not_drop_items_after_first_github_page() -> None:
    pages = CAPTURE["data"]["pages"]

    def handler(request: httpx.Request) -> httpx.Response:
        page = int(request.url.params.get("page", "1"))
        headers = {}
        if page == 1:
            headers["Link"] = (
                "<https://api.github.com/repositories/1089877520/issues"
                '?page=2&per_page=100>; rel="next"'
            )
        return httpx.Response(200, json=pages[page - 1], headers=headers)

    client = GitHubClient(transport=httpx.MockTransport(handler))
    try:
        items = client.open_issues("ml4t", "data")
    finally:
        client.close()
    assert [item["number"] for item in items] == [item["number"] for page in pages for item in page]


def test_monitor_cli_includes_reloaded_owner_without_expanding_qualification(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    requested = set()

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/issues"):
            requested.add(request.url.path.removeprefix("/repos/").removesuffix("/issues"))
        return httpx.Response(200, json=[])

    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    monkeypatch.setattr(
        "ml4t_ecosystem.cli.GitHubClient",
        lambda **kwargs: GitHubClient(transport=httpx.MockTransport(handler)),
    )
    assert main(["monitor", "--output", str(tmp_path / "monitor.json")]) == 0
    assert requested == {
        "ml4t/data",
        "ml4t/engineer",
        "ml4t/backtest",
        "ml4t/specs",
        "ml4t/live",
        "ml4t/diagnostic",
        "ml4t/models",
        "stefan-jansen/zipline-reloaded",
        "stefan-jansen/pyfolio-reloaded",
        "stefan-jansen/alphalens-reloaded",
        "stefan-jansen/empyrical-reloaded",
    }
    assert main(["validate-config"]) == 0
    assert "Validated 7 libraries" in capsys.readouterr().out


def replay(request: httpx.Request) -> httpx.Response:
    for name in ("data", "empyrical"):
        entry = CAPTURE[name]
        root = "/repos/" + entry["repository"]
        if request.url.path == root + "/issues":
            return httpx.Response(200, json=[item for page in entry["pages"] for item in page])
        for number, pull in entry["pulls"].items():
            if request.url.path == root + "/pulls/" + number:
                return httpx.Response(200, json=pull)
        if request.url.path.startswith(root) and request.url.path.endswith(
            ("/comments", "/reviews")
        ):
            return httpx.Response(200, json=[])
    return httpx.Response(404)


def collect(handler=replay):
    client = GitHubClient(transport=httpx.MockTransport(handler))
    try:
        return collect_queues(
            load_config(Path("config/libraries.toml")),
            (
                MaintainedRepository("data", "ml4t/data"),
                MaintainedRepository("empyrical-reloaded", "stefan-jansen/empyrical-reloaded"),
            ),
            client,
            now=datetime(2027, 1, 1, tzinfo=UTC),
        )
    finally:
        client.close()


def test_collector_preserves_real_repository_and_pr_revision_without_claiming_review() -> None:
    report = collect()
    assert report["complete"] is True
    assert len(report["repositories"]) == 2
    for queue, name in zip(report["repositories"], ("data", "empyrical"), strict=True):
        assert queue["repository"] == CAPTURE[name]["repository"]
        assert queue["observed_at"] == "2027-01-01T00:00:00+00:00"
        assert len(queue["items"]) == 2
        for item in queue["items"]:
            assert item["evidence_level"] == "metadata_only"
            assert item["inspected_revision"] is None
            if item["kind"] == "pull_request":
                assert (
                    item["head_revision"]
                    == CAPTURE[name]["pulls"][str(item["number"])]["head"]["sha"]
                )


@pytest.mark.parametrize("failure", ["repository", "pull", "comments", "transport", "json"])
def test_partial_api_failure_never_becomes_a_clean_complete_queue(failure: str) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if "/repos/ml4t/data" in request.url.path:
            if failure == "transport":
                raise httpx.ReadTimeout("unavailable", request=request)
            if failure == "json":
                return httpx.Response(200, content="invalid JSON")
            if (
                (failure == "repository" and request.url.path.endswith("/issues"))
                or (failure == "pull" and "/pulls/" in request.url.path)
                or (failure == "comments" and request.url.path.endswith("/comments"))
            ):
                return httpx.Response(503)
        return replay(request)

    report = collect(handler)
    assert report["complete"] is False
    assert report["repositories"][0]["complete"] is False
    assert report["repositories"][0]["errors"]
    assert report["repositories"][1]["complete"] is True
    assert any(f["code"] == "monitor.evidence" for f in report["findings"])


def test_second_page_failure_does_not_publish_first_page_as_complete() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path in ("/repos/ml4t/data/issues", "/repositories/1089877520/issues"):
            if request.url.params.get("page") == "2":
                return httpx.Response(502)
            return httpx.Response(
                200,
                json=CAPTURE["data"]["pages"][0],
                headers={
                    "Link": (
                        '<https://api.github.com/repositories/1089877520/issues?page=2>; rel="next"'
                    )
                },
            )
        return replay(request)

    report = collect(handler)
    assert report["repositories"][0]["complete"] is False
    assert report["repositories"][0]["errors"]


@pytest.mark.parametrize("endpoint", ["comments", "reviews"])
def test_maintainer_response_on_later_page_is_not_reported_overdue(endpoint: str) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/" + endpoint):
            if request.url.params.get("page") == "2":
                return httpx.Response(200, json=[{"author_association": "OWNER"}])
            resource = "/".join(request.url.path.split("/")[4:])
            repository_id = 1089877520 if "/ml4t/data/" in request.url.path else 341662136
            return httpx.Response(
                200,
                json=[{"author_association": "NONE"}],
                headers={
                    "Link": (
                        f"<https://api.github.com/repositories/{repository_id}/{resource}"
                        '?page=2>; rel="next"'
                    )
                },
            )
        return replay(request)

    report = collect(handler)
    assert report["complete"] is True
    pull_number = int(next(iter(CAPTURE["data"]["pulls"])))
    assert not any(
        f["library"] == "data"
        and f["number"] == pull_number
        and f["code"] == "monitor.response-overdue"
        for f in report["findings"]
    )


@pytest.mark.parametrize(
    "defect",
    ["identity", "closed", "labels", "timestamp", "text", "duplicate", "revision", "pr_closed"],
)
def test_invalid_or_racing_github_record_remains_missing_evidence(defect: str) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        response = replay(request)
        if request.url.path == "/repos/ml4t/data/issues":
            records = deepcopy(response.json())
            if defect == "identity":
                records[0]["html_url"] = "https://github.com/wrong/repo/pull/80"
            if defect == "closed":
                records[0]["state"] = "closed"
            if defect == "labels":
                records[0]["labels"] = None
            if defect == "timestamp":
                records[0]["updated_at"] = None
            if defect == "text":
                records[0]["body"] = 123
            if defect == "duplicate":
                records.append(records[0])
            return httpx.Response(200, json=records)
        if request.url.path.startswith("/repos/ml4t/data/pulls/") and not request.url.path.endswith(
            "/reviews"
        ):
            pull = deepcopy(response.json())
            if defect == "revision":
                pull["head"] = None
            if defect == "pr_closed":
                pull["state"] = "closed"
            return httpx.Response(200, json=pull)
        return response

    assert collect(handler)["complete"] is False


@pytest.mark.parametrize(
    "next_url",
    [
        "https://example.com/stolen",
        "https://api.github.com/repositories/1089877520/pulls?page=2",
        "https://api.github.com/repos/ml4t/engineer/issues?page=2",
        "https://api.github.com/repos/ml4t/data/issues?per_page=100&state=open&sort=created",
    ],
)
def test_pagination_rejects_foreign_and_repeated_links(next_url: str) -> None:
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(str(request.url))
        assert request.url.host == "api.github.com"
        return httpx.Response(200, json=[], headers={"Link": f'<{next_url}>; rel="next"'})

    client = GitHubClient(token="test-token", transport=httpx.MockTransport(handler))
    try:
        with pytest.raises(EvidenceError, match="pagination link"):
            client.open_issues("ml4t", "data")
    finally:
        client.close()
    assert len(calls) <= 2


@pytest.mark.parametrize(
    "contents",
    [
        "schema_version=2\nrepositories=[]",
        'schema_version=1\n[[repositories]]\nkey="data"\nrepository="data"',
        'schema_version=1\n[[repositories]]\nkey="data"\nrepository="ml4t/data"\n[[repositories]]\nkey="data"\nrepository="ML4T/Data"',
    ],
)
def test_invalid_inventory_is_rejected_before_collecting(contents: str, tmp_path: Path) -> None:
    path = tmp_path / "inventory.toml"
    path.write_text(contents)
    with pytest.raises(ValueError):
        load_maintained_repositories(path)


def test_cli_evidence_failure_writes_failure_report_and_returns_two(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    monkeypatch.setattr(
        "ml4t_ecosystem.cli.GitHubClient",
        lambda **kwargs: GitHubClient(
            transport=httpx.MockTransport(lambda request: httpx.Response(503))
        ),
    )
    output = tmp_path / "monitor.json"
    assert main(["monitor", "--output", str(output)]) == 2
    report = json.loads(output.read_text())
    assert report["complete"] is False
    assert len(report["repositories"]) == 11
    assert all(queue["errors"] for queue in report["repositories"])

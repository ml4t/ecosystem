import base64
import json

import httpx
import pytest

from ml4t_ecosystem.clients import EvidenceError, GitHubClient, PyPIClient


def response(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    if path == "/repos/ml4t/data":
        return httpx.Response(200, json={"default_branch": "main"})
    if path == "/repos/ml4t/data/commits/main":
        return httpx.Response(200, json={"sha": "abc123"})
    if path.endswith("/contents/README.md"):
        encoded = base64.b64encode(b"hello\n").decode()
        return httpx.Response(200, json={"type": "file", "content": encoded})
    if "/contents/missing" in path:
        return httpx.Response(404, json={"message": "Not Found"})
    if path.endswith("/labels"):
        return httpx.Response(200, json=[{"name": "type: bug"}])
    if path.endswith("/private-vulnerability-reporting"):
        return httpx.Response(200, json={"enabled": True})
    if path.endswith("/issues"):
        return httpx.Response(200, json=[{"number": 1}])
    if path.endswith("/issues/1/comments"):
        return httpx.Response(200, json=[{"body": "reviewed"}])
    if path.endswith("/pulls/1/reviews"):
        return httpx.Response(200, json=[{"state": "APPROVED"}])
    if path == "/pypi/ml4t-data/json":
        return httpx.Response(200, json={"info": {"version": "0.1.2"}})
    return httpx.Response(500, content=json.dumps({"message": "unexpected"}))


def test_github_client_reads_evidence() -> None:
    client = GitHubClient(token="token", transport=httpx.MockTransport(response))
    try:
        assert client.repository("ml4t", "data")["default_branch"] == "main"
        assert client.branch_commit("ml4t", "data", "main") == "abc123"
        assert client.content("ml4t", "data", "README.md") == "hello\n"
        assert client.content("ml4t", "data", "missing") is None
        assert client.labels("ml4t", "data") == {"type: bug"}
        assert client.private_vulnerability_reporting("ml4t", "data") is True
        assert client.open_issues("ml4t", "data") == [{"number": 1}]
        assert client.issue_comments("ml4t", "data", 1) == [{"body": "reviewed"}]
        assert client.pull_reviews("ml4t", "data", 1) == [{"state": "APPROVED"}]
    finally:
        client.close()


def test_github_client_reports_source_error() -> None:
    client = GitHubClient(transport=httpx.MockTransport(response))
    try:
        with pytest.raises(EvidenceError, match="returned 500"):
            client.repository("ml4t", "unknown")
    finally:
        client.close()


def test_pypi_client_reads_info_and_reports_error() -> None:
    client = PyPIClient(transport=httpx.MockTransport(response))
    try:
        assert client.package("ml4t-data") == {"version": "0.1.2"}
        with pytest.raises(EvidenceError, match="returned 500"):
            client.package("missing")
    finally:
        client.close()


@pytest.mark.parametrize(
    ("status", "expected"),
    [(404, False), (403, None)],
)
def test_private_vulnerability_reporting_states(status: int, expected: bool | None) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status)

    client = GitHubClient(transport=httpx.MockTransport(handler))
    try:
        assert client.private_vulnerability_reporting("ml4t", "data") is expected
    finally:
        client.close()


def test_invalid_github_response_shapes() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path.endswith("/commits/main"):
            return httpx.Response(200, json={})
        if "/contents/directory" in path:
            return httpx.Response(200, json={"type": "dir"})
        if "/contents/encoded" in path:
            return httpx.Response(200, json={"type": "file"})
        if path.endswith("/labels"):
            return httpx.Response(200, json={})
        if path.endswith("/issues") or path.endswith("/comments") or path.endswith("/reviews"):
            return httpx.Response(200, json={})
        if path.endswith("/private-vulnerability-reporting"):
            return httpx.Response(500)
        return httpx.Response(200, json=[])

    client = GitHubClient(transport=httpx.MockTransport(handler))
    try:
        with pytest.raises(EvidenceError, match="no SHA"):
            client.branch_commit("ml4t", "data", "main")
        assert client.content("ml4t", "data", "directory") is None
        with pytest.raises(EvidenceError, match="no encoded content"):
            client.content("ml4t", "data", "encoded")
        with pytest.raises(EvidenceError, match="labels response"):
            client.labels("ml4t", "data")
        with pytest.raises(EvidenceError, match="issues response"):
            client.open_issues("ml4t", "data")
        with pytest.raises(EvidenceError, match="comments response"):
            client.issue_comments("ml4t", "data", 1)
        with pytest.raises(EvidenceError, match="reviews response"):
            client.pull_reviews("ml4t", "data", 1)
        with pytest.raises(EvidenceError, match="private vulnerability"):
            client.private_vulnerability_reporting("ml4t", "data")
    finally:
        client.close()


def test_private_vulnerability_reporting_requires_enabled_state() -> None:
    client = GitHubClient(
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json={}))
    )
    try:
        with pytest.raises(EvidenceError, match="no enabled state"):
            client.private_vulnerability_reporting("ml4t", "data")
    finally:
        client.close()


def test_invalid_pypi_response_shape() -> None:
    client = PyPIClient(transport=httpx.MockTransport(lambda request: httpx.Response(200, json={})))
    try:
        with pytest.raises(EvidenceError, match="no info object"):
            client.package("ml4t-data")
    finally:
        client.close()

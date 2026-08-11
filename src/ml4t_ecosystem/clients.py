"""HTTP clients for GitHub and PyPI evidence."""

from __future__ import annotations

import base64
from typing import Any, Protocol

import httpx


class EvidenceError(RuntimeError):
    """Raised when an evidence source cannot return a valid response."""


class AuditGitHub(Protocol):
    """GitHub evidence required by repository qualification."""

    def repository(self, owner: str, repository: str) -> dict[str, Any]: ...

    def branch_commit(self, owner: str, repository: str, branch: str) -> str: ...

    def content(self, owner: str, repository: str, path: str) -> str | None: ...

    def labels(self, owner: str, repository: str) -> set[str]: ...

    def private_vulnerability_reporting(self, owner: str, repository: str) -> bool | None: ...


class PyPIEvidence(Protocol):
    """PyPI evidence required by package qualification."""

    def package(self, distribution: str) -> dict[str, Any]: ...


class MonitorGitHub(Protocol):
    """GitHub evidence required by issue and pull-request monitoring."""

    def open_issues(self, owner: str, repository: str) -> list[dict[str, Any]]: ...

    def issue_comments(self, owner: str, repository: str, number: int) -> list[dict[str, Any]]: ...

    def pull_reviews(self, owner: str, repository: str, number: int) -> list[dict[str, Any]]: ...


class GitHubClient:
    """Minimal read client for GitHub repository evidence."""

    def __init__(self, token: str | None = None, transport: httpx.BaseTransport | None = None):
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "ml4t-ecosystem-audit",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._client = httpx.Client(
            base_url="https://api.github.com",
            headers=headers,
            timeout=30.0,
            transport=transport,
        )

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def get_json(self, path: str, *, params: dict[str, str] | None = None) -> Any:
        """Return JSON from a GitHub endpoint."""
        response = self._client.get(path, params=params)
        if response.status_code >= 400:
            raise EvidenceError(f"GitHub {path} returned {response.status_code}")
        return response.json()

    def get_optional_json(self, path: str) -> Any | None:
        """Return JSON or None for a missing endpoint."""
        response = self._client.get(path)
        if response.status_code == 404:
            return None
        if response.status_code >= 400:
            raise EvidenceError(f"GitHub {path} returned {response.status_code}")
        if response.status_code == 204 or not response.content:
            return {}
        return response.json()

    def repository(self, owner: str, repository: str) -> dict[str, Any]:
        """Return repository metadata."""
        result = self.get_json(f"/repos/{owner}/{repository}")
        if not isinstance(result, dict):
            raise EvidenceError("GitHub repository response was not an object")
        return result

    def branch_commit(self, owner: str, repository: str, branch: str) -> str:
        """Return the commit SHA at a branch head."""
        result = self.get_json(f"/repos/{owner}/{repository}/commits/{branch}")
        if not isinstance(result, dict) or not isinstance(result.get("sha"), str):
            raise EvidenceError("GitHub commit response has no SHA")
        return result["sha"]

    def content(self, owner: str, repository: str, path: str) -> str | None:
        """Return decoded default-branch file content or None when absent."""
        result = self.get_optional_json(f"/repos/{owner}/{repository}/contents/{path}")
        if result is None:
            return None
        if not isinstance(result, dict) or result.get("type") != "file":
            return None
        encoded = result.get("content")
        if not isinstance(encoded, str):
            raise EvidenceError(f"GitHub content response for {path} has no encoded content")
        return base64.b64decode(encoded).decode("utf-8")

    def labels(self, owner: str, repository: str) -> set[str]:
        """Return all repository label names."""
        result = self.get_json(f"/repos/{owner}/{repository}/labels", params={"per_page": "100"})
        if not isinstance(result, list):
            raise EvidenceError("GitHub labels response was not a list")
        return {str(item["name"]) for item in result if isinstance(item, dict) and "name" in item}

    def private_vulnerability_reporting(self, owner: str, repository: str) -> bool | None:
        """Return private vulnerability reporting state when visible to the caller."""
        response = self._client.get(f"/repos/{owner}/{repository}/private-vulnerability-reporting")
        if response.status_code == 200:
            result = response.json()
            if not isinstance(result, dict) or not isinstance(result.get("enabled"), bool):
                raise EvidenceError("GitHub private vulnerability response has no enabled state")
            return result["enabled"]
        if response.status_code == 404:
            return False
        if response.status_code in {401, 403}:
            return None
        raise EvidenceError(
            f"GitHub private vulnerability endpoint returned {response.status_code}"
        )

    def open_issues(self, owner: str, repository: str) -> list[dict[str, Any]]:
        """Return open issues and pull requests from the issues endpoint."""
        result = self.get_json(
            f"/repos/{owner}/{repository}/issues",
            params={"state": "open", "per_page": "100", "sort": "created"},
        )
        if not isinstance(result, list):
            raise EvidenceError("GitHub issues response was not a list")
        return [item for item in result if isinstance(item, dict)]

    def issue_comments(self, owner: str, repository: str, number: int) -> list[dict[str, Any]]:
        """Return comments for an issue or pull request."""
        result = self.get_json(
            f"/repos/{owner}/{repository}/issues/{number}/comments",
            params={"per_page": "100"},
        )
        if not isinstance(result, list):
            raise EvidenceError("GitHub comments response was not a list")
        return [item for item in result if isinstance(item, dict)]

    def pull_reviews(self, owner: str, repository: str, number: int) -> list[dict[str, Any]]:
        """Return reviews for a pull request."""
        result = self.get_json(
            f"/repos/{owner}/{repository}/pulls/{number}/reviews",
            params={"per_page": "100"},
        )
        if not isinstance(result, list):
            raise EvidenceError("GitHub pull reviews response was not a list")
        return [item for item in result if isinstance(item, dict)]


class PyPIClient:
    """Minimal read client for published package metadata."""

    def __init__(self, transport: httpx.BaseTransport | None = None):
        self._client = httpx.Client(
            base_url="https://pypi.org",
            headers={"User-Agent": "ml4t-ecosystem-audit"},
            timeout=30.0,
            transport=transport,
        )

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def package(self, distribution: str) -> dict[str, Any]:
        """Return the PyPI info object for a distribution."""
        response = self._client.get(f"/pypi/{distribution}/json")
        if response.status_code >= 400:
            raise EvidenceError(f"PyPI {distribution} returned {response.status_code}")
        result = response.json()
        if not isinstance(result, dict) or not isinstance(result.get("info"), dict):
            raise EvidenceError(f"PyPI {distribution} response has no info object")
        return result["info"]

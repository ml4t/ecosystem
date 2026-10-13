"""Collect complete, revision-aware queues independently of package qualification."""

from __future__ import annotations

import hashlib
import re
import tomllib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ml4t_ecosystem.clients import EvidenceError, QueueGitHub
from ml4t_ecosystem.models import EcosystemConfig
from ml4t_ecosystem.monitor import monitor_items


@dataclass(frozen=True)
class MaintainedRepository:
    key: str
    repository: str


def load_maintained_repositories(path: Path) -> tuple[MaintainedRepository, ...]:
    """Validate full GitHub identities without changing stable qualification scope."""
    with path.open("rb") as stream:
        raw = tomllib.load(stream)
    rows = raw.get("repositories")
    if raw.get("schema_version") != 1 or not isinstance(rows, list) or not rows:
        raise ValueError("maintained inventory needs schema_version 1 and repositories")
    result = []
    for row in rows:
        if (
            not isinstance(row, dict)
            or not isinstance(row.get("key"), str)
            or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", row["key"])
            or not isinstance(row.get("repository"), str)
            or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", row["repository"])
        ):
            raise ValueError("maintained repository requires a key and owner/name identity")
        result.append(MaintainedRepository(row["key"], row["repository"]))
    if len({r.key for r in result}) != len(result) or len(
        {r.repository.casefold() for r in result}
    ) != len(result):
        raise ValueError("maintained repository keys and identities must be unique")
    return tuple(result)


def _queue_item(item: dict[str, Any], repository: str) -> dict[str, Any]:
    number = item.get("number")
    kind = "pull_request" if "pull_request" in item else "issue"
    suffix = "pull" if kind == "pull_request" else "issues"
    url = f"https://github.com/{repository}/{suffix}/{number}"
    if type(number) is not int or number <= 0 or item.get("html_url") != url:
        raise EvidenceError(f"Invalid issue identity in {repository}")
    if item.get("state") != "open":
        raise EvidenceError(f"Non-open item returned by open queue: {url}")
    labels = item.get("labels")
    if not isinstance(labels, list) or any(
        not isinstance(label, dict) or not isinstance(label.get("name"), str) for label in labels
    ):
        raise EvidenceError(f"Invalid labels: {url}")
    for field in ("created_at", "updated_at"):
        value = item.get(field)
        try:
            if not isinstance(value, str):
                raise ValueError("timestamp is not text")
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                raise ValueError("timestamp lacks timezone")
        except (AttributeError, TypeError, ValueError) as error:
            raise EvidenceError(f"Invalid {field}: {url}") from error
    body = item.get("body") or ""
    if not isinstance(body, str) or not isinstance(item.get("title"), str):
        raise EvidenceError(f"Invalid issue text: {url}")
    return {
        "number": number,
        "kind": kind,
        "title": item.get("title", ""),
        "url": url,
        "state": "open",
        "created_at": item["created_at"],
        "updated_at": item["updated_at"],
        "labels": sorted(label["name"] for label in labels),
        "body_sha256": hashlib.sha256(body.encode()).hexdigest(),
        "evidence_level": "metadata_only",
        "inspected_revision": None,
    }


def collect_queues(
    config: EcosystemConfig,
    repositories: tuple[MaintainedRepository, ...],
    github: QueueGitHub,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Collect every queue, retaining partial failures as missing evidence."""
    observed = now or datetime.now(UTC)
    if not repositories:
        raise ValueError("No maintained repositories configured")
    queues = []
    findings = []
    for entry in repositories:
        owner, repository = entry.repository.split("/")
        queue: dict[str, Any] = {
            "library": entry.key,
            "repository": entry.repository,
            "observed_at": observed.isoformat(),
            "complete": False,
            "evidence_level": "metadata_only",
            "items": [],
            "errors": [],
        }
        queues.append(queue)
        try:
            raw_items = github.open_issues(owner, repository)
            seen = set()
            for raw in raw_items:
                item = _queue_item(raw, entry.repository)
                if item["number"] in seen:
                    raise EvidenceError(f"Duplicate queue item: {item['url']}")
                seen.add(item["number"])
                queue["items"].append(item)
                if item["kind"] == "pull_request":
                    try:
                        pull = github.pull_request(owner, repository, item["number"])
                        if pull.get("number") != item["number"] or pull.get("state") != "open":
                            raise EvidenceError(f"PR changed during collection: {item['url']}")
                        for side in ("head", "base"):
                            revision = pull.get(side)
                            sha = revision.get("sha") if isinstance(revision, dict) else None
                            if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
                                raise EvidenceError(f"Missing PR {side} revision: {item['url']}")
                            item[side + "_revision"] = sha
                        item["draft"] = pull.get("draft")
                        item["mergeable_state"] = pull.get("mergeable_state")
                    except EvidenceError as error:
                        item["evidence_error"] = str(error)
                        queue["errors"].append(str(error))
            results = monitor_items(
                config, entry.key, owner, repository, github, raw_items, observed
            )
            findings.extend(result.to_dict() for result in results)
            queue["errors"].extend(
                result.message for result in results if result.code.startswith("monitor.evidence")
            )
            queue["complete"] = not queue["errors"]
        except EvidenceError as error:
            queue["errors"].append(str(error))
        for message in queue["errors"]:
            if any(f["library"] == entry.key and f["message"] == message for f in findings):
                continue
            findings.append(
                {
                    "library": entry.key,
                    "number": 0,
                    "kind": "repository",
                    "code": "monitor.evidence",
                    "message": message,
                    "url": f"https://github.com/{entry.repository}",
                }
            )
    return {
        "schema_version": 2,
        "observed_at": observed.isoformat(),
        "complete": all(queue["complete"] for queue in queues),
        "repositories": queues,
        "findings": findings,
    }

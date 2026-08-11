"""Read-only issue and pull-request response monitoring."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Any

from ml4t_ecosystem.clients import EvidenceError, MonitorGitHub
from ml4t_ecosystem.models import EcosystemConfig, Library

MAINTAINER_ASSOCIATIONS = {"OWNER", "MEMBER", "COLLABORATOR"}
REQUIRED_LABEL_PREFIXES = ("type: ", "priority: ", "status: ", "compatibility: ")


@dataclass(frozen=True)
class MonitorFinding:
    """One issue or pull-request service-level finding."""

    library: str
    number: int
    kind: str
    code: str
    message: str
    url: str

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-compatible representation."""
        return asdict(self)


def _parse_timestamp(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError("missing GitHub timestamp")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def business_days_between(start: date, end: date) -> int:
    """Count weekdays strictly after start through end."""
    if end <= start:
        return 0
    days = 0
    current = start + timedelta(days=1)
    while current <= end:
        if current.weekday() < 5:
            days += 1
        current += timedelta(days=1)
    return days


def _label_names(item: dict[str, Any]) -> set[str]:
    raw = item.get("labels")
    if not isinstance(raw, list):
        return set()
    return {
        str(label["name"])
        for label in raw
        if isinstance(label, dict) and isinstance(label.get("name"), str)
    }


def _classified(labels: set[str]) -> bool:
    return all(
        any(label.startswith(prefix) for label in labels) for prefix in REQUIRED_LABEL_PREFIXES
    )


def _maintainer_response(entries: list[dict[str, Any]], maintainer_logins: tuple[str, ...]) -> bool:
    configured = {login.casefold() for login in maintainer_logins}
    for entry in entries:
        if entry.get("author_association") in MAINTAINER_ASSOCIATIONS:
            return True
        user = entry.get("user")
        if not isinstance(user, dict):
            continue
        login = user.get("login")
        if isinstance(login, str) and login.casefold() in configured:
            return True
    return False


def _pending_review_has_date(item: dict[str, Any], comments: list[dict[str, Any]]) -> bool:
    text_values = [item.get("body"), *(comment.get("body") for comment in comments)]
    return any(
        isinstance(value, str)
        and "next review" in value.lower()
        and any(character.isdigit() for character in value)
        for value in text_values
    )


def monitor_library(
    config: EcosystemConfig,
    library: Library,
    github: MonitorGitHub,
    *,
    now: datetime | None = None,
) -> list[MonitorFinding]:
    """Return current response-target findings for a library."""
    observed = now or datetime.now(UTC)
    findings: list[MonitorFinding] = []
    try:
        items = github.open_issues(config.owner, library.repository)
    except EvidenceError as error:
        return [
            MonitorFinding(
                library=library.key,
                number=0,
                kind="repository",
                code="monitor.evidence",
                message=str(error),
                url=f"https://github.com/{config.owner}/{library.repository}",
            )
        ]

    for item in items:
        number = item.get("number")
        if not isinstance(number, int):
            continue
        is_pull = "pull_request" in item
        kind = "pull_request" if is_pull else "issue"
        url = str(item.get("html_url") or "")
        try:
            created = _parse_timestamp(item.get("created_at"))
        except ValueError:
            findings.append(
                MonitorFinding(
                    library.key, number, kind, "monitor.timestamp", "Missing creation time", url
                )
            )
            continue
        age_minutes = (observed - created).total_seconds() / 60
        labels = _label_names(item)
        if age_minutes > config.policy.classification_target_minutes and not _classified(labels):
            findings.append(
                MonitorFinding(
                    library.key,
                    number,
                    kind,
                    "monitor.classification-overdue",
                    "Item lacks a required type, priority, status, or compatibility label",
                    url,
                )
            )

        elapsed_business_days = business_days_between(created.date(), observed.date())
        if elapsed_business_days <= config.policy.response_target_business_days:
            continue
        try:
            comments = github.issue_comments(config.owner, library.repository, number)
            responses = list(comments)
            if is_pull:
                responses.extend(github.pull_reviews(config.owner, library.repository, number))
        except EvidenceError as error:
            findings.append(
                MonitorFinding(library.key, number, kind, "monitor.evidence", str(error), url)
            )
            continue
        responded = _maintainer_response(responses, config.policy.maintainer_logins)
        pending = "status: pending-review" in labels and _pending_review_has_date(item, comments)
        if not responded and not pending:
            findings.append(
                MonitorFinding(
                    library.key,
                    number,
                    kind,
                    "monitor.response-overdue",
                    (
                        "No maintainer response or dated pending-review notice within two "
                        "business days"
                    ),
                    url,
                )
            )
    return findings


def monitor_all(
    config: EcosystemConfig,
    github: MonitorGitHub,
    *,
    now: datetime | None = None,
) -> list[MonitorFinding]:
    """Monitor every configured library."""
    observed = now or datetime.now(UTC)
    findings: list[MonitorFinding] = []
    for library in config.libraries:
        findings.extend(monitor_library(config, library, github, now=observed))
    return findings

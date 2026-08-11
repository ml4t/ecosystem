"""Command-line interface for ecosystem qualification and coordination."""

from __future__ import annotations

import argparse
import json
import os
import shutil
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

from ml4t_ecosystem.audit import audit_all
from ml4t_ecosystem.clients import GitHubClient, PyPIClient
from ml4t_ecosystem.config import load_config
from ml4t_ecosystem.labels import load_labels, sync_labels
from ml4t_ecosystem.monitor import monitor_all
from ml4t_ecosystem.status import write_current_status
from ml4t_ecosystem.templates import sync_templates

ROOT = Path(__file__).resolve().parents[2]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ml4t-ecosystem")
    parser.add_argument(
        "--config", type=Path, default=ROOT / "config/libraries.toml", help="inventory TOML"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("validate-config", help="validate ecosystem configuration")

    collect = subparsers.add_parser("collect", help="collect PyPI and GitHub qualification status")
    collect.add_argument("--output", type=Path, default=ROOT / "status")
    collect.add_argument("--allow-failures", action="store_true")

    monitor = subparsers.add_parser("monitor", help="check issue and pull-request response targets")
    monitor.add_argument("--output", type=Path)

    snapshot = subparsers.add_parser("snapshot", help="retain validated current status")
    snapshot.add_argument("--status-dir", type=Path, default=ROOT / "status")

    templates = subparsers.add_parser("sync-templates", help="copy canonical collaboration files")
    templates.add_argument("target", type=Path)
    templates.add_argument("--repository", required=True)

    labels = subparsers.add_parser("sync-labels", help="create or update shared GitHub labels")
    labels.add_argument("repository")
    labels.add_argument("--labels", type=Path, default=ROOT / "config/labels.toml")
    return parser


def _collect(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    github = GitHubClient(token=os.getenv("GITHUB_TOKEN"))
    pypi = PyPIClient()
    try:
        reports = audit_all(config, github, pypi)
    finally:
        github.close()
        pypi.close()
    write_current_status(reports, args.output)
    failures = sum(not report.passed for report in reports)
    print(f"Collected {len(reports)} libraries; {failures} failed qualification")
    return 0 if failures == 0 or args.allow_failures else 1


def _monitor(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN is required for accurate maintainer-response monitoring")
    github = GitHubClient(token=token)
    try:
        findings = monitor_all(config, github)
    finally:
        github.close()
    payload = (
        json.dumps(
            {"schema_version": 1, "findings": [finding.to_dict() for finding in findings]},
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 1 if findings else 0


def _snapshot(args: argparse.Namespace) -> int:
    current = args.status_dir / "current.json"
    if not current.is_file():
        raise SystemExit("status/current.json does not exist; run collect first")
    payload = json.loads(current.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise SystemExit("current status has an unsupported schema")
    reports = payload.get("reports")
    if not isinstance(reports, list) or len(reports) != 7:
        raise SystemExit("current status must contain seven reports")
    observed_values = {report.get("observed_at") for report in reports if isinstance(report, dict)}
    if len(observed_values) != 1:
        raise SystemExit("current status reports do not share one observation time")
    timestamp = datetime.now(UTC).strftime("%Y-%m-%dT%H%M%SZ")
    destination = args.status_dir / "snapshots" / f"{timestamp}.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise SystemExit(f"snapshot already exists: {destination}")
    shutil.copy2(current, destination)
    print(destination)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Run the ecosystem command line."""
    args = _parser().parse_args(argv)
    if args.command == "validate-config":
        config = load_config(args.config)
        print(f"Validated {len(config.libraries)} libraries")
        return 0
    if args.command == "collect":
        return _collect(args)
    if args.command == "monitor":
        return _monitor(args)
    if args.command == "snapshot":
        return _snapshot(args)
    if args.command == "sync-templates":
        sync_templates(ROOT, args.target, args.repository)
        return 0
    if args.command == "sync-labels":
        sync_labels(args.repository, load_labels(args.labels))
        return 0
    raise AssertionError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())

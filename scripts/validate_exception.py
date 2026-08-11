"""Validate one qualification exception for a reusable workflow caller."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path

from ml4t_ecosystem.config import load_config
from ml4t_ecosystem.exceptions import validate_exception


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--exception-id", required=True)
    parser.add_argument("--repository", required=True)
    return parser.parse_args()


def main() -> None:
    """Validate the configured exception and print its bounded scope."""
    args = parse_args()
    config = load_config(args.config)
    library = next(
        (
            item
            for item in config.libraries
            if f"{config.owner}/{item.repository}" == args.repository
        ),
        None,
    )
    if library is None:
        raise ValueError(f"repository {args.repository} is not a managed library")
    exception = validate_exception(
        config,
        exception_id=args.exception_id,
        library_key=library.key,
        repository=args.repository,
        on_date=datetime.now(UTC).date(),
    )
    print(
        f"Approved exception {exception.id} covers {library.key} through "
        f"{exception.expires_on.isoformat()}: {exception.issue}"
    )


if __name__ == "__main__":
    main()

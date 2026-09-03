from datetime import date
from pathlib import Path

import pytest

from ml4t_ecosystem.config import load_config
from ml4t_ecosystem.exceptions import validate_exception


def test_validate_exception_accepts_matching_repository() -> None:
    config = load_config(Path("config/libraries.toml"))

    exception = validate_exception(
        config,
        exception_id="python-315-polars",
        library_key="data",
        repository="ml4t/data",
        package_version="0.1.2",
        on_date=date(2026, 8, 11),
    )

    assert exception.id == "python-315-polars"


@pytest.mark.parametrize(
    ("library_key", "repository", "package_version", "on_date", "message"),
    [
        (
            "backtest",
            "ml4t/backtest",
            "0.1.2",
            date(2026, 8, 11),
            "does not cover library",
        ),
        (
            "data",
            "ml4t/engineer",
            "0.1.2",
            date(2026, 8, 11),
            "does not match repository",
        ),
        (
            "data",
            "ml4t/data",
            "0.1.4",
            date(2026, 8, 11),
            "does not cover version",
        ),
        ("data", "ml4t/data", "0.1.2", date(2026, 10, 1), "expired"),
    ],
)
def test_validate_exception_rejects_invalid_scope(
    library_key: str,
    repository: str,
    package_version: str,
    on_date: date,
    message: str,
) -> None:
    config = load_config(Path("config/libraries.toml"))

    with pytest.raises(ValueError, match=message):
        validate_exception(
            config,
            exception_id="python-315-polars",
            library_key=library_key,
            repository=repository,
            package_version=package_version,
            on_date=on_date,
        )

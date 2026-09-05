from datetime import date
from pathlib import Path

import pytest

from ml4t_ecosystem.config import load_config


def test_load_repository_config() -> None:
    config = load_config(Path("config/libraries.toml"))

    assert config.owner == "ml4t"
    assert len(config.libraries) == 7
    assert config.library("backtest").distribution == "ml4t-backtest"
    assert config.policy.stable_python == ("3.12", "3.13", "3.14")
    assert config.policy.maintainer_logins == ("stefan-jansen",)
    assert config.library("data").prerelease_exception == "python-315-polars"
    assert config.library("diagnostic").prerelease_exception == "python-315-scipy"
    assert config.library("backtest").prerelease_exception is None

    exception = config.exception("python-315-polars")
    assert exception.libraries == ("data", "engineer")
    assert exception.is_active(date(2026, 8, 11))
    assert exception.covers_version("0.1.2")
    assert not exception.covers_version("0.1.4")

    diagnostic_exception = config.exception("python-315-scipy")
    assert diagnostic_exception.libraries == ("diagnostic",)
    assert diagnostic_exception.covers_version("0.1.2")
    assert diagnostic_exception.covers_version("0.1.3")
    assert not diagnostic_exception.covers_version("0.1.4")


def test_unknown_library_raises() -> None:
    config = load_config(Path("config/libraries.toml"))

    with pytest.raises(KeyError, match="Unknown library"):
        config.library("unknown")

    with pytest.raises(KeyError, match="Unknown exception"):
        config.exception("unknown")


@pytest.mark.parametrize(
    ("replacement", "message"),
    [
        ("schema_version = 2", "schema_version"),
        ('owner = ""', "owner"),
        ("classification_target_minutes = 0", "classification_target_minutes"),
        ("response_target_business_days = 0", "response_target_business_days"),
        ('stable_python = "3.12"', "stable_python"),
        ("maintainer_logins = []", "maintainer_logins"),
    ],
)
def test_invalid_config_rejected(tmp_path: Path, replacement: str, message: str) -> None:
    content = Path("config/libraries.toml").read_text(encoding="utf-8")
    originals = {
        "schema_version = 2": "schema_version = 1",
        'owner = ""': 'owner = "ml4t"',
        "classification_target_minutes = 0": "classification_target_minutes = 60",
        "response_target_business_days = 0": "response_target_business_days = 2",
        'stable_python = "3.12"': 'stable_python = ["3.12", "3.13", "3.14"]',
        "maintainer_logins = []": 'maintainer_logins = ["stefan-jansen"]',
    }
    path = tmp_path / "invalid.toml"
    path.write_text(content.replace(originals[replacement], replacement), encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        load_config(path)


def test_duplicate_and_incomplete_inventory_rejected(tmp_path: Path) -> None:
    content = Path("config/libraries.toml").read_text(encoding="utf-8")
    path = tmp_path / "duplicate.toml"
    path.write_text(
        content.replace('key = "models"', 'key = "data"', 1),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="unique"):
        load_config(path)

    path.write_text(content.replace('key = "models"', 'key = "other"', 1), encoding="utf-8")
    with pytest.raises(ValueError, match="inventory mismatch"):
        load_config(path)

    path.write_text(
        content.replace('repository = "models"', 'repository = "data"', 1), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="repositories must be unique"):
        load_config(path)


@pytest.mark.parametrize(
    ("replacement", "message"),
    [
        ('id = "python-315-scipy"', "exception ids must be unique"),
        ('libraries = ["unknown"]', "unknown libraries"),
        ('prerelease_exception = "unknown"', "unknown prerelease exception"),
        ('expires_on = "2026-09-30"', "expires_on must be a TOML date"),
        ('affected_versions = "invalid"', "affected_versions"),
        ('criterion = "other"', "criterion"),
    ],
)
def test_invalid_exception_config_rejected(tmp_path: Path, replacement: str, message: str) -> None:
    content = Path("config/libraries.toml").read_text(encoding="utf-8")
    originals = {
        'id = "python-315-scipy"': 'id = "python-315-polars"',
        'libraries = ["unknown"]': 'libraries = ["data", "engineer"]',
        'prerelease_exception = "unknown"': 'prerelease_exception = "python-315-polars"',
        'expires_on = "2026-09-30"': "expires_on = 2026-09-30",
        'affected_versions = "invalid"': 'affected_versions = ">=0.1.2,<0.1.4"',
        'criterion = "other"': 'criterion = "python-3.15-prerelease"',
    }
    path = tmp_path / "invalid-exception.toml"
    path.write_text(content.replace(originals[replacement], replacement, 1), encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        load_config(path)


@pytest.mark.parametrize(
    ("content", "message"),
    [
        ('schema_version = 1\nowner = "ml4t"\nlibraries = []\n', "policy must be a table"),
        (
            'schema_version = 1\nowner = "ml4t"\n[policy]\nminimum_python = "3.12"\n',
            "classification_target_minutes",
        ),
    ],
)
def test_missing_config_sections_rejected(tmp_path: Path, content: str, message: str) -> None:
    path = tmp_path / "missing.toml"
    path.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        load_config(path)

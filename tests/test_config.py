from pathlib import Path

import pytest

from ml4t_ecosystem.config import load_config


def test_load_repository_config() -> None:
    config = load_config(Path("config/libraries.toml"))

    assert config.owner == "ml4t"
    assert len(config.libraries) == 7
    assert config.library("backtest").distribution == "ml4t-backtest"
    assert config.policy.stable_python == ("3.12", "3.13", "3.14")


def test_unknown_library_raises() -> None:
    config = load_config(Path("config/libraries.toml"))

    with pytest.raises(KeyError, match="Unknown library"):
        config.library("unknown")


@pytest.mark.parametrize(
    ("replacement", "message"),
    [
        ("schema_version = 2", "schema_version"),
        ('owner = ""', "owner"),
        ("classification_target_minutes = 0", "classification_target_minutes"),
        ("response_target_business_days = 0", "response_target_business_days"),
        ('stable_python = "3.12"', "stable_python"),
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

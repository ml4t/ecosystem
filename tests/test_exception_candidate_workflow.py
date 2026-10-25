import os
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

from ml4t_ecosystem.config import load_config
from ml4t_ecosystem.exceptions import validate_exception

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("library", "version", "repository", "accepted", "message"),
    [
        ("data", "0.3.0", "ml4t/data", True, "covers data 0.3.0"),
        ("data", "0.3.1.dev3+g8ca0c3828", "ml4t/data", True, "covers data 0.3.1.dev3"),
        ("data", "0.3.99", "ml4t/data", True, "covers data 0.3.99"),
        ("data", "0.2.99", "ml4t/data", False, "does not cover version"),
        ("data", "0.4.0.dev1", "ml4t/data", False, "does not cover version"),
        ("data", "0.4.0", "ml4t/data", False, "does not cover version"),
        ("data", "0.2.0", "ml4t/engineer", False, "does not cover library"),
        ("data", "0.3.0", "ml4t/backtest", False, "does not cover library"),
        ("data", "0.3.0", "other/data", False, "not a managed library"),
        ("diagnostic", "0.1.9", "ml4t/diagnostic", True, "covers diagnostic 0.1.9"),
        ("diagnostic", "0.2.0.dev1", "ml4t/diagnostic", True, "covers diagnostic 0.2.0.dev1"),
        ("diagnostic", "0.2.0", "ml4t/diagnostic", True, "covers diagnostic 0.2.0"),
        ("diagnostic", "0.3.0.dev1", "ml4t/diagnostic", False, "does not cover version"),
        ("diagnostic", "0.3.0", "ml4t/diagnostic", False, "does not cover version"),
        ("diagnostic", "0.2.0", "ml4t/engineer", False, "does not cover library"),
    ],
)
def test_built_candidate_cannot_escape_current_exception_scopes(
    tmp_path: Path, library: str, version: str, repository: str, accepted: bool, message: str
) -> None:
    package = tmp_path / "candidate"
    module = package / "src" / "candidate"
    module.mkdir(parents=True)
    (module / "__init__.py").write_text("", encoding="utf-8")
    (package / "pyproject.toml").write_text(
        '[build-system]\nrequires = ["hatchling"]\nbuild-backend = "hatchling.build"\n'
        f'[project]\nname = "ml4t-{library}"\nversion = "{version}"\n'
        '[tool.hatch.build.targets.wheel]\npackages = ["src/candidate"]\n',
        encoding="utf-8",
    )
    config_path = ROOT / "config/libraries.toml"
    exception_id = load_config(config_path).library(library).prerelease_exception
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/validate_exception.py"),
            "--config",
            str(config_path),
            "--exception-id",
            str(exception_id),
            "--repository",
            repository,
            "--package-root",
            str(package),
        ],
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "TMPDIR": str(tmp_path)},
    )
    assert (result.returncode == 0) is accepted, result.stdout + result.stderr
    assert message in result.stdout + result.stderr


def test_diagnostic_qualification_deferral_cannot_continue_after_review_deadline() -> None:
    config = load_config(ROOT / "config/libraries.toml")
    exception_id = config.library("diagnostic").prerelease_exception
    assert exception_id is not None
    arguments = {
        "exception_id": exception_id,
        "library_key": "diagnostic",
        "repository": "ml4t/diagnostic",
        "package_version": "0.2.0",
    }
    validate_exception(config, **arguments, on_date=date(2026, 11, 24))
    with pytest.raises(ValueError, match="expired on 2026-11-24"):
        validate_exception(config, **arguments, on_date=date(2026, 11, 25))


def test_missing_dependency_evidence_cannot_authorize_a_new_data_release(tmp_path: Path) -> None:
    text = (ROOT / "config/libraries.toml").read_text(encoding="utf-8")
    evidence = "https://github.com/ml4t/data/issues/37#issuecomment-6374129753"
    text = text.replace(f'    "{evidence}",\n', "")
    text = text.replace('    "https://pypi.org/pypi/databento/0.88.0/json",\n', "")
    text = text.replace('    "https://pypi.org/pypi/databento-dbn/0.70.0/json",\n', "")
    broken = tmp_path / "missing-evidence.toml"
    broken.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError, match="evidence must be a non-empty string list"):
        load_config(broken)

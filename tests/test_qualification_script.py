from pathlib import Path
from runpy import run_path

import pytest


def test_prerelease_flags_only_apply_to_dependency_resolution() -> None:
    module = run_path(str(Path(__file__).parents[1] / "scripts" / "qualification.py"))

    assert module["dependency_prerelease_args"](True) == ["--prerelease", "allow"]
    assert "--prerelease" not in module["python_install_command"]("3.15")
    assert module["python_install_command"]("3.15.0rc1", preinstalled=True) is None
    assert "--prerelease" not in module["venv_command"]("3.15", Path("environment"))


def test_prerelease_sync_installs_only_core_and_test_dependencies() -> None:
    module = run_path(str(Path(__file__).parents[1] / "scripts" / "qualification.py"))

    assert module["sync_command"]("3.15", prerelease=True) == [
        "uv",
        "sync",
        "--python",
        "3.15",
        "--no-dev",
        "--group",
        "test",
        "--prerelease",
        "allow",
    ]
    assert module["sync_command"]("3.14", prerelease=False) == [
        "uv",
        "sync",
        "--python",
        "3.14",
        "--dev",
    ]


def test_prerelease_test_targets_are_explicit_and_validated() -> None:
    module = run_path(str(Path(__file__).parents[1] / "scripts" / "qualification.py"))

    assert module["test_targets"](prerelease=False, encoded='["missing"]') == ["tests"]
    assert module["test_targets"](
        prerelease=True,
        encoded='["tests/test_qualification_script.py"]',
    ) == ["tests/test_qualification_script.py"]
    with pytest.raises(ValueError, match="invalid prerelease test path"):
        module["test_targets"](prerelease=True, encoded='["../outside.py"]')
    assert module["uv_run_command"]("3.15", "pytest", "tests", "-q") == [
        "uv",
        "run",
        "--no-sync",
        "--python",
        "3.15",
        "pytest",
        "tests",
        "-q",
    ]

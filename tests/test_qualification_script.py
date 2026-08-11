from pathlib import Path
from runpy import run_path


def test_prerelease_flags_only_apply_to_dependency_resolution() -> None:
    module = run_path(str(Path(__file__).parents[1] / "scripts" / "qualification.py"))

    assert module["dependency_prerelease_args"](True) == ["--prerelease", "allow"]
    assert "--prerelease" not in module["python_install_command"]("3.15")
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

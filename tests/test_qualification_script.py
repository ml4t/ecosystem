from pathlib import Path
from runpy import run_path


def test_prerelease_flags_only_apply_to_dependency_resolution() -> None:
    module = run_path(str(Path(__file__).parents[1] / "scripts" / "qualification.py"))

    assert module["dependency_prerelease_args"](True) == ["--prerelease", "allow"]
    assert "--prerelease" not in module["python_install_command"]("3.15")
    assert "--prerelease" not in module["venv_command"]("3.15", Path("environment"))

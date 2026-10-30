import json
import shlex
import subprocess
from pathlib import Path
from runpy import run_path

import pytest
import yaml
from packaging.version import Version


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


@pytest.mark.parametrize("selection", ["setup", "qualification"])
def test_shared_python315_qualification_cannot_run_an_obsolete_release_candidate(
    selection: str, tmp_path: Path
) -> None:
    workflow = yaml.safe_load(
        (Path(__file__).parents[1] / ".github/workflows/qualify-library.yml").read_text()
    )
    steps = workflow["jobs"]["prerelease"]["steps"]
    if selection == "setup":
        setup = next(
            step for step in steps if step.get("uses", "").startswith("actions/setup-python@")
        )
        version = str(Version(setup["with"]["python-version"]))
    else:
        command = next(
            step["run"] for step in steps if step.get("name") == "Qualify Python 3.15 prerelease"
        )
        arguments = shlex.split(command)
        version = arguments[arguments.index("--python") + 1]
    result = subprocess.run(
        [
            "uv",
            "run",
            "--isolated",
            "--no-project",
            "--python",
            version,
            "python",
            "-I",
            "-c",
            "import json,sys; print(json.dumps(list(sys.version_info)))",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    actual = json.loads(result.stdout)
    assert actual[:2] == [3, 15], actual
    assert actual[3] == "final", actual

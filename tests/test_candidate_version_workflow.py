import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def vcs_candidate(tmp_path: Path) -> Path:
    root = tmp_path / "candidate"
    (root / "src/candidate").mkdir(parents=True)
    (root / "src/candidate/__init__.py").write_text("VALUE = 1\n")
    (root / "pyproject.toml").write_text(
        '[build-system]\nrequires = ["hatchling", "hatch-vcs"]\n'
        'build-backend = "hatchling.build"\n'
        '[project]\nname = "ml4t-live"\ndynamic = ["version"]\n'
        '[dependency-groups]\ndev = ["pytest", "ruff", "ty"]\n'
        '[tool.hatch.version]\nsource = "vcs"\n'
        '[tool.hatch.build.targets.wheel]\npackages = ["src/candidate"]\n'
    )
    for command in [
        ["git", "init", "-q", "--initial-branch", "main"],
        ["git", "config", "user.name", "Candidate fixture"],
        ["git", "config", "user.email", "candidate@example.invalid"],
        ["git", "add", "."],
        ["git", "commit", "-qm", "Published fixture"],
        ["git", "tag", "v0.1.3"],
    ]:
        subprocess.run(command, cwd=root, check=True, capture_output=True)
    (root / "src/candidate/__init__.py").write_text("VALUE = 2\n")
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "Next candidate"], cwd=root, check=True)
    return root


@pytest.mark.parametrize(
    ("version", "accepted", "message"),
    [
        (None, False, "does not cover version 0.1.4.dev"),
        ("0.2.0", True, "covers live 0.2.0"),
        ("0.3.0", False, "does not cover version 0.3.0"),
    ],
)
def test_exception_uses_built_vcs_candidate_instead_of_previous_release_line(
    vcs_candidate: Path, version: str | None, accepted: bool, message: str
) -> None:
    command = [
        sys.executable,
        str(ROOT / "scripts/validate_exception.py"),
        "--config",
        str(ROOT / "config/libraries.toml"),
        "--exception-id",
        "python-315-live-calendar-020",
        "--repository",
        "ml4t/live",
        "--package-root",
        str(vcs_candidate),
    ]
    if version:
        command.extend(["--candidate-version", version])
    environment = dict(os.environ)
    environment.pop("SETUPTOOLS_SCM_PRETEND_VERSION", None)
    result = subprocess.run(command, env=environment, capture_output=True, text=True, timeout=120)
    assert (result.returncode == 0) is accepted, result.stdout + result.stderr
    assert message in result.stdout + result.stderr


def test_exception_rejects_backend_that_ignores_requested_candidate_version(
    vcs_candidate: Path,
) -> None:
    project = vcs_candidate / "pyproject.toml"
    project.write_text(project.read_text().replace('dynamic = ["version"]', 'version = "0.1.3"'))
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/validate_exception.py"),
            "--config",
            str(ROOT / "config/libraries.toml"),
            "--exception-id",
            "python-315-live-calendar-020",
            "--repository",
            "ml4t/live",
            "--package-root",
            str(vcs_candidate),
            "--candidate-version",
            "0.2.0",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode != 0
    assert "built candidate version 0.1.3 does not match requested 0.2.0" in result.stderr


def test_full_qualification_builds_and_installs_explicit_candidate_identity(
    vcs_candidate: Path,
) -> None:
    (vcs_candidate / "tests").mkdir()
    (vcs_candidate / "tests/test_version.py").write_text(
        "from importlib.metadata import version\n\n\n"
        "def test_candidate_has_requested_version() -> None:\n"
        '    assert version("ml4t-live") == "0.2.0"\n'
    )
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/qualification.py"),
            "--python",
            "3.12",
            "--import-package",
            "candidate",
            "--candidate-version",
            "0.2.0",
        ],
        cwd=vcs_candidate,
        capture_output=True,
        text=True,
        timeout=240,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "1 passed" in result.stdout
    assert list((vcs_candidate / "dist").glob("ml4t_live-0.2.0-*.whl"))

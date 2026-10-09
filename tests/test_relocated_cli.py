import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def test_cli_finds_sibling_repositories_after_controller_relocation(tmp_path: Path) -> None:
    original = Path(__file__).resolve().parents[1]
    container = tmp_path / "libraries"
    controller = container / "ml4t-ecosystem"
    for directory in ("src", "config", ".github"):
        shutil.copytree(
            original / directory,
            controller / directory,
            ignore=shutil.ignore_patterns("__pycache__"),
        )
    (container / "ml4t-data").mkdir()
    environment = {**os.environ, "PYTHONPATH": str(controller / "src")}

    def invoke(*arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "ml4t_ecosystem.cli", *arguments],
            cwd=tmp_path,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

    configuration = invoke("validate-config")
    assert configuration.returncode == 0, configuration.stderr
    audit = invoke("audit-workspaces")
    assert audit.returncode == 1, audit.stderr
    data = json.loads(audit.stdout)["reports"][0]
    assert data["root"] == str(container)
    assert (
        next(check for check in data["checks"] if check["code"] == "release.exists")["status"]
        == "pass"
    )

    target = tmp_path / "contributor-checkout"
    templates = invoke("sync-templates", str(target), "--repository", "ml4t/data")
    assert templates.returncode == 0, templates.stderr
    assert (target / ".github/ISSUE_TEMPLATE/bug.yml").is_file()

import re
from pathlib import Path


def test_external_actions_are_pinned_to_commits() -> None:
    workflow_root = Path(__file__).parents[1] / ".github" / "workflows"
    references = [
        line.split("uses:", 1)[1].split("#", 1)[0].strip()
        for path in workflow_root.glob("*.yml")
        for line in path.read_text(encoding="utf-8").splitlines()
        if "uses:" in line and "uses: ./" not in line
    ]

    assert references
    assert all(re.search(r"@[0-9a-f]{40}$", reference) for reference in references), references


def test_shared_qualification_requires_prerelease_or_validated_exception() -> None:
    workflow = (
        Path(__file__).parents[1] / ".github" / "workflows" / "qualify-library.yml"
    ).read_text(encoding="utf-8")

    assert "prerelease-exception:" in workflow
    assert "if: ${{ inputs.prerelease-exception == '' }}" in workflow
    assert "if: ${{ inputs.prerelease-exception != '' }}" in workflow
    assert "scripts/validate_exception.py" in workflow
    assert "--repository ${{ github.repository }}" in workflow
    assert "--package-root candidate" in workflow

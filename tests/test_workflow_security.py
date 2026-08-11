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

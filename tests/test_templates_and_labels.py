from pathlib import Path

import pytest

from ml4t_ecosystem.labels import load_labels, sync_labels
from ml4t_ecosystem.templates import sync_templates


def test_load_labels() -> None:
    labels = load_labels(Path("config/labels.toml"))

    assert len(labels) >= 15
    assert len({label.name for label in labels}) == len(labels)


def test_invalid_label_color_rejected(tmp_path: Path) -> None:
    path = tmp_path / "labels.toml"
    path.write_text(
        'schema_version = 1\n[[labels]]\nname = "x"\ncolor = "bad"\ndescription = "x"\n',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="invalid label color"):
        load_labels(path)


@pytest.mark.parametrize(
    ("content", "message"),
    [
        ("schema_version = 2\n", "schema_version"),
        ("schema_version = 1\n", "labels must"),
        (
            'schema_version = 1\n[[labels]]\nname = "x"\ncolor = "ffffff"\n',
            "description",
        ),
        (
            'schema_version = 1\n[[labels]]\nname = "x"\ncolor = "ffffff"\n'
            'description = "x"\n[[labels]]\nname = "x"\ncolor = "ffffff"\n'
            'description = "x"\n',
            "unique",
        ),
    ],
)
def test_invalid_label_files_rejected(tmp_path: Path, content: str, message: str) -> None:
    path = tmp_path / "labels.toml"
    path.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        load_labels(path)


def test_sync_labels_uses_force(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []

    def fake_run(command: list[str], *, check: bool) -> None:
        assert check
        calls.append(command)

    monkeypatch.setattr("ml4t_ecosystem.labels.subprocess.run", fake_run)
    labels = load_labels(Path("config/labels.toml"))[:1]
    sync_labels("ml4t/data", labels)

    assert calls[0][:4] == ["gh", "label", "create", labels[0].name]
    assert "--force" in calls[0]


def test_sync_templates_renders_repository(tmp_path: Path) -> None:
    sync_templates(Path.cwd(), tmp_path, "ml4t/data")

    config = (tmp_path / ".github/ISSUE_TEMPLATE/config.yml").read_text(encoding="utf-8")
    assert "ml4t/data/security/advisories/new" in config
    assert "ml4t/ecosystem" not in config


def test_sync_templates_validates_before_writing(tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()

    with pytest.raises(ValueError, match="missing canonical template"):
        sync_templates(source, target, "ml4t/data")

    assert not target.exists()


def test_sync_templates_rejects_unresolved_variable(tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    for relative_name in (
        ".github/ISSUE_TEMPLATE/bug.yml",
        ".github/ISSUE_TEMPLATE/feature.yml",
        ".github/ISSUE_TEMPLATE/documentation.yml",
        ".github/ISSUE_TEMPLATE/config.yml",
        ".github/PULL_REQUEST_TEMPLATE.md",
    ):
        path = source / relative_name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("valid\n", encoding="utf-8")
    (source / ".github/ISSUE_TEMPLATE/bug.yml").write_text("{{unknown}}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="unresolved"):
        sync_templates(source, target, "ml4t/data")

    assert not target.exists()

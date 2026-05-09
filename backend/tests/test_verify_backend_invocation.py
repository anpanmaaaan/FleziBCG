from pathlib import Path

from scripts import verify_backend


def test_find_backend_root_from_repo_checkout_layout(tmp_path: Path) -> None:
    backend_root = tmp_path / "backend"
    (backend_root / "app").mkdir(parents=True)
    (backend_root / "scripts").mkdir()
    (backend_root / "app" / "__init__.py").write_text("", encoding="utf-8")

    anchor = backend_root / "scripts" / "verify_backend.py"
    anchor.write_text("# anchor\n", encoding="utf-8")

    assert verify_backend._find_backend_root(anchor) == backend_root


def test_find_backend_root_from_backend_root_container_layout(tmp_path: Path) -> None:
    backend_root = tmp_path / "app"
    (backend_root / "app").mkdir(parents=True)
    (backend_root / "scripts").mkdir()
    (backend_root / "app" / "__init__.py").write_text("", encoding="utf-8")

    anchor = backend_root / "scripts" / "verify_backend.py"
    anchor.write_text("# anchor\n", encoding="utf-8")

    assert verify_backend._find_backend_root(anchor) == backend_root


def test_find_repo_file_uses_secondary_anchor_for_backend_root_layout(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    workflow_path = repo_root / ".github" / "workflows" / "pr-gate.yml"
    workflow_path.parent.mkdir(parents=True)
    workflow_path.write_text("name: test\n", encoding="utf-8")

    container_anchor = tmp_path / "app" / "scripts" / "verify_backend.py"
    container_anchor.parent.mkdir(parents=True)
    container_anchor.write_text("# anchor\n", encoding="utf-8")

    assert verify_backend._find_repo_file(
        ".github",
        "workflows",
        "pr-gate.yml",
        anchors=[container_anchor, repo_root],
    ) == workflow_path


def test_all_checks_passed_treats_ruff_format_as_report_only_for_testenv() -> None:
    results = [
        verify_backend.Check("Backend import (app.main)", True, ""),
        verify_backend.Check("Ruff lint (ruff check .)", True, ""),
        verify_backend.Check("Ruff format (ruff format --check .)", False, "would reformat"),
        verify_backend.Check("DB connectivity", True, ""),
    ]

    assert verify_backend._all_checks_passed(results, testenv_only=True) is True
    assert verify_backend._all_checks_passed(results, testenv_only=False) is False

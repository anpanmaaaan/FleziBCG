from pathlib import Path


WORKFLOW_PATH = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "pr-gate.yml"


def _workflow_text() -> str:
    return WORKFLOW_PATH.read_text(encoding="utf-8")


def test_backend_import_check_step_is_present() -> None:
    text = _workflow_text()
    assert "- name: Backend import check" in text
    assert 'python -c "import app.main; print(\'import ok\')"' in text


def test_hard_mode_v3_skill_paths_are_current() -> None:
    text = _workflow_text()
    assert "docs/ai-skills/hard-mode-mom-v3/SKILL.md" in text
    assert "docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md" in text


def test_hard_mode_v3_required_reports_are_checked() -> None:
    text = _workflow_text()
    assert "docs/implementation/hard-mode-v3-map-report.md" in text
    assert "docs/implementation/design-gap-report.md" in text

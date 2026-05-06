from pathlib import Path


WORKFLOW_PATH = (
    Path(__file__).resolve().parents[2] / ".github" / "workflows" / "pr-gate.yml"
)


def _workflow_text() -> str:
    return WORKFLOW_PATH.read_text(encoding="utf-8")


def test_backend_import_check_step_is_present() -> None:
    text = _workflow_text()
    assert "- name: Backend import check" in text
    assert "python -c \"import app.main; print('import ok')\"" in text


def test_hard_mode_v3_skill_paths_are_current() -> None:
    text = _workflow_text()
    assert "docs/ai-skills/hard-mode-mom-v3/SKILL.md" in text
    assert "docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md" in text


def test_hard_mode_v3_required_reports_are_checked() -> None:
    text = _workflow_text()
    assert "docs/implementation/hard-mode-v3-map-report.md" in text
    assert "docs/implementation/design-gap-report.md" in text


def test_approval_security_event_tests_are_in_pr_gate() -> None:
    # P0-A-12A: approval SecurityEventLog test must stay in PR gate.
    # If this assertion fails, re-add tests/test_approval_security_events.py to pr-gate.yml.
    text = _workflow_text()
    assert "test_approval_security_events.py" in text


def test_approval_governed_resource_identity_tests_are_in_pr_gate() -> None:
    # P0-A-13: governed resource identity schema test must stay in PR gate.
    # If this assertion fails, re-add tests/test_approval_governed_resource_identity_schema.py to pr-gate.yml.
    text = _workflow_text()
    assert "test_approval_governed_resource_identity_schema.py" in text


def test_approval_rule_scope_applicability_schema_tests_are_in_pr_gate() -> None:
    # P0-A-15A: approval rule scope applicability schema test must stay in PR gate.
    # If this assertion fails, re-add tests/test_approval_rule_scope_applicability_schema.py to pr-gate.yml.
    text = _workflow_text()
    assert "test_approval_rule_scope_applicability_schema.py" in text


def test_approval_rule_scope_aware_matching_tests_are_in_pr_gate() -> None:
    # P0-A-15B: scope-aware matching test must stay in PR gate.
    # If this assertion fails, re-add tests/test_approval_rule_scope_aware_matching.py to pr-gate.yml.
    text = _workflow_text()
    assert "test_approval_rule_scope_aware_matching.py" in text


def test_approval_create_governed_context_bridge_tests_are_in_pr_gate() -> None:
    # P0-A-15C: governed context bridge test must stay in PR gate.
    # If this assertion fails, re-add tests/test_approval_create_governed_context_bridge.py to pr-gate.yml.
    text = _workflow_text()
    assert "test_approval_create_governed_context_bridge.py" in text


def test_approval_governed_context_api_tests_are_in_pr_gate() -> None:
    # P0-A-15D: API integration coverage test must stay in PR gate.
    # If this assertion fails, re-add tests/test_approval_governed_context_api.py to pr-gate.yml.
    text = _workflow_text()
    assert "test_approval_governed_context_api.py" in text

from pathlib import Path
from typing import Iterable


def _candidate_search_roots(anchors: Iterable[Path]) -> list[Path]:
    roots: list[Path] = []
    seen: set[Path] = set()
    for anchor in anchors:
        resolved = anchor.resolve()
        start = resolved.parent if resolved.suffix else resolved
        for candidate in (start, *start.parents):
            if candidate not in seen:
                seen.add(candidate)
                roots.append(candidate)
    return roots


def _resolve_repo_file(*relative_parts: str, anchors: Iterable[Path] | None = None) -> Path:
    search_anchors = list(anchors or [Path.cwd(), Path(__file__).resolve()])
    for root in _candidate_search_roots(search_anchors):
        candidate = root.joinpath(*relative_parts)
        if candidate.is_file():
            return candidate
    checked = ", ".join(str(path) for path in search_anchors)
    raise FileNotFoundError(
        f"Could not locate {'/'.join(relative_parts)} from anchors: {checked}"
    )


WORKFLOW_PATH = _resolve_repo_file(".github", "workflows", "pr-gate.yml")


def _workflow_text() -> str:
    return WORKFLOW_PATH.read_text(encoding="utf-8")


def test_workflow_path_resolution_handles_repo_checkout_layout(tmp_path: Path) -> None:
    workflow_path = tmp_path / ".github" / "workflows" / "pr-gate.yml"
    workflow_path.parent.mkdir(parents=True)
    workflow_path.write_text("name: test\n", encoding="utf-8")

    anchor = tmp_path / "backend" / "tests" / "test_pr_gate_workflow_config.py"
    anchor.parent.mkdir(parents=True)
    anchor.write_text("# anchor\n", encoding="utf-8")

    assert _resolve_repo_file(
        ".github", "workflows", "pr-gate.yml", anchors=[anchor]
    ) == workflow_path


def test_workflow_path_resolution_handles_backend_root_container_layout(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    workflow_path = repo_root / ".github" / "workflows" / "pr-gate.yml"
    workflow_path.parent.mkdir(parents=True)
    workflow_path.write_text("name: test\n", encoding="utf-8")

    container_anchor = tmp_path / "app" / "tests" / "test_pr_gate_workflow_config.py"
    container_anchor.parent.mkdir(parents=True)
    container_anchor.write_text("# anchor\n", encoding="utf-8")

    assert _resolve_repo_file(
        ".github",
        "workflows",
        "pr-gate.yml",
        anchors=[container_anchor, repo_root],
    ) == workflow_path


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


def test_approval_decision_governed_context_api_tests_are_in_pr_gate() -> None:
    # P0-A-15E: Decision API governed context coverage must stay in PR gate.
    # If this assertion fails, re-add tests/test_approval_decision_governed_context_api.py to pr-gate.yml.
    text = _workflow_text()
    assert "test_approval_decision_governed_context_api.py" in text


def test_approval_decision_specificity_api_tests_are_in_pr_gate() -> None:
    # P0-A-15F: Decision API specificity precedence coverage must stay in PR gate.
    # If this assertion fails, re-add tests/test_approval_decision_specificity_api.py to pr-gate.yml.
    text = _workflow_text()
    assert "test_approval_decision_specificity_api.py" in text


def test_approval_decision_tenant_override_api_tests_are_in_pr_gate() -> None:
    # P0-A-16: Decision API tenant-specific rule override coverage must stay in PR gate.
    # If this assertion fails, re-add tests/test_approval_decision_tenant_override_api.py to pr-gate.yml.
    text = _workflow_text()
    assert "test_approval_decision_tenant_override_api.py" in text


def test_approval_decision_same_score_api_tests_are_in_pr_gate() -> None:
    # P0-A-17: Same-score role group determinism coverage must stay in PR gate.
    # If this assertion fails, re-add tests/test_approval_decision_same_score_api.py to pr-gate.yml.
    text = _workflow_text()
    assert "test_approval_decision_same_score_api.py" in text

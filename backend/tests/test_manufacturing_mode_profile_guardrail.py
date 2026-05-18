"""Manufacturing mode profile guardrail tests.

These tests lock the product decision that the pilot runtime is discrete-first
while batch/process remains a supported future profile, not an implemented
runtime mode.
"""

from pathlib import Path

from app.models.manufacturing_mode import (
    MANUFACTURING_MODE_PROFILE_BATCH_PROCESS,
    MANUFACTURING_MODE_PROFILE_DISCRETE,
    SUPPORTED_MANUFACTURING_MODE_PROFILES,
)
from app.models.plant_hierarchy import Plant
from app.models.rbac import Scope
from app.models.tenant import Tenant

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_DIR.parent
MIGRATION_PATH = (
    BACKEND_DIR / "alembic" / "versions" / "0021_manufacturing_mode_profiles.py"
)
MODE_DOC = REPO_ROOT / "docs" / "system" / "manufacturing-mode-profile.md"
TRUTH_DOC = REPO_ROOT / "docs" / "implementation" / "current-implementation-truth.md"
ROADMAP_DOC = REPO_ROOT / "docs" / "roadmap" / "flezibcg-overall-roadmap-latest.md"


def test_supported_manufacturing_mode_profiles_are_locked() -> None:
    assert MANUFACTURING_MODE_PROFILE_DISCRETE == "DISCRETE"
    assert MANUFACTURING_MODE_PROFILE_BATCH_PROCESS == "BATCH_PROCESS"
    assert SUPPORTED_MANUFACTURING_MODE_PROFILES == (
        "DISCRETE",
        "BATCH_PROCESS",
    )


def test_manufacturing_mode_columns_exist_on_scope_anchors() -> None:
    assert "manufacturing_mode_default" in Tenant.__table__.c
    assert "manufacturing_mode_profile" in Plant.__table__.c
    assert "manufacturing_mode_profile" in Scope.__table__.c


def test_tenant_default_manufacturing_mode_is_discrete() -> None:
    tenant = Tenant(
        tenant_id="t-mode",
        tenant_code="MODE",
        tenant_name="Mode Tenant",
    )

    assert tenant.manufacturing_mode_default == "DISCRETE"


def test_manufacturing_mode_migration_adds_only_profile_columns() -> None:
    source = MIGRATION_PATH.read_text(encoding="utf-8")

    assert 'revision: str = "0021"' in source
    assert '"0020"' in source
    assert "manufacturing_mode_default" in source
    assert "manufacturing_mode_profile" in source
    assert "op.create_table" not in source


def test_current_truth_docs_point_to_runtime_authority() -> None:
    truth = TRUTH_DOC.read_text(encoding="utf-8")
    mode = MODE_DOC.read_text(encoding="utf-8")

    assert "frontend/src/app/screenStatus.ts" in truth
    assert "DISCRETE" in mode
    assert "BATCH_PROCESS" in mode
    assert "No batch/process runtime" in mode


def test_old_roadmap_is_marked_historical() -> None:
    text = ROADMAP_DOC.read_text(encoding="utf-8")

    assert "Historical baseline note" in text
    assert "current-implementation-truth.md" in text

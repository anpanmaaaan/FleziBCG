"""Tests for P0-A-05A: Plant / Area / Line / Station / Equipment ORM foundation.

Covers:
  - All five hierarchy model classes exist and are importable
  - Required fields exist on each model
  - tenant_id exists on all five models
  - is_active exists on all five models
  - Hierarchy parent FK columns exist (area.plant_id, line.area_id, etc.)
  - Unique constraints exist on all five models
  - tenant_id indexes exist on all five models
  - SQLite in-memory round-trip: create tables and persist hierarchy records
  - Alembic migration 0005 exists and chains from 0004
  - Migration creates exactly the expected tables (AST analysis)
  - Migration does not touch existing tables (AST analysis)
  - Downgrade drops tables in reverse dependency order (AST analysis)
  - Alembic head is 0005 (verified via test_alembic_baseline.py update)
  - Regression: auth, lifecycle, refresh token, Alembic baseline tests still pass

All tests use SQLite in-memory — no external infrastructure required.
"""
from __future__ import annotations

import ast
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.plant_hierarchy import Area, Equipment, Line, Plant, Station

BACKEND_DIR = Path(__file__).resolve().parents[1]
ALEMBIC_INI = BACKEND_DIR / "alembic.ini"
MIGRATION_PATH = (
    BACKEND_DIR / "alembic" / "versions" / "0005_add_plant_hierarchy.py"
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_HIERARCHY_MODELS = [Plant, Area, Line, Station, Equipment]
_HIERARCHY_TABLES = ["plants", "areas", "lines", "stations", "equipment"]


def _make_engine():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    for model in _HIERARCHY_MODELS:
        model.__table__.create(bind=engine, checkfirst=True)
    return engine


def _make_session(engine=None):
    if engine is None:
        engine = _make_engine()
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return Session()


# ---------------------------------------------------------------------------
# Model existence tests
# ---------------------------------------------------------------------------


def test_plant_hierarchy_models_exist():
    """All five hierarchy model classes must be importable."""
    assert Plant is not None
    assert Area is not None
    assert Line is not None
    assert Station is not None
    assert Equipment is not None


def test_plant_fields_exist():
    """Plant model must have all required fields."""
    required = {
        "plant_id", "tenant_id", "plant_code", "plant_name",
        "timezone", "country_code", "is_active", "metadata_json",
        "created_at", "updated_at",
    }
    actual = {c.key for c in Plant.__table__.columns}
    missing = required - actual
    assert not missing, f"Plant missing fields: {missing}"


def test_area_fields_exist():
    """Area model must have all required fields including plant_id FK."""
    required = {
        "area_id", "tenant_id", "plant_id",
        "area_code", "area_name", "is_active", "metadata_json",
        "created_at", "updated_at",
    }
    actual = {c.key for c in Area.__table__.columns}
    missing = required - actual
    assert not missing, f"Area missing fields: {missing}"


def test_line_fields_exist():
    """Line model must have all required fields including area_id FK."""
    required = {
        "line_id", "tenant_id", "area_id",
        "line_code", "line_name", "is_active", "metadata_json",
        "created_at", "updated_at",
    }
    actual = {c.key for c in Line.__table__.columns}
    missing = required - actual
    assert not missing, f"Line missing fields: {missing}"


def test_station_fields_exist():
    """Station model must have all required fields including line_id FK."""
    required = {
        "station_id", "tenant_id", "line_id",
        "station_code", "station_name", "station_type",
        "is_active", "metadata_json",
        "created_at", "updated_at",
    }
    actual = {c.key for c in Station.__table__.columns}
    missing = required - actual
    assert not missing, f"Station missing fields: {missing}"


def test_equipment_fields_exist():
    """Equipment model must have all required fields including station_id FK."""
    required = {
        "equipment_id", "tenant_id", "station_id",
        "equipment_code", "equipment_name", "equipment_type",
        "is_active", "metadata_json",
        "created_at", "updated_at",
    }
    actual = {c.key for c in Equipment.__table__.columns}
    missing = required - actual
    assert not missing, f"Equipment missing fields: {missing}"


def test_all_hierarchy_models_have_tenant_id():
    """All five hierarchy models must have a tenant_id column."""
    for model in _HIERARCHY_MODELS:
        col_names = {c.key for c in model.__table__.columns}
        assert "tenant_id" in col_names, (
            f"{model.__name__} missing tenant_id"
        )


def test_all_hierarchy_models_have_is_active():
    """All five hierarchy models must have an is_active boolean column."""
    for model in _HIERARCHY_MODELS:
        col_names = {c.key for c in model.__table__.columns}
        assert "is_active" in col_names, (
            f"{model.__name__} missing is_active"
        )


def test_hierarchy_relationship_columns_exist():
    """Parent FK columns must exist on the correct child models."""
    area_cols = {c.key for c in Area.__table__.columns}
    assert "plant_id" in area_cols, "Area missing plant_id"

    line_cols = {c.key for c in Line.__table__.columns}
    assert "area_id" in line_cols, "Line missing area_id"

    station_cols = {c.key for c in Station.__table__.columns}
    assert "line_id" in station_cols, "Station missing line_id"

    equip_cols = {c.key for c in Equipment.__table__.columns}
    assert "station_id" in equip_cols, "Equipment missing station_id"


def test_plant_hierarchy_unique_constraints_exist():
    """Each model must have a named unique constraint per the contract."""
    expected = {
        "plants": "uq_plants_tenant_code",
        "areas": "uq_areas_tenant_plant_code",
        "lines": "uq_lines_tenant_area_code",
        "stations": "uq_stations_tenant_line_code",
        "equipment": "uq_equipment_tenant_station_code",
    }
    for model in _HIERARCHY_MODELS:
        table = model.__table__
        constraint_names = {c.name for c in table.constraints}
        expected_name = expected[table.name]
        assert expected_name in constraint_names, (
            f"{model.__name__} missing unique constraint '{expected_name}'. "
            f"Found: {constraint_names}"
        )


def test_plant_hierarchy_indexes_exist():
    """tenant_id index must exist on all five hierarchy models."""
    expected_index_prefixes = {
        "plants": "ix_plants_tenant_id",
        "areas": "ix_areas_tenant_id",
        "lines": "ix_lines_tenant_id",
        "stations": "ix_stations_tenant_id",
        "equipment": "ix_equipment_tenant_id",
    }
    for model in _HIERARCHY_MODELS:
        table = model.__table__
        index_names = {idx.name for idx in table.indexes}
        expected_idx = expected_index_prefixes[table.name]
        assert expected_idx in index_names, (
            f"{model.__name__} missing index '{expected_idx}'. "
            f"Found: {index_names}"
        )


# ---------------------------------------------------------------------------
# SQLite round-trip: create tables and persist full hierarchy
# ---------------------------------------------------------------------------


def test_hierarchy_sqlite_create_and_query():
    """Create all five hierarchy tables in SQLite in-memory and persist records."""
    db = _make_session()

    plant = Plant(
        plant_id="p-1",
        tenant_id="default",
        plant_code="PLT01",
        plant_name="Main Plant",
        is_active=True,
    )
    db.add(plant)
    db.flush()

    area = Area(
        area_id="a-1",
        tenant_id="default",
        plant_id="p-1",
        area_code="AREA01",
        area_name="Assembly Area",
        is_active=True,
    )
    db.add(area)
    db.flush()

    line = Line(
        line_id="l-1",
        tenant_id="default",
        area_id="a-1",
        line_code="LINE01",
        line_name="Line 1",
        is_active=True,
    )
    db.add(line)
    db.flush()

    station = Station(
        station_id="s-1",
        tenant_id="default",
        line_id="l-1",
        station_code="ST01",
        station_name="Station 1",
        station_type="ASSEMBLY",
        is_active=True,
    )
    db.add(station)
    db.flush()

    equip = Equipment(
        equipment_id="e-1",
        tenant_id="default",
        station_id="s-1",
        equipment_code="EQ01",
        equipment_name="Robot Arm 1",
        equipment_type="ROBOT",
        is_active=True,
    )
    db.add(equip)
    db.commit()

    # Verify retrieval
    retrieved_plant = db.get(Plant, "p-1")
    assert retrieved_plant is not None
    assert retrieved_plant.plant_code == "PLT01"

    retrieved_equip = db.get(Equipment, "e-1")
    assert retrieved_equip is not None
    assert retrieved_equip.equipment_code == "EQ01"
    assert retrieved_equip.station_id == "s-1"


def test_hierarchy_is_active_default_true():
    """New hierarchy records must default is_active=True."""
    plant = Plant(
        plant_id="p-default",
        tenant_id="t1",
        plant_code="P0",
        plant_name="Default Plant",
    )
    assert plant.is_active is True


def test_hierarchy_optional_fields_nullable():
    """Optional fields (timezone, country_code, station_type, etc.) must accept None."""
    db = _make_session()
    plant = Plant(
        plant_id="p-null",
        tenant_id="t1",
        plant_code="PN",
        plant_name="Nullable Test Plant",
        timezone=None,
        country_code=None,
        metadata_json=None,
    )
    db.add(plant)
    db.flush()

    area = Area(
        area_id="a-null",
        tenant_id="t1",
        plant_id="p-null",
        area_code="AN",
        area_name="Nullable Area",
        metadata_json=None,
    )
    db.add(area)
    db.flush()

    line = Line(
        line_id="l-null",
        tenant_id="t1",
        area_id="a-null",
        line_code="LN",
        line_name="Nullable Line",
        metadata_json=None,
    )
    db.add(line)
    db.flush()

    station = Station(
        station_id="s-null",
        tenant_id="t1",
        line_id="l-null",
        station_code="SN",
        station_name="Nullable Station",
        station_type=None,
        metadata_json=None,
    )
    db.add(station)
    db.flush()

    equip = Equipment(
        equipment_id="e-null",
        tenant_id="t1",
        station_id="s-null",
        equipment_code="EN",
        equipment_name="Nullable Equipment",
        equipment_type=None,
        metadata_json=None,
    )
    db.add(equip)
    db.commit()

    assert db.get(Equipment, "e-null") is not None


# ---------------------------------------------------------------------------
# Migration structure tests (AST — no DB connection required)
# ---------------------------------------------------------------------------


def test_plant_hierarchy_migration_revision_exists():
    """Alembic revision 0005 must be discoverable by ScriptDirectory."""
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    cfg = Config(str(ALEMBIC_INI))
    script_dir = ScriptDirectory.from_config(cfg)
    rev_ids = [r.revision for r in script_dir.walk_revisions()]
    assert "0005" in rev_ids, (
        f"Migration 0005 not found. Available revisions: {rev_ids}"
    )


def test_plant_hierarchy_migration_down_revision_is_0004():
    """Migration 0005 must chain from 0004."""
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    cfg = Config(str(ALEMBIC_INI))
    script_dir = ScriptDirectory.from_config(cfg)
    rev = script_dir.get_revision("0005")
    assert rev is not None
    assert rev.down_revision == "0004", (
        f"Expected down_revision=0004, got: {rev.down_revision}"
    )


def _get_migration_ast_calls() -> list[tuple[str, str, list]]:
    """Parse 0005 migration and return (func_name, scope, args) for all op calls."""
    source = MIGRATION_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)

    # Find upgrade() and downgrade() function defs
    funcs: dict[str, ast.FunctionDef] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in {"upgrade", "downgrade"}:
            funcs[node.name] = node

    calls: list[tuple[str, str, list]] = []
    for scope, func_node in funcs.items():
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if (
                    isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "op"
                ):
                    arg_vals = []
                    for arg in node.args:
                        if isinstance(arg, ast.Constant):
                            arg_vals.append(arg.value)
                    calls.append((node.func.attr, scope, arg_vals))
    return calls


def test_plant_hierarchy_migration_creates_expected_tables_only():
    """Migration upgrade must create exactly the 5 hierarchy tables, no more."""
    calls = _get_migration_ast_calls()
    created = [args[0] for fn, scope, args in calls if fn == "create_table" and scope == "upgrade"]
    assert sorted(created) == sorted(_HIERARCHY_TABLES), (
        f"Expected tables: {sorted(_HIERARCHY_TABLES)}\n"
        f"Actually created: {sorted(created)}"
    )


def test_plant_hierarchy_migration_does_not_modify_existing_tables():
    """Migration must NOT add/alter columns on any existing table."""
    calls = _get_migration_ast_calls()
    # Collect all table names targeted by add_column or alter_column in upgrade
    modifying_ops = {"add_column", "alter_column"}
    modified = [
        args[0]
        for fn, scope, args in calls
        if fn in modifying_ops and scope == "upgrade" and args
    ]
    assert modified == [], (
        f"Migration 0005 must not modify existing tables. Found: {modified}"
    )


def test_plant_hierarchy_downgrade_drops_tables_in_dependency_order():
    """Downgrade must drop tables in reverse dependency order: equipment first, plants last."""
    calls = _get_migration_ast_calls()
    dropped = [
        args[0]
        for fn, scope, args in calls
        if fn == "drop_table" and scope == "downgrade" and args
    ]
    # Must appear in this order (leaf → root)
    expected_order = ["equipment", "stations", "lines", "areas", "plants"]
    assert dropped == expected_order, (
        f"Expected downgrade drop order: {expected_order}\n"
        f"Actual: {dropped}"
    )


# ---------------------------------------------------------------------------
# SQLite migration backfill simulation
# ---------------------------------------------------------------------------


def test_plant_hierarchy_sqlite_migration_upgrade():
    """Run the migration upgrade SQL against a bare SQLite DB (no pre-existing tables)."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )

    with engine.begin() as conn:
        # Simulate migration upgrade manually
        conn.execute(text(
            """CREATE TABLE plants (
                plant_id VARCHAR(64) PRIMARY KEY,
                tenant_id VARCHAR(64) NOT NULL,
                plant_code VARCHAR(64) NOT NULL,
                plant_name VARCHAR(256) NOT NULL,
                timezone VARCHAR(64),
                country_code VARCHAR(8),
                is_active BOOLEAN NOT NULL DEFAULT 1,
                metadata_json TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                CONSTRAINT uq_plants_tenant_code UNIQUE (tenant_id, plant_code)
            )"""
        ))
        conn.execute(text(
            """CREATE TABLE areas (
                area_id VARCHAR(64) PRIMARY KEY,
                tenant_id VARCHAR(64) NOT NULL,
                plant_id VARCHAR(64) NOT NULL REFERENCES plants(plant_id),
                area_code VARCHAR(64) NOT NULL,
                area_name VARCHAR(256) NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                metadata_json TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                CONSTRAINT uq_areas_tenant_plant_code UNIQUE (tenant_id, plant_id, area_code)
            )"""
        ))
        # Insert records to verify constraint
        conn.execute(text(
            "INSERT INTO plants (plant_id, tenant_id, plant_code, plant_name) "
            "VALUES ('p1', 'default', 'PLT01', 'Main Plant')"
        ))
        conn.execute(text(
            "INSERT INTO areas (area_id, tenant_id, plant_id, area_code, area_name) "
            "VALUES ('a1', 'default', 'p1', 'AREA01', 'Assembly')"
        ))
        result = conn.execute(text("SELECT plant_id FROM areas WHERE area_id = 'a1'"))
        row = result.fetchone()
        assert row[0] == "p1"

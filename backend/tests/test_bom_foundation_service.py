"""Tests for BOM foundation service/repository layer (MMD-BE-05, MMD-BE-12)."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.bom import Bom, BomItem
from app.models.product import Product
from app.models.security_event import SecurityEventLog
from app.repositories.bom_repository import get_bom_by_id as get_bom_row
from app.schemas.bom import (
    BomCreateRequest,
    BomItemCreateRequest,
    BomItemUpdateRequest,
    BomUpdateRequest,
    _ALLOWED_BOM_LIFECYCLE_STATUSES,
)
from app.schemas.product import ProductCreateRequest
from app.services.bom_service import (
    add_bom_item,
    create_bom,
    get_bom,
    list_boms,
    release_bom,
    remove_bom_item,
    retire_bom,
    update_bom,
    update_bom_item,
)
from app.services.product_service import create_product


def _make_session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Product.__table__.create(bind=engine)
    Bom.__table__.create(bind=engine)
    BomItem.__table__.create(bind=engine)
    SecurityEventLog.__table__.create(bind=engine)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return session_local()


def _mk_product(db, tenant_id: str = "tenant_a") -> str:
    created = create_product(
        db,
        tenant_id=tenant_id,
        actor_user_id="admin-a",
        payload=ProductCreateRequest(
            product_code=f"FG-{uuid.uuid4().hex[:8]}",
            product_name="Product",
            product_type="FINISHED_GOOD",
        ),
    )
    return created.product_id


def _mk_bom(db, *, tenant_id: str, product_id: str, bom_code: str, bom_name: str = "Main BOM") -> Bom:
    row = Bom(
        bom_id=uuid.uuid4().hex,
        tenant_id=tenant_id,
        product_id=product_id,
        bom_code=bom_code,
        bom_name=bom_name,
        lifecycle_status="DRAFT",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _mk_bom_item(
    db,
    *,
    tenant_id: str,
    bom_id: str,
    component_product_id: str,
    line_no: int,
    quantity: float,
    unit_of_measure: str = "PCS",
) -> BomItem:
    row = BomItem(
        bom_item_id=uuid.uuid4().hex,
        tenant_id=tenant_id,
        bom_id=bom_id,
        component_product_id=component_product_id,
        line_no=line_no,
        quantity=quantity,
        unit_of_measure=unit_of_measure,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def test_list_boms_returns_boms_for_product_and_tenant():
    db = _make_session()
    product_a = _mk_product(db, "tenant_a")
    product_b = _mk_product(db, "tenant_a")
    product_c = _mk_product(db, "tenant_b")

    bom_a1 = _mk_bom(db, tenant_id="tenant_a", product_id=product_a, bom_code="BOM-A-1")
    bom_a2 = _mk_bom(db, tenant_id="tenant_a", product_id=product_a, bom_code="BOM-A-2")
    _mk_bom(db, tenant_id="tenant_a", product_id=product_b, bom_code="BOM-B-1")
    _mk_bom(db, tenant_id="tenant_b", product_id=product_c, bom_code="BOM-C-1")

    result = list_boms(db, tenant_id="tenant_a", product_id=product_a)

    assert len(result) == 2
    ids = {x.bom_id for x in result}
    assert bom_a1.bom_id in ids
    assert bom_a2.bom_id in ids


def test_list_boms_returns_empty_for_product_with_no_boms():
    db = _make_session()
    product_id = _mk_product(db, "tenant_a")

    result = list_boms(db, tenant_id="tenant_a", product_id=product_id)

    assert result == []


def test_get_bom_returns_detail_with_items():
    db = _make_session()
    parent_product = _mk_product(db, "tenant_a")
    component_1 = _mk_product(db, "tenant_a")
    component_2 = _mk_product(db, "tenant_a")

    bom = _mk_bom(db, tenant_id="tenant_a", product_id=parent_product, bom_code="BOM-001")
    _mk_bom_item(
        db,
        tenant_id="tenant_a",
        bom_id=bom.bom_id,
        component_product_id=component_1,
        line_no=20,
        quantity=2.0,
    )
    _mk_bom_item(
        db,
        tenant_id="tenant_a",
        bom_id=bom.bom_id,
        component_product_id=component_2,
        line_no=10,
        quantity=1.0,
    )

    detail = get_bom(db, tenant_id="tenant_a", product_id=parent_product, bom_id=bom.bom_id)

    assert detail.bom_id == bom.bom_id
    assert len(detail.items) == 2
    assert [x.line_no for x in detail.items] == [10, 20]


def test_get_bom_returns_none_for_wrong_product():
    db = _make_session()
    product_a = _mk_product(db, "tenant_a")
    product_b = _mk_product(db, "tenant_a")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_a, bom_code="BOM-A")

    row = get_bom_row(db, tenant_id="tenant_a", product_id=product_b, bom_id=bom.bom_id)

    assert row is None


def test_get_bom_returns_none_for_wrong_tenant():
    db = _make_session()
    product_a = _mk_product(db, "tenant_a")
    _mk_product(db, "tenant_b")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_a, bom_code="BOM-A")

    row = get_bom_row(db, tenant_id="tenant_b", product_id=product_a, bom_id=bom.bom_id)

    assert row is None


def test_bom_item_order_by_line_no():
    db = _make_session()
    parent_product = _mk_product(db, "tenant_a")
    c1 = _mk_product(db, "tenant_a")
    c2 = _mk_product(db, "tenant_a")
    c3 = _mk_product(db, "tenant_a")

    bom = _mk_bom(db, tenant_id="tenant_a", product_id=parent_product, bom_code="BOM-ORDER")
    _mk_bom_item(db, tenant_id="tenant_a", bom_id=bom.bom_id, component_product_id=c1, line_no=30, quantity=1)
    _mk_bom_item(db, tenant_id="tenant_a", bom_id=bom.bom_id, component_product_id=c2, line_no=10, quantity=1)
    _mk_bom_item(db, tenant_id="tenant_a", bom_id=bom.bom_id, component_product_id=c3, line_no=20, quantity=1)

    detail = get_bom(db, tenant_id="tenant_a", product_id=parent_product, bom_id=bom.bom_id)

    assert [x.line_no for x in detail.items] == [10, 20, 30]


def test_lifecycle_status_values_are_stable():
    assert _ALLOWED_BOM_LIFECYCLE_STATUSES == {"DRAFT", "RELEASED", "RETIRED"}


def test_bom_model_does_not_include_product_version_binding():
    columns = set(Bom.__table__.columns.keys())
    assert "product_version_id" not in columns


def test_bom_model_has_no_backflush_or_erp_fields():
    columns = set(Bom.__table__.columns.keys())
    forbidden = {
        "backflush",
        "backflush_policy",
        "erp_posting",
        "erp_document",
        "inventory_movement",
        "inventory_issue",
        "material_consumption",
    }
    assert columns.isdisjoint(forbidden)


# ─── MMD-BE-12 service write tests ───────────────────────────────────────────

def test_create_bom_validates_product_exists():
    db = _make_session()
    with pytest.raises(LookupError, match="Product not found"):
        create_bom(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin-a",
            product_id="nonexistent-product",
            payload=BomCreateRequest(bom_code="X", bom_name="X"),
        )


def test_create_bom_sets_draft_default():
    db = _make_session()
    product_id = _mk_product(db, "tenant_a")
    result = create_bom(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        product_id=product_id,
        payload=BomCreateRequest(bom_code="BOM-CREATE", bom_name="Create BOM"),
    )
    assert result.lifecycle_status == "DRAFT"
    assert result.product_id == product_id


def test_create_bom_enforces_unique_code_per_product():
    db = _make_session()
    product_id = _mk_product(db, "tenant_a")
    create_bom(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        product_id=product_id,
        payload=BomCreateRequest(bom_code="BOM-DUP", bom_name="BOM"),
    )
    with pytest.raises(ValueError, match="Duplicate bom_code"):
        create_bom(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin-a",
            product_id=product_id,
            payload=BomCreateRequest(bom_code="BOM-DUP", bom_name="BOM"),
        )


def test_effective_date_range_validation():
    db = _make_session()
    product_id = _mk_product(db, "tenant_a")
    from datetime import date

    with pytest.raises(Exception):
        BomCreateRequest(
            bom_code="X",
            bom_name="X",
            effective_from=date(2026, 12, 31),
            effective_to=date(2026, 1, 1),
        )


def test_update_bom_only_draft():
    db = _make_session()
    product_id = _mk_product(db, "tenant_a")
    bom_released = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="U-REL")
    bom_released.lifecycle_status = "RELEASED"
    db.commit()

    with pytest.raises(ValueError, match="RELEASED BOM"):
        update_bom(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin-a",
            product_id=product_id,
            bom_id=bom_released.bom_id,
            payload=BomUpdateRequest(bom_name="Changed"),
        )


def test_release_only_draft():
    db = _make_session()
    product_id = _mk_product(db, "tenant_a")
    comp_id = _mk_product(db, "tenant_a")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="R-SVC")
    _mk_bom_item(
        db,
        tenant_id="tenant_a",
        bom_id=bom.bom_id,
        component_product_id=comp_id,
        line_no=10,
        quantity=1.0,
    )

    result = release_bom(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        product_id=product_id,
        bom_id=bom.bom_id,
    )
    assert result.lifecycle_status == "RELEASED"

    with pytest.raises(ValueError, match="Only DRAFT"):
        release_bom(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin-a",
            product_id=product_id,
            bom_id=bom.bom_id,
        )


def test_retire_draft_or_released():
    db = _make_session()
    product_id = _mk_product(db, "tenant_a")
    bom_draft = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="RT-D")
    bom_released = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="RT-R")
    bom_released.lifecycle_status = "RELEASED"
    db.commit()

    r1 = retire_bom(
        db, tenant_id="tenant_a", actor_user_id="admin-a", product_id=product_id, bom_id=bom_draft.bom_id
    )
    assert r1.lifecycle_status == "RETIRED"

    r2 = retire_bom(
        db, tenant_id="tenant_a", actor_user_id="admin-a", product_id=product_id, bom_id=bom_released.bom_id
    )
    assert r2.lifecycle_status == "RETIRED"

    with pytest.raises(ValueError, match="already RETIRED"):
        retire_bom(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin-a",
            product_id=product_id,
            bom_id=bom_draft.bom_id,
        )


def test_add_update_remove_item_only_draft_parent():
    db = _make_session()
    product_id = _mk_product(db, "tenant_a")
    comp_id = _mk_product(db, "tenant_a")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="ITEM-DRAFT")
    bom.lifecycle_status = "RELEASED"
    db.commit()

    with pytest.raises(ValueError, match="DRAFT"):
        add_bom_item(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin-a",
            product_id=product_id,
            bom_id=bom.bom_id,
            payload=BomItemCreateRequest(
                component_product_id=comp_id, line_no=10, quantity=1.0, unit_of_measure="PCS"
            ),
        )


def test_component_product_must_exist():
    db = _make_session()
    product_id = _mk_product(db, "tenant_a")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="COMP-EXIST")

    with pytest.raises(LookupError, match="Component product not found"):
        add_bom_item(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin-a",
            product_id=product_id,
            bom_id=bom.bom_id,
            payload=BomItemCreateRequest(
                component_product_id="does-not-exist", line_no=10, quantity=1.0, unit_of_measure="PCS"
            ),
        )


def test_component_product_cannot_equal_parent_product():
    db = _make_session()
    product_id = _mk_product(db, "tenant_a")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="CIRCULAR")

    with pytest.raises(ValueError, match="parent product_id"):
        add_bom_item(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin-a",
            product_id=product_id,
            bom_id=bom.bom_id,
            payload=BomItemCreateRequest(
                component_product_id=product_id, line_no=10, quantity=1.0, unit_of_measure="PCS"
            ),
        )


def test_quantity_positive():
    db = _make_session()
    product_id = _mk_product(db, "tenant_a")
    comp_id = _mk_product(db, "tenant_a")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="QTY-POS")

    with pytest.raises(ValueError, match="quantity must be greater than zero"):
        add_bom_item(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin-a",
            product_id=product_id,
            bom_id=bom.bom_id,
            payload=BomItemCreateRequest(
                component_product_id=comp_id, line_no=10, quantity=0.0, unit_of_measure="PCS"
            ),
        )


def test_scrap_factor_non_negative():
    db = _make_session()
    product_id = _mk_product(db, "tenant_a")
    comp_id = _mk_product(db, "tenant_a")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="SCRAP-NEG")

    with pytest.raises(ValueError, match="scrap_factor must be non-negative"):
        add_bom_item(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin-a",
            product_id=product_id,
            bom_id=bom.bom_id,
            payload=BomItemCreateRequest(
                component_product_id=comp_id,
                line_no=10,
                quantity=1.0,
                unit_of_measure="PCS",
                scrap_factor=-0.05,
            ),
        )


def test_no_product_version_binding_field_or_behavior():
    columns = set(Bom.__table__.columns.keys())
    assert "product_version_id" not in columns
    # BomCreateRequest must not accept product_version_id
    with pytest.raises(Exception):
        BomCreateRequest(bom_code="X", bom_name="X", product_version_id="pv-x")

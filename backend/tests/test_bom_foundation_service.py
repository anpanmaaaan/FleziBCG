"""Tests for BOM foundation service/repository layer (MMD-BE-05)."""

from __future__ import annotations

import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.bom import Bom, BomItem
from app.models.product import Product
from app.models.security_event import SecurityEventLog
from app.repositories.bom_repository import get_bom_by_id as get_bom_row
from app.schemas.bom import _ALLOWED_BOM_LIFECYCLE_STATUSES
from app.schemas.product import ProductCreateRequest
from app.services.bom_service import get_bom, list_boms
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

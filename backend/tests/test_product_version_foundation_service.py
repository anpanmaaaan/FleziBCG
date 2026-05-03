"""Tests for product version service layer.

Covers read foundations and MMD-BE-11 write API foundation service invariants.
"""

import json
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.product import Product
from app.models.product_version import ProductVersion
from app.models.security_event import SecurityEventLog
from app.schemas.product import (
    ProductCreateRequest,
    ProductVersionCreateRequest,
    ProductVersionUpdateRequest,
)
from app.services.product_service import create_product
from app.services.product_version_service import (
    create_product_version,
    get_product_version,
    list_product_versions,
    release_product_version,
    retire_product_version,
    update_product_version,
)


def _make_session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Product.__table__.create(bind=engine)
    ProductVersion.__table__.create(bind=engine)
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
            product_name="Test Product",
            product_type="FINISHED_GOOD",
        ),
    )
    return created.product_id


def _mk_version(
    db,
    tenant_id: str,
    product_id: str,
    version_code: str,
    *,
    lifecycle_status: str = "DRAFT",
    is_current: bool = False,
) -> ProductVersion:
    row = ProductVersion(
        product_version_id=uuid.uuid4().hex,
        tenant_id=tenant_id,
        product_id=product_id,
        version_code=version_code,
        version_name=f"Version {version_code}",
        lifecycle_status=lifecycle_status,
        is_current=is_current,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def test_list_product_versions_returns_versions_for_product():
    db = _make_session()
    product_id = _mk_product(db)
    v1 = _mk_version(db, "tenant_a", product_id, "v1.0")
    v2 = _mk_version(db, "tenant_a", product_id, "v2.0")

    result = list_product_versions(db, tenant_id="tenant_a", product_id=product_id)

    assert len(result) == 2
    ids = {r.product_version_id for r in result}
    assert v1.product_version_id in ids
    assert v2.product_version_id in ids


def test_get_product_version_returns_correct_item():
    db = _make_session()
    product_id = _mk_product(db)
    v = _mk_version(db, "tenant_a", product_id, "v1.0", is_current=True)

    result = get_product_version(
        db,
        tenant_id="tenant_a",
        product_id=product_id,
        product_version_id=v.product_version_id,
    )

    assert result.product_version_id == v.product_version_id
    assert result.version_code == "v1.0"
    assert result.product_id == product_id
    assert result.is_current is True


def test_create_product_version_validates_product_exists():
    db = _make_session()
    try:
        create_product_version(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin-a",
            product_id="missing-product",
            payload=ProductVersionCreateRequest(version_code="v1"),
        )
        assert False, "Expected LookupError"
    except LookupError as exc:
        assert "Product not found" in str(exc)


def test_create_product_version_sets_draft_default():
    db = _make_session()
    product_id = _mk_product(db)

    created = create_product_version(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        product_id=product_id,
        payload=ProductVersionCreateRequest(version_code="v1", version_name="First"),
    )

    assert created.lifecycle_status == "DRAFT"
    assert created.is_current is False


def test_create_product_version_enforces_unique_code_per_product():
    db = _make_session()
    product_id = _mk_product(db)

    create_product_version(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        product_id=product_id,
        payload=ProductVersionCreateRequest(version_code="dup"),
    )

    try:
        create_product_version(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin-a",
            product_id=product_id,
            payload=ProductVersionCreateRequest(version_code="dup"),
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "Duplicate version_code" in str(exc)


def test_update_product_version_only_draft():
    db = _make_session()
    product_id = _mk_product(db)
    released = _mk_version(db, "tenant_a", product_id, "v1", lifecycle_status="RELEASED")

    try:
        update_product_version(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin-a",
            product_id=product_id,
            product_version_id=released.product_version_id,
            payload=ProductVersionUpdateRequest(description="blocked"),
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "Only DRAFT" in str(exc)


def test_release_only_draft():
    db = _make_session()
    product_id = _mk_product(db)
    retired = _mk_version(db, "tenant_a", product_id, "v1", lifecycle_status="RETIRED")

    try:
        release_product_version(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin-a",
            product_id=product_id,
            product_version_id=retired.product_version_id,
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "Only DRAFT" in str(exc)


def test_retire_draft_or_released():
    db = _make_session()
    product_id = _mk_product(db)
    draft = _mk_version(db, "tenant_a", product_id, "d", lifecycle_status="DRAFT")
    released = _mk_version(db, "tenant_a", product_id, "r", lifecycle_status="RELEASED")

    draft_retired = retire_product_version(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        product_id=product_id,
        product_version_id=draft.product_version_id,
    )
    released_retired = retire_product_version(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        product_id=product_id,
        product_version_id=released.product_version_id,
    )

    assert draft_retired.lifecycle_status == "RETIRED"
    assert released_retired.lifecycle_status == "RETIRED"


def test_effective_date_range_validation():
    db = _make_session()
    product_id = _mk_product(db)

    try:
        create_product_version(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin-a",
            product_id=product_id,
            payload=ProductVersionCreateRequest(
                version_code="v1",
                effective_from="2026-06-01",
                effective_to="2026-05-01",
            ),
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "effective_from" in str(exc)


def test_no_is_current_change_in_create_update_release():
    db = _make_session()
    product_id = _mk_product(db)

    created = create_product_version(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        product_id=product_id,
        payload=ProductVersionCreateRequest(version_code="v1"),
    )
    assert created.is_current is False

    updated = update_product_version(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        product_id=product_id,
        product_version_id=created.product_version_id,
        payload=ProductVersionUpdateRequest(version_name="updated"),
    )
    assert updated.is_current is False

    released = release_product_version(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        product_id=product_id,
        product_version_id=created.product_version_id,
    )
    assert released.is_current is False


def test_product_version_events_stay_within_mmd_audit_boundary():
    db = _make_session()
    product_id = _mk_product(db)

    created = create_product_version(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        product_id=product_id,
        payload=ProductVersionCreateRequest(version_code="v1", version_name="first"),
    )
    update_product_version(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        product_id=product_id,
        product_version_id=created.product_version_id,
        payload=ProductVersionUpdateRequest(description="updated"),
    )
    release_product_version(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        product_id=product_id,
        product_version_id=created.product_version_id,
    )
    retire_product_version(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        product_id=product_id,
        product_version_id=created.product_version_id,
    )

    events = (
        db.query(SecurityEventLog)
        .filter(SecurityEventLog.resource_type == "product_version")
        .order_by(SecurityEventLog.id.asc())
        .all()
    )

    assert [event.event_type for event in events] == [
        "PRODUCT_VERSION.CREATED",
        "PRODUCT_VERSION.UPDATED",
        "PRODUCT_VERSION.RELEASED",
        "PRODUCT_VERSION.RETIRED",
    ]

    forbidden_terms = (
        "execution",
        "state_machine",
        "backflush",
        "erp",
        "traceability",
        "genealogy",
        "quality",
        "material",
    )

    for event in events:
        assert event.resource_type == "product_version"
        assert event.resource_id == created.product_version_id

        event_text = f"{event.event_type} {event.detail or ''}".lower()
        for term in forbidden_terms:
            assert term not in event_text

        detail = json.loads(event.detail or "{}")
        assert detail["product_id"] == product_id
        assert detail["product_version_id"] == created.product_version_id


def test_product_version_tenant_and_product_isolation_reads():
    db = _make_session()
    product_id_a = _mk_product(db, tenant_id="tenant_a")
    product_id_b = _mk_product(db, tenant_id="tenant_b")

    v_a = _mk_version(db, "tenant_a", product_id_a, "v1.0")

    result_b = list_product_versions(db, tenant_id="tenant_b", product_id=product_id_b)
    assert result_b == []

    try:
        list_product_versions(db, tenant_id="tenant_b", product_id=product_id_a)
        assert False, "Expected LookupError"
    except LookupError:
        pass

    result_a = list_product_versions(db, tenant_id="tenant_a", product_id=product_id_a)
    assert len(result_a) == 1
    assert result_a[0].product_version_id == v_a.product_version_id

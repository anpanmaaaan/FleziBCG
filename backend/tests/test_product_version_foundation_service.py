"""Tests for product version foundation service layer (MMD-BE-03).

These tests verify:
- list_product_versions returns correct items
- get_product_version returns correct item
- Tenant isolation: Tenant B cannot see Tenant A versions
- Product isolation: versions are product-scoped
- Missing product raises LookupError
- Missing version raises LookupError
"""
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.product import Product
from app.models.product_version import ProductVersion
from app.models.security_event import SecurityEventLog
from app.schemas.product import ProductCreateRequest
from app.services.product_service import create_product
from app.services.product_version_service import (
    get_product_version,
    list_product_versions,
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


def _mk_version(db, tenant_id: str, product_id: str, version_code: str, is_current: bool = False) -> ProductVersion:
    row = ProductVersion(
        product_version_id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        product_id=product_id,
        version_code=version_code,
        version_name=f"Version {version_code}",
        lifecycle_status="DRAFT",
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


def test_list_product_versions_returns_empty_for_product_with_no_versions():
    db = _make_session()
    product_id = _mk_product(db)

    result = list_product_versions(db, tenant_id="tenant_a", product_id=product_id)

    assert result == []


def test_list_product_versions_404_for_missing_product():
    db = _make_session()

    try:
        list_product_versions(db, tenant_id="tenant_a", product_id="nonexistent-id")
        assert False, "Expected LookupError"
    except LookupError as exc:
        assert "Product not found" in str(exc)


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
    assert result.tenant_id == "tenant_a"
    assert result.is_current is True
    assert result.lifecycle_status == "DRAFT"


def test_get_product_version_404_for_missing_version():
    db = _make_session()
    product_id = _mk_product(db)

    try:
        get_product_version(
            db,
            tenant_id="tenant_a",
            product_id=product_id,
            product_version_id="nonexistent-version-id",
        )
        assert False, "Expected LookupError"
    except LookupError as exc:
        assert "version" in str(exc).lower() or "not found" in str(exc).lower()


def test_get_product_version_404_for_missing_product():
    db = _make_session()

    try:
        get_product_version(
            db,
            tenant_id="tenant_a",
            product_id="nonexistent-product-id",
            product_version_id="any-version-id",
        )
        assert False, "Expected LookupError"
    except LookupError as exc:
        assert "Product not found" in str(exc)


def test_product_version_tenant_isolation():
    db = _make_session()
    product_id_a = _mk_product(db, tenant_id="tenant_a")
    product_id_b = _mk_product(db, tenant_id="tenant_b")

    v_a = _mk_version(db, "tenant_a", product_id_a, "v1.0")

    # Tenant B cannot see tenant A's versions using tenant B's product
    result_b = list_product_versions(db, tenant_id="tenant_b", product_id=product_id_b)
    assert result_b == []

    # Tenant B gets 404 for tenant A's product (different tenant)
    try:
        list_product_versions(db, tenant_id="tenant_b", product_id=product_id_a)
        assert False, "Expected LookupError"
    except LookupError:
        pass

    # Tenant A only sees its own versions
    result_a = list_product_versions(db, tenant_id="tenant_a", product_id=product_id_a)
    assert len(result_a) == 1
    assert result_a[0].product_version_id == v_a.product_version_id


def test_product_version_product_isolation():
    db = _make_session()
    product_id_a = _mk_product(db)
    product_id_b = _mk_product(db)

    v_a = _mk_version(db, "tenant_a", product_id_a, "v1.0")

    result_b = list_product_versions(db, tenant_id="tenant_a", product_id=product_id_b)
    assert result_b == []

    result_a = list_product_versions(db, tenant_id="tenant_a", product_id=product_id_a)
    assert len(result_a) == 1
    assert result_a[0].product_version_id == v_a.product_version_id


def test_product_version_lifecycle_status_values_stable():
    """Ensures lifecycle_status string constants are stable — used by future slices."""
    from app.schemas.product import _ALLOWED_VERSION_LIFECYCLE_STATUSES

    assert "DRAFT" in _ALLOWED_VERSION_LIFECYCLE_STATUSES
    assert "RELEASED" in _ALLOWED_VERSION_LIFECYCLE_STATUSES
    assert "RETIRED" in _ALLOWED_VERSION_LIFECYCLE_STATUSES
    assert len(_ALLOWED_VERSION_LIFECYCLE_STATUSES) == 3

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.product import ProductCreateRequest, ProductItem, ProductUpdateRequest, ProductVersionItem
from app.security.dependencies import RequestIdentity, require_action, require_authenticated_identity
from app.services.product_service import (
    create_product as create_product_service,
    get_product_by_id as get_product_by_id_service,
    list_products as list_products_service,
    release_product as release_product_service,
    retire_product as retire_product_service,
    update_product as update_product_service,
)
from app.services.product_version_service import (
    get_product_version as get_product_version_service,
    list_product_versions as list_product_versions_service,
)

router = APIRouter(prefix="/products", tags=["products"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[ProductItem])
def list_products(
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
) -> list[ProductItem]:
    return list_products_service(db, tenant_id=identity.tenant_id)


@router.get("/{product_id}", response_model=ProductItem)
def get_product_by_id(
    product_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
) -> ProductItem:
    row = get_product_by_id_service(
        db,
        tenant_id=identity.tenant_id,
        product_id=product_id,
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return row


@router.post("", response_model=ProductItem)
def create_product(
    payload: ProductCreateRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.master_data.product.manage")),
) -> ProductItem:
    try:
        return create_product_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            payload=payload,
        )
    except ValueError as exc:
        if str(exc) == "Duplicate product_code in tenant":
            raise HTTPException(status_code=409, detail=str(exc))
        raise HTTPException(status_code=400, detail=str(exc))


@router.patch("/{product_id}", response_model=ProductItem)
def update_product(
    product_id: str,
    payload: ProductUpdateRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.master_data.product.manage")),
) -> ProductItem:
    try:
        return update_product_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            product_id=product_id,
            payload=payload,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        if str(exc) == "Duplicate product_code in tenant":
            raise HTTPException(status_code=409, detail=str(exc))
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{product_id}/release", response_model=ProductItem)
def release_product(
    product_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.master_data.product.manage")),
) -> ProductItem:
    try:
        return release_product_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            product_id=product_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/{product_id}/versions", response_model=list[ProductVersionItem])
def list_product_versions(
    product_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
) -> list[ProductVersionItem]:
    try:
        return list_product_versions_service(
            db,
            tenant_id=identity.tenant_id,
            product_id=product_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/{product_id}/versions/{version_id}", response_model=ProductVersionItem)
def get_product_version(
    product_id: str,
    version_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
) -> ProductVersionItem:
    try:
        return get_product_version_service(
            db,
            tenant_id=identity.tenant_id,
            product_id=product_id,
            product_version_id=version_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/{product_id}/retire", response_model=ProductItem)
def retire_product(
    product_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.master_data.product.manage")),
) -> ProductItem:
    try:
        return retire_product_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            product_id=product_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

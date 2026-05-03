from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.bom import BomDetail, BomItem
from app.schemas.bom import (
    BomComponentItem,
    BomCreateRequest,
    BomItemCreateRequest,
    BomItemUpdateRequest,
    BomUpdateRequest,
)
from app.schemas.product import (
    ProductCreateRequest,
    ProductItem,
    ProductUpdateRequest,
    ProductVersionCreateRequest,
    ProductVersionItem,
    ProductVersionUpdateRequest,
)
from app.security.dependencies import RequestIdentity, require_action, require_authenticated_identity
from app.security.rbac import has_action
from app.services.bom_service import get_bom as get_bom_service
from app.services.bom_service import list_boms as list_boms_service
from app.services.bom_service import (
    add_bom_item as add_bom_item_service,
    create_bom as create_bom_service,
    release_bom as release_bom_service,
    remove_bom_item as remove_bom_item_service,
    retire_bom as retire_bom_service,
    update_bom as update_bom_service,
    update_bom_item as update_bom_item_service,
)
from app.services.product_service import (
    create_product as create_product_service,
    get_product_by_id as get_product_by_id_service,
    list_products as list_products_service,
    release_product as release_product_service,
    retire_product as retire_product_service,
    update_product as update_product_service,
)
from app.services.product_version_service import (
    create_product_version as create_product_version_service,
    get_product_version as get_product_version_service,
    list_product_versions as list_product_versions_service,
    release_product_version as release_product_version_service,
    retire_product_version as retire_product_version_service,
    update_product_version as update_product_version_service,
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
    has_manage = has_action(db, identity, "admin.master_data.product_version.manage")
    return list_products_service(db, tenant_id=identity.tenant_id, has_manage_permission=has_manage)


@router.get("/{product_id}", response_model=ProductItem)
def get_product_by_id(
    product_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
) -> ProductItem:
    has_manage = has_action(db, identity, "admin.master_data.product_version.manage")
    row = get_product_by_id_service(
        db,
        tenant_id=identity.tenant_id,
        product_id=product_id,
        has_manage_permission=has_manage,
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
    has_pv_manage = has_action(db, identity, "admin.master_data.product_version.manage")
    try:
        return create_product_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            payload=payload,
            has_pv_manage=has_pv_manage,
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
    has_pv_manage = has_action(db, identity, "admin.master_data.product_version.manage")
    try:
        return update_product_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            product_id=product_id,
            payload=payload,
            has_pv_manage=has_pv_manage,
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
    has_pv_manage = has_action(db, identity, "admin.master_data.product_version.manage")
    try:
        return release_product_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            product_id=product_id,
            has_pv_manage=has_pv_manage,
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
    has_manage = has_action(db, identity, "admin.master_data.product_version.manage")
    try:
        return list_product_versions_service(
            db,
            tenant_id=identity.tenant_id,
            product_id=product_id,
            has_manage_permission=has_manage,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/{product_id}/versions", response_model=ProductVersionItem)
def create_product_version(
    product_id: str,
    payload: ProductVersionCreateRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.master_data.product_version.manage")),
) -> ProductVersionItem:
    try:
        return create_product_version_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            product_id=product_id,
            payload=payload,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        if str(exc) == "Duplicate version_code in product":
            raise HTTPException(status_code=409, detail=str(exc))
        raise HTTPException(status_code=400, detail=str(exc))


@router.patch("/{product_id}/versions/{version_id}", response_model=ProductVersionItem)
def update_product_version(
    product_id: str,
    version_id: str,
    payload: ProductVersionUpdateRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.master_data.product_version.manage")),
) -> ProductVersionItem:
    try:
        return update_product_version_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            product_id=product_id,
            product_version_id=version_id,
            payload=payload,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{product_id}/versions/{version_id}/release", response_model=ProductVersionItem)
def release_product_version(
    product_id: str,
    version_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.master_data.product_version.manage")),
) -> ProductVersionItem:
    try:
        return release_product_version_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            product_id=product_id,
            product_version_id=version_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{product_id}/versions/{version_id}/retire", response_model=ProductVersionItem)
def retire_product_version(
    product_id: str,
    version_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.master_data.product_version.manage")),
) -> ProductVersionItem:
    try:
        return retire_product_version_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            product_id=product_id,
            product_version_id=version_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/{product_id}/boms", response_model=list[BomItem])
def list_boms(
    product_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
) -> list[BomItem]:
    try:
        return list_boms_service(
            db,
            tenant_id=identity.tenant_id,
            product_id=product_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/{product_id}/boms/{bom_id}", response_model=BomDetail)
def get_bom(
    product_id: str,
    bom_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
) -> BomDetail:
    try:
        return get_bom_service(
            db,
            tenant_id=identity.tenant_id,
            product_id=product_id,
            bom_id=bom_id,
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
    has_manage = has_action(db, identity, "admin.master_data.product_version.manage")
    try:
        return get_product_version_service(
            db,
            tenant_id=identity.tenant_id,
            product_id=product_id,
            product_version_id=version_id,
            has_manage_permission=has_manage,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/{product_id}/retire", response_model=ProductItem)
def retire_product(
    product_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.master_data.product.manage")),
) -> ProductItem:
    has_pv_manage = has_action(db, identity, "admin.master_data.product_version.manage")
    try:
        return retire_product_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            product_id=product_id,
            has_pv_manage=has_pv_manage,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# ─── BOM write endpoints — MMD-BE-12 ─────────────────────────────────────────

@router.post("/{product_id}/boms", response_model=BomItem, status_code=201)
def create_bom(
    product_id: str,
    payload: BomCreateRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.master_data.bom.manage")),
) -> BomItem:
    try:
        return create_bom_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            product_id=product_id,
            payload=payload,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        if str(exc) == "Duplicate bom_code for product in tenant":
            raise HTTPException(status_code=409, detail=str(exc))
        raise HTTPException(status_code=400, detail=str(exc))


@router.patch("/{product_id}/boms/{bom_id}", response_model=BomItem)
def update_bom(
    product_id: str,
    bom_id: str,
    payload: BomUpdateRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.master_data.bom.manage")),
) -> BomItem:
    try:
        return update_bom_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            product_id=product_id,
            bom_id=bom_id,
            payload=payload,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{product_id}/boms/{bom_id}/release", response_model=BomItem)
def release_bom(
    product_id: str,
    bom_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.master_data.bom.manage")),
) -> BomItem:
    try:
        return release_bom_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            product_id=product_id,
            bom_id=bom_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{product_id}/boms/{bom_id}/retire", response_model=BomItem)
def retire_bom(
    product_id: str,
    bom_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.master_data.bom.manage")),
) -> BomItem:
    try:
        return retire_bom_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            product_id=product_id,
            bom_id=bom_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{product_id}/boms/{bom_id}/items", response_model=BomComponentItem, status_code=201)
def add_bom_item(
    product_id: str,
    bom_id: str,
    payload: BomItemCreateRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.master_data.bom.manage")),
) -> BomComponentItem:
    try:
        return add_bom_item_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            product_id=product_id,
            bom_id=bom_id,
            payload=payload,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        if str(exc) == "Duplicate line_no within BOM":
            raise HTTPException(status_code=409, detail=str(exc))
        raise HTTPException(status_code=400, detail=str(exc))


@router.patch(
    "/{product_id}/boms/{bom_id}/items/{bom_item_id}",
    response_model=BomComponentItem,
)
def update_bom_item(
    product_id: str,
    bom_id: str,
    bom_item_id: str,
    payload: BomItemUpdateRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.master_data.bom.manage")),
) -> BomComponentItem:
    try:
        return update_bom_item_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            product_id=product_id,
            bom_id=bom_id,
            bom_item_id=bom_item_id,
            payload=payload,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/{product_id}/boms/{bom_id}/items/{bom_item_id}", status_code=204)
def remove_bom_item(
    product_id: str,
    bom_id: str,
    bom_item_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.master_data.bom.manage")),
) -> None:
    try:
        remove_bom_item_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            product_id=product_id,
            bom_id=bom_id,
            bom_item_id=bom_item_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


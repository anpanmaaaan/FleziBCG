# FASTAPI ROUTE SKELETON

## Purpose
Template for thin route layer.

---

from fastapi import APIRouter, Depends
from app.schemas.execution import StartRequest, ExecutionResponse
from app.services.execution_service import ExecutionService
from app.security.deps import get_current_user, get_scope

router = APIRouter(prefix="/execution")

@router.post("/{op_id}/start", response_model=ExecutionResponse)
def start_operation(
    op_id: str,
    payload: StartRequest,
    user=Depends(get_current_user),
    scope=Depends(get_scope),
    svc: ExecutionService = Depends()
):
    # no business logic here
    return svc.start_operation(op_id=op_id, payload=payload, user=user, scope=scope)

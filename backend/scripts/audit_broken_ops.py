"""
Cleanup operations bị lỗi:
  1. Reset stuck ops (IN_PROGRESS / BLOCKED, không có OPEN session) → PLANNED
  2. Xóa hẳn dữ liệu test cũ có prefix TEST-DT-AUTH-* và TEST-CLOSE-AUTH-*

Safe:
  - COMPLETED operations → giữ nguyên
  - Operations đang có OPEN session → giữ nguyên (vd SS-DEMO in-progress)
"""
from __future__ import annotations

import sys

from sqlalchemy import delete, select

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.execution import ExecutionEvent
from app.models.master import (
    ClosureStatusEnum,
    Operation,
    ProductionOrder,
    StatusEnum,
    WorkOrder,
)
from app.models.station_session import StationSession

# Prefixes của test data cũ cần xóa hẳn
_PURGE_PREFIXES = ["TEST-DT-AUTH-", "TEST-CLOSE-AUTH-"]

# Trạng thái bị stuck (không phải terminal, không phải planned)
_STUCK_STATUSES = [StatusEnum.in_progress.value, StatusEnum.blocked.value, StatusEnum.paused.value]


def _has_active_session(db, tenant_id: str, station_id: str) -> bool:
    return db.scalar(
        select(StationSession).where(
            StationSession.station_id == station_id,
            StationSession.tenant_id == tenant_id,
            StationSession.status == "OPEN",
        )
    ) is not None


def _is_test_data(op_number: str) -> bool:
    return any(op_number.startswith(p) for p in _PURGE_PREFIXES)


def audit(db) -> dict:
    ops = db.scalars(
        select(Operation).where(
            Operation.status.notin_([StatusEnum.planned.value])
        )
    ).all()

    stuck = []   # IN_PROGRESS/BLOCKED/PAUSED, no session → reset to PLANNED
    purge = []   # TEST-DT-AUTH-* / TEST-CLOSE-AUTH-* → delete entirely
    ok = []      # COMPLETED or has active session → keep

    for op in ops:
        wo = db.get(WorkOrder, op.work_order_id)
        po = db.get(ProductionOrder, wo.production_order_id) if wo else None
        event_count = db.query(ExecutionEvent).filter(
            ExecutionEvent.operation_id == op.id
        ).count()
        has_sess = _has_active_session(db, op.tenant_id, op.station_scope_value)
        row = {
            "id": op.id,
            "op_number": op.operation_number,
            "status": op.status,
            "closure": op.closure_status,
            "station": op.station_scope_value,
            "tenant": op.tenant_id,
            "events": event_count,
            "po": po.order_number if po else "?",
            "has_session": has_sess,
        }

        if _is_test_data(op.operation_number):
            purge.append(row)
        elif op.status in _STUCK_STATUSES and not has_sess:
            stuck.append(row)
        else:
            ok.append(row)

    return {"stuck": stuck, "purge": purge, "ok": ok}


def _get_po_ids_by_prefix(db) -> list[int]:
    """Lấy PO ids cần purge (có prefix trong _PURGE_PREFIXES)."""
    all_ids = []
    for prefix in _PURGE_PREFIXES:
        ids = list(db.scalars(
            select(ProductionOrder.id).where(
                ProductionOrder.order_number.like(f"{prefix}%")
            )
        ))
        all_ids.extend(ids)
    return all_ids


def do_cleanup(db, result: dict) -> None:
    # 1. Reset stuck ops → PLANNED
    stuck = result["stuck"]
    if stuck:
        stuck_ids = [r["id"] for r in stuck]
        ev_deleted = db.execute(
            delete(ExecutionEvent).where(ExecutionEvent.operation_id.in_(stuck_ids))
        ).rowcount
        ops = db.scalars(select(Operation).where(Operation.id.in_(stuck_ids))).all()
        for op in ops:
            op.status = StatusEnum.planned.value
            op.actual_start = None
            op.actual_end = None
            op.completed_qty = 0
            op.good_qty = 0
            op.scrap_qty = 0
        db.flush()
        print(f"\n[RESET] {len(stuck_ids)} stuck ops → PLANNED ({ev_deleted} events xóa)")
        for r in stuck:
            print(f"  id={r['id']} {r['op_number']} ({r['status']} → PLANNED)")

    # 2. Xóa hẳn test data cũ (PO → WO → Op + events)
    purge = result["purge"]
    if purge:
        po_ids = _get_po_ids_by_prefix(db)
        if po_ids:
            wo_ids = list(db.scalars(
                select(WorkOrder.id).where(WorkOrder.production_order_id.in_(po_ids))
            ))
            if wo_ids:
                op_ids = list(db.scalars(
                    select(Operation.id).where(Operation.work_order_id.in_(wo_ids))
                ))
                if op_ids:
                    ev2 = db.execute(
                        delete(ExecutionEvent).where(ExecutionEvent.operation_id.in_(op_ids))
                    ).rowcount
                    db.execute(delete(Operation).where(Operation.id.in_(op_ids)))
                    print(f"\n[PURGE] {len(op_ids)} test ops + {ev2} events xóa")
                db.execute(delete(WorkOrder).where(WorkOrder.id.in_(wo_ids)))
            db.execute(delete(ProductionOrder).where(ProductionOrder.id.in_(po_ids)))
            print(f"  {len(po_ids)} test POs xóa ({', '.join(_PURGE_PREFIXES)})")

    db.commit()
    print("\n✓ Cleanup hoàn tất")


def main():
    dry_run = "--dry-run" in sys.argv
    do_run = "--cleanup" in sys.argv

    if "--skip-init-db" not in sys.argv:
        init_db()
    db = SessionLocal()
    try:
        result = audit(db)
        stuck = result["stuck"]
        purge = result["purge"]
        ok = result["ok"]

        print(f"\n=== Stuck (sẽ reset → PLANNED): {len(stuck)} ops ===")
        for r in stuck:
            print(f"  id={r['id']} | {r['op_number']} | {r['status']} | {r['po']}")

        print(f"\n=== Purge (xóa hẳn test data): {len(purge)} ops ===")
        for r in purge:
            print(f"  id={r['id']} | {r['op_number']} | {r['status']} | {r['po']}")

        print(f"\n=== Giữ nguyên (COMPLETED hoặc có session): {len(ok)} ops ===")
        for r in ok:
            tag = "has_session" if r["has_session"] else r["status"]
            print(f"  id={r['id']} | {r['op_number']} | {r['status']} | {tag}")

        if not stuck and not purge:
            print("\nKhông có gì cần dọn.")
            return

        if dry_run:
            print("\n[DRY RUN] Thêm --cleanup để thực hiện.")
        elif do_run:
            do_cleanup(db, result)
        else:
            print("\nThêm --cleanup để thực hiện, hoặc --dry-run để xem trước.")
    finally:
        db.close()


if __name__ == "__main__":
    main()

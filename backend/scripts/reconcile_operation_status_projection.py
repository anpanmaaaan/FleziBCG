"""
Status projection drift audit/reconcile command.

Run this after maintenance/repair flows that append runtime execution events
to ensure operation.status projection remains aligned with event-derived truth.

Recommended runbook usage:
1) dry-run first (default)
2) review mismatch rows
3) re-run with --apply to reconcile projection

This command never mutates execution event history; it only reconciles
operation.status projection.
"""

from __future__ import annotations

import argparse
import json
from typing import TextIO

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.master import Operation, StatusEnum
from app.services.operation_service import (
    detect_operation_status_projection_mismatches,
    reconcile_operation_status_projection,
)


def _parse_operation_ids(value: str | None) -> list[int] | None:
    if not value:
        return None
    parts = [part.strip() for part in value.split(",") if part.strip()]
    if not parts:
        return None
    ids: list[int] = []
    for part in parts:
        if not part.isdigit():
            raise ValueError(f"Invalid operation id: {part}")
        ids.append(int(part))
    return ids


def _resolve_scanned_operation_ids(
    *,
    tenant_id: str,
    operation_ids: list[int] | None,
    station_scope_value: str | None,
    active_only: bool,
) -> list[int]:
    db = SessionLocal()
    try:
        statement = select(Operation.id).where(Operation.tenant_id == tenant_id)
        if operation_ids:
            statement = statement.where(Operation.id.in_(operation_ids))
        if station_scope_value:
            statement = statement.where(
                Operation.station_scope_value == station_scope_value
            )
        if active_only:
            statement = statement.where(
                Operation.status.in_(
                    [
                        StatusEnum.planned.value,
                        StatusEnum.in_progress.value,
                        StatusEnum.paused.value,
                        StatusEnum.blocked.value,
                    ]
                )
            )
        return list(db.scalars(statement.order_by(Operation.id.asc())))
    finally:
        db.close()


def run_status_projection_reconcile(
    *,
    tenant_id: str,
    operation_ids: list[int] | None = None,
    station_scope_value: str | None = None,
    active_only: bool = False,
    apply: bool = False,
    output_json: bool = False,
    out: TextIO | None = None,
) -> dict:
    out_stream = out
    if out_stream is None:
        import sys

        out_stream = sys.stdout

    scanned_operation_ids = _resolve_scanned_operation_ids(
        tenant_id=tenant_id,
        operation_ids=operation_ids,
        station_scope_value=station_scope_value,
        active_only=active_only,
    )

    db = SessionLocal()
    try:
        mismatches = detect_operation_status_projection_mismatches(
            db,
            tenant_id=tenant_id,
            operation_ids=scanned_operation_ids,
        )

        reconciled_rows: list[dict] = []
        failures: list[dict] = []
        if apply:
            mismatch_operation_ids = [int(item["operation_id"]) for item in mismatches]
            operation_by_id = {
                operation.id: operation
                for operation in db.scalars(
                    select(Operation).where(
                        Operation.tenant_id == tenant_id,
                        Operation.id.in_(mismatch_operation_ids),
                    )
                )
            }

            for mismatch in mismatches:
                operation_id = int(mismatch["operation_id"])
                operation = operation_by_id.get(operation_id)
                if operation is None:
                    failures.append(
                        {
                            "operation_id": operation_id,
                            "reason": "operation_not_found_for_tenant",
                        }
                    )
                    continue
                try:
                    reconcile_operation_status_projection(
                        db,
                        operation=operation,
                        tenant_id=tenant_id,
                    )
                    db.refresh(operation)
                    reconciled_rows.append(
                        {
                            "operation_id": operation.id,
                            "operation_number": operation.operation_number,
                            "new_snapshot_status": operation.status,
                            "derived_status": mismatch["derived_status"],
                        }
                    )
                except Exception as exc:  # pragma: no cover - defensive branch
                    failures.append(
                        {
                            "operation_id": operation_id,
                            "reason": str(exc),
                        }
                    )

        summary = {
            "tenant_id": tenant_id,
            "apply_mode": apply,
            "filters": {
                "operation_ids": operation_ids,
                "station_scope_value": station_scope_value,
                "active_only": active_only,
            },
            "total_scanned": len(scanned_operation_ids),
            "mismatch_count": len(mismatches),
            "reconciled_count": len(reconciled_rows),
            "unchanged_count": len(scanned_operation_ids) - len(mismatches),
            "failure_count": len(failures),
            "mismatches": mismatches,
            "reconciled": reconciled_rows,
            "failures": failures,
        }

        if output_json:
            out_stream.write(json.dumps(summary, indent=2, sort_keys=True) + "\n")
            return summary

        mode = "APPLY" if apply else "DRY-RUN"
        out_stream.write(f"status-projection-reconcile [{mode}]\n")
        out_stream.write(
            f"tenant={tenant_id} scanned={summary['total_scanned']} "
            f"mismatches={summary['mismatch_count']} reconciled={summary['reconciled_count']} "
            f"unchanged={summary['unchanged_count']} failures={summary['failure_count']}\n"
        )

        if mismatches:
            out_stream.write("mismatches:\n")
            for item in mismatches:
                out_stream.write(
                    "- op_id={operation_id} op_no={operation_number} "
                    "snapshot={snapshot_status} derived={derived_status}\n".format(**item)
                )
        else:
            out_stream.write("mismatches: none\n")

        if apply and reconciled_rows:
            out_stream.write("reconciled:\n")
            for item in reconciled_rows:
                out_stream.write(
                    "- op_id={operation_id} op_no={operation_number} "
                    "snapshot->{new_snapshot_status}\n".format(**item)
                )

        if failures:
            out_stream.write("failures:\n")
            for item in failures:
                out_stream.write(
                    "- op_id={operation_id} reason={reason}\n".format(**item)
                )
        return summary
    finally:
        db.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit/reconcile operation.status projection from event-derived truth."
    )
    parser.add_argument("--tenant-id", default="default", help="Tenant id to scope")
    parser.add_argument(
        "--operation-ids",
        default=None,
        help="Comma-separated operation ids (optional)",
    )
    parser.add_argument(
        "--station-scope-value",
        default=None,
        help="Optional station_scope_value filter",
    )
    parser.add_argument(
        "--active-only",
        action="store_true",
        help="Limit scan set to active snapshot statuses",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply reconciliation. Default is dry-run detect-only.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON summary",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    operation_ids = _parse_operation_ids(args.operation_ids)
    run_status_projection_reconcile(
        tenant_id=args.tenant_id,
        operation_ids=operation_ids,
        station_scope_value=args.station_scope_value,
        active_only=args.active_only,
        apply=args.apply,
        output_json=args.json,
    )


if __name__ == "__main__":
    main()

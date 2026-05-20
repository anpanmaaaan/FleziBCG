# Product Version `set_current` Governance Contract (MMD-PV-SETCURRENT-GOV-01)

## Status

`CONTRACT_PROPOSED_READY_FOR_HUMAN_REVIEW`

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-20 | v0.1 | PO-SA agent draft. Contract only — no implementation, no migration applied. |

---

## 1. Why this contract exists

Per `mmd-bom-pv-binding-baseline-01-freeze-handoff.md` §14 row 2 and §15 rule 1, `is_current` on `ProductVersion` is **advisory only** today. Partial-unique enforcement is deferred. No setter, no UI control, no event.

Source inspection (2026-05-20) confirms:

- `backend/app/models/product_version.py:33` — comment “is_current is advisory; partial-unique enforcement is deferred.”
- `backend/app/models/product_version.py:57` — `is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)`.
- `backend/alembic/versions/0007_product_versions.py` — original migration that added the field.
- `backend/app/services/product_version_service.py:204` — new PVs are created with `is_current=False`.
- `backend/app/services/product_version_service.py:54` — `can_retire=(status in ("DRAFT", "RELEASED") and not row.is_current)`.
- `backend/app/services/product_version_service.py:385` — `if row.is_current: raise ValueError("Current product version cannot be retired")`.
- `grep is_current` returns **no hits** in: any execution service / API, any APS code, the product event registry, the action code registry.

**Consequence**: `is_current` has an in-MMD retire-blocking consumer but no setter — meaning the consumer never fires in production. The flag is a dangling field. P0-C Execution will need a deterministic “current version per product” concept before it can pick a routing/BOM target. Without governance, agents will be tempted to flip the flag via PATCH or write ad-hoc `set_current` endpoints.

This contract closes that ambiguity by defining the rules **before** implementation, in the spirit of Hard Mode MOM v3.

---

## 2. Scope

### 2.1 In scope (governance only — no code)

- The semantics of `is_current`: who can be true, when, what it means downstream.
- The command(s) by which `is_current` becomes true / false.
- Authorization, lifecycle preconditions, cardinality invariant.
- Event emission and audit posture.
- Cross-domain boundary guardrails.
- Migration proposal for partial-unique enforcement (proposed, NOT applied).
- Reconciliation rule for existing data (today: all rows are false, so no backfill conflict).

### 2.2 Out of scope (do NOT bundle into the implementation slice)

- Automatic current-version selection on release. (Future contract.)
- Multi-plant / scope-aware “current” (i.e., one current per (tenant, plant, product)). (MMD-SCOPE-APPLICABILITY-01.)
- Effective-dating of currentness. (Future contract.)
- Execution / APS pickup logic. (P0-C / P2-B scope.)
- BOM “current” mirroring. (Out of scope; BOM currentness is governed by BOM↔PV binding.)
- ERP “current item” sync. (P1-A.)

---

## 3. Semantics

### 3.1 Definition

For a given `(tenant_id, product_id)`, **at most one ProductVersion row** may have `is_current = true` at any moment. The current version is the deterministic pointer used by downstream consumers (execution scheduling, planning lookup, BOM-binding presentation) to answer “which version is in production right now?”.

### 3.2 Lifecycle precondition

- `is_current = true` is permitted ONLY when `lifecycle_status = "RELEASED"`.
- Setting `is_current = true` on a DRAFT or RETIRED PV is rejected.
- Releasing a PV does NOT automatically set it as current. (Automatic selection is a separate future contract.)
- Retiring the current PV is forbidden (already enforced at line 385 of `product_version_service.py`).
- Unsetting current (`is_current = true` → `false`) is permitted via the same command; recommended only as part of a switch (`set_current` on a different PV atomically clears the previous).

### 3.3 Cardinality invariant

```
For each (tenant_id, product_id): COUNT(*) WHERE is_current = true ≤ 1
```

Enforced at two levels (defense in depth):

1. **Service layer** — `set_current` service function reads existing current (if any) within the same DB transaction and clears it before setting the new one. Uses `SELECT … FOR UPDATE` on the product's PV rows.
2. **Database layer** — Postgres **partial unique index**:
   ```sql
   CREATE UNIQUE INDEX uq_product_version_current_per_tenant_product
     ON product_versions (tenant_id, product_id)
     WHERE is_current = true;
   ```
   This is a partial index — only rows where `is_current = true` are indexed, so unsetting does not violate uniqueness, and the index does not blow up on the (currently very many) `false` rows.

### 3.4 Atomicity

`set_current` and the implicit clear of the previous current MUST occur in a single DB transaction. The partial-unique index protects against concurrent inserts/updates that would race to set two PVs current.

---

## 4. Command surface

### 4.1 Command name

`set_product_version_current` (alternatively expressed at the API as `POST /api/v1/products/{product_id}/versions/{version_id}/set-current` and `POST .../clear-current`).

Recommended API shape:

| Method | Path | Body | Response |
|---|---|---|---|
| `POST` | `/api/v1/products/{product_id}/versions/{version_id}/set-current` | `{}` (empty) | 200 with updated PV; capability fields refreshed |
| `POST` | `/api/v1/products/{product_id}/versions/{version_id}/clear-current` | `{}` (empty) | 200 with updated PV (now `is_current=false`); capability fields refreshed |

Notes:

- A separate `clear-current` route avoids ambiguity vs. PATCH (which historically updates many fields). Mirrors the binding API design.
- `set-current` is idempotent on the same PV: calling it on the already-current PV returns 200 unchanged and emits no event.
- `set-current` on another PV in the same product clears the previous current within the same transaction.

### 4.2 Authorization

| Action | Required action code | AND-semantics? | Reasoning |
|---|---|---|---|
| `set-current` | `admin.master_data.product_version.manage` | NO (single action) | Set-current is an intra-PV state change; no other domain is mutated. Adding `product.manage` would be over-restrictive — product-header is the entity that *contains* PVs, not a co-owner of the current pointer. **Opinion (PO-SA):** keep single-action. |
| `clear-current` | same | NO | Symmetric. |

This matches the pattern of `release`/`retire` on PV which already require only `product_version.manage` and not `product.manage`.

### 4.3 Lifecycle preconditions enforced server-side

- `set-current` rejects when PV `lifecycle_status != "RELEASED"` → HTTP 422.
- `set-current` rejects when PV is soft-deleted (if applicable) → HTTP 422.
- `clear-current` rejects when PV is not currently `is_current = true` → HTTP 409.
- Concurrent `set-current` from two callers on different PVs within the same product → one succeeds, the other gets HTTP 409 (race resolved by DB partial-unique index).

### 4.4 Idempotency

- `set-current` on already-current PV: HTTP 200, no event emitted, no audit log row.
- `clear-current` on already-not-current PV: HTTP 409 (explicit conflict; prevents silent no-ops in scripts).

---

## 5. Capability surface

Add to PV response:

```json
{
  ...,
  "allowed_actions": {
    "can_release": true,
    "can_retire": false,
    "can_set_current": true,
    "can_clear_current": false
  }
}
```

Computation:

| Capability | Conditions |
|---|---|
| `can_set_current` | caller has `product_version.manage` AND `lifecycle_status = "RELEASED"` AND `is_current = false` AND no soft-delete |
| `can_clear_current` | caller has `product_version.manage` AND `is_current = true` |

Note that `can_set_current = true` does NOT require the absence of another current PV in the same product — the set-current command itself handles the clear-then-set atomically. If the caller cannot mutate the other PV (e.g., row-level scope restriction), the partial-unique index will reject and the call returns 409. This rare error path must be surfaced in FE as “another version is currently active”.

Page-level capability on the product detail (or PV list) endpoint:

```json
{
  ...,
  "product_version_capabilities": {
    "can_create": true,
    "can_set_current_anywhere": true   // NEW
  }
}
```

`can_set_current_anywhere` is true iff caller has `product_version.manage` and at least one RELEASED PV exists for the product.

---

## 6. Event emission

Add to `docs/design/02_registry/product-event-registry.md`:

| Event | Emitted when |
|---|---|
| `PRODUCT_VERSION.SET_CURRENT` | `set-current` succeeds on a PV that was not already current. Payload includes `tenant_id`, `product_id`, `product_version_id`, `previous_current_product_version_id` (nullable), `actor_user_id`, `occurred_at`. |
| `PRODUCT_VERSION.CLEAR_CURRENT` | `clear-current` succeeds. Payload includes `tenant_id`, `product_id`, `product_version_id`, `actor_user_id`, `occurred_at`. |

Both events are CANONICAL_FOR_P0_B addition; registry must be patched in the implementation slice.

Audit: `record_security_event()` writes one entry per successful command. Idempotent no-ops emit nothing (consistent with binding-baseline §11 “Blocked release emits no event”).

---

## 7. Cross-domain boundary guardrails

| Boundary | Rule | Reason |
|---|---|---|
| `set-current` ↔ Execution / APS | Setting current must NOT trigger execution dispatch, work order creation, APS replan, or any side effect outside PV. | MMD command must not become an execution trigger. P0-C consumers may read `is_current`; that is a pull, not a push. |
| `set-current` ↔ BOM / BOM binding | Setting current must NOT mutate BOM bindings. Binding is a separate governed entity. | Binding lifecycle is owned by `mmd-bom-pv-binding-baseline-01`. |
| `set-current` ↔ Product header | Product header is not mutated. | Product header has its own action code and lifecycle. |
| `set-current` ↔ ERP | No ERP posting. | ERP integration is P1-A. |
| `set-current` ↔ Traceability / Quality | No traceability or quality event emitted. | Cross-domain coupling forbidden. |

These mirror the binding-baseline §15 do-not-do rules and must be assertion-tested in the implementation slice.

---

## 8. Migration proposal (NOT applied in this slice)

```sql
-- 0020_product_version_partial_unique_current.sql (proposed)
-- Adds a partial unique index on (tenant_id, product_id) WHERE is_current = true.
-- Safe at apply time because all existing rows have is_current = false (verified
-- by the existing service code that creates PVs with is_current=False and never sets true).

CREATE UNIQUE INDEX CONCURRENTLY uq_product_version_current_per_tenant_product
  ON product_versions (tenant_id, product_id)
  WHERE is_current = true;
```

Constraints:

- `CONCURRENTLY` to avoid table lock on large tenants (Postgres-only — Alembic supports via `op.create_index(..., postgresql_concurrently=True)`).
- Alembic transaction handling: this index must be created **outside** an autocommit transaction. The migration script must set `transaction_per_migration = False` or use `op.execute("COMMIT")` patterns. Alembic-on-Postgres pattern reference required in the implementation slice.
- Down migration: `DROP INDEX CONCURRENTLY IF EXISTS uq_product_version_current_per_tenant_product;`.

The migration head will advance from current `0019` (Quality) to `0020`. The implementation slice MUST verify it does not collide with any in-flight Quality migration patch.

### 8.1 Backfill rule

No backfill required for v0.1 of this contract — all existing `is_current` rows are `false`. If at some future point this assumption no longer holds (e.g., data import seeds current versions), the implementation slice must add a backfill assertion: at most one `is_current = true` row per `(tenant_id, product_id)` BEFORE the index is created, else the index creation fails.

---

## 9. Frontend impact

- ProductDetail (PV table): add **Set Current** / **Clear Current** buttons per row, gated by `allowed_actions.can_set_current` / `can_clear_current`.
- Visual indicator: show a “CURRENT” badge on the row where `is_current = true`. Style consistent with existing lifecycle badges.
- Error mapping: 409 on race → toast “Another version became current. Refreshing…”; FE refetches PV list.
- i18n: en + ja keys for: `Set Current`, `Clear Current`, `Current`, race-condition message, RELEASED-precondition message.
- No lifecycle-status inference — buttons consume only `allowed_actions.*`.

---

## 10. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Partial-unique index creation deadlock on a large `product_versions` table | LOW | MEDIUM | `CREATE INDEX CONCURRENTLY`; document Alembic pattern. |
| Service-layer race condition between `SELECT FOR UPDATE` and partial-unique-index rejection on different DB nodes | LOW | LOW | Single-leader Postgres; both layers reject concurrent contention. |
| FE allows clicking “Set Current” twice quickly → second call returns 200 idempotent | LOW | LOW | Idempotent server-side; FE disables button during in-flight call. |
| Setting current triggers a downstream side effect that nobody expected | LOW | HIGH | Explicit guardrails in §7; assertion tests in implementation slice. |
| Operators interpret CURRENT as “release” and start production on a non-released version | n/a | n/a | Cannot happen — set-current is rejected unless RELEASED. |
| Adding `is_current` enforcement breaks existing PV release tests | LOW | LOW | Existing tests do not exercise `set-current`; release path is unchanged. |
| Some future MMD-SCOPE-APPLICABILITY-01 redefines “current per plant” | MEDIUM | MEDIUM | This contract explicitly scopes “current per (tenant, product)”. Plant-scoped current is a NEW contract; this one does not block that future contract because plant-scope adds an axis, not redefines the existing pair. |

---

## 11. Acceptance criteria for this contract

- Reviewed by lead PO/architect (An).
- Reviewed by DB lead for the partial-unique-index pattern (especially the `CONCURRENTLY` + Alembic combination).
- Reviewed by execution/APS leads for the “no automatic selection” decision (explicit opt-out).
- Reviewed by ISA-95 alignment lens: setting current does NOT change Product Definition object identity; it is a presentation-layer pointer that downstream consumers may read.
- All §7 boundary guardrails listed; agreed not to be relaxed in the implementation slice.

When all five are signed off, status moves from `CONTRACT_PROPOSED_READY_FOR_HUMAN_REVIEW` to `CONTRACT_APPROVED_READY_FOR_IMPLEMENTATION`.

---

## 12. Implementation slice handoff

When this contract is approved, open implementation slice **`MMD-PV-SETCURRENT-IMPL-01`** with the following skeleton:

> Implement `set-current` / `clear-current` for ProductVersion per
> `docs/design/02_domain/product_definition/product-version-set-current-governance-contract.md`.
> Add capabilities + buttons in FE. Add Alembic migration 0020 with partial-unique
> index (CONCURRENTLY). Add events to product-event-registry. Write capability-matrix
> BE tests; write FE regression Section for the new buttons.
>
> **Read first (ack each by name in first reply):**
> 1. This contract (above)
> 2. `docs/audit/mmd-bom-pv-binding-baseline-01-freeze-handoff.md` (pattern reference)
> 3. `docs/audit/mmd-master-baseline-01-freeze-handoff.md` (do-not-do rules)
> 4. `docs/ai-skills/hard-mode-mom-v3/SKILL.md`
>
> Verification gates (paste exit codes — required by `feedback_pass_claims_need_exit_code`):
> ```powershell
> g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_product_version_foundation_api.py tests/test_mmd_rbac_action_codes.py tests/test_alembic_baseline.py
> cd g:\Work\FleziBCG\frontend
> npm.cmd run check:mmd:read
> npm.cmd run build
> npm.cmd run lint
> npm.cmd run lint:i18n:registry
> ```
>
> Stop conditions:
> - If applying the partial-unique index fails because data contains a `(tenant_id, product_id)` with multiple `is_current = true` rows → halt; this contract assumed all-false baseline.
> - If any test in `test_product_version_foundation_api.py` regresses → halt.
> - If FE adds lifecycle-status inference anywhere → halt.

---

## 13. Definition of Done (this contract slice)

- ✅ Contract published with verdict `CONTRACT_PROPOSED_READY_FOR_HUMAN_REVIEW`.
- ✅ All sections of the PO-SA decision format completed (Verdict implicit in §1–§11; Recommended Decision in §12; Scope in §2; Architecture/Product Impact in §3–§9; Risks in §10; Next Agent Prompt in §12; DoD in §13).
- ✅ Risk register lists migration concurrency + partial-unique-on-multi-tenant pattern note.
- ✅ Acknowledged that `is_current` already has an in-MMD retire-blocking consumer (§1 evidence) — contract does not break that behavior.
- ✅ No source code changed in this slice.

End of MMD-PV-SETCURRENT-GOV-01 v0.1.

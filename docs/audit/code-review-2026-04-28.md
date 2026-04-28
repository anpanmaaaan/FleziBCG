# Code Review: FleziBCG MOM Platform — Full Source Code

**Reviewer:** Engineering code-review skill
**Date:** 2026-04-28
**Scope:** `backend/app/**`, `backend/scripts/**`, `frontend/src/**`, `docker/**`, `.github/**`
**Truth baseline:** `.github/agent/AGENT.md`, `docs/design/**`, `docs/governance/CODING_RULES.md` v2.0, `docs/design/10_hardening/**`

---

## Summary

The repo has solid layering bones (route → service → repository), event-driven execution semantics, an explicit RBAC + impersonation + approval model, and i18n discipline on the frontend. However, several **canonical hardening rules from `CODING_RULES.md` v2.0 are violated by the live code path**, including some that the design pack expressly calls out as P0-A blockers. The most consequential issues are (1) a cross-tenant data leak in the global-operations stats path, (2) JWT stored in `localStorage`, (3) `Base.metadata.create_all()` + ad-hoc SQL splitter as the actual schema manager despite Alembic being declared canonical, (4) a default JWT secret that is silently used when env is unset, (5) repository-owned transactions producing two-phase commits between event log and snapshot, and (6) `CORS` / rate-limit baselines that are simply not implemented. Verdict: **Request Changes** before any further P0 build-out.

---

## Critical Issues

| # | File | Line | Issue | Severity |
|---|------|-----:|-------|----------|
| 1 | `backend/app/repositories/operation_repository.py` | 32–41 | `get_operations_by_names` has **no `tenant_id` filter**. Called from `services/global_operation_service.py:131` to compute `delay_count`, `delay_frequency`, `repeat_flag`, `qc_fail_count`, `often_late_flag`. Result: tenant A's "STEP_001" history is mixed with every other tenant's operations sharing that name. **Cross-tenant data leak**, directly violates `CODING_RULES.md` §7.1 "no repository method may execute tenant-blind access to tenant-owned entities". | 🔴 Critical |
| 2 | `backend/app/repositories/operation_repository.py` | 18–29 | Companion: `get_operations_by_numbers` is also tenant-blind. Currently unused by routes but exported and ready to be the next foot-gun. | 🔴 Critical |
| 3 | `frontend/src/app/auth/AuthContext.tsx` | 23, 32, 35 | JWT access token is persisted in `window.localStorage` under `mes.auth.token`. Directly violates `CODING_RULES.md` §14.4 "**Forbidden: storing JWT in Zustand or localStorage**" and exposes the token to any XSS payload. | 🔴 Critical |
| 4 | `backend/app/config/settings.py` | 22 | `jwt_secret_key: str = "change-me"`. The accompanying comment claims this "fails auth" if forgotten, but `decode_access_token` happily verifies any token signed with `"change-me"`. A misconfigured prod deploy will silently issue and accept tokens with a publicly known secret. Boot must hard-fail when `app_env != "dev"` and the default is in effect. | 🔴 Critical |
| 5 | `backend/app/db/init_db.py` | 38–64 | Production schema is bootstrapped via `Base.metadata.create_all(bind=engine)` followed by a hand-rolled `_apply_sql_migrations()` that splits files on `;`. Violates `CODING_RULES.md` §10.3 "**`Base.metadata.create_all()` must not be used as production schema management**" and §25 P0-A scope guard ("introduce/use Alembic"). Alembic 1.18.4 is in `requirements.txt` but no `alembic.ini`, `versions/`, or `env.py` exists. The naive `;` splitter will also corrupt any future migration containing a function body, `DO $$ ... $$`, or string literal containing `;`. | 🔴 Critical |
| 6 | `backend/app/main.py` | 19–32, 50–52 | No `CORSMiddleware`. With frontend served on `:80` and backend on `:8010` (per `docker-compose.yml`), all cross-origin requests are blocked in browser, but more importantly there is no explicit allowlist posture, contradicting `CODING_RULES.md` §17.4 "default deny; allowed origins are explicit per environment" and §23.7 "CORS allowlist explicit". Reverse-proxying via nginx hides the gap in the docker stack but exposes it the moment any tenant deploys without nginx. | 🔴 Critical |
| 7 | `backend/app/api/v1/auth.py` | 31–51 | `/api/v1/auth/login` has **no rate limiting** of any kind (no SlowAPI, no Redis, no in-memory bucket). Same for `/auth/logout-all` and admin session revoke. Violates `CODING_RULES.md` §17.5, where login is mandated at 5/15min per-IP+per-username. | 🔴 Critical |
| 8 | `backend/app/repositories/operation_repository.py` + `backend/app/repositories/execution_event_repository.py` | repo: 99, 117, 126, 135, 147, 160, 177, 196; events: 27 | **Repositories own transactions and double-commit per command.** `start_operation`, `complete_operation`, `pause_operation`, etc. each call `create_execution_event` (commits) **then** `mark_operation_*` (commits again) — two distinct transactions per "atomic" mutation. Violates `CODING_RULES.md` §5.1/§5.3/§10.1 ("Service layer owns transaction boundaries"). Operationally: an OS-level interrupt or DB blip between the event commit and the snapshot commit leaves the event log ahead of the snapshot, making the very `INVARIANT: Event is appended before the snapshot is updated` comment in `operation_service.py:981` *aspirational rather than enforced*. | 🔴 Critical |

---

## High-Severity Issues

| # | File | Line | Issue | Category |
|---|------|-----:|-------|----------|
| 9 | `backend/app/services/work_order_execution_service.py` | 82 | `now = datetime.utcnow()` — deprecated in Py3.12, returns naive UTC. Violates §10.8 "Avoid naive datetimes in persisted operational truth". | Correctness |
| 10 | `backend/app/services/operation_service.py` | 950, 1014, 1065, 1069, 1122, 1124, 1195 | All execution state guards are evaluated against `operation.status` (the snapshot column) rather than the derived projection. The platform's stated truth model says snapshot is a cache and the event log is authoritative. If `reconcile_operation_status_projection` ever lags or fails, the guards reject *or* admit transitions based on stale state. The very fact that a `reconcile_*` reconcile path exists (`scripts/reconcile_operation_status_projection.py`) confirms drift is anticipated. | Correctness |
| 11 | `backend/app/repositories/operation_repository.py` | 191 | `operation.reopen_count = (operation.reopen_count or 0) + 1` is read-modify-write without `with_for_update()` or atomic UPDATE. Concurrent reopen attempts on the same operation race; last writer wins. The reopen path also doesn't lock the operation row before incrementing. | Correctness / Concurrency |
| 12 | `backend/app/repositories/execution_event_repository.py` | 32–41 | Function comment claims `id` is used as a tiebreaker but the `order_by` is `created_at` only. Sub-millisecond inserts can return events in non-deterministic order, causing `_derive_status` to produce flapping results. The work-order variant on line 51–53 *does* include `ExecutionEvent.id`; the per-operation variant must too. | Correctness |
| 13 | `backend/app/services/operation_service.py` | start: 975, complete: 1074 | `request.started_at` / `request.completed_at` are accepted from the client and persisted without validation against `_utcnow_naive()` or sanity bounds. Allows backdating events. Violates §10.8 "`recorded_at` must be generated by trusted backend/database clock". `recorded_at` and `occurred_at` are not separated in the event payload. | Security / Correctness |
| 14 | `backend/app/api/v1/operations.py` | 314, 345 | Hardcoded `if _effective_role_code(identity) != "SUP"` checks duplicate authorization logic that belongs in the RBAC layer. Violates §23.1 "no duplicated authorization logic" and the layering rule that routes stay thin. The same role check is also expressed as `require_action("execution.close")` — making this either a contradiction or dead code. | Maintainability / Auth |
| 15 | `frontend/src/app/pages/OEEDeepDive.tsx`, `ProductionTracking.tsx`, `RouteList.tsx` | imports of `@/app/data/mockData`, `@/app/data/oee-mock-data` | Mock data is imported into pages that ship to production. `SOURCE_STRUCTURE.md` §4 marks `data/` as "Mock-only development data". Frontend cannot present uncertain/mock output as system fact (§18.1, §14). At a minimum these pages must be feature-flagged out of the prod bundle or wired to real APIs. | Correctness |
| 16 | `backend/app/services/dashboard_service.py` (`get_work_orders_for_dashboard`), `backend/app/repositories/dashboard_repository.py` | dashboard repo loads all WOs unbounded | The dashboard endpoint pulls **every** work order for the tenant on every page load, no pagination, no filter. Same for `read_production_orders` in `api/v1/production_orders.py`. Violates `CODING_RULES.md` §9.5 (master-data endpoints use offset-based pagination, default size 50, max 200). At plant scale (10k+ WOs) this is a performance and memory cliff. | Performance |
| 17 | `backend/app/services/operation_service.py` | 752 | `derive_operation_detail` calls `get_events_for_operation` and processes the entire history — unbounded. A long-running operation with thousands of `QTY_REPORTED` events pays O(n) on every detail GET. Even the snapshot columns (`good_qty`, `scrap_qty`) are *already maintained*, but the function recomputes them from events. | Performance |
| 18 | `frontend/src/app/components/Layout.tsx`, `frontend/src/app/pages/LoginPage.tsx`, `frontend/src/app/components/TopBar.tsx` | Layout: 47, 50, 53, 55; LoginPage: 50, 33 | Hardcoded user-facing text: `"Dashboard"`, `"Global Operations"`, `"Station Execution"`, `"MES Lite"`, `"Sign in to MES Lite"`, `"Login failed. Please try again."`. Violates `CODING_RULES.md` §2.6 mandatory rules. The `lint:i18n:hardcode` script intentionally only scans `./src/app/pages` for a narrow grep set, so it doesn't catch `components/Layout.tsx` or string returns. The lint is not actually enforcing the rule it claims to. | i18n |
| 19 | `backend/app/security/auth.py` | 68–76 | `_verify_password` falls back to plaintext string equality if the stored value doesn't start with `$2`, `$argon2`, or `$pbkdf2`. Comment says "Plain comparison is intentional for the config path only." But the function is also reused from `authenticate_user_db`, where `user.password_hash` is the DB column. If any code path ever stores an unhashed password (admin import, bug, env-driven seed) the system silently accepts plaintext credentials. Footgun masquerading as a feature. | Security |
| 20 | `backend/scripts/migrations/0001_rbac_core.sql` vs `backend/app/models/rbac.py` | model adds `tenant_id`, `role_type`, `base_role_id`, `owner_user_id`, `review_due_at`, `is_active`; migration 0001 doesn't | The SQL migrations declare a leaner schema than the SQLAlchemy models. The system papers over this with `Base.metadata.create_all()` running first to fill in missing columns, then SQL `ALTER TABLE` bumps in later files. This is the exact anti-pattern §10.3 forbids and means production DB and dev DB schemas diverge depending on init order. With Alembic missing, there's no migration linearization at all. | Migration |
| 21 | `README.docker.md` | 67–69 | CloudBeaver credentials committed in plain text (`flelibcg` / `beniceSCM2026`). Even if dev-only, §17.1 says "no secrets in repo" without exception. Combined with §23.6 ("no CloudBeaver in production runtime") and §25 P0-A guard ("CloudBeaver dev-only posture"), the `docker-compose.yml` ships CloudBeaver at the same orchestration tier as prod services. | Security |
| 22 | `backend/app/services/operation_service.py`, all command handlers | 191, 593, 596 etc. | Multiple in-loop `db.commit()` calls inside `start_downtime` (lines 191, 596) and the projection reconcile path. Each commit is a separate transaction, increasing the chance of partial state and producing audit logs split across transactions. | Correctness |

---

## Medium-Severity Issues

| # | File | Line | Issue | Category |
|---|------|-----:|-------|----------|
| 23 | `backend/app/main.py` | 14–16 | `@app.on_event("startup")` is deprecated (FastAPI 0.93+). Move to `lifespan` context manager. | Maintainability |
| 24 | `backend/app/main.py` | 19–28 | The auth middleware decodes the JWT on every request including `/health`, `/openapi.json`, static-like paths. Move JWT decoding into a route dependency rather than global middleware to avoid wasted CPU on liveness probes. | Performance |
| 25 | `backend/app/security/auth.py` (`_settings`), `backend/app/security/rbac.py` (`_load_default_users`) | 28–29, 103–104 | New `Settings()` is constructed on every call, re-reading env files. The module-level `settings` singleton in `db/session.py` is what the rest of the system uses. Pick one or the other. | Maintainability |
| 26 | `backend/app/models/master.py` | 44, 45, 71, 72, 73, 74, 117, 118, 121, 122, 123, 124 | `DateTime` columns on `Operation`/`WorkOrder`/`ProductionOrder` are declared without `timezone=True`. `_utcnow_naive()` exists explicitly to strip tzinfo so values "land cleanly" — i.e. the schema baked in naive datetimes. Combined with `DateTime(timezone=True)` on audit/session tables, this gives the system a split-personality datetime story and reliably produces aware/naive comparison errors (note the `_normalize_dt`, `_align_for_diff` helpers across the code base). Long-term direction per §10.8 is timezone-safe; migrate. | Correctness |
| 27 | `backend/app/services/impersonation_service.py` | 22 | `MAX_DURATION_MINUTES = settings.impersonation_max_duration_minutes` is captured at import time. If settings ever reload (test fixtures, env override), the captured value is stale. Read from `settings` at call time. | Correctness |
| 28 | `backend/app/api/v1/production_orders.py` | 105–117 | `read_production_order` does up to two DB queries (`isdigit()` then number lookup) on every request. Fold into a single `OR` query or branch decisively. | Performance |
| 29 | `backend/app/services/global_operation_service.py` | 124–253 | `build_work_order_operation_summaries` performs O(N×H) work in Python where N is the WO operation count and H is the historical operation count by name. Cycle/delay derivation iterates `historical_cycle_minutes` twice and recomputes per operation. With the §7 tenant-leak fixed, also consider a single grouped SQL aggregation rather than per-operation list comprehensions. | Performance |
| 30 | `backend/app/services/impersonation_service.py` | 174–189 | `log_impersonation_permission_use` swallows all exceptions from the audit write. Comment justifies it ("a failed audit write must not block the permission-gated operation itself") — but this directly conflicts with §16.3 "Auditable operations" and §12.3 "impersonation must be fully audited". A dropped audit row should at least raise an alert / structured log error of severity ERROR, not just a logger.exception. | Auditability |
| 31 | `backend/app/services/operation_service.py` | 64, 132 | `if operation.tenant_id != tenant_id: raise StartDowntimeConflictError("TENANT_MISMATCH")` checks tenant inside the service, but the route also checks tenant. Two places of truth. Belongs in repository / dependency layer once. | Maintainability |
| 32 | `backend/app/services/session_service.py` | 14, 53 | `expires_at = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)` ties the **session** lifetime to the access-token lifetime. Per §11.2 access tokens are 15 min, refresh tokens 7 days; the session is a different thing. With the current default (480 min ≈ shift), tokens and sessions are aligned, but once refresh tokens are introduced the session must outlive the access token. | Auth |
| 33 | `frontend/src/app/api/httpClient.ts` | 99–104 | `fetch` has no AbortController-based timeout, no retry/backoff, and no correlation-id propagation. Compare with `CODING_RULES.md` §16 (correlation IDs), §9.4 (`correlation_id` mandatory on errors). | Observability |
| 34 | `frontend/scripts/check_i18n_hardcode.sh` | 9–14 | The "i18n hardcode lint" only scans `./src/app/pages` and only for a narrow set of grep patterns — JSX text nodes only, no template literals, no `aria-label`, no `placeholder`, no string returns. It misses every violation in `Layout.tsx` (which is in `components/`) and the static `"MES Lite"` return on line 55. Either expand the scanner or move enforcement to AST-based ESLint. | Maintainability |
| 35 | `backend/app/services/operation_service.py` | 244 | `_ensure_operation_open_for_write` raises `ClosedRecordConflictError("STATE_CLOSED_RECORD")` without an `i18n` message key. The whole error-shape strategy is `HTTPException(detail=str(exc))`, which violates §9.4 "RFC 9457 Problem Details with FleziBCG extensions" — the responses do not include `type`, `title`, `code`, `correlation_id`, or `instance`. None of the routes return the shape the design pack mandates. | API Contract |
| 36 | `backend/app/api/v1/*.py` | every route | No `Idempotency-Key` handling on any command-style mutation endpoint. `start_operation`, `complete_operation`, `claim_operation`, `start_downtime`, etc. are all retried-unsafe under network blips. Violates §9.7. | API Contract |
| 37 | `backend/app/api/v1/*.py` | every route | All routes return raw `HTTPException(detail="...")` strings, often human-readable English. Violates §9.3 "Backend returns codes, not translated labels" — need `code` enums (the `STATE_*` strings exist in the service layer but never reach the wire). | API Contract / i18n |
| 38 | `backend/scripts/migrations/0009_station_claims.sql` | 24 | `operation_id INTEGER NOT NULL REFERENCES operations(id)` — no `ON DELETE` clause. If an operation is ever physically deleted (e.g. tenant offboarding), the FK violates. The 0001_rbac_core migration uses `ON DELETE CASCADE` consistently; this one doesn't. Pick a policy. | Migration |
| 39 | `backend/app/api/v1/iam.py` | 73–94 | `create_tenant_custom_role` permits any user with the `admin.user.manage` action to create roles that mirror the *base role's* permission set (line 165–182 in `services/iam_service.py`). The protection against `admin.*` actions only catches namespace prefixes, not `EXECUTE`-family escalation. A custom role with base `OPR` can then be granted `EXECUTE` to any user. Add a least-privilege ceiling check. | Auth |
| 40 | `backend/app/services/station_claim_service.py` | 144–169 | `_expire_claim_if_needed` writes to the audit log but the surrounding `db.commit()` is in the caller; if the caller raises before commit, expired-claim audit rows are lost. Wrap in service-level transaction boundary. | Auditability |

---

## Low-Severity Notes

- `backend/app/models/master.py:1` — `from app.models.execution import ExecutionEvent` is imported at top-level and then again under `TYPE_CHECKING` in `execution.py`. The eager import works but couples the two modules tighter than necessary.
- `backend/app/main.py:34–48` — i18n exception handler is registered, but no route uses `I18nHTTPException`. The whole i18n error-message infra is dead code today.
- `frontend/src/app/App.tsx:14–24` — Suppressing Recharts warnings by globally monkey-patching `console.error` is a known smell. Wrap or replace the chart instead.
- `frontend/package.json` — `name: "@figma/my-make-file"` and `"version": "0.0.1"` are placeholder values.
- `backend/Dockerfile` — `pip install --no-cache-dir -r requirements.txt` uses requirements.txt only; no `pip-audit` step despite §17.6 / §4.6 saying it should run when configured.
- `backend/app/main.py` — no `/health/ready` vs `/health/live` separation; the single `/health` returns `{"status": "ok"}` whether or not the DB is reachable. Add a readiness probe that pings the DB.
- `backend/app/services/work_order_execution_service.py:60–79` — recompute scans all operations in Python; for large WOs use a single SQL aggregate.
- `frontend/nginx.conf` — no `add_header Strict-Transport-Security`, `X-Content-Type-Options nosniff`, `X-Frame-Options DENY`, `Content-Security-Policy`, `Referrer-Policy`. Required for prod.
- `frontend/src/app/components/GanttChart.tsx` — 1201 LOC, single file. Past the 800-line "smell" line for a React component.
- Test suite uses `app.dependency_overrides` to bypass real auth (e.g. `tests/test_close_operation_auth.py`). Tests verify routing, not the actual `require_action` security path.
- `backend/scripts/seed/*` runs unconditionally via `init_db()` on app startup. There's no `app_env != "prod"` guard. Demo users `admin / password123` will boot in any environment that lets the app start with default config.

---

## What Looks Good

- **Layering is largely clean.** Routes are mostly thin wrappers over services; services contain business logic; repositories isolate queries. The handful of exceptions are called out above (§14, §31).
- **Impersonation model is rigorous.** `FORBIDDEN_ACTING_ROLES`, `ALLOWED_IMPERSONATORS`, the requester-≠-decider rule using the *real* user_id under impersonation (`approval_service.decide_approval_request:161`), and the audit log per permission use are all on point.
- **Append-only event log + projection split** is the right shape. `derive_operation_runtime_projection_for_ids` is well-factored and uses a single SQL `GROUP BY` for status counts plus a window-function subquery for last-event derivation.
- **Comment hygiene is excellent.** The `WHY:` / `INVARIANT:` / `EDGE:` prefix discipline from §19.3 is consistently applied across the touched files. Reading `services/operation_service.py` is markedly easier than typical FastAPI code of similar size because of this.
- **Claim model is properly locked.** `_get_unreleased_claim_for_update` and `_get_operator_unreleased_claims_for_station_for_update` use `with_for_update()`. Lazy expiry on read avoids scheduler clock-skew races.
- **i18n key registry parity check** (`check_i18n_registry_parity.mjs`) is exactly the right safety net for the en/ja split and is wired into CI (`.github/workflows/frontend-i18n.yml`).
- **Approval rules are DB-driven**, not code-driven, with tenant-specific overrides via `tenant_id="*"` wildcard semantics.
- **`derive_operation_runtime_projection_for_ids`** correctly tenant-filters and uses a deterministic last-event signal.

---

## Verdict

**Request Changes.** The repo is on the right architectural track but the gap between `CODING_RULES.md` v2.0 and the live code is too wide to merge a follow-up P0-A slice without first closing the tier-1 violations.

**Minimum bar before next P0-A PR (do these together as one Architecture/Contract PR):**

1. Add `tenant_id` to `get_operations_by_names` / `get_operations_by_numbers` and any caller. Add a regression test that proves cross-tenant isolation.
2. Move JWT off `localStorage`. Switch to in-memory + a refresh-token http-only cookie path, or accept a documented dev-only carve-out behind an explicit env flag with a hard CSP that mitigates XSS.
3. Make startup hard-fail when `app_env != "dev"` and `jwt_secret_key == "change-me"` (or any of: empty, < 32 bytes, default).
4. Stand up Alembic. Replace `Base.metadata.create_all() + _apply_sql_migrations()` with `alembic upgrade head` at startup. Linearize the existing `0001_*.sql … 0012_*.sql` files into Alembic revisions.
5. Add `CORSMiddleware` with an env-driven allowlist; default deny.
6. Add login rate limiting (in-process token bucket is fine for P0-A; do not introduce Redis just for this).
7. Push `db.commit()` out of repositories; let services own transaction boundaries. Wrap "create event + update snapshot + update WO projection" in a single transaction per command.
8. Fix `_apply_sql_migrations` to stop being needed (Alembic supersedes), but until then replace the naive `;` split with `sqlparse.split` or similar.

**Should follow shortly (Phase B / next slice):**

9. Replace snapshot-driven state guards with derived-status guards (or document why snapshot is the guard's source of truth, given the reconcile script's existence).
10. Adopt RFC 9457 Problem Details on the wire; expose stable error `code` strings; honor `Idempotency-Key` on command-style mutations.
11. Add an honest i18n linter (ESLint plugin or equivalent) covering `components/` and string returns.
12. Pull mock data out of production page imports.
13. Fix the `id` tiebreaker in `get_events_for_operation`.
14. Add `with_for_update()` around the `reopen_count` increment.

---

## Sources

- `.github/copilot-instructions.md`
- `.github/agent/AGENT.md`
- `docs/governance/CODING_RULES.md` v2.0
- `docs/governance/ENGINEERING_DECISIONS.md`
- `docs/governance/SOURCE_STRUCTURE.md`
- `docs/design/INDEX.md`
- `docs/design/AUTHORITATIVE_FILE_MAP.md`
- `docs/design/10_hardening/hardening-baseline-summary.md`
- `docs/design/10_hardening/source-code-audit-response.md`
- All `backend/app/**/*.py` and the cited `frontend/src/app/**/*.tsx` files

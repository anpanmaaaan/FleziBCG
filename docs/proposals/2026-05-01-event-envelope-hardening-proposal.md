# Proposal — Event Envelope Hardening + Projection Drift Root-Cause (Slice 0)

| Field | Value |
|---|---|
| Date | 2026-05-01 |
| Status | DRAFT — for team review |
| Author | PO-SA Agent (with An) |
| Audience | Backend, Architecture, QA, PO |
| Type | Architecture / platform-foundation slice proposal |
| Decision needed by | Trước khi mở track AI / APS / projection layer song song |

---

## 1. TL;DR

Đề xuất chèn **một slice tiền điều kiện (Slice 0)** vào roadmap trước khi mở bất kỳ track song song nào (AI advisory, APS-Lite, Operational Read-Model layer). Slice 0 gồm 2 phần gắn liền:

1. **Hardening event envelope** cho `execution_events` (schema, naming, scope, versioning, atomic write contract).
2. **Root-cause + fix `operation.status` projection drift** đã có evidence empirical (script `reconcile_operation_status_projection.py` đang tồn tại trong repo).

Lý do: 2/3 module song song mà team đang cân nhắc (Shift Summary AI, Anomaly Detection trên QC, Operational Read-Model layer) đều đứng trên foundation event-driven. Foundation đó hiện đang ở giữa migration claim → session, và contract event chưa đủ sâu để derive projection ổn định. Build feature trên foundation flux sẽ phải re-work 2 lần.

---

## 2. Context

### 2.1 Tình huống hiện tại

- Core FleziBCG đang được hoàn thiện song song với mong muốn bắt đầu track feature parallel: APS, Anomaly Detection (gắn vào QC), hoặc các option khác.
- Slice claim → session-based execution ownership đang chạy (chưa merge).
- Downtime + reason capture mới được implement, chưa qua giai đoạn ổn định usage.
- Quality Lite (inspection / disposition flow) chưa có.
- Không có team song song nào đang build BI / reporting riêng.

### 2.2 Mục tiêu của proposal

- Trả lời câu hỏi "module nào nên bắt đầu song song bây giờ là khả thi nhất".
- Make sure team thống nhất về **thứ tự đầu tư**: foundation hardening → projection layer → feature module.
- Lock down event contract trước khi nó bị nhân bản dưới nhiều assumption khác nhau từ các track AI/APS.

---

## 3. Hiện trạng — Evidence từ docs

### 3.1 Docs đã có

| File | Mức độ chi tiết |
|---|---|
| `docs/design/00_platform/eventing-and-projection-architecture.md` (v2.1) | Direction + event family. Không có schema. |
| `docs/design/02_domain/execution/domain-contracts-execution.md` (v2.0) | Canonical event intent names. Không có payload schema. |
| `docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md` (v4.0) | Command + event names cho session-based + payload field guidance cho `report_production`, `start_downtime`, `reopen_operation` + error families. |
| v3 (claim-based) | Vẫn còn song song với v4 trong repo — chưa retire. |

### 3.2 Docs còn thiếu

- Event envelope spec: không có doc nào định nghĩa envelope chuẩn (sequence, aggregate, scope, actor, versioning, correlation/causation, occurred_at vs recorded_at).
- Event payload JSON schema chi tiết per event_type.
- Naming convention map: hiện docs dùng lower_snake (v4), code dùng mix UPPER_SNAKE legacy + lower_snake mới.
- Versioning rule cho payload khi schema thay đổi.

---

## 4. Hiện trạng — Evidence từ source

### 4.1 Model `ExecutionEvent` (file `backend/app/models/execution.py`)

Schema hiện tại:

```python
id, event_type (String 64), production_order_id, work_order_id,
operation_id, payload (JSON), tenant_id, created_at
```

**Thiếu so với best-practice event-sourcing-lite:**

- `sequence_no` (per aggregate, dùng để detect missing/duplicate event)
- `aggregate_type` + `aggregate_id` (chỉ có operation_id, hardcoded 1 aggregate)
- `scope_path` (tenant/plant/area/line/station — projection không filter theo scope hierarchy được)
- `actor_user_id`, `actor_session_id` (audit/governance)
- `payload_version` (versioning khi schema thay đổi)
- `occurred_at` vs `recorded_at` (nếu offline, late arrival, lệch nhau)
- `correlation_id`, `causation_id` (link command → event chain)

### 4.2 Enum `ExecutionEventType` (file `backend/app/models/execution.py`)

Mixed naming hiện tại:

```python
# Legacy UPPER_SNAKE
OP_STARTED, QTY_REPORTED, NG_REPORTED, QC_MEASURE_RECORDED,
OP_COMPLETED, OP_ABORTED

# New lower_snake (theo canonical contract v4)
EXECUTION_PAUSED = "execution_paused"
EXECUTION_RESUMED = "execution_resumed"
DOWNTIME_STARTED = "downtime_started"
DOWNTIME_ENDED = "downtime_ended"
OPERATION_CLOSED_AT_STATION = "operation_closed_at_station"
OPERATION_REOPENED = "operation_reopened"
```

Comment trong code: *"legacy UPPER_SNAKE entries above remain until the envelope migration."* → team đã biết debt này nhưng chưa làm.

**Naming v4 chưa hiện diện đầy đủ trong source:**

- `station_session_opened`, `operator_identified_at_station`, `equipment_bound_to_station_session`, `station_session_closed` — không có trong enum.
- `report_production` (v4) đang được nhận lưu dưới tên cũ `QTY_REPORTED`.

### 4.3 Repository `execution_event_repository.py`

- 2 query: by `operation_id`, by `work_order_id+tenant`.
- **Thiếu:** by `scope_path`, by `event_type`, by time range. → Projection layer sẽ rất khó build.
- `create_execution_event` gọi `db.commit()` ngay sau add event. Đây là **code smell**: repository nên là unit-of-work neutral, commit thuộc service layer.

### 4.4 Status casing mismatch

- Doc `domain-contracts-execution.md`: `PLANNED / IN_PROGRESS / PAUSED / BLOCKED / COMPLETED / ABORTED` (UPPER).
- Code `StatusEnum`: `planned / in_progress / paused / blocked` (lower).
- Code `ExecutionEventType`: mixed (UPPER cũ + lower mới).

### 4.5 Projection hiện có

- Đúng 1 projection: `operation.status` snapshot column trên bảng `operations`.
- Có script audit: `backend/scripts/reconcile_operation_status_projection.py` (dry-run + apply mode + JSON output).
- **Đã từng hit drift** → script tồn tại như một fix vận hành, không phải prevention. Empirical evidence rằng event-projection contract chưa stable.

---

## 5. Risk 3 — Root-cause projection drift

### 5.1 Logic derive hiện tại (`operation_service.py`)

Có 2 đường derive:

- **`_derive_status(events)`** — list-based, scan tuần tự events đã sort.
- **`derive_operation_runtime_projection_for_ids(...)`** — set-based SQL, GROUP BY + window function lấy last_runtime_event.

Cả hai dùng cùng `_derive_status_from_runtime_facts(...)` đầu ra. Logic xử lý:

1. Terminal states (`aborted`, `completed`) wins.
2. Open downtime (`downtime_started_count > downtime_ended_count`) → `blocked`.
3. `last_runtime_event` làm tiebreaker giữa `paused` / `in_progress`.

### 5.2 Các nguồn drift đã xác định

#### Root cause A — Non-atomic event-write + snapshot-update

`create_execution_event` trong repository gọi `db.commit()` ngay sau khi add event. Sau đó, caller (service) phải update `operation.status` snapshot — và nếu caller crash giữa 2 commit, **drift xảy ra ngay lập tức**. Không có transactional bracket bao trùm event write + snapshot update.

**Đây là root cause khả dĩ nhất.** Append-only event log đáng lẽ phải là atomic write — repository không nên commit, service phải bao trùm transaction.

#### Root cause B — Mixed casing/naming risk

Nếu một code path nào đó (test, seed, migration, manual ops) ghi event_type với casing khác (UPPER vs lower) → derive function sẽ không match enum value → projection coi như event không tồn tại. Drift có thể tự sinh ra từ data dirty.

#### Root cause C — Thiếu invariant check write-time

Logic không reject:

- `DOWNTIME_STARTED` 2 lần liên tiếp (không có `DOWNTIME_ENDED` ở giữa) — vi phạm invariant "open downtime tối đa 1 cùng lúc".
- `EXECUTION_RESUMED` khi không đang paused / blocked.
- `OP_COMPLETED` rồi vẫn ghi tiếp `OP_STARTED`.

Khi data có row vi phạm invariant, derive logic vẫn trả ra status, nhưng status đó có thể không khớp snapshot do snapshot được update bởi service path đã bypass (hoặc đã từng có version cũ của logic).

#### Root cause D — `OPERATION_CLOSED_AT_STATION` không nằm trong runtime status family

Closed/Reopen là **closure dimension**, runtime status là **runtime dimension** — 2 trục riêng. Nếu code nào đó set `operation.status = "closed"` dưới dạng runtime status, derive function sẽ rebuild ra `completed` hoặc `paused` → mismatch. Cần verify column `operation.status` có lưu closure status không, hay chỉ runtime.

#### Root cause E — Race condition giữa concurrent writes

Append-only event log không có aggregate version (optimistic lock). 2 concurrent service calls cho cùng operation có thể ghi event interleaved → derive ra status khác tùy thứ tự `created_at + id`. Nếu snapshot được update bởi cả 2 path không có serialization, kết quả cuối cùng phụ thuộc race.

### 5.3 Mức độ ưu tiên fix

| Root cause | Severity | Effort | Slice 0 inclusion? |
|---|---|---|---|
| A — Non-atomic write | High | Medium | YES |
| B — Mixed casing | Medium | Low | YES |
| C — Thiếu invariant check | Medium | Medium | YES (subset) |
| D — Status dimension confusion | Medium | Low (verify + fix) | YES (verify + doc) |
| E — Race condition | Low (chưa có evidence) | High | NO — defer, cần evidence trước |

---

## 6. Proposed Plan

### 6.1 Goals (Slice 0)

1. **Lock event contract** dưới mức envelope cụ thể (schema, naming, scope, versioning) để mọi track sau (AI, APS, projection layer) build trên cùng base.
2. **Eliminate root-cause A, B, C, D** của projection drift bằng atomic write contract + canonicalized naming + write-time invariant check + status dimension separation.
3. **Mở đường an toàn** cho Slice 1 (Operational Read-Model / KPI Projection Layer) và Slice 2 (APS-Lite Sequencing Advisor) ở các sprint kế tiếp.

### 6.2 Non-Goals (Slice 0)

| Non-goal | Rationale |
|---|---|
| Build new projection (line state, KPI, OEE) | Thuộc Slice 1, sau Slice 0. |
| Build dashboard / FE mới | Slice 0 thuần backend foundation. |
| API frontend mới | Không có FE-facing change. |
| Multi-aggregate event sourcing framework | Over-engineering. Chỉ harden execution domain trước. |
| Event broker / Kafka / outbox pattern | Doc đã ghi "optional later". Không cần cho Slice 0. |
| Refactor Quality / Material event | Quality Lite chưa có. Material chưa scope. Chờ. |
| Race condition fix (root cause E) | Chưa có evidence empirical. Defer. |
| Claim → session migration | Đang slice riêng (slice (a)). Slice 0 sẽ chờ slice (a) merge. |

### 6.3 Pre-conditions

- Slice (a) — claim → session migration — đã merge và list event_type session-based đã chốt trong code.
- Master data + WO state model không thay đổi đột xuất trong cùng sprint.

### 6.4 Requirements

#### P0 — Must have

**P0-1. Event envelope schema migration**

Thêm vào `execution_events` table:

- `sequence_no INT NOT NULL` (per `(aggregate_type, aggregate_id)` — backfill bằng `created_at + id` order).
- `aggregate_type VARCHAR(32) NOT NULL` (mặc định `"operation"` khi backfill).
- `aggregate_id BIGINT NOT NULL` (default = `operation_id` khi backfill).
- `scope_path JSONB NOT NULL` (object: `{tenant_id, plant_id, area_id, line_id, station_id}`; backfill từ operation.station_scope_value + parent traversal).
- `actor_user_id BIGINT NULL` (backfill NULL cho legacy).
- `actor_session_id BIGINT NULL` (backfill NULL).
- `payload_version SMALLINT NOT NULL DEFAULT 1`.
- `occurred_at TIMESTAMP WITH TIME ZONE NULL` (mặc định = `created_at` khi backfill; new events: server-set khi command processed).
- `recorded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()` (rename từ `created_at` hoặc giữ song song).
- `correlation_id UUID NULL`.
- `causation_id UUID NULL`.

Acceptance criteria:

- Migration up + down chạy clean.
- Backfill script dry-run output verified với production-like data; apply chạy không error.
- All existing tests pass với schema mới.

**P0-2. Event_type naming canonicalization**

- Chốt **lower_snake** làm canonical (đồng bộ với contract v4).
- Migration rename data: UPPER_SNAKE → lower_snake, ví dụ `OP_STARTED` → `execution_started`, `OP_COMPLETED` → `execution_completed`, `OP_ABORTED` → `execution_aborted`, `QTY_REPORTED` → `production_reported`, `NG_REPORTED` → `scrap_reported` (cần xác nhận với team), `QC_MEASURE_RECORDED` → `qc_measurement_recorded`.
- Giữ `event_type_alias_map` table hoặc enum value alias để query historical data dùng tên cũ vẫn match.
- `ExecutionEventType` enum chỉ còn lower_snake values.
- Update `_derive_status` + `derive_operation_runtime_projection_for_ids` dùng tên mới.

Acceptance criteria:

- Không còn UPPER_SNAKE trong code (trừ alias map).
- Reconcile script chạy clean trên data đã rename.
- Test coverage cho cả 2 hướng (tên mới + alias cho legacy data).

**P0-3. Atomic write contract (root cause A fix)**

- Repository `create_execution_event` **không** `db.commit()`. Chỉ `db.add()` + `db.flush()` (nếu cần ID).
- Service layer (operation_service / execution_service) bao trùm transaction:
  - Event write + snapshot update + invariant check trong cùng `with db.begin()` block.
  - Nếu invariant violated → rollback toàn bộ.
- Add unit test: simulate failure giữa event write và snapshot update → cả 2 phải rollback.

Acceptance criteria:

- 0 occurrences of `db.commit()` trong repository layer cho `execution_events`.
- Test "atomic event + snapshot" pass.
- Tích hợp test: chạy reconcile sau N atomic writes → 0 mismatch (trong test data deterministic).

**P0-4. Write-time invariant check (root cause C subset)**

Trong service layer, validate trước khi append event:

- `DOWNTIME_STARTED` chỉ khi không có open downtime active.
- `DOWNTIME_ENDED` chỉ khi đang có open downtime.
- `EXECUTION_RESUMED` chỉ khi `paused` hoặc `blocked` (state có thể resume).
- `EXECUTION_PAUSED` chỉ khi `in_progress`.
- `OP_COMPLETED` chỉ khi không phải terminal state.
- `OP_STARTED` chỉ khi `planned` (cấm restart sau complete/abort/reopen — reopen có flow riêng).

Acceptance criteria:

- Mỗi invariant có test happy + violation case.
- Violation trả error trong family `STATE_INVALID_TRANSITION`.

**P0-5. Status dimension separation (root cause D fix)**

- Verify `operation.status` column hiện lưu runtime status hay closure status hay cả hai.
- Nếu lưu cả hai (mixed) → tách thành 2 columns: `runtime_status` + `closure_status`.
- Update derive function + reconcile script để rebuild đúng dimension.
- Update doc `domain-contracts-execution.md` + `station-execution-state-matrix-v4.md` reflect tách dimension.

Acceptance criteria:

- 2 dimension độc lập trong schema + code.
- Reconcile script chạy clean cho cả 2.

**P0-6. Repository query API mở rộng**

Thêm vào `execution_event_repository.py`:

- `get_events_by_scope(db, scope_path, time_range, event_types, tenant_id)`.
- `get_events_by_aggregate(db, aggregate_type, aggregate_id)`.
- `get_event_count_by_type(db, scope_path, time_range, group_by)` — cho projection aggregation sau.

Acceptance criteria:

- Query chạy với index cover trên `(scope_path, recorded_at)` (tạo index migration kèm).
- Tests cover empty result + filter combinations.

#### P1 — Should have (post-Slice-0 hoặc cùng Slice 0 nếu effort cho phép)

- **P1-1.** Pydantic schema per event_type cho payload validation tại write path.
- **P1-2.** Doc `event-envelope-spec.md` mới trong `docs/design/00_platform/`, link từ `eventing-and-projection-architecture.md`.
- **P1-3.** Aggregate version field (`aggregate_version`) — chuẩn bị cho race condition fix sau, dù chưa enforce optimistic lock ở Slice 0.

#### P2 — Future considerations

- **P2-1.** Optimistic lock dùng aggregate_version (root cause E) — sau khi có evidence drift do race.
- **P2-2.** Event broker / outbox pattern — nếu cần publish event ra ngoài.
- **P2-3.** Multi-aggregate framework — khi Quality / Material domain mature.
- **P2-4.** Event payload schema registry với version migration tooling.

### 6.5 Acceptance Criteria — Slice 0 overall

Given Slice 0 đã merge.

- When team chạy `reconcile_operation_status_projection.py --tenant-id ... --apply` trên môi trường staging với production-like data:
  - Then số mismatches phải = 0 sau lần chạy đầu tiên (giả sử data trước đó đã reconcile).
  - And không có mismatch sinh ra mới sau N giờ chạy execution path bình thường.
- When team query `SELECT DISTINCT event_type FROM execution_events`:
  - Then chỉ thấy lower_snake values (trừ legacy alias rows nếu giữ).
- When team chạy migration up + down lần lượt → schema clean cả 2 chiều.
- When developer mới đọc `event-envelope-spec.md` → có thể trả lời được: envelope có gì, naming convention, versioning, atomic write contract, scope hierarchy.

### 6.6 Effort estimate

- **2–3 tuần backend** với 1 dev senior + 1 dev mid + QA pair.
- **Pre-condition:** slice (a) merge xong (chưa estimate được).

### 6.7 Stop conditions

Pause Slice 0 nếu:

- Slice (a) chưa merge / chưa chốt event_type session-based.
- Phát hiện multi-aggregate concern lớn hơn (Quality / Material event đang dùng chung table `execution_events`) → cần re-design lớn hơn.
- Drift root cause E (race condition) có evidence empirical mạnh hơn — cần re-prioritize.

---

## 7. Why this slice, not APS/Anomaly first

### 7.1 So sánh option

| Option | Data fitness | Execution-truth dependency | Blast radius | ROI realistic |
|---|---|---|---|---|
| Slice 0: Event envelope hardening | N/A (foundation) | Direct fix | Medium (governed by tests) | 2–3 tuần → multiplier cho mọi slice sau |
| Operational Read-Model / KPI layer | OK nếu Slice 0 xong | Đứng tách qua contract | Low | 4–6 tuần sau Slice 0 |
| APS-Lite Sequencing Advisor | OK (dùng master data + WO backlog) | Thấp | Low (advisory) | Có thể parallel sau Slice 0 |
| Shift Summary AI | Chờ downtime stable + Slice 0 | High | Medium (AI nhầm = mất tin tưởng) | Lùi 4–6 tuần |
| Anomaly Detection on Downtime | Cần 4 tuần data + Slice 0 | High | Medium | Lùi 6–8 tuần |
| Anomaly Detection on QC | Không có data (Quality Lite chưa có) | Block | N/A | Loại |
| APS full module | Dependency lớn | Very high | Very high (phá truth boundary) | Loại khỏi giai đoạn này |

### 7.2 Recommendation

**Top pick: Slice 0 (Event Envelope Hardening + Drift Root-Cause).** Đây là *infrastructure play*, không phải feature. ROI trải dài cho mọi slice sau. Không tạo trap về truth boundary. Phù hợp với principle event-driven + governance-first đã đặt trong Product Business Truth.

**Sau Slice 0:** mở 2 track song song — Operational Read-Model layer (Slice 1) + APS-Lite Sequencing Advisor (Slice 2). Đây là điểm an toàn để bắt đầu "feature mới" mà không vi phạm boundary.

**Defer:** Shift Summary AI, Anomaly Detection (Downtime / QC), APS full — chờ data dày + foundation stable.

---

## 8. Open Questions for Team

| # | Question | Owner |
|---|---|---|
| Q1 | Slice (a) claim → session — ETA merge? Có chốt list event_type session-based chưa hay vẫn đang propose? | Backend lead |
| Q2 | Bảng `execution_events` hiện có Quality / Material event đang ghi vào không, hay chỉ Execution domain? Nếu shared, multi-aggregate concern có thể nâng scope Slice 0. | Backend lead |
| Q3 | `operation.status` column hiện lưu runtime status hay closure status hay cả hai? Cần verify để quyết định P0-5 effort. | Backend dev (operation_service) |
| Q4 | Casing convention chốt cho `StatusEnum` value: lower (như code hiện tại) hay UPPER (như doc)? Cần align cả doc + code. | PO + Architecture |
| Q5 | Aggregate model: chỉ `operation` là aggregate, hay `work_order` + `production_order` cũng là aggregate riêng? Quyết định ảnh hưởng `aggregate_type` column. | Architecture |
| Q6 | Có service nào đang ghi `execution_events` từ ngoài operation_service không (e.g., admin tool, seed, migration)? Cần biết để P0-3 atomic contract cover hết entry point. | Backend lead |
| Q7 | Production-like data hiện tại có bao nhiêu rows trong `execution_events`? Backfill script cần tối ưu hay đơn giản đủ? | Backend dev + DB admin |
| Q8 | Có nên giữ `event_type_alias_map` hay rename hard (data migration không có rollback)? Trade-off: alias dễ rollback nhưng phức tạp query. | Architecture + Backend lead |

---

## 9. Timeline & Dependencies

```
[Slice (a): claim → session]  ───────────────► merge
                                                  │
                                                  ▼
                                        [Slice 0: envelope + drift]  (2–3 tuần)
                                                  │
                                              ┌───┴───┐
                                              ▼       ▼
                                     [Slice 1:        [Slice 2:
                                      Read-Model]      APS-Lite Advisor]
                                     (4–6 tuần)        (4–6 tuần, parallel-able)
                                              │       │
                                              └───┬───┘
                                                  ▼
                                         [Wave AI advisory:
                                          Shift Summary,
                                          Anomaly Downtime]
                                          (chờ data + Slice 1)
```

Dependencies cứng:

- Slice 0 chờ Slice (a) merge.
- Slice 1 chờ Slice 0 merge.
- Slice 2 (APS-Lite) có thể chạy parallel với Slice 1 nếu master data + WO state đã chốt.
- Wave AI chờ Slice 1 + 4 tuần data downtime ổn định.

---

## 10. Hard Mode MOM v3 Compliance Note

Slice 0 chạm: execution events, projections, scope, audit, critical invariant, DB migration enforcing operational truth.

→ **Bắt buộc Hard Mode MOM v3.** Trước khi code, phải có:

1. Design Evidence Extract.
2. Event Map (current + target).
3. Invariant Map.
4. State Transition Map (runtime + closure dimension separately nếu P0-5 confirm tách).
5. Test Matrix (atomic write, naming migration, invariant check, reconcile drift, scope filter).
6. Verdict before coding.

PO-SA Agent sẽ produce coding-agent prompt + evidence pack riêng sau khi proposal này được team accept và Q1–Q8 được trả lời.

---

## 11. Appendix — Evidence References

### A. Files đã đọc cho proposal này

- `README.md`
- `.github/copilot-instructions.md`
- `.github/agent/AGENT.md`
- `.copilot/README.md`
- `.copilot/DESIGN.md`
- `docs/design/00_platform/system-overview-and-target-state.md`
- `docs/design/00_platform/product-business-truth-overview.md`
- `docs/design/00_platform/product-scope-and-phase-boundary.md`
- `docs/design/00_platform/eventing-and-projection-architecture.md`
- `docs/design/02_domain/execution/domain-contracts-execution.md`
- `docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md` (partial)
- `backend/app/models/execution.py`
- `backend/app/repositories/execution_event_repository.py`
- `backend/app/services/operation_service.py` (`_derive_status`, `_derive_status_from_runtime_facts`, `derive_operation_runtime_projection_for_ids`, `reconcile_operation_status_projection`, `detect_operation_status_projection_mismatches`)
- `backend/scripts/reconcile_operation_status_projection.py`

### B. Files được tham chiếu nhưng chưa verify tồn tại

`copilot-instructions.md` chỉ định read-order các file sau — trước khi Slice 0 vào kỹ thuật, PO-SA cần verify và đọc:

- `docs/design/INDEX.md`
- `docs/design/AUTHORITATIVE_FILE_MAP.md`
- `docs/governance/CODING_RULES.md`
- `docs/governance/ENGINEERING_DECISIONS.md`
- `docs/governance/SOURCE_STRUCTURE.md`
- `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md`
- `docs/ai-skills/hard-mode-mom-v3/SKILL.md`

---

## 12. Review Instructions for Team

1. Đọc Section 3, 4, 5 trước (evidence + root cause). Đây là phần dễ challenge — verify bằng cách mở source theo reference ở Appendix A.
2. Sau đó đọc Section 6 (Proposed Plan). Comment trực tiếp vào P0-1 → P0-6 nếu có disagree.
3. Trả lời Q1–Q8 ở Section 8 trước stand-up tới.
4. Nếu có phản đối thứ tự "Slice 0 trước AI/APS" — comment vào Section 7 với evidence ngược.
5. Decision merge/reject proposal: cần ít nhất 1 backend lead + PO + 1 architecture reviewer.

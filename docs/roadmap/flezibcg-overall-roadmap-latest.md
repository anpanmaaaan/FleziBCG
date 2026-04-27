Dưới đây là **roadmap tổng thể mới nhất của FleziBCG** sau khi đã chốt:

```text id="1xmxo7"
Latest Design Baseline 2026-04-26
+ Hardening v1
+ Hardening Housekeeping v1.1
+ Source Code Audit Response
+ CODING_RULES.md v2.0
```

# FleziBCG Overall Roadmap

## 0. Current Position — Chúng ta đang ở đâu?

FleziBCG hiện đã qua giai đoạn **design baseline** và **production-hardening baseline**.

Tức là bây giờ không nên tiếp tục mở rộng function list hay screen inventory nữa. Việc cần làm tiếp theo là chuyển sang **implementation slicing**, bắt đầu từ foundation nhỏ nhất nhưng chắc nhất.

Trạng thái hiện tại:

| Area | Status |
|---|---|
| Product / MOM direction | Chốt |
| Function List | Chốt v2.1 |
| Screen UI Inventory | Chốt v2.2 |
| Database Design | Chốt v1.2 |
| Domain Boundary | Chốt v2.2 |
| Hardening ADRs | Chốt v1 + v1.1 |
| CODING_RULES | Chốt v2.0 |
| Source Code Audit | Đã review, accepted with corrections |
| Next action | P0-A Foundation implementation prompt |

---

# Phase 0 — Pre-Implementation Alignment

## Goal

Đảm bảo Agent/code implementation không đi lệch baseline.

## 0.1 Already Done

| Task | Status |
|---|---|
| Function List | Done |
| Screen Inventory | Done |
| Database Design | Done |
| Cross-review design | Done |
| Hardening Action Register | Done |
| Immediate Consistency Patch | Done |
| Hardening ADR Pack | Done |
| Housekeeping v1.1 | Done |
| Source Code Audit | Done |
| CODING_RULES v2.0 | Done |

## 0.2 Last item before coding

Việc còn lại ngay trước khi code:

```text id="4ca70x"
Task 5 — Write P0-A Foundation Database Implementation Prompt
```

Không code ngay bằng prompt rộng. Phải viết prompt slice thật chặt.

---

# Phase 1 — P0-A Foundation Database Slice

## Goal

Xây phần nền tảng tối thiểu để các domain sau không bị lệch: tenant, IAM, session, access control, audit, plant hierarchy, scope.

Đây là phase quan trọng nhất hiện tại.

## Scope build

| Area | Build in P0-A |
|---|---|
| Migration system | Alembic baseline |
| Tenant | tenant table / tenant context |
| IAM user | user model, lifecycle status |
| Session | user sessions, revoke, logout all |
| Refresh token | refresh token table + rotation path |
| Roles/actions | system roles, action registry foundation |
| Scope | scope node / assignment |
| Plant hierarchy | plant, area, line, station, equipment foundation |
| Audit | audit log / security event foundation |
| Config | CORS, safer environment config |
| Runtime hygiene | remove `create_all()` production path |
| DevOps hygiene | CloudBeaver dev-only posture |
| Backend CI | minimum backend test/lint workflow if absent |

## Explicit exclusions

Không làm trong P0-A:

```text id="2ym2bj"
ERP Integration
Acceptance Gate
Backflush
APS
AI
Digital Twin
Compliance/e-record
OPC UA / MQTT / Sparkplug
Redis
Kafka
OPA / Casbin migration
Frontend React Query/Zustand migration
Station Execution refactor lớn
Claim removal
Rework flow
```

## Expected output

Sau P0-A, repo nên có:

```text id="za6ds9"
backend foundation aligned
Alembic working
IAM/session/scope/audit/plant hierarchy foundation
tests for core foundation
no broad domain implementation
```

## Decision style

Vì source audit nói repo hiện tại đã có một phần IAM/RBAC/session, nên P0-A nên là:

```text id="5swrz3"
Hybrid alignment slice
```

Không build lại từ đầu 100%, cũng không giữ nguyên cái cũ nếu lệch baseline.

---

# Phase 2 — P0-B Manufacturing Master Data Minimum

## Goal

Tạo nền dữ liệu sản xuất tối thiểu để Execution Core có thể chạy đúng.

## Scope

| Area | Build |
|---|---|
| Product | product, product version |
| Routing | routing, routing operation |
| Resource requirement | operation ↔ station/equipment requirement |
| Work center mapping | mapping nhẹ với line/station/equipment |
| Master data status | draft/released/retired |
| Reference data | reason code/master data foundation nếu cần |

## Explicit exclusions

```text id="zxdvl6"
Recipe/phase ISA-88 full model
Backflush rule
Acceptance policy
ERP master data sync
Advanced versioning workflow
```

## Why after P0-A?

Vì MMD cần tenant/scope/plant hierarchy trước. Nếu build MMD trước foundation, schema sẽ dễ lệch.

---

# Phase 3 — P0-C Execution Core

## Goal

Xây execution core production-grade nhưng vẫn giới hạn P0.

## Scope

| Area | Build |
|---|---|
| Work order | work order / operation foundation |
| Station session | session-owned execution |
| Operator identification | operator context at station |
| Equipment binding | minimal equipment binding |
| Operation queue | station queue |
| Start execution | command + event |
| Pause/resume | command + event |
| Report production | good/scrap only |
| Downtime | start/end downtime |
| Complete | complete execution |
| Close/reopen | controlled close/reopen |
| Events | append-only execution events |
| Status projection | derived operation status |
| Allowed actions | backend-derived allowed actions |
| BLOCKED reason | block_source, block_reason_code, blocked_since, etc. |

## Explicit exclusions

```text id="9zo52z"
Do not remove all claim code yet unless isolated migration is planned
Do not add rework_qty
Do not implement Acceptance Gate
Do not implement Backflush
Do not implement ERP posting
Do not implement AI recommendations
```

## Important principle

Execution P0 phải đi theo baseline:

```text id="3r2vzh"
Session-owned target
Claim = migration debt
Status = derived/projection
Frontend = display only
Backend = action truth
```

---

# Phase 4 — P0-D Quality Lite

## Goal

Thêm quality tối thiểu để execution có inspection/measurement/result visibility, nhưng chưa thành full QMS.

## Scope

| Area | Build |
|---|---|
| QC requirement | operation/product quality requirement |
| Measurement | measurement entry |
| Evaluation | backend pass/fail/hold evaluation |
| QC status | QC_PENDING, QC_PASSED, QC_FAILED, QC_HOLD |
| Quality visibility | operation detail quality panel |
| Basic hold visibility | show quality hold status |

## Explicit exclusions

```text id="biz4dt"
Full Acceptance Gate workflow
Deviation approval
Nonconformance lifecycle
Disposition workflow
E-sign
Full QMS/CAPA
```

## Note

Acceptance Gate đã design rồi, nhưng không build full trong P0-D nếu chưa cần.

---

# Phase 5 — P0-E Supervisory Operations

## Goal

Tạo visibility cho supervisor/manager dựa trên execution truth.

## Scope

| Area | Build |
|---|---|
| Global operations dashboard | current operations |
| Line monitor | line/station state |
| Operation list | filterable operation list |
| Operation detail | detail screen backed by backend |
| Gantt/timeline | shift/day/week viewport |
| Event timeline | operation event history |
| Basic reports | execution status, downtime, quantity |

## Explicit exclusions

```text id="6eagl7"
Advanced APS
AI explanation
Digital Twin scenario
Full OEE deep dive
```

## Principle

Supervisory layer đọc từ projection/read model, không tự tạo truth.

---

# Phase 6 — P1-A Integration Foundation

## Goal

Chuẩn bị nền integration nhưng chưa thay ERP.

## Scope

| Area | Build |
|---|---|
| External system registry | ERP/QMS/CMMS/WMS registry |
| External ID map | mapping internal ↔ external IDs |
| Inbox/outbox tables | inbound/outbound message foundation |
| Message status | pending/processed/failed/retrying |
| Retry/error | retry and error tracking |
| Status mapping | MOM ↔ ERP status mapping |
| Reconciliation foundation | compare request/result |

## Explicit exclusions

```text id="08c97l"
No full SAP adapter yet
No financial posting truth inside FleziBCG
No full ERP replacement
No full WMS/QMS/CMMS
```

## Why P1, not P0?

P0 phải có execution truth trước. Integration mà build sớm sẽ dễ ép ERP shape vào MOM core.

---

# Phase 7 — P1-B Acceptance Gate + Quality Expansion

## Goal

Nâng Quality Lite thành operational quality gate có kiểm soát.

## Scope

| Area | Build |
|---|---|
| Acceptance Gate definition | gate definition |
| Pre-Acceptance Check | gate_type = pre_acceptance |
| Gate instance | operation/lot/batch context |
| Measurement/result | gate measurement and evaluation |
| Hold/release | gate-controlled hold/release |
| Deviation | deviation request/approval |
| Nonconformance | basic NC capture |
| Disposition | accept/reject/rework/scrap foundation |
| Execution gating | allowed_actions blocked by quality |

## Explicit exclusions

```text id="z4q16u"
Full enterprise QMS
Full CAPA
Supplier quality
Document control
```

---

# Phase 8 — P1-C Material Readiness + Backflush

## Goal

Đưa material/WIP vào execution context nhưng vẫn không thay ERP/WMS.

## Scope

| Area | Build |
|---|---|
| Material availability snapshot | ERP/WMS context if integrated |
| Staging/kitting | station/operation material readiness |
| Component verification | scan/confirm component |
| Backflush rule | MMD-defined rule |
| Backflush consumption record | operational consumption |
| Material consumption event | append-only material fact |
| Traceability link | input-output genealogy |
| ERP posting request | integration request, not ERP truth |

## Explicit exclusions

```text id="b6zl2w"
Full WMS
Financial inventory truth
Advanced warehouse optimization
```

## Backflush rule

Chốt theo baseline:

```text id="7nnrkw"
MMD defines rule
Execution triggers
Inventory/WIP records consumption
Traceability records genealogy
Integration posts summary to ERP
ERP owns financial/inventory posting truth
```

---

# Phase 9 — P1-D Reporting / KPI / OEE

## Goal

Tạo deterministic reporting trước khi AI.

## Scope

| Area | Build |
|---|---|
| OEE formula | Availability × Performance × Quality |
| Downtime analysis | by reason/equipment/station/shift |
| Production performance | actual vs target |
| Quality performance | pass/fail/hold/reject |
| Material/WIP report | WIP/material status |
| Integration status report | message/posting/reconciliation |

## Explicit exclusions

```text id="9rycir"
AI OEE deep dive
Predictive explanation
Natural-language insight
```

## Principle

Reporting/KPI là deterministic. AI chỉ explain sau.

---

# Phase 10 — P1-E Andon / Notification / Maintenance Lite

## Goal

Thêm coordination layer cho shopfloor.

## Scope

| Area | Build |
|---|---|
| Andon trigger | raise issue from station/operation |
| Andon board | active incidents |
| Notification center | alerts/ack |
| Escalation rules | simple escalation |
| Equipment availability | equipment status |
| Downtime-maintenance link | link downtime to maintenance context |
| Calibration status | basic visibility |

## Explicit exclusions

```text id="r33avi"
Full CMMS
Predictive maintenance
Complex notification workflow
```

---

# Phase 11 — P2-A Process / Batch / ISA-88 Depth

## Goal

Mở rộng cho process/batch/hybrid manufacturing.

## Scope

| Area | Build |
|---|---|
| Recipe | recipe/procedure |
| Phase | recipe phase |
| Material weighing | weighing/dispensing |
| Material charging | charge confirmation |
| Process parameter | temperature/pressure/pH/speed |
| Batch genealogy | batch-specific traceability |
| eBR foundation | electronic batch record package if needed |

## Trigger to move earlier

Kéo phase này lên P1 nếu customer đầu tiên là:

```text id="4cnkd0"
food
pharma
chemical
batch/process-heavy
regulated production
```

---

# Phase 12 — P2-B APS-lite / Scheduling Support

## Goal

Planning support nhưng không overwrite execution.

## Scope

| Area | Build |
|---|---|
| Planning board | plan overview |
| Dispatch recommendation | advisory sequence |
| Capacity load | finite capacity view |
| Plan vs actual | compare plan to execution |
| Replanning impact | disruption impact |

## Principle

```text id="op4tor"
APS proposes
Execution confirms reality
```

---

# Phase 13 — P2-C AI Wave 1

## Goal

AI advisory layer đầu tiên.

## Scope

| Use case | Build |
|---|---|
| Shift summary | summarize shift from events |
| OEE deep dive | explain OEE loss |
| Anomaly detection | detect unusual downtime/quality |
| Delay risk | predict delay risk |
| Bottleneck explanation | explain line/station bottleneck |
| Quality trend explanation | explain quality patterns |
| Natural-language insights | query operational data safely |

## Guardrails

```text id="njuxuz"
AI cannot mutate execution
AI cannot approve
AI cannot bypass SoD
AI cannot post ERP
AI cannot mark quality pass/fail
```

---

# Phase 14 — P2-D Operational Digital Twin

## Goal

Operational twin, not 3D-first.

## Scope

| Area | Build |
|---|---|
| Operational graph | line/station/equipment/WO/WIP |
| State snapshot | derived state |
| WIP/queue flow | operational flow |
| Block/delay map | blockage state |
| What-if scenario | future simulation |
| AI over twin | explain/predict/recommend |

## Principle

Digital Twin is derived.

Không bao giờ là source of truth.

---

# Phase 15 — P2/P3 Compliance / Electronic Records

## Goal

Support regulated operation if needed.

## Scope

| Area | Build |
|---|---|
| Electronic production record | ePR |
| Electronic batch record | eBR |
| Record package | source fact package |
| Review workflow | record review |
| E-signature | controlled signature |
| Audit export | audit-ready package |

## Explicit exclusions

```text id="9g5m0l"
Full enterprise compliance suite
Full QMS replacement
Full document control
```

---

# Phase 16 — P3 Broader MOM Expansion

## Goal

Mở rộng từ MES execution core sang full MOM ecosystem.

## Possible modules

| Area | Future expansion |
|---|---|
| Advanced APS | optimizer |
| Advanced WIP/material | WMS-like adjunct |
| Maintenance | CMMS integration/depth |
| Quality | stronger QMS integration |
| Digital twin | what-if simulation |
| AI | autonomous recommendation workflow, still governed |
| Multi-plant analytics | enterprise-level operational intelligence |
| Marketplace/adapters | ERP/QMS/SCADA connectors |

---

# Implementation Order — Practical Version

Nếu nói theo thứ tự thực tế nên làm từ hôm nay:

```text id="l8mr0r"
0. Final baseline / coding rules / audit response — Done
1. Task 5 Prompt — P0-A Foundation Database Slice
2. Implement P0-A
3. Review P0-A implementation
4. Patch CODING_RULES/docs if implementation reveals mismatch
5. P0-B Manufacturing Master Data minimum
6. P0-C Station Execution Core
7. P0-D Quality Lite
8. P0-E Supervisory Operations
9. P1-A Integration Foundation
10. P1-B Acceptance Gate
11. P1-C Material Readiness + Backflush
12. P1-D Reporting/KPI/OEE
13. P1-E Andon/Notification/Maintenance Lite
14. P2 Process/Batch depth
15. P2 APS-lite
16. P2 AI Wave 1
17. P2/P3 Operational Digital Twin
18. P2/P3 Compliance/e-record
```

---

# What Must Be Done Now

Ngay bây giờ chỉ nên tập trung vào:

```text id="az4gzm"
Task 5 — Write P0-A Foundation Database Implementation Prompt
```

Sau đó Agent implement:

```text id="id91w5"
Alembic
tenant
IAM
session
refresh token
role/action/scope
audit/security event
plant hierarchy
scope-node compatibility
CORS/config hardening
CloudBeaver dev-only
backend CI minimum
```

---

# What Should Be Designed Now, Built Later

Các phần đã có ADR/design, nhưng chưa build:

```text id="z2d4e1"
RLS
Outbox
CloudEvents external boundary
OPC UA/MQTT/Sparkplug
EPCIS
ISA-88
OEE reporting
AI guardrails
Digital Twin
Compliance/e-record
Redis/Kafka/OPA
```

---

# What Can Wait

Chưa cần đụng:

```text id="80i8ea"
Full async migration
React Query/Zustand migration
ERP adapter implementation
Acceptance Gate full workflow
Backflush implementation
APS optimizer
AI implementation
Digital Twin scenario editor
Full eBR/e-sign
Full WMS/QMS/CMMS replacement
K8s/secrets/backup vendor decision
```

---

# Final Recommendation

Roadmap chốt lại rất rõ:

> **Build Foundation first, then Execution truth, then Quality/Material/Integration, then Reporting, then AI/Digital Twin.**

Không đi ngược thứ tự này. Đặc biệt không build AI, APS, Backflush, Acceptance Gate hoặc ERP integration trước khi foundation + execution truth ổn.

Bước tiếp theo mình khuyên làm ngay:

```text id="eie9xf"
Task 5 — P0-A Foundation Database Implementation Prompt
```
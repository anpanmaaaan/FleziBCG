# Proposal — Manufacturing Master Data Full Coverage & Hardening

> **STATUS: REJECTED v1.0 — superseded by PO-SA review and MMD-BE-00 evidence. Do not implement directly.**
>
> This proposal was reviewed on 2026-05-01 and rejected for direct implementation due to:
> 1. Logical inconsistency between Phase A (release/retire in scope) and Phase C (approval workflow as separate phase).
> 2. Foundation dependency P0-A (tenant/IAM/scope/audit/action registry/Alembic) was not verified before scoping.
> 3. Reason Code unification grouped with Phase A despite high regression risk on Station Execution downtime path.
>
> Proposal v1.1 / slice plan v1.1 will be authored after `docs/audit/mmd-be-00-evidence-and-contract-lock.md` produces verified foundation evidence.
>
> This document is preserved for historical reference and contains useful analysis. **Do not use as implementation authority.**

| Field | Value |
|---|---|
| Date | 2026-05-01 |
| Status | REJECTED v1.0 — see header notice |
| Author | PO-SA Agent (with An) |
| Audience | PO, Architecture, Backend lead, Frontend lead, QA |
| Type | Multi-slice track proposal — feature + governance |
| Track classification | Parallel track (independent of Slice 0 event envelope, independent of claim → session migration, independent of FE Foundation/IAM/Governance track) |
| Related docs | `docs/audit/mmd-current-state-report.md` (v1.0 2026-05-01), `docs/proposals/2026-05-01-event-envelope-hardening-proposal.md` |
| Hard Mode MOM v3 | TRIGGERED — chạm tenant/scope/auth, audit, DB migration governance, role/action/scope assignment |

---

## 1. TL;DR

Đề xuất **Master Data Hardening track** — track parallel độc lập với BE-claim-removal và FE-Foundation/IAM. Mục tiêu: nâng MMD từ "ADEQUATE FOR VISUALIZATION" lên "ADEQUATE FOR GOVERNANCE" theo verdict của current-state report.

Chia thành **5 phases incremental**, mỗi phase ship được riêng, không phá nhau:

- **Phase A — Backend Foundation Gaps** (BOM domain, Routing Op extended, Resource Requirements API, unified Reason Codes API + permission code fix)
- **Phase B — Frontend Connect** (lift 5 SHELL screens lên CONNECTED)
- **Phase C — Mutation Enablement** (release/retire/edit cho Product + Routing + BOM, kèm versioning + approval workflow)
- **Phase D — Import/Export Onboarding Tool** (CSV/Excel import cho tenant onboarding + audit snapshot export)
- **Phase E — Cross-Reference & Polish** (BOM tab trong ProductDetail, RouteDetail → RoutingOperationDetail link, BOM-Routing reference view)

Total estimate: **10–14 tuần** với 2 BE + 1 FE dev. Có thể parallel sub-tracks trong cùng phase.

3 quyết định kiến trúc chính trong proposal này:

1. **Versioning depth** (Section 8) — đề xuất "3-state lifecycle + version_no + supersedes_id" (minimal versioning), không full bitemporal.
2. **Approval workflow** (Section 9) — đề xuất SoD gate **chỉ** trên transition `RELEASED` và `RETIRED`, không gate trên DRAFT mutation.
3. **Import/Export scope** (Section 10) — đề xuất CSV import cho tenant onboarding + JSON snapshot export cho audit. KHÔNG bulk update production data, KHÔNG continuous ERP sync trong scope này.

---

## 2. Context & Motivation

### 2.1 Trạng thái hiện tại (theo `mmd-current-state-report.md` v1.0)

- **9 MMD screens** tổng cộng: 4 PARTIAL (read-only, mutation disabled) + 5 SHELL (mock fixture, no backend API).
- **PARTIAL screens (CONNECTED nhưng disable mutation):** Product List, Product Detail, Routing List, Routing Detail.
- **SHELL screens (mock only):** BOM List, BOM Detail, Routing Operation Detail, Resource Requirements, Reason Code Management.
- **Backend service đã tồn tại:** `product_service.py`, `routing_service.py`, `resource_requirement_service.py`. Nhưng **API endpoint chưa expose** cho resource_requirements; **toàn bộ BOM domain chưa có**; reason codes chỉ có downtime endpoint riêng.
- **Audit:** Product service đã ghi audit qua `security_event_service` với event types `PRODUCT.CREATED/UPDATED/RELEASED/RETIRED`. Routing chưa verified.
- **Invariant đã có ở Product service:** unique product_code per tenant, RETIRED không update được, RELEASED không sửa structural fields (product_code, product_type), chỉ DRAFT mới release được.
- **Permission code SAI:** `products.py` API dùng `require_action("admin.user.manage")` cho create/update/release/retire product → đây là placeholder, không đúng semantic. Cần action code riêng.

### 2.2 Vì sao làm bây giờ

- **Track FE Foundation/IAM** đang chiếm dụng team FE — không xung đột với MMD track.
- **Track BE bỏ claim** đang chiếm dụng team BE chính — MMD track giao "team coding agent" làm parallel.
- **MMD là multiplier** cho APS, Quality, Traceability, Material/Inventory, ERP integration. Không có MMD đầy đủ thì các module đó bị block.
- **MMD đứng tách hoàn toàn với event-driven execution layer** — không phụ thuộc Slice 0 (event envelope hardening), không phụ thuộc claim → session migration.

### 2.3 Tại sao chọn MMD thay vì APS/Anomaly Detection

Theo brainstorm trước (lưu trong conversation):

| Option | Data fitness | Dependency on flux core | Blast radius | ROI |
|---|---|---|---|---|
| MMD Hardening | High (data đã tồn tại) | None (đứng tách) | Low (governed by lifecycle + audit) | Multiplier cho 5 module sau |
| APS-Lite Sequencing Advisor | Medium (cần master data version stable trước) | Phụ thuộc MMD versioning | Low (advisory) | Wave 2 |
| OEE Deep Dive / Anomaly Downtime | Low (cần Slice 0 + 4 tuần data) | High | Medium | Wave 3 |
| Anomaly QC | None (Quality Lite chưa có) | Block | N/A | Loại |

→ MMD Hardening là track parallel an toàn nhất + ROI cao nhất ở giai đoạn này.

---

## 3. Goals

1. **Lift toàn bộ 9 MMD screens lên CONNECTED state**, không còn SHELL/MOCK_FIXTURE trong domain master data.
2. **Enable lifecycle mutations** (create / update / release / retire) cho 4 sub-domain chính: Product, Routing, BOM, Reason Code (unified). Resource Requirement enable theo nhu cầu (xem Section 6).
3. **Establish versioning model** đủ dùng cho production: mỗi master data entity có version_no + supersedes_id + lifecycle state machine.
4. **Establish approval gate** cho governed transitions (RELEASED, RETIRED) theo SoD principle (requester ≠ approver).
5. **Provide onboarding tool** (CSV/Excel import) để tenant mới setup master data trong 1 ngày thay vì 1 tuần manual entry.
6. **Fix permission code semantic** — không dùng `admin.user.manage` cho master data action.
7. **Maintain Hard Mode MOM v3 compliance** trên mọi slice chạm governance.

---

## 4. Non-Goals

| Non-goal | Rationale |
|---|---|
| Continuous bidirectional ERP sync | Out of scope. Chỉ làm read-only ERP integration tham khảo nếu có. Bidirectional sync = riêng track integration sau. |
| Bulk update production master data (UPDATE many rows from CSV) | Quá rủi ro. RELEASED data chỉ sửa qua "create new version + release" flow. |
| Full bitemporal versioning (effective_date + recorded_date independently) | Over-engineered cho phase này. Giữ lại trong P2 future considerations. |
| BOM explosion / resource roll-up calculator | Thuộc Material/Inventory module, không phải MMD. |
| Recipe / Formula / Phase model (ISA-88) cho batch/continuous | Đã được đưa vào "explicitly out of current immediate scope" trong Product Scope and Phase Boundary. |
| Workflow engine generic | Reuse existing `approval_service.py`, không build engine mới. |
| Master data migration từ legacy system | Có thể tận dụng CSV import nếu legacy có thể export ra CSV. Không build dedicated migration tool. |
| Real-time master data change notification (event broker) | Wait for Slice 0 envelope + future eventing. |
| GraphQL / read-model unification across MMD | Premature. REST endpoints riêng từng entity là đủ. |
| Mobile-first MMD UI | MMD là engineering screen, desktop-first. Tablet OK. Mobile defer. |

---

## 5. Pre-conditions & Dependencies

| Pre-condition | Status | Owner |
|---|---|---|
| FE Foundation/IAM track không chạm Product/Routing/BOM/Reason/Resource screens | Confirmed (different scope) | FE lead |
| BE claim → session migration không chạm Product/Routing tables | Confirmed (different domain) | BE lead |
| Action registry hỗ trợ thêm action code mới (cho permission fix) | Verify needed (do action registry FE đang được làm) | FE Foundation team |
| Approval service `approval_service.py` đã hỗ trợ generic resource type | Verify needed | BE lead |
| Security event service có thể nhận resource_type="product" / "routing" / "bom" / "reason_code" | Verified ✓ (đã thấy product service dùng) | — |
| Database có write capacity cho versioning columns | Should be fine | DBA / Backend lead |

---

## 6. Phase Breakdown

### Phase A — Backend Foundation Gaps (4–5 tuần)

#### A.1 BOM Backend Domain (NEW) — P0

**Scope:**
- New tables: `boms` (header) + `bom_components` (lines).
- Schema includes: `bom_id`, `tenant_id`, `product_id` (FK), `bom_code`, `bom_name`, `version_no`, `supersedes_bom_id` (nullable), `lifecycle_status` (DRAFT/RELEASED/RETIRED), `effective_from` (nullable), `effective_to` (nullable), `description`, `created_at`, `updated_at`.
- Component schema: `component_id`, `bom_id` (FK), `sequence_no`, `component_code`, `component_name`, `quantity`, `uom`, `scrap_factor`, `item_type` (raw/sub_assembly/purchased), `note`.
- New service `bom_service.py` mirror pattern của `product_service.py`: create / update / release / retire + invariant checks + audit via security_event.
- New API `/v1/boms` + `/v1/boms/{bom_id}` + `/v1/boms/{bom_id}/components`.
- New repository `bom_repository.py`.
- Migration script.

**Acceptance:**
- All 4 lifecycle transitions tested.
- Unique constraint: `(tenant_id, product_id, version_no)` for BOM, `(tenant_id, bom_id, sequence_no)` for component.
- RELEASED BOM không sửa structural; chỉ tạo new version mới được.
- Audit ghi đầy đủ với `resource_type="bom"`.

#### A.2 Routing Operation API Extension — P0

**Scope:**
- Extend `RoutingOperationItemFromAPI` để bao gồm: `setup_time`, `run_time_per_unit`, `work_center`, `required_skill`, `required_skill_level`, `qc_checkpoint_count`.
- Verify model `routing.py` đã có các field này chưa; nếu chưa, migration thêm.
- Optional: tách endpoint `GET /v1/routings/{routing_id}/operations/{operation_id}` (decision: nested response trong `GET /v1/routings/{id}` đủ rồi, không cần tách endpoint riêng nếu nested response không quá lớn).

**Acceptance:**
- Frontend có thể render full operation detail từ API (không cần mock fixture).
- Backward compatibility: nested operations array vẫn hoạt động.

#### A.3 Resource Requirements API Expose — P0

**Scope:**
- Service `resource_requirement_service.py` đã có. Cần expose qua API endpoint `/v1/resource-requirements` với filter `routing_id`, `operation_id`, `station_id`.
- Schema: `requirement_id`, `tenant_id`, `operation_id` (FK), `station_id` (nullable), `equipment_capability` (string), `required_skill_level`, `setup_constraint`, `lifecycle_status`.
- Add lifecycle (DRAFT/RELEASED/RETIRED) + audit + invariant nếu service chưa có.

**Acceptance:**
- API trả ra đúng record cho filter.
- Lifecycle transition tested.

#### A.4 Unified Reason Codes API — P0 (CRITICAL — tránh disrupt downtime)

**Scope:**
- New table `reason_codes` (unified across domains: downtime, scrap, pause, reopen, quality_hold).
- Schema: `reason_code_id`, `tenant_id`, `code`, `name`, `domain` (enum), `requires_comment`, `requires_supervisor_review`, `lifecycle_status`, `created_at`, `updated_at`.
- New service `reason_code_service.py` + repository + API `/v1/reason-codes` với filter `domain`.
- **CRITICAL:** giữ nguyên `/v1/downtime-reasons` endpoint hoạt động — operationally active. Có thể implement bằng cách:
  - Option 1 (đề xuất): `/v1/downtime-reasons` nội bộ delegate sang `reason_code_service.list_by_domain("downtime")`. Một bảng nguồn duy nhất.
  - Option 2: keep 2 bảng song song — ❌ KHÔNG đề xuất, tạo data duplication.
- Migration: import data hiện có của downtime_reasons vào reason_codes table với `domain="downtime"`.

**Acceptance:**
- `/v1/downtime-reasons` vẫn trả ra đúng data như cũ (regression test).
- `/v1/reason-codes?domain=downtime` trả cùng kết quả.
- 5 domain hoạt động đầy đủ.
- Station Execution `StartDowntimeDialog` không bị break (smoke test bắt buộc).

#### A.5 Permission Code Fix — P0

**Scope:**
- Define new action codes:
  - `admin.master_data.product.create / update / release / retire`
  - `admin.master_data.routing.create / update / release / retire`
  - `admin.master_data.bom.create / update / release / retire`
  - `admin.master_data.resource_requirement.create / update / release / retire`
  - `admin.master_data.reason_code.create / update / release / retire`
- Coordinate với FE Foundation/IAM team về Action Registry — đăng ký các action code mới.
- Thay `require_action("admin.user.manage")` trong `products.py` (và các file tương tự) bằng action code đúng.
- Update default role bindings: IEP/PMG có action create/update; ADM có action release/retire (xem Section 9 approval workflow).

**Acceptance:**
- Không còn `admin.user.manage` trong master data API.
- Action codes hiển thị trong Action Registry UI.
- Authorization tests pass cho từng role.

---

### Phase B — Frontend Connect (2–3 tuần, parallel-able với cuối Phase A)

#### B.1 BOM List + Detail Connect — P0

- Tạo `frontend/src/app/api/bomApi.ts`.
- Replace mock fixture trong `BomList.tsx` + `BomDetail.tsx` bằng real API call.
- Update `screenStatus.ts` từ SHELL → CONNECTED.
- Remove `MockWarningBanner`, giữ `BackendRequiredNotice` (vì governance workflow sẽ disable lifecycle action ban đầu).

#### B.2 Routing Operation Detail Connect — P0

- Update `routingApi.ts` để bao gồm extended fields.
- Replace mock fixture trong `RoutingOperationDetail.tsx`.
- Wire link từ `RouteDetail.tsx` operation rows.

#### B.3 Resource Requirements Connect — P0

- Tạo `frontend/src/app/api/resourceRequirementsApi.ts`.
- Replace mock fixture trong `ResourceRequirements.tsx`.

#### B.4 Reason Codes Connect — P0

- Tạo `frontend/src/app/api/reasonCodesApi.ts`.
- Replace mock fixture trong `ReasonCodes.tsx`.
- **Smoke test:** Station Execution `StartDowntimeDialog` vẫn fetch downtime list đúng (regression).

#### B.5 i18n Update — P0

- Add new i18n keys cho BOM/Routing Op/Resource Req/Reason Code mutation actions, error messages, lifecycle badges.
- Maintain en/ja parity (theo report hiện tại 1092 keys).

---

### Phase C — Mutation Enablement (3–4 tuần, sau Phase A + B)

Đây là phase phức tạp nhất vì kèm versioning + approval workflow.

#### C.1 Versioning Model Implementation — P0

Theo Section 8 đề xuất.

#### C.2 Approval Workflow Integration — P0

Theo Section 9 đề xuất.

#### C.3 Frontend Mutation Enablement — P0

- Enable Create / Edit dialog cho Product, Routing, BOM, Reason Code, Resource Requirement.
- Enable Release / Retire actions (qua approval flow).
- Show lifecycle state machine clearly trong UI (DRAFT → RELEASED → RETIRED + new version flow).
- Approval pending state hiển thị rõ.

#### C.4 RELEASED → New Version Flow — P0

- UI: nút "Create New Version" trên RELEASED entity → tạo DRAFT mới với `supersedes_id` trỏ về RELEASED hiện tại.
- BE: service hỗ trợ flow này transactionally.

#### C.5 Audit Trail UI Hook — P1

- ProductDetail / RoutingDetail / BomDetail có tab "History" show change history từ `security_event` filtered theo `resource_id`.
- Reuse `AuditLog.tsx` component nếu khả thi.

---

### Phase D — Import/Export Onboarding Tool (2 tuần, có thể parallel với Phase C)

Theo Section 10 đề xuất.

---

### Phase E — Cross-Reference & Polish (1–2 tuần, sau Phase C)

#### E.1 BOM Tab in ProductDetail — P1

- ProductDetail.tsx thêm tab "BOM" liệt kê BOM versions linked với product.
- Click → `/bom/{bom_id}`.

#### E.2 BOM-Routing Cross-Reference View — P1

- Trang `/products/{product_id}` show "Routing & BOM" section với cả routing nào dùng product này + BOM nào.

#### E.3 Routing-Operation-ResourceRequirement chain — P1

- Trên RoutingOperationDetail, show resource requirements applicable cho operation này.

---

## 7. Requirements Summary (P0 / P1 / P2)

### P0 — Must have

| ID | Requirement | Phase |
|---|---|---|
| P0-1 | BOM backend domain (table + service + API) | A.1 |
| P0-2 | Routing Operation API extended fields | A.2 |
| P0-3 | Resource Requirements API expose | A.3 |
| P0-4 | Unified Reason Codes API + downtime backward compat | A.4 |
| P0-5 | Permission code semantic fix (no more `admin.user.manage` for MMD) | A.5 |
| P0-6 | Frontend connect 5 SHELL screens | B.1–B.4 |
| P0-7 | Versioning model (3-state + version_no + supersedes_id) | C.1 |
| P0-8 | Approval workflow on RELEASED + RETIRED transitions (SoD enforced) | C.2 |
| P0-9 | Mutation UI enabled cho 4 sub-domain | C.3 |
| P0-10 | RELEASED → new version flow | C.4 |
| P0-11 | i18n parity maintained (en/ja) | B.5 |
| P0-12 | Audit logging cho mọi mutation | A.1, A.3, A.4 |
| P0-13 | CSV import cho tenant onboarding (Product, Routing, BOM, Reason Code) | D |
| P0-14 | JSON snapshot export per master data domain | D |

### P1 — Should have (post-P0 hoặc parallel khi capacity cho phép)

| ID | Requirement | Phase |
|---|---|---|
| P1-1 | Audit Trail tab trong DetailView | C.5 |
| P1-2 | BOM tab in ProductDetail | E.1 |
| P1-3 | BOM-Routing cross-reference view | E.2 |
| P1-4 | Routing-Operation-ResourceRequirement chain view | E.3 |
| P1-5 | Excel (xlsx) import option ngoài CSV | D |
| P1-6 | Import dry-run + validation report | D |
| P1-7 | Bulk download tất cả master data 1 tenant ra zip | D |

### P2 — Future considerations (out of scope, designed but not built)

| ID | Requirement |
|---|---|
| P2-1 | Bitemporal versioning (effective + recorded date independent) |
| P2-2 | Master data change event broker / outbox |
| P2-3 | ERP bidirectional sync |
| P2-4 | Recipe/Formula/Phase model (ISA-88) |
| P2-5 | Workflow engine generic |
| P2-6 | Bulk update production data via CSV (governed) |
| P2-7 | Master data lineage / impact analysis |
| P2-8 | A/B versioning (multiple RELEASED versions concurrent) |

---

## 8. Architecture Decision: Versioning Depth

### 8.1 Vấn đề

Hiện tại Product chỉ có `lifecycle_status` (DRAFT/RELEASED/RETIRED). Không có `version_no`, không có concept "version 2 của product X supersedes version 1". Điều này dẫn đến:

- Khi sửa RELEASED product, hiện tại bị reject (`RELEASED product structural update is not allowed`). Nhưng KHÔNG có cách "tạo version mới" để track lịch sử.
- WO/Production Order pin `product_id` (chuỗi UUID), không pin version → khi product retired, WO cũ tham chiếu vào dead reference.
- Không có cách trace "WO này dùng version nào của BOM/Routing".

### 8.2 Position của PO-SA Agent (đánh dấu opinion)

**Đề xuất: 3-state lifecycle + version_no + supersedes_id (minimal versioning), KHÔNG full bitemporal.**

#### 8.2.1 Schema thay đổi

Thêm vào `products` (và tương tự cho `routings`, `boms`, `resource_requirements`, `reason_codes`):

```sql
ALTER TABLE products
  ADD COLUMN version_no INT NOT NULL DEFAULT 1,
  ADD COLUMN supersedes_product_id VARCHAR(64) NULL REFERENCES products(product_id),
  ADD COLUMN superseded_by_product_id VARCHAR(64) NULL REFERENCES products(product_id),
  ADD COLUMN released_at TIMESTAMPTZ NULL,
  ADD COLUMN retired_at TIMESTAMPTZ NULL;

-- Unique constraint: 1 product_code có thể có nhiều version, nhưng chỉ 1 version RELEASED tại 1 thời điểm
CREATE UNIQUE INDEX idx_products_code_released
  ON products (tenant_id, product_code)
  WHERE lifecycle_status = 'RELEASED';
```

#### 8.2.2 Lifecycle state machine

```
[DRAFT]
   │
   │ release (approval gate, see Section 9)
   ▼
[RELEASED] ────────── create_new_version ────────► [DRAFT] (new row, supersedes prev)
   │                                                   │
   │ retire (approval gate)                            │ release
   ▼                                                   ▼
[RETIRED]                                          [RELEASED] (prev becomes RETIRED auto)
```

#### 8.2.3 Invariant rules

- 1 `(tenant_id, product_code)` chỉ có **tối đa 1 row RELEASED** tại 1 thời điểm.
- Nhiều DRAFT có thể tồn tại nhưng chỉ 1 sẽ được release (việc release thứ 2 sẽ auto-retire row trước).
- `supersedes_product_id` phải trỏ về row RELEASED hoặc RETIRED của cùng `product_code`.
- `superseded_by_product_id` được set tự động khi version mới release.
- WO/Production Order khi tạo phải pin `product_id` cụ thể (UUID), không phải `product_code`. → guarantee reproducibility.

#### 8.2.4 Tại sao không full bitemporal?

Bitemporal versioning (tách `effective_from/to` và `recorded_from/to`) cần thiết khi:
- Có nhiều version active đồng thời cho các time-window khác nhau (vd: BOM mùa hè vs mùa đông).
- Cần "as-of" query: "BOM ngày 1/3/2026 trông như thế nào?"
- Có ERP audit yêu cầu temporal correctness chuẩn.

→ **Phase này chưa có use-case cụ thể**. Thêm bitemporal sớm = over-engineering. Defer P2.

#### 8.2.5 Tại sao không multi-active version (A/B)?

Cùng lý do — chưa có use-case. WO chỉ pin 1 version cụ thể, không cần nhiều RELEASED concurrent. Defer P2.

#### 8.2.6 Migration strategy

- Backfill `version_no = 1` cho tất cả existing rows.
- Backfill `released_at`/`retired_at` từ `updated_at` khi `lifecycle_status` chuyển trạng thái (nếu có history; nếu không, NULL).
- Existing `RELEASED` rows phải pass unique constraint mới — có thể conflict nếu có data dirty (cùng product_code có 2+ RELEASED). Cần audit trước migration.

#### 8.2.7 Trap warning

- **Trap 1:** đừng để `version_no` được auto-increment per row insert. Phải tính theo `(tenant_id, product_code)` group. Logic ở service layer.
- **Trap 2:** UI phải hiển thị version_no rõ ràng trên mọi screen. Operator nhầm version sẽ tạo defect.
- **Trap 3:** `supersedes_product_id` phải đảm bảo cycle prevention (A supersedes B, B supersedes A). DB constraint không catch được, service phải check.
- **Trap 4:** Search/filter UI phải có toggle "show all versions" vs "show released only" — default "released only".

---

## 9. Architecture Decision: Approval Workflow

### 9.1 Vấn đề

Hiện tại `release_product()` direct mutation, không có approval gate. Nguyên tắc SoD trong FleziBCG (theo Product Business Truth + IAM direction):

> "production actions by ADM/OTS should go through controlled impersonation / support session"
> "keep separation of duties strict: requester must not equal approver, even under impersonation"

→ Vi phạm SoD nếu cùng 1 user create + release master data.

### 9.2 Position của PO-SA Agent (đánh dấu opinion)

**Đề xuất: SoD gate CHỈ trên transitions RELEASED và RETIRED, KHÔNG gate trên DRAFT mutation.**

#### 9.2.1 State transitions có gate

| Transition | Gate? | Lý do |
|---|---|---|
| Create DRAFT | ❌ No gate | Engineer tự do tạo nháp, chưa có ảnh hưởng production |
| Update DRAFT | ❌ No gate | Tinh chỉnh draft tự do |
| DRAFT → RELEASED | ✅ **Approval required, SoD enforced** | Released = production truth, ảnh hưởng WO + execution |
| RELEASED → RETIRED | ✅ **Approval required, SoD enforced** | Retired = withdraw production capability |
| Create new version (RELEASED → DRAFT) | ❌ No gate | Tạo nháp version mới chưa ảnh hưởng |
| Edit RELEASED structural | 🚫 Cấm | Phải qua flow new version |

#### 9.2.2 Approval flow integration

Reuse `approval_service.py` hiện có:

```
Engineer A: requestRelease(product_id) 
  → approval_service.create(
      resource_type="product",
      resource_id=product_id,
      action="release",
      requested_by=A,
      required_approver_roles=["PMG", "ADM"]  // configurable per tenant
    )
  → Status: PENDING_APPROVAL
  → Notification sent to eligible approvers

Approver B (B != A): approve(approval_id)
  → approval_service.approve(approval_id, approver_user_id=B)
  → On approval: trigger product_service.release_product()
  → product.lifecycle_status: DRAFT → RELEASED
  → audit logged with both A (requester) and B (approver) IDs
```

#### 9.2.3 Approver role per resource type

Default config (configurable per tenant):

| Resource type | Approver roles | Rationale |
|---|---|---|
| Product release | PMG, ADM | Cross-functional impact |
| Product retire | PMG, ADM | Same |
| Routing release | IEP (if requester != IEP) hoặc PMG | Engineering-led approval |
| Routing retire | PMG, ADM | Higher approval (impacts execution) |
| BOM release | IEP, PMG | Material planning impact |
| BOM retire | PMG, ADM | Higher |
| Resource Req release | IEP, PMG | Capability-related |
| Reason Code release | PMG, ADM | Governance vocabulary |

#### 9.2.4 SoD enforcement

- `requested_by != approved_by` — enforce ở `approval_service.approve()`.
- Impersonation case: nếu A impersonating B request → effective requester là B (acting), audit ghi cả 2. Approval phải đến từ user khác B (effective) và khác A (impersonator).

#### 9.2.5 Edge cases

- **Single-person tenant (testing/dev):** Có config flag `tenant.master_data_approval.single_person_allowed` để bypass SoD ở dev/staging. Production tenant **không được set flag này**.
- **Approval expires:** PENDING_APPROVAL có TTL (e.g., 30 ngày) → tự động cancel. Engineer phải re-request.
- **Approval rejected:** ghi audit, gửi notification về requester. Product giữ nguyên DRAFT.

#### 9.2.6 Tại sao không gate DRAFT mutation?

Engineer cần freedom để iterate. Gate DRAFT làm chậm engineering velocity 10x mà không tăng safety (DRAFT chưa được consume bởi production).

#### 9.2.7 Trap warning

- **Trap 1:** đừng để approval workflow trở thành blocker. Phải có dashboard "My pending approvals" cho approvers, notification kịp thời.
- **Trap 2:** approval queue có thể tích tụ nếu approver bận. Cần delegation rule (approver vắng mặt → delegate cho người khác). Có thể defer P1.
- **Trap 3:** edit RELEASED structural cấm — UI phải làm rõ "muốn sửa? hãy create new version" thay vì chỉ disable nút.
- **Trap 4:** approval audit phải link với security_event để có 1 timeline duy nhất, không tách rời.

---

## 10. Architecture Decision: Import/Export Scope

### 10.1 Câu hỏi từ An: "Cụ thể Import/export cái gì?"

Có nhiều use case khác nhau, mình tách rõ:

| Use case | In scope? | Lý do |
|---|---|---|
| **A. Tenant onboarding** — import full set product/routing/BOM/reason code khi setup tenant mới | ✅ YES | High value cho sales + onboarding team |
| **B. Master data backup snapshot** — export current state ra file để audit/restore | ✅ YES | Compliance + DR |
| **C. Bulk update production data** — import CSV để update many existing rows | ❌ NO (P2) | Quá rủi ro, RELEASED data phải qua new version flow |
| **D. Continuous ERP sync** (bidirectional) | ❌ NO (out of MMD scope) | Track integration riêng |
| **E. Migration từ legacy MES** | ⚠️ Tận dụng A | Nếu legacy export ra CSV, dùng A. Không build dedicated migration tool. |
| **F. Bulk download tất cả master data 1 tenant** | ✅ P1 | Nice to have, gộp vào B |
| **G. Download template CSV trống để fill** | ✅ YES | Bắt buộc cho A |

### 10.2 Position của PO-SA Agent (đánh dấu opinion)

**Đề xuất: làm A + B + G ở Phase D. Defer C/D/E/F (F nâng lên P1 nếu capacity cho phép).**

#### 10.2.1 Import (use case A) — scope chi tiết

**Format:** CSV (UTF-8, header row required) hoặc Excel (.xlsx). Phase 1 chỉ CSV; Excel là P1.

**Scope per domain:**

- **Product import:** columns = `product_code, product_name, product_type, description`. Import = create as DRAFT.
- **Routing import:** 2 sheets (CSV: 2 file riêng) — `routings.csv` (header) + `routing_operations.csv` (lines). Linked by `routing_code`.
- **BOM import:** 2 sheets — `boms.csv` + `bom_components.csv`. Linked by `bom_code`. BOM phải reference product_code đã tồn tại.
- **Reason Code import:** 1 sheet `reason_codes.csv`. Columns = `code, name, domain, requires_comment, requires_supervisor_review`.
- **Resource Requirement import:** P1, defer (cần model rõ trước).

**Validation:**

- Pre-validate trước commit:
  - Reference integrity (BOM trỏ product_code phải tồn tại).
  - Duplicate detection.
  - Format validation (enum values, numeric ranges).
- Output validation report: số rows OK, số rows error, lý do error per row.
- **Dry-run mode (P1):** validate only, không commit.
- **Commit mode (P0):** commit toàn bộ trong 1 transaction. Rollback nếu bất kỳ row nào fail.

**Authorization:**

- Action code `admin.master_data.{domain}.import` riêng (tách khỏi create/update single).
- Approval gate **không** áp cho import (vì import tạo DRAFT, chưa release). Release phải qua flow C.2 từng row.

**Audit:**

- Log 1 audit event "MASTER_DATA.IMPORT_BATCH" với detail = source filename, row count, success count, fail count.
- Log audit event riêng cho mỗi row created (PRODUCT.CREATED, etc.) để consistency với manual create.

#### 10.2.2 Export (use case B + F) — scope chi tiết

**Format:** JSON (canonical) + CSV (per domain) đều support.

**Scope:**

- Export per domain: `GET /v1/{domain}/export?format=csv|json&lifecycle=all|released_only`.
- Bulk export tenant (P1): zip file chứa toàn bộ domain.

**Authorization:**

- Action code `admin.master_data.{domain}.export`.
- Default: PMG, ADM allowed. IEP có thể export domain mình quản lý.

**Audit:**

- Log "MASTER_DATA.EXPORT" với filter scope. Quan trọng cho audit data exfiltration.

#### 10.2.3 Tại sao không bulk update production data (use case C)?

Updating RELEASED data trực tiếp vi phạm versioning model (Section 8) + bypass approval (Section 9). Nếu cho phép, mọi safety net của master data hardening bị vô hiệu hóa. Defer P2 nếu thực sự cần — và khi đó phải design riêng.

#### 10.2.4 Trap warning

- **Trap 1:** import file chứa hàng nghìn rows có thể timeout HTTP. Cần background job pattern (return job_id, poll status). Hoặc giới hạn file size (e.g., 5000 rows / file).
- **Trap 2:** import từ Excel với encoding khác UTF-8 → garbled data. Force UTF-8 + clear error message.
- **Trap 3:** export JSON chứa toàn bộ data tenant — security concern. Phải audit + rate limit.
- **Trap 4:** download template CSV trống — phải chứa header + 1 row example commented out (hoặc separate README) để user biết format.
- **Trap 5:** import CSV với column thừa → silent ignore vs error? Đề xuất: warning, không error (forgiving on extra, strict on missing).

---

## 11. Acceptance Criteria — Track Overall

Given track Master Data Hardening đã hoàn thành Phase A + B + C + D.

- When stakeholder mở MMD section trong UI:
  - Then 9 screens hoạt động với real data, không còn SHELL/MOCK_FIXTURE.
  - And mỗi screen có lifecycle action (Create / Edit DRAFT / Release / Retire / Create New Version) hoạt động đúng theo state machine.
- When engineer A tạo product DRAFT và request release:
  - Then approval pending notification gửi đến PMG/ADM.
  - And A không thể tự approve (SoD enforced).
- When approver B (B != A) approve:
  - Then product → RELEASED, audit log có cả A và B.
- When engineer cố sửa RELEASED product:
  - Then UI hiển thị "create new version" thay vì cho sửa.
- When admin import CSV product cho tenant mới:
  - Then validation report hiển thị, commit thành công nếu pass, rollback toàn bộ nếu fail.
- When admin export master data:
  - Then file download chứa đúng data theo filter, audit log ghi nhận.
- When permission audit chạy:
  - Then không còn `admin.user.manage` trong master data API.
- When `/v1/downtime-reasons` được gọi từ Station Execution:
  - Then trả ra cùng kết quả như trước (regression pass).

---

## 12. Open Questions for Team

| # | Question | Owner |
|---|---|---|
| Q1 | Action Registry FE đang được làm — có thể đăng ký thêm `admin.master_data.*` action codes mới không? Timeline? | FE Foundation lead |
| Q2 | `approval_service.py` hiện tại có support generic `resource_type` chưa, hay đang hardcoded cho 1 use case? Nếu hardcoded, cần extend trước Phase C. | BE lead |
| Q3 | Production data có row `products` nào hiện đang vi phạm unique constraint mới `(tenant_id, product_code, RELEASED)` không? Cần audit trước migration. | DBA |
| Q4 | Reason code unification: chọn Option 1 (delegate `/v1/downtime-reasons` sang reason_code_service) hay Option 2 (giữ 2 bảng)? Đề xuất Option 1 — confirm? | BE lead + Architecture |
| Q5 | Import file size limit: 5000 rows / file đủ không? Nếu tenant onboarding cần 50000 rows, phải dùng background job pattern. | Sales / Onboarding team |
| Q6 | Default approver role per resource type (Section 9.2.3) — config theo tenant hay hardcoded? Đề xuất config với default. | PO + Architecture |
| Q7 | RELEASED → RETIRED có cần approval không? Hay RETIRED chỉ cần audit log? Đề xuất có approval (Section 9). Confirm? | PO |
| Q8 | Single-person tenant bypass SoD — chấp nhận trong dev/staging, cấm production. Có cần làm UI flag rõ ràng không? | Architecture |
| Q9 | Export JSON full tenant — security concern: ai được phép, rate limit thế nào? | Security/Architecture |
| Q10 | i18n cho Vietnamese ngoài en + ja? Theo report hiện chỉ en/ja. Có cần thêm vi không? | PO |
| Q11 | Audit Trail tab (P1-1) có thể defer hoàn toàn nếu AuditLog.tsx (FE Foundation track) đã đủ generic để filter theo resource_id? | FE Foundation lead |
| Q12 | Resource Requirements lifecycle — có cần Release/Retire không, hay chỉ Active/Inactive là đủ? Resource req khác Product/BOM ở chỗ ít "version" hơn. | IEP / PO |

---

## 13. Timeline & Dependencies

```
Week:    1   2   3   4   5   6   7   8   9   10  11  12  13  14
Phase A: ████████████████████
   A.1 BOM BE         ████████
   A.2 Routing Op ext     ████
   A.3 Resource Req API   ████
   A.4 Reason Codes API ████████
   A.5 Permission fix       ████

Phase B:                 ████████████
   B.1–B.5 FE connect

Phase C:                         ████████████████
   C.1 Versioning            ████████
   C.2 Approval                  ████████
   C.3 Mutation UI                  ████████████
   C.4 New version flow                 ████████
   C.5 Audit tab (P1)                       ████

Phase D:                         ████████████ (parallel với C)
   Import/export

Phase E:                                         ████████
   Cross-reference & polish
```

Hard dependencies:

- Phase B chờ Phase A từng sub-component (B.1 chờ A.1, B.2 chờ A.2, etc.). Có thể parallel khi sub-component xong.
- Phase C chờ Phase B (cần CONNECTED screens mới enable mutation).
- Phase D có thể parallel với Phase C (independent backend).
- Phase E chờ Phase C.

External dependencies:

- Action Registry (FE Foundation track) cần xong trước Phase A.5 commit.
- `approval_service.py` extend (nếu cần) trước Phase C.2.

---

## 14. Hard Mode MOM v3 Compliance

Track này chạm:

- ✅ Tenant/scope/auth — permission code refactor
- ✅ Audit/security event — extending audit family
- ✅ DB migration enforcing governance — versioning unique constraint, lifecycle invariant
- ✅ Role/action/scope assignment — new action codes
- ⚠️ Production reporting (indirectly) — RELEASED master data ảnh hưởng WO/execution

→ **Hard Mode MOM v3 mandatory** trước khi code mỗi slice. Mỗi sub-slice (A.1, A.2, ..., E.3) phải produce:

1. Design Evidence Extract (link tới source files inspected)
2. Event Map (cho slice có audit event mới)
3. Invariant Map (cho slice có DB constraint mới)
4. State Transition Map (cho slice chạm lifecycle)
5. Test Matrix
6. Verdict before coding

PO-SA sẽ produce mini evidence pack cho từng slice khi An kích hoạt slice đó. Không produce all 17 slices upfront — chỉ produce khi sắp code.

---

## 15. Stop Conditions

Pause toàn track nếu:

- FE Foundation track gặp delay nghiêm trọng → Action Registry không sẵn sàng đúng hạn → Phase A.5 block.
- Phát hiện multi-tenancy isolation gap nghiêm trọng trong existing master data → cần fix isolation trước.
- Phát hiện `approval_service.py` cần rewrite lớn → defer Phase C, làm thay bằng Phase D parallel.
- Production master data dirty → migration không thể chạy → cần data cleanup task riêng trước.

Pause sub-slice nếu:

- Hard Mode MOM v3 evidence pack không pass review.
- Test coverage không đạt (≥80% cho service layer).
- Smoke test downtime regression fail (Phase A.4 critical).

---

## 16. Coding Agent Operating Rules (cho PO-SA Agent khi code)

User explicit instruction: track này "team bạn code luôn" → PO-SA Agent vận hành như coding team cho track này.

Quy tắc:

1. **Mỗi slice = 1 PR riêng**, không bundle.
2. **Trước khi code mỗi slice:** produce Hard Mode MOM v3 evidence pack + Verdict, gửi An review.
3. **Sau khi An accept:** code + tests + run verification commands (`npm run build`, `npm run lint`, `pytest`).
4. **Không touch:** execution events, claim/session migration, FE Foundation/IAM screens, station execution code, downtime_reasons endpoint behavior.
5. **i18n parity:** mọi user-facing string mới phải có cả en + ja keys.
6. **Audit:** mọi mutation phải emit security_event.
7. **Backward compatibility:** existing API/screens không được break (regression test required).
8. **Surgical changes** (theo karpathy-guidelines): chỉ touch files trong slice scope, không "improve" adjacent code.

---

## 17. Review Instructions for Team

1. **Read Section 1 (TL;DR) + Section 6 (Phase Breakdown) trước** — get the big picture trong 5 phút.
2. **Read Section 8 + 9 + 10** — đây là 3 quyết định kiến trúc quan trọng nhất, cần feedback rõ. Nếu disagree, comment vào sub-section cụ thể với lý do + alternative.
3. **Trả lời Q1–Q12 ở Section 12** trước stand-up tới — đây là blocker cho việc PO-SA produce coding-agent prompt.
4. **Verify phasing ở Section 13** — timeline có realistic không với capacity team có (1 BE coding agent + coordinate với BE/FE team chính)?
5. **Decision merge/reject:** cần ít nhất 1 BE lead + 1 FE lead + PO + 1 architecture reviewer.
6. **Nếu accept:** PO-SA sẽ produce evidence pack cho Phase A.1 (BOM backend) là slice đầu tiên.
7. **Nếu reject:** comment lý do + alternative track. PO-SA sẽ re-propose.

---

## 18. Appendix — Evidence References

### Files đã đọc cho proposal này (additional to event envelope proposal)

- `docs/audit/mmd-current-state-report.md` (v1.0 2026-05-01) — primary reference
- `frontend/src/app/pages/ProductList.tsx` (verified PARTIAL/SHELL state)
- `backend/app/api/v1/products.py` (verified permission code issue)
- `backend/app/api/v1/__init__.py` listing (verified missing endpoints: bom, resource_requirements, unified reason_codes)
- `backend/app/services/product_service.py` (verified lifecycle + audit + invariants pattern)
- `backend/app/services/__init__.py` listing (verified existing services: product, routing, resource_requirement, downtime_reason, approval, security_event)
- Frontend pages glob — verified 9 MMD screens existence

### Files chưa verify nhưng tham chiếu

- `backend/app/services/routing_service.py` — assume similar pattern to product_service
- `backend/app/services/resource_requirement_service.py` — exists but lifecycle/API status unknown
- `backend/app/services/approval_service.py` — exists but generic resource_type support unknown (Q2)
- `frontend/src/app/api/productApi.ts`, `routingApi.ts`, `downtimeReasons.ts` — referenced in mmd report

PO-SA sẽ verify các file này trước khi code mỗi slice (Hard Mode MOM v3 evidence requirement).

---

**End of Master Data Hardening Proposal**

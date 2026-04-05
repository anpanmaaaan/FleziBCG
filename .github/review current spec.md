Hiện tại tài liệu gốc của bạn đang có vài điểm quan trọng cần “bẻ trục” trước khi code tiếp: backend mới là source of truth nhưng screen matrix lại đang bị dùng như auth truth; `SUP` có `EXECUTE` ở backend nhưng không có execution screen; `ADM/OTS` vừa bị mô tả là unrestricted/admin, vừa bị bó ở strict matrix; QC UI và APS engine đều đang ngoài scope nhưng screen matrix lại đang diễn đạt như thể đã có module nghiệp vụ thật. Đồng thời spec hiện tại vẫn đang khóa `tenant-only scope`, `no custom roles`, `no multi-role`, và `modular monolith`.  

---

# 1) Mục tiêu thiết kế mới

## 1.1 Mình đề xuất đổi từ “role matrix” sang “Access Architecture”

Thay vì chỉ có một bảng ROLE × SCREEN, mình khuyên chốt thành 4 lớp:

1. **Identity & AuthN**
2. **Authorization model**
3. **Frontend screen exposure**
4. **Support / impersonation / break-glass policy**

Đây là cách làm sạch nhất để không lặp lại lỗi cũ:
**FE visibility ≠ BE authorization**. Tài liệu business logic của bạn vốn đã khẳng định nguyên tắc này rồi. 

---

# 2) Những chỉnh sửa bắt buộc so với matrix cũ

## 2.1 Những gì mình giữ

* **Station Execution chỉ dành cho OPR trong UX mặc định**
* **PMG là persona nhìn toàn cảnh sản xuất**
* **ADM ≠ production manager**
* **ADM/OTS muốn làm production action thì đi qua impersonation**
* **QC và APS vẫn giữ tên screen** nếu bạn muốn, nhưng phải đổi nghĩa của chúng ở thời điểm hiện tại

## 2.2 Những gì mình sửa

### Sửa 1 — Tách official business matrix khỏi dev/support override

`ADM (DEV superadmin_view)` không nên nằm trong bảng business-facing chính.
Nó phải là:

* **support override policy**
* hoặc **support-mode appendix**

Matrix cũ đang để `ADM (STRICT)` và `ADM (DEV)` cùng bảng, điều này không tốt cho governance. 

### Sửa 2 — PMG không được gọi là “read-only”

Vì backend logic hiện tại của bạn cho `PMG` có quyền `APPROVE`, và approval rules còn cho PMG approve một số action như `SCRAP`, `WO_SPLIT`, `WO_MERGE`. 

### Sửa 3 — SUP không còn bị “lửng”

Matrix cũ chặn SUP khỏi Station Execution, nhưng backend lại cho SUP có `EXECUTE`.
Mình chốt lại theo best practice MES như sau:

* **SUP không dùng operator station flow**
* nhưng **SUP có limited supervisory actions**

  * unblock
  * assist resume
  * log / close downtime reason
  * escalate
  * request hold / rework
  * supervisor-side intervention

Như vậy vừa khớp MES thực tế, vừa không biến SUP thành operator thứ hai. Current backend mapping của bạn đã có `SUP = VIEW, EXECUTE`, nên cách này khớp hơn là xóa EXECUTE khỏi SUP. 

### Sửa 4 — Giữ tên screen `QC` và `APS`, nhưng đổi nghĩa

* `QC` = **Quality Review / Approval Context / Quality Analytics**
* `APS` = **Schedule Workspace / Planning Snapshot / APS-lite future shell**

Điều này cần thiết vì current spec vẫn đang nói:

* chưa có full QC inspection UI
* chưa có APS engine thật. 

### Sửa 5 — Auth model phải được generic hóa ngay từ bây giờ

Spec hiện tại đang khóa:

* tenant-only scope
* no custom roles
* no multi-role
* modular monolith. 

Nếu bạn định hướng microservice + multi-tenant + custom role, thì **schema và service contract phải mở ngay bây giờ**, kể cả khi UI chưa bật hết feature.

---

# 3) Target design mình khuyên chốt

## 3.1 Role model: hybrid, best practice

### System roles (baseline, immutable)

* `OPR`
* `SUP`
* `IEP`
* `QCI`
* `QAL`
* `PMG`
* `EXE`
* `ADM`
* `OTS`

### Custom roles (future-ready, có thể bật sau)

* derived from system role template
* ví dụ:

  * `SUP_PACKAGING`
  * `QAL_RELEASE_ONLY`
  * `PMG_VIEW_ONLY`
  * `IEP_TRACE_EDITOR`

### Quy tắc

* **System role** = baseline semantics
* **Custom role** = business-fit extension
* **ADM / OTS** không nên custom bởi business user

---

# 4) Final role design — đủ chi tiết để code

## 4.1 FE Screen Exposure Matrix (official)

Đây là bảng dùng cho frontend/navigation.

| Role    | Dashboard | OEE | Global Ops | Station Exec | QC | Traceability | APS |
| ------- | --------: | --: | ---------: | -----------: | -: | -----------: | --: |
| **OPR** |         ❌ |   ❌ |          ❌ |            ✅ |  ❌ |            ❌ |   ❌ |
| **SUP** |         ❌ |  👀 |          ✅ |            ❌ | 👀 |           👀 |   ❌ |
| **IEP** |         ❌ |  👀 |          ✅ |            ❌ | 👀 |            ✅ |   ❌ |
| **QCI** |         ❌ |   ❌ |          ✅ |            ❌ | 👀 |            ✅ |   ❌ |
| **QAL** |         ❌ |   ❌ |          ✅ |            ❌ |  ✅ |            ✅ |   ❌ |
| **PMG** |         ✅ |   ✅ |          ✅ |            ❌ | 👀 |            ✅ |  👀 |
| **EXE** |         ✅ |   ✅ |          ❌ |            ❌ |  ❌ |            ❌ |   ❌ |
| **ADM** |         ✅ |   ✅ |          ❌ |            ❌ |  ❌ |            ❌ |   ❌ |
| **OTS** |         ✅ |   ✅ |          ❌ |            ❌ |  ❌ |            ❌ |   ❌ |

### Support override appendix

| Role                     | Global Ops | QC | Traceability | APS |
| ------------------------ | ---------: | -: | -----------: | --: |
| **ADM/OTS support mode** |         👀 | 👀 |           👀 |  👀 |

### Hard rules

* `Station Execution` chỉ cho `OPR`
* `ADM/OTS` không phải production persona mặc định
* `SUP` không vào station screen, nhưng có supervisory actions
* `QC` và `APS` là shell/future-capable screen, không tự động đồng nghĩa với full module

---

## 4.2 Backend capability model

Đây là bảng backend, quan trọng hơn screen matrix.

### Permission families

* `VIEW`
* `EXECUTE`
* `APPROVE`
* `CONFIGURE`
* `ADMIN`

### Action codes

Đừng dừng ở permission family. Hãy thêm `action_code` ngay từ bây giờ.

#### EXECUTE actions

* `execution.start`
* `execution.report_quantity`
* `execution.complete`
* `execution.block`
* `execution.unblock`
* `execution.abort`
* `execution.downtime.log`
* `execution.supervisor.intervene`

#### APPROVE actions

* `approval.qc_hold.request`
* `approval.qc_hold.decide`
* `approval.qc_release.request`
* `approval.qc_release.decide`
* `approval.scrap.request`
* `approval.scrap.decide`
* `approval.rework.request`
* `approval.rework.decide`
* `approval.wo_split.request`
* `approval.wo_split.decide`
* `approval.wo_merge.request`
* `approval.wo_merge.decide`

#### CONFIGURE actions

* `config.route.edit`
* `config.operation.edit`
* `config.work_instruction.edit`
* `config.reason_code.edit`
* `config.dashboard.layout.edit`
* `config.qc_rule.edit`
* `config.schedule_rule.edit`

#### ADMIN actions

* `admin.user.manage`
* `admin.role.manage`
* `admin.permission.manage`
* `admin.scope.manage`
* `admin.audit.read`
* `admin.impersonation.create`
* `admin.impersonation.revoke`
* `admin.tenant.manage`

---

## 4.3 Role-to-capability mapping

### OPR

* `VIEW`: own assigned work / own station context
* `EXECUTE`:

  * start
  * report quantity
  * complete
  * block
  * request qc_hold
  * request scrap
  * request rework
* không có:

  * decide approval
  * configure
  * admin

### SUP

* `VIEW`: line / area scope
* `EXECUTE`:

  * unblock
  * intervene
  * downtime.log
  * assist execution transitions
* `APPROVE`: không mặc định
* lưu ý: SUP **không** có full operator execution UI, nhưng backend có limited execute actions

### IEP

* `VIEW`
* `CONFIGURE`:

  * route
  * operation
  * work instruction
  * process parameter
  * reason code (nếu được cấp)
* không execution, không approval mặc định

### QCI

* `VIEW`
* `APPROVE`: không
* transaction quality sâu có thể bật sau

### QAL

* `VIEW`
* `APPROVE`:

  * qc_hold.decide
  * qc_release.decide
  * scrap.decide
  * rework.decide

### PMG

* `VIEW`
* `APPROVE`:

  * wo_split.decide
  * wo_merge.decide
  * scrap.decide (nếu business muốn)
* không execute station actions

### EXE

* `VIEW`
* không execute
* không approve
* nên đổi semantic thành executive/reporting user

### ADM

* `VIEW`
* `ADMIN`
* production actions chỉ qua impersonation/support mode
* không cấp `EXECUTE/APPROVE` mặc định ở production mode

### OTS

* giống ADM về quyền hệ thống
* khác ở audit / support semantics
* production actions chỉ qua impersonation

---

# 5) Scope model — để code luôn

## 5.1 Scope hierarchy

Thay vì chỉ `tenant`, hãy code model tổng quát ngay từ đầu:

```text
tenant
 └─ plant
     └─ area
         └─ line
             └─ station
                 └─ equipment
```

Spec hiện tại mới chỉ có `tenant`, còn plant/area/line là future scope. Nếu bạn định hướng multi-tenant + microservice + custom role, đây là lúc phải mở model này. 

## 5.2 Scope assignment rule

Mỗi assignment nên là:

* `principal_id`
* `role_id`
* `scope_type`
* `scope_value`
* `is_primary`
* `is_active`
* `valid_from`
* `valid_to`

Ví dụ:

* `user_123` + `SUP` + `line` + `LINE_A`
* `user_123` + `QAL` + `plant` + `PLANT_01`

---

# 6) Data model — code-ready

## 6.1 Tables

### users

* `user_id`
* `tenant_id`
* `username`
* `email`
* `password_hash`
* `is_active`
* `created_at`
* `updated_at`

### roles

* `role_id`
* `tenant_id` nullable
* `code`
* `name`
* `description`
* `role_type` = `system | custom`
* `base_role_code` nullable
* `is_active`
* `created_by`
* `created_at`

### permissions

* `permission_id`
* `family`
* `action_code`
* `description`

### role_permissions

* `role_id`
* `permission_id`
* `effect` = `allow | deny`

### scopes

* `scope_id`
* `tenant_id`
* `scope_type`
* `scope_value`
* `parent_scope_id`

### user_role_assignments

* `assignment_id`
* `user_id`
* `role_id`
* `scope_id`
* `is_primary`
* `is_active`
* `valid_from`
* `valid_to`

### screen_exposures

* `role_id`
* `screen_code`
* `visibility` = `hidden | readonly | full`
* `lens_code` nullable

### approval_rules

* `action_code`
* `approver_role_code`
* `scope_type`
* `is_active`

### impersonation_sessions

* `session_id`
* `real_user_id`
* `acting_role_code`
* `scope_id`
* `reason`
* `created_at`
* `expires_at`
* `revoked_at`

### audit_logs

* `audit_id`
* `tenant_id`
* `user_id`
* `effective_role_code`
* `action_code`
* `resource_type`
* `resource_id`
* `scope_id`
* `impersonation_session_id`
* `payload_json`
* `created_at`

---

# 7) Microservice architecture — mình khuyên thế này

Vì bạn định hướng **microservice + on-prem/cloud + multi-tenant**, role/auth không nên nằm rải trong từng service.

## 7.1 Service boundaries

### 1. Identity Service

Phụ trách:

* login
* password / local auth
* future identity provider adapter
* JWT / refresh token

### 2. Access Control Service

Phụ trách:

* roles
* permissions
* scopes
* user-role assignments
* custom role
* screen exposure
* policy evaluation

### 3. Approval Service

Phụ trách:

* request/decide approval
* SoD
* approver resolution
* audit for approval

### 4. Impersonation Service

Có thể tách riêng hoặc để trong Access Control Service:

* create/revoke session
* effective principal resolution
* break-glass / support mode

### 5. MES Execution Service

* WO / OP / execution event
* station execution
* status derivation

### 6. Query / UI BFF

* tổng hợp capability cho FE
* `/me/screens`
* `/me/capabilities`
* lens config

## 7.2 Mình khuyên triển khai thế nào thực tế

Dù target là microservice, ở giai đoạn này mình vẫn khuyên:

* **code tách domain/service boundary như microservice**
* nhưng **deploy 2–3 service trước**, không cần 6 service tách vật lý ngay

Ví dụ:

* `identity-access` service
* `approval` service
* `mes-core` service

Cách này vừa không quá nặng, vừa future-ready.

---

# 8) Auth flow — code-ready

## 8.1 JWT claims

JWT chỉ nên chứa:

* `sub`
* `tenant_id`
* `username`
* `primary_role_code` (optional)
* `session_id`
* `exp`

Không nhét full permissions vào JWT, vì permission/scope/impersonation có thể đổi giữa session. Current spec cũng đang đi theo hướng derive permission ở request time. 

## 8.2 Authorization check flow

```text
API request
→ extract JWT
→ resolve tenant
→ resolve active impersonation session (if any)
→ build effective principal
→ ask Access Control Service:
   "Can principal P perform action X on resource Y in scope Z?"
→ allow / deny
→ log audit
```

## 8.3 Effective principal object

```json
{
  "real_user_id": "u123",
  "effective_user_id": "u123",
  "tenant_id": "t1",
  "roles": [
    { "code": "SUP", "scope": { "type": "line", "value": "LINE_A" } },
    { "code": "QAL", "scope": { "type": "plant", "value": "PLANT_01" } }
  ],
  "impersonation": {
    "active": true,
    "acting_role_code": "OPR",
    "scope_id": "station:S01"
  }
}
```

---

# 9) API contracts — tối thiểu để code

## Identity

* `POST /auth/login`
* `POST /auth/refresh`
* `POST /auth/logout`
* `GET /auth/me`

## Access control

* `GET /iam/me/capabilities`
* `GET /iam/me/screens`
* `POST /iam/authorize`
* `GET /iam/roles`
* `POST /iam/roles`
* `PUT /iam/roles/{id}`
* `POST /iam/users/{id}/assignments`
* `GET /iam/scopes`

## Impersonation

* `POST /iam/impersonations`
* `DELETE /iam/impersonations/{id}`
* `GET /iam/impersonations/active`

## Approval

* `POST /approvals`
* `POST /approvals/{id}/decide`
* `GET /approvals`
* `GET /approvals/{id}`

## FE bootstrap

* `GET /ui/bootstrap`
  trả về:
* user
* active roles
* scopes
* visible screens
* lenses
* feature flags

---

# 10) On-prem / cloud both adapt — design note

## 10.1 Những gì nên giữ portable

* PostgreSQL
* Redis optional
* object storage qua S3-compatible interface
* config qua env + secret manager abstraction
* auth provider abstraction
* event transport abstraction

## 10.2 Đừng hard-code cloud-only

Nếu muốn on-prem/cloud đều chạy:

* đừng phụ thuộc IAM của 1 cloud vendor ngay
* đừng phụ thuộc Kafka bắt buộc ngay
* đừng phụ thuộc managed identity bắt buộc ngay

## 10.3 Multi-tenant rule

Mọi entity business hoặc security đều phải có `tenant_id`, trừ:

* system dictionary toàn cục nếu bạn chủ động design multi-tenant shared catalog

---

# 11) Thứ tự triển khai phần role/auth từ bây giờ

## Sprint A — khóa model

* roles
* permissions
* scopes
* assignments
* approval actions
* screen exposure
* impersonation policy

## Sprint B — code Access Control Service

* tables
* role CRUD
* assignment CRUD
* authorize endpoint
* `/me/capabilities`
* `/me/screens`

## Sprint C — sửa MES core để dùng Access Control Service

* remove role hard-code khỏi FE
* move policy check về backend
* implement supervisory actions cho SUP
* tách PMG khỏi “read-only” wording
* chuyển ADM production action sang impersonation

## Sprint D — feature flag

* `enable_custom_roles=false`
* `enable_multi_role=true/false`
* `enable_support_override=true`

Mình khuyên:

* schema hỗ trợ **custom role + multi-role** ngay
* UI chưa cần mở hết

---

# 12) Bản chốt ngắn gọn mình khuyên bạn dùng

Nếu phải chốt một design ngắn nhất để team code, mình sẽ chốt như này:

* **Official FE matrix** như mục 4.1
* **Backend auth** theo action-level model như mục 4.2
* **ADM/OTS** = full system access, không full business action mặc định
* **SUP** = monitoring + limited intervention, không station persona
* **PMG** = broad view + selected approvals
* **QC/APS** giữ tên screen, nhưng current meaning phải được define rõ
* **Microservice target**: tách `identity-access`, `approval`, `mes-core`
* **Schema** hỗ trợ ngay từ đầu:

  * multi-tenant
  * multi-role
  * custom role
  * scope hierarchy
    dù UI có thể chưa bật hết



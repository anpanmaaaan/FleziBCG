# Station Execution — Screen List (Pre-QC Baseline, patched)

## Scope
Tài liệu này chốt **screen inventory** cho phần Station Execution **trước khi sang QC lite**.

### In scope
- queue / operation selection
- claim / release claim
- execution cockpit
- report quantity
- pause / resume
- downtime start / end
- active-state continuity (`IN_PROGRESS`, `PAUSED`, `BLOCKED`)
- queue filter persistence / selected-outside-filter helper

### Out of scope for this baseline
- QC measurement / QC hold / quality disposition
- exception / approval / disposition inbox
- close / reopen
- station session open/close as first-class screen
- supervisor/global-ops screens ngoài operator station flow
- claim handover / reassignment / support recovery transfer

## Nguyên tắc
- Một “screen” ở đây có thể là **page**, **mode trong page**, hoặc **modal/dialog** nếu nó có mục đích nghiệp vụ rõ.
- Không nhân bản cùng một truth ở nhiều màn; queue và cockpit phải đọc cùng execution truth.
- Queue visibility != claimability.
- Claimability hiện chỉ áp dụng cho status claimable; active non-terminal states vẫn phải nhìn thấy trong queue.
- **Release Claim hiện chỉ là safe path cho `PLANNED`**; không phải recovery tool cho active execution.

## Screen inventory

| ID | Screen | Type | Primary role | Purpose | Entry point | Current baseline |
|---|---|---|---|---|---|---|
| SE-SCR-01 | Station Queue / Operation Selection | Main page mode | OPR | Xem queue tại station, lọc, scan, claim item claimable, mở lại active item | Default landing của station execution | Yes |
| SE-SCR-02 | Station Execution Cockpit | Main page mode | OPR | Thực hiện execution commands trên operation đã chọn | Chọn item từ queue | Yes |
| SE-SCR-03 | Start Downtime | Modal / inline panel | OPR | Nhập downtime reason + note và mở downtime | Từ cockpit | Yes |
| SE-SCR-04 | Release Claim Confirmation | Dialog | OPR / ADM-OTS support | Xác nhận release claim **chỉ cho planned/unstarted context** | Từ queue/cockpit khi status cho phép | Yes |
| SE-SCR-05 | Queue helper state: selected item outside active filter | Inline helper state | OPR | Giữ filter hiện tại, báo item đang chọn không còn nằm trong filtered set | Từ queue sau refresh / action | Yes |

## Deferred screens / flows (explicitly not in this baseline)

| ID | Screen / Flow | Why deferred |
|---|---|---|
| SE-SCR-06 | QC Measurement Entry | Thuộc nhánh QC lite kế tiếp |
| SE-SCR-07 | QC Hold / Quality Disposition | Thuộc nhánh QC lite kế tiếp |
| SE-SCR-08 | Exception Raise / Disposition | Thuộc nhánh exception / approval |
| SE-SCR-09 | Close / Reopen Operation | Thuộc nhánh close/reopen |
| SE-SCR-10 | Station Session Entry / Close | Chưa harden thành first-class flow |
| SE-SCR-11 | Claim Handover / Reassignment / Support Recovery | Chưa có; không dùng ordinary release path để giải quyết active execution dead-end |

## Notes
- Queue hiện phải hiển thị ít nhất các active non-terminal statuses: `PLANNED`, `IN_PROGRESS`, `PAUSED`, `BLOCKED`.
- `PAUSED` / `BLOCKED` là **visible**, nhưng không mặc định là **claimable**.
- `downtime_open` là signal bắt buộc ở queue để giải thích `BLOCKED` do downtime.
- `Release Claim` không phải công cụ để “nhả rồi claim lại” trong flow `BLOCKED -> PAUSED -> RESUME`; flow đó hiện dựa vào **claim continuity**.

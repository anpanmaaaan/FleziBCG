# Station Execution — Screen Transition (Pre-QC Baseline, patched)

## Scope
Chỉ cover operator station flow trước QC lite.

---

## 1. Navigation-level transitions

| From | Trigger | To | Rule |
|---|---|---|---|
| Queue | Select operation row | Cockpit | Không reset queue filter |
| Queue | Claim success | Queue or Cockpit current flow | Refresh queue + selected item state nhất quán |
| Cockpit | Back to queue / list mode | Queue | Giữ filter hiện tại |
| Queue | Refresh queue | Queue | Giữ filter hiện tại |
| Queue | Selected item no longer matches filter | Queue + helper state | Giữ filter, hiện helper message |

---

## 2. Queue state transitions

### 2.1 Filter behavior
- Chọn filter không được mutate selected item một cách ngầm.
- Chọn item không được reset filter về `All`.
- Refresh queue không được reset filter về `All`.

### 2.2 Claim affordance behavior
- `Claim` chỉ hiện khi item claimable thật.
- `PAUSED` / `BLOCKED`:
  - visible
  - selectable/openable
  - không hiện `Ready to claim` nếu backend hiện không cho claim lại

### 2.3 Release affordance behavior
- `Release` chỉ là safe action cho `PLANNED` trong baseline hiện tại
- `IN_PROGRESS / PAUSED / BLOCKED`:
  - Release phải bị chặn / disable
  - không được tạo dead-end flow rồi buộc reclaim

---

## 3. Execution flow transitions

| Current state | Trigger | Resulting state | Screen expectation |
|---|---|---|---|
| PLANNED | Claim + Start Execution | IN_PROGRESS | Ở lại cockpit |
| IN_PROGRESS | Report Qty | IN_PROGRESS | Refresh context, không rời cockpit |
| IN_PROGRESS | Pause | PAUSED | Ở lại cockpit |
| IN_PROGRESS | Start Downtime | BLOCKED + downtime_open=true | Ở lại cockpit, show downtime-active focus |
| BLOCKED | End Downtime | PAUSED + downtime_open=false | Ở lại cockpit, không auto-resume |
| PAUSED | Resume | IN_PROGRESS | Ở lại cockpit |
| PLANNED | Release Claim | PLANNED (unclaimed) | Queue/Cockpit refreshed đúng |
| IN_PROGRESS / PAUSED / BLOCKED | Release Claim | Rejected / unavailable | Không tạo dead-end active execution flow |

---

## 4. Downtime-specific transitions

### 4.1 Start downtime
- Trigger từ cockpit
- Mở Start Downtime modal/panel
- Submit thành công:
  - đóng modal
  - quay về cùng cockpit
  - status thành `BLOCKED`
  - `downtime_open = true`
  - action focus chuyển sang `End Downtime`

### 4.2 End downtime
- Trigger từ cockpit khi đang blocked vì downtime
- Submit thành công:
  - ở lại cùng cockpit
  - status thành `PAUSED`
  - `downtime_open = false`
  - không auto-resume
  - next correct action là `Resume`

---

## 5. Claim continuity transitions

### 5.1 Intended continuity
Flow chuẩn:
1. Claim
2. Start execution
3. Start downtime -> BLOCKED
4. End downtime -> PAUSED
5. Resume execution

### 5.2 Design expectation
- Claim ownership phải persist qua `IN_PROGRESS`, `BLOCKED`, `PAUSED` cho đến khi:
  - explicit release on a safe state
  - expiry
  - terminal close policy
- Queue phải tiếp tục hiển thị active item trong các state này
- UI không được buộc reclaim trên `PAUSED` / `BLOCKED` nếu backend không hỗ trợ claim lại

### 5.3 Current safety guard
- Ordinary `Release Claim` không còn hợp lệ trên `IN_PROGRESS`, `PAUSED`, `BLOCKED`
- Nếu cần reassignment trong tương lai, đó phải là handover/transfer/support flow riêng

---

## 6. Exceptional UI continuity rules
- Nếu release claim fail: ở lại screen hiện tại + show backend error rõ ràng
- Nếu claim expire giữa flow:
  - action tiếp theo fail theo backend ownership check
  - UI phải refresh claim state và không hứa affordance sai
- Nếu selected operation biến mất khỏi filtered subset:
  - giữ filter
  - hiện helper state
  - không reset về `All`

---

## 7. Deferred transitions (not in this baseline)
- QC submit -> QC_HOLD / disposition
- raise_exception -> disposition workflow
- close_operation / reopen_operation
- open_station_session / close_station_session
- claim handover / supervised reassignment / support recovery transfer

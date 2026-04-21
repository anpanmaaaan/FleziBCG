# Station Execution — Canonical Screen Pack (Pre-QC Baseline, v2)

Tài liệu này gom 3 file canonical về screen của Station Execution thành **một pack duy nhất** để baseline trước khi sang nhánh QC lite.

## Included sections
1. Screen List
2. Screen Design
3. Screen Transition

## Baseline scope
- queue / operation selection
- claim / release claim
- execution cockpit
- report quantity
- pause / resume
- downtime start / end
- active-state continuity (`IN_PROGRESS`, `PAUSED`, `BLOCKED`)
- queue filter persistence / selected-outside-filter helper

## Explicitly deferred
- QC measurement / QC hold / quality disposition
- exception / approval / disposition
- close / reopen
- station session open/close as first-class hardened flow
- claim handover / reassignment / support recovery transfer


---

## Screen List

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


---

## Screen Design

# Station Execution — Screen Design (Pre-QC Baseline, patched)

## 1. Design principles
- Backend là source of truth.
- Queue là **scan / select / claim / reopen-context surface**, không phải chỉ là “start list”.
- Cockpit là **action surface**.
- Queue visibility != claimability.
- Không reset filter ngầm khi user chọn operation.
- Nếu selected operation không còn match filter hiện tại, giữ filter và hiện helper message.
- **Claim continuity** phải được giữ qua `IN_PROGRESS`, `BLOCKED`, `PAUSED` cho tới khi explicit release/expiry/terminal policy.
- **Release Claim không được dùng để phá continuity của active execution**.

---

## 2. SE-SCR-01 — Station Queue / Operation Selection

### 2.1 Purpose
Giúp operator:
- scan nhanh queue tại station
- hiểu item nào cần chú ý ngay
- claim item claimable
- mở lại item đang active (`IN_PROGRESS`, `PAUSED`, `BLOCKED`) mà không mất context

### 2.2 Data used
- `status`
- `downtime_open`
- `claim.state`
- `claim.claimed_by_user_id`
- `planned_start`, `planned_end`
- operation / WO / PO identifiers

### 2.3 Layout
1. **Header strip**
   - Workstation / station code
   - Refresh
   - context summary ngắn

2. **Queue summary panel**
   - Ready
   - Paused
   - Blocked
   - Downtime
   - Mine

3. **Quick filter chips**
   - All
   - Mine
   - Ready
   - Paused
   - Blocked
   - Downtime

4. **Queue list**
   - mỗi row/card hiển thị:
     - operation name
     - operation number
     - work order number
     - status badge
     - claim state cue
     - downtime indicator nếu `downtime_open = true`

5. **Inline helper state**
   - khi selected operation không còn match active filter:
     - giữ filter
     - hiện helper message
     - không reset về `All`

### 2.4 Row content
Mỗi row phải có:
- **primary text**: operation name
- **secondary text**: operation number + WO
- **status badge**: Planned / In Progress / Paused / Blocked
- **downtime hint**:
  - `Downtime active` nếu `downtime_open = true`
  - `Blocked by active downtime` nếu `status = BLOCKED` và `downtime_open = true`
- **claim hint**:
  - Claimed by you
  - Claimed by another operator
  - Ready to claim (chỉ khi claimable thật)

### 2.5 Claim affordance rules
`Ready to claim` và nút `Claim` chỉ hiện khi:
- `claim.state = none`
- và status đang thuộc claimable set của backend baseline hiện tại

`PAUSED` / `BLOCKED`:
- vẫn hiện
- vẫn chọn/mở được nếu flow cho phép
- nhưng không được hiển thị claimable cue sai

### 2.6 Release affordance rules
`Release Claim` hiện chỉ được coi là safe khi:
- `claim.state = mine`
- `status = PLANNED`

`IN_PROGRESS` / `PAUSED` / `BLOCKED`:
- ordinary release phải **disabled / unavailable**
- vì release ở các state này tạo dead-end flow khi operator không reclaim lại được
- nếu sau này cần reassignment/handover, phải là flow riêng có audit, không dùng release thường

### 2.7 Visual priority
- `BLOCKED`: accent mạnh hơn
- `PAUSED`: accent trung bình
- `downtime_open`: indicator rõ nhưng gọn
- selected row: highlight ổn định
- claim-state lock visual giữ nguyên với `claim.state = other`

---

## 3. SE-SCR-02 — Station Execution Cockpit

### 3.1 Purpose
Màn action chính cho operation đã chọn.

### 3.2 Layout
1. **Context strip**
   - station
   - work order
   - operation
   - claim ownership

2. **Execution state / production context**
   - status
   - remaining / reported quantities
   - downtime active / not active
   - next-action hint

3. **Quantity entry**
   - Good Qty (delta)
   - Scrap Qty (delta)
   - Report Qty = primary action

4. **Execution actions**
   - Pause
   - Resume
   - Start Downtime
   - End Downtime
   - Complete Operation

5. **Session / secondary actions**
   - Release Claim (only when safe under current semantics)
   - session-level controls nếu có

### 3.3 Action logic
- `allowed_actions` từ backend là nguồn chính cho action enable/disable
- `claim.state = mine` vẫn là ownership UX gate
- reject codes backend vẫn phải được surfacing khi action bị từ chối

### 3.4 Status behavior
- `BLOCKED + downtime_open=true`:
  - focus chính là `End Downtime`
- sau `end_downtime`:
  - về `PAUSED`
  - không auto-resume
- `PAUSED`:
  - `Resume` chỉ khi backend cho phép

### 3.5 Claim continuity rule
Flow active work hiện tại giả định:
- operator claim từ đầu
- claim vẫn là của operator qua:
  - `IN_PROGRESS`
  - `BLOCKED`
  - `PAUSED`
- ordinary release không được phá continuity này ở active execution states

---

## 4. SE-SCR-03 — Start Downtime

### 4.1 Form fields
- reason class
- note (optional)

### 4.2 Behavior
- submit xong quay lại cockpit của chính operation hiện tại
- không back về queue
- cockpit chuyển sang blocked/downtime-active state

---

## 5. SE-SCR-04 — Release Claim Confirmation

### 5.1 Purpose
Xác nhận operator thực sự muốn nhả ownership của operation hiện tại **trong context an toàn**.

### 5.2 Rules
- ordinary release hiện chỉ nên xảy ra ở `PLANNED`
- release xong phải refresh queue + selected state nhất quán
- không dùng ordinary release để giải quyết active execution recovery
- không dùng validator claimability-only, nhưng vẫn phải obey safe release semantics hiện tại

### 5.3 UX expectation
- warning ngắn
- không destructive-style quá nặng, nhưng phải rõ rằng user đang nhả ownership
- với active execution states, affordance release phải bị disable hoặc không present như action hợp lệ

---

## 6. SE-SCR-05 — Selected item outside filter helper

### 6.1 Purpose
Giữ continuity khi user đang dùng filter mà item selected không còn thuộc filtered subset sau refresh/action.

### 6.2 Rules
- giữ filter hiện tại
- không reset ngầm về `All`
- hiện helper message ngắn
- selected row chỉ highlight nếu còn nằm trong visible filtered list

---

## 7. Explicit non-goals of this baseline
- QC entry / QC hold
- exception/disposition
- close/reopen
- generic block cause beyond downtime
- URL persistence / storage persistence của queue filter
- claim handover / claim transfer / supervised reassignment


---

## Screen Transition

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

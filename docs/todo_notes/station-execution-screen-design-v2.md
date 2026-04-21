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

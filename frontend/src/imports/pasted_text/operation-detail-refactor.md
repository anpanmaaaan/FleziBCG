Mình tổng hợp lại TOÀN BỘ các điểm thay đổi so với source OperationDetail.tsx hiện tại, theo dạng checklist định hướng implementation, để bạn apply từng bước, không bị lạc và không phá code đang có.
👉 Đây không phải ý kiến thiết kế nữa, mà là bản “diff logic + UX” ở mức hệ thống.

✅ TỔNG HỢP THAY ĐỔI – OPERATION DETAIL (GANTT‑CENTRIC)
⚠️ PHẠM VI

Áp dụng cho: OperationDetail.tsx
Không đụng StationExecution.tsx
Không đụng backend (chỉ UI refactor)
Phù hợp Phase 1 – Read‑only analysis view


1️⃣ ĐỊNH VỊ LẠI VAI TRÒ MÀN HÌNH (QUAN TRỌNG NHẤT)
🔄 Thay đổi khái niệm





















Hiện tạiSau thay đổiOperation Detail (mơ hồ)Operation Execution DetailFocus vào 1 OPFocus vào Operation Sequence của 1 WO/POTab‑centricGantt‑centric
✅ Action cần làm:

Đổi title / breadcrumb / comment trong code:
TypeScript// Operation Execution Detail (Read-only, Phase 1)Show more lines



2️⃣ PAGE HEADER – GIỮ NHƯNG GIẢM QUYỀN
✅ Giữ nguyên

Operation / WO / PO info
Status badge (In Progress / Late / Completed)
Timing badge (On‑time / Late)

❌ Loại bỏ khỏi OperationDetail

Start / Pause / Complete execution buttons

✅ Thay bằng

← Back
Open in Station Execution

✅ Action:

Remove execution buttons
Thêm 1 CTA điều hướng sang StationExecution


3️⃣ GANTT CHART – THÊM MỚI (CORE CHANGE)
🚀 Đây là thay đổi lớn nhất
✅ Thêm section mới NGAY SAU header:
Operation Sequence – Gantt Chart

✅ Gantt thể hiện:

Mỗi row = 1 Operation execution trong sequence
Planned vs Actual
Delay / Late / Blocked

✅ Tương tác Gantt (Phase 1)

























Hành viTrạng tháiClick bar✅ Select OPHover tooltip✅Drag / Resize❌Reorder❌
✅ Action:

Thêm component: OperationGantt
State mới:
TypeScriptselectedOperationId``Show more lines



4️⃣ DETAIL TABS – CHUYỂN SANG CONTEXTUAL (KHÔNG XOÁ)
🔄 Thay đổi cấu trúc

















Hiện tạiSau thay đổiTabs là layout chínhTabs = context của OP được chọn từ GanttTabs globalTabs gắn với 1 OP execution instance
✅ Tabs GIỮ LẠI (Phase 1)

Overview
Quality
✅ Materials (giữ theo yêu cầu của bạn)
Timeline
Documents

❌ Tabs LOẠI BỎ KHỎI OperationDetail

Execution (trùng StationExecution)

✅ Action:

Bọc Tabs trong OperationContextPanel
Render Tabs chỉ khi có OP được chọn


5️⃣ OPERATION SUMMARY PANEL – THÊM MỚI (TRÁI)
✅ Panel mới, luôn hiện khi chọn OP
Hiển thị:

OP ID / Name
Sequence no
Station / Workcenter
Status
Progress %
Planned vs Actual time
Delay (+ minutes)
Block reason (nếu có)

✅ Action:

Trích logic từ Overview hiện tại
Đưa sang OperationSummaryPanel


6️⃣ MATERIALS TAB – GIỮ, NHƯNG ĐỔI VAI TRÒ
✅ Giữ Materials trong Operation Detail
📌 Nhưng chỉ là READ‑ONLY context
✅ Materials tab hiển thị:

BOM theo OP execution
Required vs Consumed
Lot / Traceability info
Status highlight (OK / Overuse / Missing)

❌ Không cho phép:

Consume
Adjust quantity
Change lot
Stock mutation

✅ Action:

Remove / disable mọi nút action
Thêm tooltip “Read‑only (Phase 1)”


7️⃣ QUICK INFO SIDEBAR – XOÁ HOÀN TOÀN ✅
❌ Loại bỏ

Alerts
Related Operations
Comments
Quick actions sidebar

✅ Lý do

Gantt đã thay thế vai trò “nhìn nhanh”
Tránh nhiễu và tránh hiểu nhầm là cockpit điều khiển

✅ Action:

Remove right sidebar section
Không migrate content sang chỗ khác (Phase 1 không cần)


8️⃣ DATA & STATE – KHÔNG THAY LOGIC
✅ Giữ nguyên:

mockOperation
mockQCCheckpoints
mockMaterials
mockTimeline

✅ Chỉ đổi cách dùng:

Dùng list Operation → feed cho Gantt
OP được chọn → feed cho Summary + Tabs


9️⃣ TỔNG HỢP QUICK CHECKLIST (ĐỂ APPLY)
✅ Bạn cần làm:

 Đổi khái niệm: Operation Detail → Execution Detail
 Remove execution buttons
 Thêm Gantt component
 Thêm selectedOperationId state
 Bọc tabs thành contextual panel
 Giữ Materials tab (read‑only)
 Remove Quick Info sidebar
 Thêm link sang StationExecution

❌ Bạn KHÔNG cần:

Viết lại nghiệp vụ
Đổi backend
Viết thêm API
Xoá dữ liệu hiện có
TỔNG HỢP CUỐI – THAY ĐỔI LIÊN QUAN ĐẾN OPERATION (PHASE 1)

Nguyên tắc xuyên suốt

Mọi “Operation” trong UI Phase 1 đều là Operation Execution (runtime)
UI chỉ xem – điều hướng – phân tích, không điều khiển



I. LÀM RÕ LẠI CÁC KHÁI NIỆM (CHỐT CÁI GÌ LÀ GÌ)
✅ Phân biệt 3 khái niệm (rất quan trọng)

























Khái niệmÝ nghĩaUI nào dùngOperation DefinitionTemplate / routing❌ Không dùng trong các màn dướiOperation Execution1 công đoạn đang/chạy✅ Gantt / DetailWork Order ExecutionTình trạng tổng thể WO✅ “Operation List” sau khi đổi vai
📌 Hệ quả bắt buộc:

Mọi progress, status, QC, materials trong các màn này → runtime
Không gọi chung chung là “Operation” nữa trong comment / title (nên ghi rõ execution)


II. “OPERATION LIST” → ĐỔI VAI TRÒ (KHÔNG XOÁ)
🔄 Nhận định mới (CHỐT)

Cái bạn đang gọi là Operation List thực chất là
✅ Work Order Execution Status List

👉 Đây là thay đổi nhận thức, không phải chỉ UI.

✅ Vai trò mới của màn này

Mỗi dòng = 1 Work Order
Trả lời:

WO này đang chạy hay trễ?
Đã xong bao nhiêu %?
Click vào đâu để xem tiếp?



❌ Không phải danh sách operation chi tiết

✅ UI cần có (GIỮ GỌN)





























CộtÝ nghĩaWO IDĐịnh danhProduct / LineNhận diện nhanhStatus (✅ ⚠ ⛔)Aggregate từ các OPProgress %Overall WO progressCTAView
✅ Giữ progress bar, nhưng:

progress = WO progress
bar nhỏ, mảnh, không encode trạng thái


❌ UI không còn

Operation‑level detail
QC / Materials
Timeline
Nhiều CTA


✅ CTA duy nhất
View → Operation Execution Overview (Gantt)


III. OPERATION EXECUTION OVERVIEW (GANTT – MÀN HÌNH MỚI)
✅ Mục đích

Nhìn toàn bộ sequence operation execution của 1 WO
Phát hiện:

OP nào trễ
OP nào block




✅ Đặc điểm UI

Gantt full width
Mỗi bar = 1 Operation Execution
Planned vs Actual
Màu theo trạng thái

Spec màu (áp dụng thống nhất)

Planned: gray / outline
Running: blue
Completed on‑time: green
Late: orange + ⚠
Blocked: red + ⛔
Pending: dashed gray


✅ Hành vi

Click bar → vào Operation Execution Detail
Hover → tooltip (plan / actual / delay)

❌ Không drag
❌ Không schedule
❌ Không action

IV. OPERATION EXECUTION DETAIL (REFATOR – KHÔNG ĐẬP)
✅ Bản chất sau refactor

Xem sâu 1 Operation Execution instance


✅ Những gì GIỮ

Overview
Quality (read‑only)
Materials (read‑only, giữ theo yêu cầu của bạn)
Timeline
Documents

📌 Tất cả đều gắn với OP execution cụ thể

❌ Những gì BỎ

Gantt
Execution tab
Quick Info sidebar
Start / Pause / Complete


✅ Materials tab (nhắc lại vì quan trọng)

✅ Hiển thị:

BOM
Required vs Consumed
Lot / Traceability
Warning (overuse, mismatch)


❌ Không:

consume
adjust
change lot




V. STATION EXECUTION – CHỐT LÀ NƠI DUY NHẤT ĐỂ LÀM VIỆC
Không đổi cấu trúc, nhưng chốt quyền:

✅ Start / Pause / Complete
✅ QC input (chỉ nhập value)
✅ Andon
✅ Material consume (nếu có)

❌ Các màn khác chỉ link về đây, không lặp chức năng

VI. FLOW OPERATION SAU KHI ĐÃ CHỈNH (CHỐT LUỒNG)
Work Order Execution Status List
        ↓ View
Operation Execution Overview (Gantt)
        ↓ Click OP
Operation Execution Detail
        ↓ CTA
Station Execution

👉 Mỗi màn 1 vai – 1 nhiệm vụ, không chồng xuyên

✅ OEE DEEP DIVE MVP
Component List cho Figma Make

Scope MVP:
✅ Chứng minh giá trị OEE + AI
✅ Nuôi data cho AI Scheduling / Bottleneck
❌ Không phải full enterprise OEE platform


🟦 GLOBAL PAGE LAYOUT (Figma Make)
[ Page: OEE Deep Dive ]

┌─────────────────────────────────────────────┐
│ Top Filter Bar                              │
├─────────────────────────────────────────────┤
│ KPI Cards (OEE Overview)                    │
├─────────────────────────────────────────────┤
│ AI Insight Cards                            │
├─────────────────────────────────────────────┤
│ Six Big Losses (Bar / Mini chart)           │
├───────────────────────┬─────────────────────┤
│ Downtime Pareto       │ OEE Trend Over Time │
├───────────────────────┴─────────────────────┤
│ Line-by-Line Comparison Table               │
└─────────────────────────────────────────────┘


1️⃣ TOP FILTER BAR (GLOBAL CONTROL)
🎛 Component: OEE_FilterBar
Purpose: điều khiển toàn bộ dashboard
Sub‑components:

Date Range Picker
Shift Selector
Line Selector
Product (optional – hidden by default)
Export Button (CSV / Image – MVP)

Figma Make Components:

DatePicker
Dropdown
MultiSelect
Button


✅ MVP NOTE:
Filter logic chỉ cần GET query params với Supabase
Không cần complex state sync


2️⃣ KPI CARDS – OEE OVERVIEW (CORE)
📊 Component Group: OEE_KPI_Cards
Card list (4 cards – bắt buộc):

OEE_Card
Availability_Card
Performance_Card
Quality_Card

Common structure cho mỗi card:

Large % value
Trend indicator (▲▼ %)
Status badge (Green / Yellow / Red)
Clickable (drill‑down sau – MVP chưa cần)

UI Example:
OEE
85%
▲ +3.2%
🟢 Good

✅ Figma Make Hint:
Dùng Container + StatCard pattern, reusable.

3️⃣ AI INSIGHT CARDS (BẮT BUỘC – “AI‑DRIVEN” FEEL)
🤖 Component Group: AI_Insight_Panel
👉 Đây là thứ phân biệt bạn với BI dashboard.

3.1 AI Card #1 – Top Loss Today
Component: AI_TopLoss_Card
Content:

Title: “AI Insight – Biggest OEE Impact Today”
Loss type
Absolute impact (min / %)
Confidence level
Optional “Focus Line”

Example UI:
AI Insight
Biggest loss:
Equipment Failure – 48 min
Confidence: High
Suggested focus: Line 3


3.2 AI Card #2 – OEE Risk Next Shift
Component: AI_OEE_Risk_Card
Content:

Predicted OEE band (Low / Medium / High risk)
Simple reason list (max 2 bullets)

Example UI:
AI Prediction
Next shift OEE risk: Medium
Reasons:
• High downtime frequency
• Slow recovery after stop


3.3 AI Card #3 – Quick “What‑If” Hint
Component: AI_QuickWin_Card
Content:

1 suggested improvement
Projected OEE gain

Example UI:
What if…
Reduce setup loss by 10%
→ OEE +3.4%

✅ IMPORTANT:
Không gọi đây là “simulation” trong MVP
→ gọi là AI estimation / quick insight

4️⃣ SIX BIG LOSSES – MVP VERSION
📉 Component: SixBigLosses_BarChart
Displayed items (6 rows):

Equipment Failures
Setup & Adjustment
Small Stops
Reduced Speed
Startup Rejects
Production Rejects

Each row includes:

Loss name
Bar (relative size)
Absolute value (min or units)
% impact

✅ Sorting: by impact (desc)
✅ Clickable: show tooltip only (MVP)
❌ Chưa cần:

Full event list
Root cause tree


5️⃣ DOWNTIME PARETO (80/20)
📊 Component: Downtime_Pareto_Chart
Purpose:

Show top downtime causes
Reinforce continuous improvement logic

Elements:

Bar chart (minutes)
Cumulative % line (80% marker)
Category labels

✅ MVP: 5–7 top causes max
✅ Filter follows Top Filter Bar

6️⃣ OEE TREND OVER TIME
📈 Component: OEE_Trend_Chart
Series:

OEE
Availability
Performance
Quality

Features (MVP):

Date x‑axis
Target line
Hover tooltip

✅ Toggle series on/off
❌ Zoom deep history (phase 2)

7️⃣ LINE‑BY‑LINE COMPARISON TABLE
📋 Component: Line_Comparison_Table
Columns (MVP):

Line Name
OEE %
Availability %
Performance %
Quality %
Current Status icon

Status icons:

🟢 Running
🟡 Reduced Speed
🟠 Setup
🔴 Downtime

✅ Sortable by OEE
✅ Click row → future drill‑down

8️⃣ NOTIFICATIONS / ALERT STRIP (OPTIONAL MVP+)
🚨 Component: OEE_Alert_Banner

Shows when:

OEE < threshold
Downtime > X minutes



✅ Can be hidden for cleaner UI if needed

🔁 COMPONENT REUSE MAP (QUAN TRỌNG)

























ComponentReuse ở đâuKPI CardsDashboard tổngAI Insight CardScheduling screenTrend ChartProduction TrackingLine TableHome / Dispatch
→ bạn không build OEE riêng lẻ, mà là core design system.

✅ MVP COMPONENT COUNT (THỰC TẾ)





































GroupCountFilter1KPI Cards4AI Cards3Charts3Table1Alert1 (optional)TOTAL12–13 components
→ rất hợp cho Figma Make.

🚫 NHỮNG THỨ CỐ TÌNH KHÔNG CHO VÀO MVP

Full MTBF / MTTR dashboard
Event‑by‑event timeline
Custom report builder
ML‑heavy predictive maintenance
CMMS deep integration

👉 Mấy cái này để Phase 2, không mất điểm.
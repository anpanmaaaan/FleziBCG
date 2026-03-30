***

# 🟦 **I. SRS (Software Requirements Specification) — UNIVERSAL MANUFACTURING EDITION**

### (đã loại bỏ VehicleOrder, VIN, Trim… chuyển sang Production Order trung tính)

***

# **1. Purpose**

Hệ thống cung cấp các chức năng cốt lõi của một **MES Lite + APS + Routing + Execution Tracking** dùng cho mọi ngành sản xuất discrete, đặc biệt là automotive parts/assembly.

Hệ thống bao gồm:

*   Production Planning (PO/WO)
*   Routing & Operation Sequence
*   Dispatch
*   Execution Tracking
*   Quality
*   Traceability
*   APS Scheduling (optional)
*   Real‑time Dashboard

***

# **2. Actors (User Types)**

| Actor             | Description                   |
| ----------------- | ----------------------------- |
| Line Operator     | Thực hiện tác vụ tại station  |
| Supervisor        | Giám sát tiến độ, defect, KPI |
| Planner           | Lập kế hoạch, tạo PO, routing |
| Quality Inspector | QC, defect recording          |
| System Admin      | Cấu hình hệ thống             |

***

# **3. Functional Requirements**

***

## 🟦 **FR‑01. Product & Routing Management**

### FR‑01.1: Product Master

System manages product\_id, product\_type, optional config\_code.

### FR‑01.2: Routing (Operation Sequence)

*   Mỗi product có 1+ routing.
*   Routing gồm nhiều operations theo thứ tự (op\_seq).

### FR‑01.3: Operation Details

Operation gồm:

*   Sequence (010,020,…)
*   Name
*   Type: Setup / Process / Inspection / Wait / Transport
*   Work Center
*   Machine (optional)
*   Setup time
*   Run time
*   QC required or not
*   Tools / Skills / Resources

### UI Mapping

| UI File         | Section          |
| --------------- | ---------------- |
| RouteList.tsx   | List routes      |
| RouteDetail.tsx | Operation editor |

***

## 🟦 **FR‑02. Order Management**

### FR‑02.1: Create Production Order (PO)

Fields:

*   po\_id
*   product\_id
*   quantity
*   planned start/end
*   priority
*   route\_id (optional)

### FR‑02.2: Work Order (WO)

*   Mỗi PO có thể split thành nhiều WO.
*   WO = đơn vị thực thi tại station.

### FR‑02.3: PO/WO Status

*   Planned
*   Released
*   In‑Progress
*   Completed
*   On Hold

### UI Mapping

| UI                      | Description              |
| ----------------------- | ------------------------ |
| ProductionOrderList.tsx | PO list, add/edit/search |

***

## 🟦 **FR‑03. Dispatch Management**

### FR‑03.1: Dispatch Queue

*   WO được assign vào station/lane.
*   Mỗi station có queue riêng.
*   Sequence\_no xác định thứ tự chạy.

### FR‑03.2: Next Work Order API

UI station sẽ gọi:

    GET /dispatch_queue?station_id=eq.ST-01&status=eq.Waiting&order=sequence_no.asc&limit=1

### UI mapping

| UI File           | Purpose                                         |
| ----------------- | ----------------------------------------------- |
| OperationList.tsx | Show operations for PO → feed dispatch decision |
| Home.tsx          | Shows queue summary                             |

***

## 🟦 **FR‑04. Execution Tracking**

### FR‑04.1: Start Execution

Record fields:

*   wo\_id
*   product\_id
*   operator\_id
*   station\_id
*   start\_time

### FR‑04.2: Complete Execution

Add:

*   end\_time
*   result (OK/NG)

### FR‑04.3: Execution result triggers:

*   Update WO status
*   Update KPI
*   Update dashboard realtime

### UI Mapping

| UI File                | Purpose                   |
| ---------------------- | ------------------------- |
| OperationList.tsx      | list steps (view only)    |
| ProductionTracking.tsx | display execution results |
| Execution UI (chưa có) | sẽ build trong Figma Make |

***

## 🟦 **FR‑05. Quality Management**

### FR‑05.1: QC Checkpoint

Dynamic list per station or per operation.

### FR‑05.2: QC Result Recording

Fields:

*   exec\_id
*   value
*   result (OK/NG)

### FR‑05.3: Defect Recording

### UI Mapping

| UI                     | Purpose                   |
| ---------------------- | ------------------------- |
| ProductionTracking.tsx | show defects, metrics     |
| RouteDetail.tsx        | operation QC requirements |

***

## 🟦 **FR‑06. Traceability**

### FR‑06.1: Serial / Lot Tracking

*   serial\_no
*   product\_id
*   lot\_no

### FR‑06.2: Genealogy

Parent-child linkage:

*   parent\_sn → child\_sn
*   station\_id
*   timestamp

### UI Mapping

Chưa có UI — bạn sẽ thêm sau:

*   Serial Scan
*   Traceability Lookup

***

## 🟦 **FR‑07. APS Scheduling**

### FR‑07.1: Basic Scheduling (MVP)

Heuristic:

*   EDD
*   SPT/LPT
*   Priority-based
*   Optional: ATC

### FR‑07.2: Generate sequence for dispatch queue

APS writes sequence into `dispatch_queue`.

### FR‑07.3: Re-scheduling when conditions change.

### UI Mapping

| UI                     | Purpose             |
| ---------------------- | ------------------- |
| Home.tsx               | queue order changes |
| ProductionTracking.tsx | show late orders    |

***

## 🟦 **FR‑08. Dashboard (Real-time)**

Dashboard shows:

*   Target vs Actual
*   Defects
*   Efficiency
*   OEE
*   Line performance
*   Alerts
*   Weekly trend

Mapping:

*   Dashboard.tsx (charts & KPIs)

***

# 🟪 **4. Non‑Functional Requirements**

*   Response time < 200 ms
*   Realtime latency < 150 ms
*   Multi-language EN/JP
*   Supabase hosting (REST, Realtime)
*   Scalable to 100 stations
*   Permissions via Supabase Auth

***

# 🟩 **5. Data Model (Summary)**

You already have DB schema (MES + APS).  
Mapping with UI:

| MES Entity         | UI Screen                        |
| ------------------ | -------------------------------- |
| product            | RouteDetail, ProductionOrderList |
| routing            | RouteList                        |
| operation          | RouteDetail                      |
| production\_order  | ProductionOrderList              |
| work\_order        | Home                             |
| dispatch\_queue    | Home / Execution                 |
| station\_execution | ProductionTracking               |
| quality\_result    | ProductionTracking               |
| defect             | ProductionTracking               |

***

# 🟦 II. **BASIC DESIGN (BD) — LEVEL 1 & LEVEL 2**

Đây là phần bạn dùng trực tiếp để làm UI logic trong Figma Make.

***

# 🟩 **BD-01: Screen Structure Mapping**

### **1. Production Order List Screen**

Functions:

*   Load PO list → GET /production\_order
*   Filter/search columns
*   Add new PO → POST /production\_order

### **2. Route Management**

*   RouteList → GET /routing
*   RouteDetail → GET /operation?route\_id=xx
*   Edit → PATCH /operation
*   Add → POST /operation
*   Delete → DELETE /operation

### **3. Execution Flow (MVP)**

Flow:

1.  Load next WO
2.  Start execution
3.  Update execution
4.  Mark OK/NG

APIs:

    GET /dispatch_queue
    POST /station_execution
    PATCH /station_execution

### **4. Dashboard**

*   Load aggregated data
*   Subscribe to realtime:
    *   station\_execution
    *   defect
    *   machine\_event

***

# 🟦 **BD‑02: Page → API Behavior Mapping**

(để bạn implement trong Figma Make)

### **Page: Home**

| Action                | API                  |
| --------------------- | -------------------- |
| Load production queue | GET /work\_order     |
| Load production lines | GET /routing or mock |

***

### **Page: ProductionOrderList**

| Action       | API                      |
| ------------ | ------------------------ |
| Load PO list | GET /production\_order   |
| Create PO    | POST /production\_order  |
| Edit PO      | PATCH /production\_order |
| Pagination   | range= query             |

***

### **Page: RouteList**

| Action              | API            |
| ------------------- | -------------- |
| Load routes         | GET /routing   |
| Update route status | PATCH /routing |

***

### **Page: RouteDetail**

| Action          | API                         |
| --------------- | --------------------------- |
| Load operations | GET /operation?route\_id=xx |
| Add operation   | POST /operation             |
| Update          | PATCH /operation            |
| Reorder         | PATCH op\_seq               |
| Delete          | DELETE /operation           |

***

### **Page: OperationList**

| Action                         | API                         |
| ------------------------------ | --------------------------- |
| Load list of operations for PO | GET /operation?route\_id=xx |

***

### **Page: ProductionTracking**

| Action              | API                                        |
| ------------------- | ------------------------------------------ |
| Load execution logs | GET /station\_execution                    |
| Load defects        | GET /defect                                |
| Subscribe realtime  | station\_execution, defect, machine\_event |

***

### **Page: Dashboard**

| Action      | API                  |
| ----------- | -------------------- |
| Load KPI    | multiple GET queries |
| Load charts | aggregate queries    |
| Alerts      | machine\_event       |

***

# 🟩 **BD‑03: System Flow (MVP)**

    PO Created → WO Created → WO Dispatch → Station Execution → QC → Traceability → Dashboard

APS (optional):

    PO/WO -> APS -> Dispatch Queue Reordering -> MES Execution

***

# 🟦 **III. BẢN SRS + BD NÀY PHÙ HỢP UI HIỆN TẠI**

✔ Không còn field automotive‑locked  
✔ Không còn VIN/Color/Trim/Variant  
✔ UI mapping đúng với file .tsx bạn gửi  
✔ Figma Make có thể implement ngay  
✔ Supabase REST → phù hợp 100% (no backend local)


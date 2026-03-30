📘 1. FUNCTION LIST (FULL LIST – AUTOMOTIVE MES LITE PLATFORM)
Mình chia theo module để bạn bắt đầu implement theo sprint.

A. Work Order & Scheduling Module
A1. Vehicle Order Management

Tạo mới / import Vehicle Order (VO)
Validate Model / Variant / Option code
Quản lý sequence number
Assign line/shift

A2. Production Order (PO) & Dispatch

Tự động tạo PO từ VO
Release / Hold PO
Dispatch WO xuống station theo thứ tự
API lấy next serial cho station

A3. AI Scheduling Integration

Nhận schedule từ AI
Ghi nhận các constraint (takt, skill, equipment availability)
Re-sequence theo AI suggestion
Hiển thị bảng sequence cho planner


B. Station Execution Module
B1. Operator Login

Đăng nhập bằng mã thẻ / PIN / Face-ID optional
Kiểm tra skill matrix

B2. Serial Processing

Nhận serial từ dispatch queue
Scan barcode
Tải Work Instruction theo trạm

B3. Task Execution

Ghi nhận start/stop
Ghi kết quả từng bước trong WI
Thời gian thực tế vs takt


C. Quality & Torque Module
C1. Torque Capture

Nhận torque/angle từ IoT Gateway
Mapping serial ↔ station ↔ tool
Evaluate OK/NG

C2. QC Checkpoint

Checksheet dynamic
Auto QC trigger theo model
Ghi measurement & spec control

C3. Defect & Repair Loop

Tạo defect ticket
Phân loại defect
Gửi Repair Station
Đóng loop sau khi repair OK


D. Traceability Module
D1. Serial / Lot / Component Tracking

Tạo serial
Link với lot
Link component → assembly

D2. Genealogy Tree

Parent–child relationship
Export trace report theo yêu cầu OEM

D3. Station History

Chi tiết từng station đã qua
Torque, QC, timestamp


E. Digital Twin Module
E1. Line Simulation

Station cycle simulation
Defect generation
WIP movement

E2. Machine Behavior Simulation

Status change
Breakdown injection
Cycle time variation

E3. Twin → MES Event Streaming

Publish events via MQTT
Sync WIP position
Run scenario (bypass station, reorder sequence)


F. AI Engine Module
F1. Scheduling AI

Heuristic ATC/EDD
RL-based optimization
Line balancing

F2. Quality Prediction

Defect risk scoring
Early-warning for stations

F3. Anomaly Detection

Machine cycle anomaly
Torque abnormal patterns


G. System / Platform Module

User & Role management
Logs / Audit trail
API Gateway
Event Bus (MQTT)
Dashboard
Health monitoring


📙 2. SRS CHI TIẾT (Software Requirements Specification)
Dưới đây là bản SRS theo chuẩn IEEE‑29148.

2.1. Introduction
2.1.1 Purpose
Tài liệu SRS mô tả chi tiết yêu cầu chức năng / phi chức năng của hệ thống Automotive MES Lite + Digital Twin + AI Scheduling, dành cho đội phát triển sản phẩm.
2.1.2 Scope
Hệ thống bao gồm:

MES Lite (Dispatch, Execution, Quality, Traceability)
Digital Twin Simulator
AI Scheduling Engine
IoT Gateway Integration
Dashboard

Not included:

ERP
Full APS
Advanced QMS
Supplier portal


2.2. Overall Description
2.2.1 User Classes

Operator: thực thi công việc ở station
Line Leader: theo dõi line status
Quality Inspector: thực hiện QC
Planner: xem schedule / re-sequence
Admin: cấu hình hệ thống
AI Engine: hệ thống tự động


2.3 Functional Requirements

FR‑01. Vehicle Order Management
Description
Hệ thống cho phép tạo và quản lý Vehicle Order (VO) theo model/variant.
Requirements

FR‑01.1: System shall support manual VO creation.
FR‑01.2: System shall validate model/variant against master data.
FR‑01.3: System shall assign sequence number for each VO.
FR‑01.4: System shall support VO import (CSV/API).


FR‑02. Production Order & Dispatch

FR‑02.1: System shall auto-generate PO from VO.
FR‑02.2: System shall allow planner to release/hold PO.
FR‑02.3: System shall maintain dispatch queue per station.
FR‑02.4: System shall provide API for station to fetch next serial.
FR‑02.5: System shall update WO status in real-time.


FR‑03. Station Execution

FR‑03.1: Operator login required.
FR‑03.2: System shall verify operator skill matrix.
FR‑03.3: System shall load Work Instruction (WI) based on model/station.
FR‑03.4: System shall record start/stop timestamps.
FR‑03.5: System shall record completion result (OK/NG).


FR‑04. Quality Management

FR‑04.1: System shall support configurable QC checkpoints.
FR‑04.2: System shall receive torque data from IoT Gateway.
FR‑04.3: System shall evaluate torque result based on spec.
FR‑04.4: System shall create defect ticket on QC failure.
FR‑04.5: System shall track defect → repair → re-check loop.


FR‑05. Traceability

FR‑05.1: System shall generate serial number.
FR‑05.2: System shall link serial ↔ component ↔ lot.
FR‑05.3: System shall build genealogy tree.
FR‑05.4: System shall store full station history.
FR‑05.5: System shall export genealogy report in JSON/CSV.


FR‑06. Digital Twin

FR‑06.1: System shall simulate stations with configurable cycle times.
FR‑06.2: System shall simulate defect probability per station.
FR‑06.3: System shall simulate machine events (run/stop/anomaly).
FR‑06.4: System shall publish events via MQTT in MES-compatible format.
FR‑06.5: System shall run multiple simulation scenarios in parallel.


FR‑07. AI Engine
Scheduling

FR‑07.1: AI shall generate optimal build sequence.
FR‑07.2: AI shall consider constraints: takt, skill, breakdown.
FR‑07.3: AI shall send recommended scheduling to MES.

Quality

FR‑07.4: AI shall compute defect risk score.

Anomaly

FR‑07.5: AI shall detect cycle-time anomaly.


FR‑08. Dashboard

FR‑08.1: Display station status in real-time
FR‑08.2: Display WIP and genealogy graph
FR‑08.3: Display AI scheduling recommendation
FR‑08.4: Display defect trend


2.4 Non‑Functional Requirements (NFR)

NFR‑01: Response time < 200ms for MES operations
NFR‑02: MQTT event latency < 100ms
NFR‑03: System uptime ≥ 99.5%
NFR‑04: Support 10 lines x 50 stations simultaneously
NFR‑05: Audit logs must be stored ≥ 1 year
NFR‑06: Data encryption for serial/genealogy data


2.5 Data Requirements

Canonical manufacturing data model (bạn đã có)
Station Execution table
Quality/Torque tables
Genealogy graph model
Machine signals table
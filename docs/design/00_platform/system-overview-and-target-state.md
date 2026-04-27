# System Overview and Target State

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v2.0 | Reframed the platform as manufacturing-mode-neutral and session-owned for execution. |

Status: Canonical system-level design note for the target MOM platform.

## 1. Purpose

This document gives the whole-system picture for the AI-driven MES/MOM platform.
It should be read together with `product-business-truth-overview.md`, which is the authoritative product-shape document.
It answers:
- what the product is
- what the current strongest app baseline is
- what the platform target state is
- how execution, governance, integration, and AI fit together

## 2. Product direction

The system is a lightweight but production-grade MES/MOM platform aligned with ISA-95.
The delivery strategy is:
1. start from a strong execution core
2. harden governance and auditability early
3. keep the platform neutral across manufacturing modes
4. deliver Station Execution first as the discrete-first execution app
5. add supervisory, quality, traceability, material, maintenance, digital twin, and Planning & Scheduling (APS) progressively
6. keep AI advisory by default

## 3. Core system principles

### 3.1 Backend is the source of truth
The backend owns:
- execution truth
- authorization truth
- approval truth
- audit truth
- master-data truth where configured

The frontend owns:
- visibility
- navigation
- composition
- i18n
- ergonomic interaction

### 3.2 Execution is event-driven
Important operational facts are append-only events.
Status is derived from facts.
Read models and projections are support data, not the canonical source of truth.

### 3.3 Governance is first-class
Identity, access control, session governance, approvals, delegation, and impersonation are platform-level capabilities.

### 3.4 AI is advisory by default
AI may observe, explain, predict, and recommend.
AI does not silently mutate execution state or bypass authorization, approval, or separation of duties.

### 3.5 Platform abstractions must remain manufacturing-mode-neutral
The platform must not hard-code `station + WO/OP + claim + count-only reporting` as its universal production grammar.
Those are valid discrete-mode specializations, not the only possible execution model.

## 4. Target capability map

### 4.1 Foundation
- tenant and hierarchy model
- identity and session lifecycle
- role and scope assignment
- approval and SoD
- audit and observability
- master-data governance

### 4.2 Unified execution core
- production request / execution run / execution step abstractions
- resource, personnel, and material context
- session-owned execution mutation
- runtime, closure, quality, review, and dispatch dimensions over time
- mode-specific execution apps on top of common foundations

### 4.3 Current first app: Station Execution
- discrete-first UI for station/work-center execution
- operator identification
- equipment binding where relevant
- quantity and downtime capture
- closure/reopen foundation

### 4.4 Quality and traceability
- Quality Lite
- accepted-good derivation
- hold / review / disposition
- lot / serial / genealogy evolution

### 4.5 AI and intelligence
- shift summary
- OEE deep-dive insights
- anomaly detection
- delay and bottleneck explanation
- natural-language operational insights

### 4.6 Future MOM expansion
- material operations
- maintenance operations
- operational digital twin
- Planning & Scheduling (APS) support
- broader process/batch execution surfaces

## 5. Manufacturing mode stance

The platform must support:
- `DISCRETE`
- `BATCH`
- `CONTINUOUS`
- `HYBRID`

The initial delivery focus is discrete-first, but the architecture must avoid making discrete assumptions irreversible.

## 6. Runtime architecture direction

Current runtime: modular monolith.

Design rule:
- stay boundary-clean
- keep extraction-ready modules
- avoid premature microservice complexity
- remain deployable on-prem or cloud

## 7. Current baseline vs target state

### Current strongest app baseline
Strongest design maturity currently exists in:
- execution core foundations
- quality-lite framing
- engineering governance
- source-of-truth hierarchy

### Approved transition direction
- deprecate claim from the target execution model
- introduce station-session-based ownership
- separate authenticated user, operator, and equipment context
- introduce unified execution abstractions so later batch/process apps can sit on the same platform

### Designed now, implemented later
- full process/batch execution app
- richer traceability and genealogy
- maintenance and material operations
- AI use cases beyond advisory insight
- digital twin and APS-lite depth

## 8. Architectural success criteria

The architecture is successful when:
- execution facts remain reproducible from event history
- governance remains auditable
- tenant and scope isolation remain explicit
- frontend never becomes truth for execution or authorization
- new domains can be added without rewriting the core
- Station Execution can evolve without blocking batch/process growth
- AI remains clearly labeled and safely constrained


## 9. Mapping note

For manufacturing-mode-neutral hierarchy interpretation, see `manufacturing-mode-hierarchy-mapping.md`.

# MASTER DATA vs ENUM POLICY

Version: v2.0  
Status: Active  
Scope: Backend, Frontend, API contracts, Data modeling  
Applies to: All contributors  

---

## HISTORY

| Date       | Version | Change Summary |
|------------|--------|----------------|
| 2026-04-22 | v2.0   | Added lifecycle, RBAC, versioning, governance rules |
| 2026-04-22 | v1.0   | Initial version |

---

## 1. Purpose

Define authoritative rules for choosing between ENUM and Master Data,
and establish governance for lifecycle, ownership, and evolution.

---

## 2. Core Principle

ENUM = system semantics  
DB   = business semantics  

---

## 3. ENUM — Allowed Use Cases

Use ENUM only if ALL conditions are true:

- System invariant  
- Stable over time  
- Not used in analytics  
- Not tenant-dependent  

Examples:
- Execution status
- Approval status

---

## 4. Master Data — Required Use Cases

Use DB if ANY is true:

- Business-defined  
- Configurable  
- Used in analytics  
- Tenant-specific  
- Requires audit  

Examples:
- Downtime reasons  
- Defect codes  
- QC parameters  

---

## 5. Master Data Lifecycle (NEW)

Every master data entity must support lifecycle:

### States

- DRAFT → not usable in execution  
- ACTIVE → usable  
- INACTIVE → not selectable but kept for history  
- DEPRECATED → replaced by newer version  

---

## 6. Versioning & Effective Dating (NEW)

Master data must support:

- version_number  
- effective_from  
- effective_to (nullable)

### Rule

- Events must bind to version at execution time  
- Historical data must NOT change when master data changes  

---

## 7. RBAC for Master Data (NEW)

Define ownership:

| Role        | Permission |
|------------|-----------|
| Admin       | Full CRUD |
| Engineer    | Create / update |
| Supervisor  | View only |
| Operator    | No access |

Optional:
- approval_required flag for sensitive data

---

## 8. Event Binding Requirement

Execution events must store:

- code (ID)
- resolved snapshot (name, category)

Purpose:
- audit
- historical accuracy

---

## 9. Anti-Patterns

- FE enum for business data  
- Hardcoded UI lists  
- ENUM + DB hybrid logic  
- No versioning  

---

## 10. Decision Tree

1. System-defined? → ENUM  
2. Business-defined? → DB  
3. Used in analytics? → DB  
4. Tenant-specific? → DB  

---

## 11. Backend Responsibilities

- Source of truth  
- Enforce validation  
- Attach snapshot to events  
- Handle versioning  

---

## 12. Frontend Responsibilities

- Fetch from API  
- No hardcoding  
- No business logic derivation  

---

## 13. Governance Enforcement

PR must include:

- ENUM vs DB decision  
- justification  

Reviewer must verify:

- no FE duplication  
- tenant-awareness  
- audit readiness  

---

## 14. Final Rule

If unsure → use Master Data (DB)


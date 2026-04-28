# GitHub Copilot Instructions — FleziBCG MOM + AI Brain v6

---

# 🔰 0. Entry Rule (MANDATORY)

Before coding, always read in order:

1. `.github/agent/AGENT.md`
2. `docs/design`
3. `docs/governance/CODING_RULES.md`
4. `docs/governance/ENGINEERING_DECISIONS.md`
5. `docs/governance/SOURCE_STRUCTURE.md`

⚠️ This file is NOT the source of truth for:

* business logic
* API contracts
* database rules
* IAM/session rules

Those live in design & governance docs.

---

# 🧠 1. AI Brain v6 — Auto Execution (DEFAULT)

Use:

```text
docs/ai-skills/flezibcg-ai-brain-v6-auto-execution.md
```

---

## 🔁 Auto Routing (MANDATORY)

For every non-trivial task, ALWAYS start with:

```markdown
## Routing
- Selected brain:
- Selected mode:
- Hard Mode MOM:
- Reason:
```

---

## 🧠 Brain Selection

### Use MOM Brain when:

* execution / operation
* station / session / operator
* event / projection
* production / downtime / quantity
* quality affecting execution
* material / WIP / traceability
* ERP manufacturing integration
* OEE / shopfloor / Andon

### Use Generic Brain when:

* normal software logic
* UI / dashboard
* generic API
* non-MOM feature

👉 If unsure → **default to MOM Brain**

---

## ⚙️ Mode Selection

| Mode         | Use                       |
| ------------ | ------------------------- |
| Fast         | trivial change            |
| Strict       | DB / auth / state / event |
| QA           | testing / E2E             |
| Architecture | design                    |
| Product      | scope / roadmap           |
| Refactor     | cleanup                   |
| Debug        | bug                       |
| Release      | deploy                    |

⚠️ Never use Fast for risky logic.

---

## 🔥 Hard Mode MOM (AUTO-TRIGGER)

Turn ON if task touches:

* state machine
* execution command
* event
* projection truth
* station/session/operator
* production / downtime
* completion / closure
* invariant / tenant / auth

---

## 🚫 Hard Mode Reject Rules

Reject code if:

* sai state machine
* thiếu event
* thiếu invariant
* mutate state trực tiếp
* projection = source of truth
* frontend quyết định logic
* thiếu tenant/auth check
* bypass service layer

---

# 🏗️ 2. Core MOM Constraints (NON-NEGOTIABLE)

## Backend = source of truth

* frontend chỉ gửi intent
* frontend không derive state
* frontend không authorize

---

## Event-driven execution

* event = append-only
* state = derive từ event
* projection ≠ truth

---

## Tenant isolation

* luôn có tenant context
* không query cross-tenant

---

## Layer responsibility

* service = business logic
* route = thin
* repo = data only

---

## Auth model

* JWT = identity only
* permission = backend

---

## Privileged access

* không implicit admin
* phải audit

---

# 🧪 3. Engineering Principles

* small, reviewable change
* vertical slice
* explicit assumption
* behavior-based test
* no scope invention

---

# 🎯 4. AI Skill System

Skills nằm ở:

```text
docs/ai-skills/
```

### Mapping

| Intent       | Skill                            |
| ------------ | -------------------------------- |
| TDD          | tdd.md                           |
| breakdown    | to-issues.md                     |
| audit        | triage-issue.md                  |
| architecture | improve-codebase-architecture.md |
| PRD          | to-prd.md                        |

---

# 🔍 5. PR Rules

Phải classify:

* Mechanical
* Behavior
* Architecture

Theo:

```text
docs/governance/CODING_RULES.md
```

---

# ⚠️ 6. Conflict Resolution

1. Business truth doc
2. Coding rules
3. Engineering decisions
4. Source structure

❌ Never invent new interpretation

---

# 🧠 7. Expected AI Behavior

Copilot must behave like:

* MOM domain-aware engineer
* strict with invariants
* architecture-aware
* explicit reasoning

NOT:

* autocomplete tool
* guess-based generator
* shortcut coder

---

# 🧱 8. Final Principle

```text
Route → Select brain → Select mode → Hard Mode if needed → Execute → Verify
```

```text
Execution truth > speed
Event integrity > shortcut
Invariant > convenience
```
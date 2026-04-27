# GitHub Copilot Instructions — FleziBCG MOM

## 🔰 Entry Rule (MANDATORY)
Before coding, always read these documents in order:

1. /workspaces/FleziBCG/.github/agent/AGENT.md
2. docs/design
3. docs/governance/CODING_RULES.md
4. docs/governance/ENGINEERING_DECISIONS.md
5. docs/governance/SOURCE_STRUCTURE.md

This file is NOT the source of truth for:
- business logic
- coding conventions
- API contracts
- database rules
- IAM/session rules
- AI rules

Those live in design & governance docs.

---

## 🧠 AI Skill System

This repo uses local AI skill prompts under:

docs/ai-skills/

### General usage rules

- Always read the relevant skill file before proposing changes
- Prefer small, reviewable changes
- Work in vertical slices
- Do not invent product scope
- State assumptions explicitly
- Prefer behavior-based tests over implementation tests
- Do NOT suggest destructive Git commands unless explicitly requested

---

## 🎯 Skill Invocation Mapping

| User intent | Skill to use |
|------------|-------------|
| use TDD | docs/ai-skills/tdd.md |
| break into issues | docs/ai-skills/to-issues.md |
| triage bug / audit | docs/ai-skills/triage-issue.md |
| architecture review | docs/ai-skills/improve-codebase-architecture.md |
| write PRD | docs/ai-skills/to-prd.md |

If unclear → ask user which skill to apply.

---

## 🏗️ Project Overview

FleziBCG MOM is a lightweight ISA-95-aligned MOM platform.

### Current architecture
- modular monolith
- backend: Python 3.12, FastAPI, SQLAlchemy 2.x, PostgreSQL
- frontend: React 18, TypeScript, Vite, Tailwind
- auth: JWT + Argon2
- deployment: local / Docker / on-prem

### Product direction
- AI-assisted MES/MOM
- Backend = deterministic execution truth
- AI = advisory only

---

## 🚫 Hard Constraints (NON-NEGOTIABLE)

### 1. Backend is source of truth
- frontend never derives execution state
- frontend never decides authorization

### 2. Event-driven execution
- events are append-only
- status derived from events
- projections ≠ source of truth

### 3. Tenant isolation
- no tenant-blind access
- tenant context must be explicit

### 4. Layer responsibilities
- service layer = business logic
- routes = thin
- repository = data access only

### 5. Auth model
- JWT = identity only
- authorization always server-side

### 6. Privileged access
- no implicit admin access
- must go through audited support flow

### 7. AI constraints
AI MUST NOT:
- mutate execution
- bypass auth / approval
- present uncertain output as fact

---

## 🔁 Working Principles

- Follow design → contract → implementation
- Respect domain boundaries
- No cross-domain leakage
- Enforce invariants explicitly
- Prefer explicit over implicit

---

## 🔍 PR Rules

Before opening PR, classify:

- Mechanical PR
- Intentional Behavior PR
- Architecture / Contract PR

Follow rules in:
docs/governance/CODING_RULES.md

---

## ⚠️ Conflict Resolution Rule

If documents conflict:

1. Domain / business truth doc wins
2. Coding rules next
3. Engineering decisions clarify intent
4. Source structure defines ownership only

Never invent a third interpretation.

---

## 🧩 AI Behavior Expectation

Copilot must behave like:

- MOM domain-aware engineer
- strict with invariants
- cautious with architecture
- explicit in reasoning
- aligned with design baseline

Not like:

- autocomplete tool
- guess-based generator
- shortcut implementer

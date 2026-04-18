# Governance Docs

This folder contains the authoritative engineering governance documents for MOM Lite.

Use these files to understand:
- what is locked business behavior
- what engineering rules are mandatory
- how ambiguous implementation decisions are reconciled
- where code lives and who owns which layer
- which file is the single source of truth for each type of rule

---

## Reading Order

Read these documents in the following order:
1. `../system/mes-business-logic-v1.md` — business logic contract
2. `./CODING_RULES.md` — engineering rules (authoritative)
3. `./ENGINEERING_DECISIONS.md` — reconciled truths / clarifications
4. `./SOURCE_STRUCTURE.md` — repo layout and ownership only

---

## File Roles

### `../system/mes-business-logic-v1.md`
**Authoritative business truth**
Use for:
- execution semantics
- status/lifecycle model
- approval/impersonation constraints
- official business rules
Never override this file with UI or engineering assumptions.

---

### `./CODING_RULES.md`
**Authoritative engineering rules**
Use for:
- PR classification
- verification gates
- layering rules
- tenant/scope isolation policy
- API/DB/session rules
- AI engineering rules
- definition of done
This is the single source of truth for all engineering rules.

---

### `./ENGINEERING_DECISIONS.md`
**Reconciled implementation truths**
Use for:
- clarifying ambiguity between docs
- current engineering interpretations
- role taxonomy
- runtime architecture stance
- frontend/backend responsibility boundary
- AI-driven MOM guardrails
This file is intentionally short and helps avoid conflicting interpretations.

---

### `./SOURCE_STRUCTURE.md`
**Repository structure and ownership**
Use for:
- repo layout
- entrypoints
- folder/module ownership
- runtime surfaces
- frozen public contract baselines
This file is NOT the source of business or coding rules.

---

## When Documents Disagree

Apply this order of precedence:
1. `../system/mes-business-logic-v1.md`
2. `./CODING_RULES.md`
3. `./ENGINEERING_DECISIONS.md`
4. `./SOURCE_STRUCTURE.md`
5. `.github/copilot-instructions.md` (pointer only)
6. inline comments
If a conflict still matters for implementation:
- stop coding
- open a docs clarification PR
- reconcile the documents first
Never invent a third interpretation in code.

---

## Current Engineering Position

The codebase is:
- modular monolith
- backend as source of truth
- event-driven execution
- persona as UX-only
- JWT as identity proof only
- tenant/scope isolation mandatory
- AI advisory by default
For the exact interpretation, see `ENGINEERING_DECISIONS.md`.

---

## Contribution Workflow

Before changing code:
1. Identify whether the change is:
   - Mechanical PR
   - Intentional Behavior PR
   - Architecture / Contract PR
2. Read:
   - business logic contract
   - coding rules
   - engineering decisions
3. Confirm whether the change affects:
   - business truth
   - engineering truth
   - public API contract
   - DB schema
   - AI behavior
   - approval / impersonation / security semantics
4. Update docs in the same PR when required.

---

## Typical Questions

### “Where do I check whether a workflow is allowed?”
See:
- `../system/mes-business-logic-v1.md`
- then `./CODING_RULES.md`

### “Where do I check whether frontend may gate a screen?”
See:
- `./ENGINEERING_DECISIONS.md`
- `./CODING_RULES.md`

### “Where do I check folder ownership?”
See:
- `./SOURCE_STRUCTURE.md`

### “Where do I check whether a PR may change OpenAPI?”
See:
- `./CODING_RULES.md` → PR classification and verification gates

### “Where do I check how AI features should behave?”
See:
- `./CODING_RULES.md`
- `./ENGINEERING_DECISIONS.md`

---

## Maintenance Rule

Keep these documents small and role-specific.
Do not:
- move business rules into source structure
- move coding conventions into entry instructions
- duplicate governance rules across files
- let `.github/copilot-instructions.md` become a second coding rules file
If a rule needs to exist in multiple places, keep the full rule in one authoritative file and reference it elsewhere.

---

## Recommended Folder Contents

```text
docs/
├── governance/
│   ├── README.md
│   ├── CODING_RULES.md
│   ├── ENGINEERING_DECISIONS.md
│   └── SOURCE_STRUCTURE.md
│
├── system/
│   └── mes-business-logic-v1.md
│
├── architecture/
│   ├── SYSTEM_OVERVIEW.md
│   ├── EXECUTION_MODEL.md
│   ├── READ_WRITE_SEPARATION.md
│   ├── I18N_STRATEGY.md
│   └── AI_GUARDRAILS.md
│
└── phases/
  └── PHASE_*.md
```

---

Final Reminder
These docs exist to reduce ambiguity.
Use:
- mes-business-logic-v1.md for what the system means
- CODING_RULES.md for how engineering must behave
- ENGINEERING_DECISIONS.md for how to interpret implementation truth
- SOURCE_STRUCTURE.md for where code belongs
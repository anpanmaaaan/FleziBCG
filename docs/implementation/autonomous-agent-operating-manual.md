# FleziBCG Autonomous Agent Operating Manual

## Operating Loop

```text
PLAN
→ HARD MODE MOM v3 GATE
→ TEST FIRST
→ CODE
→ BUILD
→ TEST
→ VERIFY
→ UPDATE REPORT
→ NEXT SLICE
```

## Build Commands

Use available project commands. Try:

```bash
cd backend && python -c "import app.main; print('import ok')"
cd backend && python -m pytest -q
cd frontend && npm run build
cd frontend && npm run lint
cd frontend && npm run typecheck
cd frontend && npm test
```

If a command cannot run, explain why.

## Reports

Update:

```text
docs/implementation/autonomous-implementation-plan.md
docs/implementation/autonomous-implementation-verification-report.md
```

## Stop Conditions

Do not stop after one slice. Stop only for real blockers:

- missing design
- excluded scope
- dangerous migration
- build/test environment blocked
- Hard Mode v3 rejects implementation
- business/security ADR required

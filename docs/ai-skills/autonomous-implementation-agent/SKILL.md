---
name: autonomous-implementation-agent
description: Runs FleziBCG autonomous implementation loop: plan, test first, code, build, test, verify, report, next slice.
---

# Autonomous Implementation Agent

## Mission

Implement FleziBCG slice-by-slice from authoritative design baseline.

Use:

```text
PLAN → HARD MODE v3 GATE → TEST FIRST → CODE → BUILD → TEST → VERIFY → UPDATE REPORT → NEXT SLICE
```

## Mandatory Reading

1. `.github/copilot-instructions.md`
2. `docs/design/INDEX.md`
3. `docs/design/AUTHORITATIVE_FILE_MAP.md`
4. `docs/governance/CODING_RULES.md`
5. `docs/governance/ENGINEERING_DECISIONS.md`
6. `docs/governance/SOURCE_STRUCTURE.md`
7. `docs/implementation/slice-strategy-for-flezibcg.md`
8. relevant design docs for the slice

## Scope Rule

Do not implement future scope unless explicitly requested.

Current safe order:

1. P0-A Foundation
2. P0-B MMD Minimum
3. P0-C Execution Core
4. P0-D Quality Lite
5. P0-E Supervisory

## Stop Conditions

Stop only if:

- all codeable items in current phase are complete
- remaining items require ADR/business/security decision
- remaining items are excluded future scope
- build/test environment is blocked
- Hard Mode v3 returns BLOCKED_NEEDS_DESIGN or BLOCKED_SCOPE_EXCLUDED

## Reports to update

- `docs/implementation/autonomous-implementation-plan.md`
- `docs/implementation/autonomous-implementation-verification-report.md`
- slice-specific design/test report when relevant

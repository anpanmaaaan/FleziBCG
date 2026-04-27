# Skill: improve-codebase-architecture

## Purpose
Identify architecture improvement opportunities based on domain language, ADRs, current code, and recurring friction.

## Use when
- Codebase works but is becoming harder to evolve.
- Boundaries are unclear.
- Domain concepts are leaking across layers.
- You want architecture recommendations before scaling development.

## Process
1. Read project context and ADRs if available.
2. Identify domain language and invariants.
3. Inspect module boundaries.
4. Look for:
   - Ambiguous ownership
   - Duplicate concepts
   - Cross-layer coupling
   - Hidden business rules
   - Missing tests at boundaries
   - Overly shallow modules
5. Recommend improvements.
6. Split into safe incremental steps.

## Output format
```md
# Architecture Improvement Review

## Current Architecture Summary
## Strengths
## Risks / Friction Points
## Domain Boundary Issues
## Recommended Improvements
## Suggested ADRs
## Incremental Implementation Plan
## What Not To Change Yet
```

## Rules
- Do not recommend rewrites without strong justification.
- Tie recommendations to real pain or domain risk.
- Prefer incremental boundary improvements.
- Separate product/domain decisions from technical cleanup.

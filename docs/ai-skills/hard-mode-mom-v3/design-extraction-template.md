# Hard Mode MOM v3 — Design Extraction Template

```markdown
# Design Evidence Extract

## Source docs read

| Doc | Why used | Read status |
|---|---|---|

## Commands / actions found

| Command / Action | Domain | Source doc | Evidence |
|---|---|---|---|

## Events found

| Event | Trigger | Source doc | Evidence |
|---|---|---|---|

## States found

| State | Entity | Source doc | Evidence |
|---|---|---|---|

## Invariants found

| Invariant | Type | Source doc | Evidence |
|---|---|---|---|

## Explicit exclusions

| Exclusion | Source doc | Reason |
|---|---|---|
```

## Extraction Rules

- Do not invent command names.
- Do not invent state names.
- Do not invent event names.
- If design uses conceptual wording but no event name exists, propose candidate event name and mark `NEEDS_CONFIRMATION`.
- If source docs conflict, use conflict resolution from governance docs.
- If behavior is excluded in phase boundary docs, mark `BLOCKED_SCOPE_EXCLUDED`.

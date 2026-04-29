---
name: slice-strategy
description: Guides FleziBCG implementation as vertical slices instead of backend-only module builds.
---

# Slice Strategy

## Principle

Do not build the whole backend first.

Build verified system slices:

```text
DB → backend truth → event/invariant → tests → minimal FE/API verification if needed
```

## Recommended order

```text
P0-A Foundation
→ P0-B Manufacturing Master Data Minimum
→ P0-C Execution Core
→ P0-D Quality Lite
→ P0-E Supervisory Operations
→ P1 Integration / Acceptance Gate / Material / Reporting
```

## Slice done criteria

A slice is done only when:

- tests pass
- event/invariant maps exist where required
- build/import check passes
- no excluded scope added
- reports updated
- next slice selected

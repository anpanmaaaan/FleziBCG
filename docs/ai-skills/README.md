# FleziBCG Native AI Skills — Enterprise v4

This folder uses folder-based `SKILL.md` pattern.

## Default Skill

```text
docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md
```

## Skills

| Skill | Purpose | Status |
|---|---|---|
| `flezibcg-ai-brain-v6-auto-execution` | Main router and adaptive brain | Active |
| `hard-mode-mom-v3` | Design-driven autonomous implementation gate | Active |
| `hard-mode-mom-v2` | Manual review/rejection gate | Active |
| `qa-e2e-layer` | Real-world QA/E2E simulation | Active |
| `pr-gate-reviewer` | PR review and merge gate | Active |
| `design-md-ui-governor` | **Canonical UI/UX skill** — DESIGN.md, FE, screen packs, industrial UX, anti-clutter | Active (v3, 2026-05-17) |
| `stitch-design-md-ui-ux` | (DEPRECATED — see design-md-ui-governor) | Stub |
| `design-system-enforcer` | (DEPRECATED — see design-md-ui-governor) | Stub |
| `autonomous-implementation-agent` | Agent execution loop | Active |
| `slice-strategy` | Vertical slicing strategy | Active |
| `generic-brain-core` | Generic engineering brain | Active |
| `mom-brain-core` | MOM-specific domain brain | Active |
| `skill-authoring-standard` | How to write new local skills | Active |

## Version Rule

- v3 = autonomous implementation
- v2 = review/manual enforcement
- v1 = deprecated

## FE/UI Skill Routing (2026-05-17)

For any task that touches frontend UI/UX, load **`design-md-ui-governor`**.
It is the consolidated canonical skill covering:

- DESIGN.md governance and updates;
- React + Tailwind v4 + shadcn/ui implementation rules;
- Figma Make / Google Stitch design-md output;
- Screen packs and source alignment;
- Industrial UX numerics (touch, type, contrast, viewing distance);
- Layout templates (cockpit / dashboard / form / list / multi-station / single-screen wizard);
- Anti-clutter diagnostic ("rối" gate);
- Offline / scanner / alert / multi-station / long-op guardrails;
- Backend-truth boundary;
- MOM safety gates.

The earlier skills `stitch-design-md-ui-ux` and `design-system-enforcer` are
now deprecated stubs that point to `design-md-ui-governor`. Do not load them
in parallel.

For execution, quality, material, station, operation, or governed-action UI,
load **both** `design-md-ui-governor` and `hard-mode-mom-v3`.

# Prompt — Refresh Frontend Source Alignment Snapshot

You are a senior frontend architect and source-code auditor.

Refresh the frontend source alignment snapshot after UI changes.

Allowed file change:

```text
docs/audit/frontend-source-alignment-snapshot.md
```

Do not modify production source code.
Do not refactor.
Do not install dependencies.
Do not change routes.
Do not change backend.
Do not change database/migrations.

Inspect:

```text
frontend/
frontend/src/
frontend/package.json
frontend/vite.config.*
frontend/tsconfig*.json
frontend/tailwind.config.*
DESIGN.md
docs/design/DESIGN.md
docs/ai-skills/design-md-ui-governor/SKILL.md
```

Update the snapshot with:

- current route registry;
- current page inventory;
- current component inventory;
- current API/data-access pattern;
- current state management pattern;
- current i18n pattern;
- current styling/design-token pattern;
- current mock/fixture pattern;
- preserve/extend/replace decisions;
- missing screen groups;
- updated source-alignment constraints;
- risks and warnings.

Every meaningful claim must include evidence file paths.

Final reply:

```text
Frontend Source Alignment Snapshot refreshed.
Report updated: docs/audit/frontend-source-alignment-snapshot.md
Overall verdict: ...
Recommended next step: ...
```

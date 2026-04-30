# Source Alignment Rules

## Purpose

Prevent Figma Make, Stitch, or coding agents from generating pretty but source-incompatible UI.

## Required Evidence

Before designing or implementing UI, identify:

- existing routes;
- existing page files;
- existing app shell/navigation;
- existing API client pattern;
- existing component library;
- existing i18n pattern;
- existing mock/fixture pattern;
- existing build/lint/test commands.

## Rules

1. Preserve working screens unless replacement is explicitly approved.
2. Extend current app shell where possible.
3. Do not invent route patterns without checking current router.
4. Do not invent API response fields.
5. Do not infer backend connectivity from UI mock data.
6. Separate mocks from production API paths.
7. Mark future screens as `FUTURE` or `DISABLED`.
8. Update screen inventory or source-alignment report when UI structure changes.
9. Do not implement all screens in one PR.
10. Report exact files changed and verification commands.

## Recommended UI Pack Sequence

1. UI-00 Global Shell Alignment
2. UI-01 Foundation / IAM
3. UI-02 Manufacturing Master Data
4. UI-03 Execution
5. UI-04 Supervisory Operations
6. UI-05 Quality Lite
7. UI-06 Material / Traceability
8. UI-07 Integration
9. UI-08 Reporting / APS / AI / Twin / Compliance Future

Adjust only when source evidence justifies it.

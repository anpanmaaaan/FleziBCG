# Source Alignment Rules

Before designing/implementing UI, identify: existing routes, page files, app shell/navigation, API client, component library, i18n pattern, mock/fixture pattern, build/lint/test commands.

Rules:
1. Preserve working screens unless replacement approved.
2. Extend current app shell where possible.
3. Do not invent route patterns without checking router.
4. Do not invent API response fields.
5. Do not infer backend connectivity from UI mocks.
6. Separate mocks from production API paths.
7. Mark future screens as FUTURE or DISABLED.
8. Update screen inventory or source-alignment report when UI changes.
9. Do not implement all screens in one PR.
10. Report exact files changed and verification commands.

Recommended UI Pack Sequence: UI-00 Shell, UI-01 IAM, UI-02 Master Data, UI-03 Execution, UI-04 Supervisory, UI-05 Quality Lite, UI-06 Material/Traceability, UI-07 Integration, UI-08 Future.

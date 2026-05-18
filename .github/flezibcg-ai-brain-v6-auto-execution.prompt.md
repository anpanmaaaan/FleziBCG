Follow docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md.

Task:
{{task}}

Required:
1. Select brain automatically.
2. Select mode automatically.
3. Turn Hard Mode MOM ON if triggered.
4. Output routing decision first, including selected skills read, Hard Mode decision, and coverage class.
5. Keep Hard Mode MOM v3 for follow-up fixes when the parent slice required v3, unless the change is purely text/comment-only.
6. Execute using the selected flow.
7. In the final report, distinguish service, API, frontend, and E2E coverage; do not claim broader coverage than the tests actually prove.
8. Before marking done, overwrite `docs/agent-reports/latest-agent-report.md` with the final report. The chat response may summarize it, but the repo file is canonical for review.

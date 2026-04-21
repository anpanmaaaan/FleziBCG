We are continuing an interrupted Station Execution implementation session.

Project context:
- AI-driven MES/MOM platform
- Current focus: Station Execution
- Backend is source of truth
- Frontend is UX only
- Canonical Station Execution docs provided in earlier session are the source of truth
- Do not invent behavior outside current grounded backend model
- Do not overclaim completion

Current implementation state:
- pause/resume backend done
- downtime backend loop done
- downtime_open projection done
- allowed_actions projection done
- FE cockpit already consumes allowed_actions
- queue/selection list issue is under active work

Most recent accepted findings:
- Backend queue currently omits PAUSED/BLOCKED operations
- Frontend selection list is not the primary cause
- Next task is to include active non-terminal states in station queue and project downtime_open

Task currently in progress:
SE-BE-STATION-QUEUE-INCLUDE-ACTIVE-STATES-001

Task prompt:
[PASTE THE EXACT TASK PROMPT HERE]

Most recent report:
[PASTE THE LAST AGENT REPORT HERE]

Instructions:
- Continue from this exact point
- Be evidence-based
- Keep the change set focused
- Return the requested report format only
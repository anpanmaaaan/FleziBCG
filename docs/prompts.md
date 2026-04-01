# start app
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8010 --reload

cd frontend
npm install
npm run dev

# agent-review-promp
Please review this repository as a Phase 1–2 MES backend + frontend implementation.

Context:
- This is a lightweight MES (Manufacturing Execution System) project.
- Backend: FastAPI + SQLAlchemy
- Frontend: React + TypeScript + Vite
- Database: SQLite (temporary, PostgreSQL planned later)
- Read-only Phase 1 UI has been integrated:
  - ProductionOrderList
  - OperationList
- ExecutionEvent model exists and is intended to be the source of truth.
- Current scope is Phase 1 read-side, preparing for Phase 2 write-flow.
- No advanced scheduling, no AI, no streaming, no microservices.

IMPORTANT CONSTRAINTS:
- Do NOT rewrite large parts of the code.
- Do NOT add new features.
- Do NOT introduce new domains.
- Do NOT refactor unless there is a clear architectural risk.
- Assume this is a solo developer project.
- Favor practical MES engineering over theoretical perfection.

Your role:
Act as a senior MES/Manufacturing IT architect reviewing this codebase
before Phase 2 (write-flow) implementation begins.

Please review the following aspects:

1. Backend domain model
   - ProductionOrder, WorkOrder, Operation relationships
   - ExecutionEvent design
   - Whether ExecutionEvent is correctly positioned as the source of truth
   - Whether snapshot fields on Operation are clearly projection/derived state

2. Backend layering and responsibilities
   - Route layer (API)
   - Service layer (business logic)
   - Repository layer (DB access)
   - Check that business rules are not leaking into routes or repositories

3. Event vs Snapshot consistency
   - Are there any places where snapshot fields are updated directly
     without appending an ExecutionEvent?
   - Are there any risks of future inconsistency when write-flow is added?

4. Frontend integration correctness
   - ProductionOrderList and OperationList data flow
   - Use of real backend APIs (no mock data)
   - UI not deriving business state
   - Placeholder handling for Phase 1 gaps

5. Database usage
   - SQLite usage for Phase 1–2
   - Any SQLite-specific assumptions that could block PostgreSQL later

6. Readiness for Phase 2 (write-flow)
   - Is the codebase structurally ready to implement:
     POST /operations/{id}/start
     POST /operations/{id}/report-quantity
     POST /operations/{id}/complete
   - What constraints or rules should be locked before adding these?

Output format:
- High-level assessment (PASS / MINOR ISSUES / BLOCKING ISSUES)
- Strengths (what is already done well)
- Risks (only real risks, not hypothetical)
- Small, focused recommendations (if any)
- Clear statement: “Ready for Phase 2 write-flow: YES/NO”
- If NO, list exactly what must be fixed first (max 3 items)

Please keep the review concise, practical, and MES-oriented.


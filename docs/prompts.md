# start app
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8010 --reload

cd frontend
npm install
npm run dev

# init DB
python - <<'EOF'
from app.db.init_db import init_db
init_db()
print("✅ DB initialized")
EOF

# NOTE
.gitignore
# =========================
# Node / Frontend
# =========================

# Dependency directories
node_modules/

# Build output (Vite / React)
frontend/dist/
frontend/.vite/

# Environment variables
.env
.env.*
!.env.example

# =========================
# Backend / Python
# =========================

# Python cache
__pycache__/
*.py[cod]
*.pyo
*.pyd

# Virtual environment
.venv/
venv/

# =========================
# Database (local only)
# =========================

# SQLite local databases
*.db
*.sqlite
*.sqlite3

# =========================
# OS / Editor
# =========================

.DS_Store
Thumbs.db
.vscode/
.idea/

# =========================
# Logs / Temp
# =========================

*.log
tmp/
.temp/
.cache/

# agent-review-promp
Please perform a FULL CODEBASE REVIEW for this MES project before merge.

Context:
- This is a Manufacturing Execution System (MES) implementation.
- Backend: FastAPI + SQLAlchemy.
- Frontend: React + TypeScript + Vite.
- Database: SQLite for Phase 1–2, PostgreSQL planned later.
- Phase 1 (read-side) is complete:
  - ProductionOrderList
  - OperationList
- Phase 2 (write-flow) is complete:
  - start_operation
  - report_quantity
  - complete_operation
- ExecutionEvent is explicitly designed as the append-only source of truth.
- Operation snapshot fields are derived/projection state.
- This is a solo developer project aiming for long-term maintainability.

IMPORTANT CONSTRAINTS (very strict):
- Do NOT rewrite or refactor the code unless there is a clear architectural risk.
- Do NOT introduce new features.
- Do NOT expand scope beyond Phase 1–2.
- Do NOT propose microservices, message queues, or full event sourcing frameworks.
- Do NOT optimize prematurely.
- Assume the goal is correctness, clarity, and architectural soundness—not cleverness.

Your role:
Act as a senior MES / Manufacturing IT architect performing a final pre-merge technical review.

Please review the codebase across these dimensions:

1. DOMAIN MODEL & MES CORRECTNESS
- ProductionOrder / WorkOrder / Operation / ExecutionEvent relationships
- Alignment with ISA‑95 Level 3 concepts
- Operation lifecycle correctness (PENDING → IN_PROGRESS → COMPLETED)
- Event types completeness and minimalism

2. EVENT & STATE MANAGEMENT
- Is ExecutionEvent consistently treated as the source of truth?
- Are snapshot fields clearly derived/projection state?
- Are there any direct state mutations that bypass events?
- Are write-flows (start / report / complete) safe and consistent?

3. BACKEND ARCHITECTURE
- Route layer responsibilities
- Service layer business logic placement
- Repository layer DB responsibility boundaries
- Error handling and idempotency
- Tenant isolation enforcement

4. FRONTEND INTEGRATION (READ-SIDE)
- Correct usage of backend APIs
- Absence of mock data
- UI not deriving execution logic
- Placeholder handling for Phase 1 gaps
- Separation of display vs business logic

5. DATABASE STRATEGY
- SQLite usage appropriateness for Phase 2
- Absence of SQLite-specific assumptions that block PostgreSQL
- Migration preparedness

6. PHASE 2 COMPLETENESS
- Are all required write-flows implemented correctly?
- Is the execution lifecycle truly complete?
- Are there any missing guards or edge cases?

7. TECH DEBT & FUTURE RISKS
- Identify only REAL risks, not hypothetical ones
- Defer performance concerns unless they block correctness
- Flag anything that would make Phase 3 unsafe

OUTPUT FORMAT (mandatory):
- ✅ High-level assessment: PASS / MINOR ISSUES / BLOCKING ISSUES
- ✅ Strengths (what is done especially well)
- ⚠️ Risks (only concrete, actionable risks)
- 🔧 Small recommendations (max 3, non-breaking)
- 🟢 Merge readiness: YES / NO
- If NO:
  - List EXACTLY what must be fixed before merge (max 3 items)
- Final statement:
  - “This codebase is structurally ready for Phase 3.”

Tone:
- Practical
- Architecture-focused
- MES-oriented
- No generic advice
- No over-engineering

Please keep the review concise but authoritative.

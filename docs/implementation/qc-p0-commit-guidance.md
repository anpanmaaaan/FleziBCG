# QC P0 Commit Guidance

## Purpose

Provide a safe, non-interactive commit flow for the QC P0 slice while avoiding unrelated changes currently present in the working tree.

## Scope rule

Only stage QC P0 files. Do not stage unrelated execution/IAM/frontend platform files in the same commit set.

## Pre-check

```bash
cd /workspaces/FleziBCG
git status --short
```

Expected: many files may be modified. This is okay as long as staging is path-constrained.

## Recommended commit split

### Commit 1: Backend quality foundation and invariants

Stage:

```bash
git add \
  backend/alembic/versions/0015_quality_measurement_foundation.py \
  backend/alembic/versions/0016_quality_disposition_decisions.py \
  backend/app/api/v1/quality.py \
  backend/app/models/quality.py \
  backend/app/repositories/quality_repository.py \
  backend/app/schemas/quality.py \
  backend/app/services/quality_service.py \
  backend/tests/test_quality_measurement_service.py \
  backend/tests/test_quality_hold_execution_gating.py
```

Verify staged set:

```bash
git diff --cached --name-only
```

Commit message:

```text
feat(quality): implement QC measurement and disposition backbone with hold-gate invariants
```

Commit:

```bash
git commit -m "feat(quality): implement QC measurement and disposition backbone with hold-gate invariants"
```

### Commit 2: Frontend quality contract and regression coverage

Stage:

```bash
git add \
  frontend/src/app/api/qualityApi.ts \
  frontend/src/app/pages/MeasurementEntry.tsx \
  frontend/src/app/pages/QualityHolds.tsx \
  frontend/src/app/i18n/registry/en.ts \
  frontend/src/app/i18n/registry/ja.ts \
  frontend/e2e/quality-measurement-completeness.spec.ts \
  frontend/e2e/header-operational-context.spec.ts \
  frontend/README.md
```

Verify staged set:

```bash
git diff --cached --name-only
```

Commit message:

```text
feat(frontend): align QC measurement UI contract and add E2E gating coverage
```

Commit:

```bash
git commit -m "feat(frontend): align QC measurement UI contract and add E2E gating coverage"
```

### Commit 3: Design and implementation evidence

Stage:

```bash
git add \
  docs/design/05_application/api-catalog-current-baseline.md \
  docs/implementation/qc-p0-a-initial-measurement-hard-mode-mom-v3-gate.md \
  docs/implementation/qc-p0-a-initial-measurement-implementation-report.md \
  docs/implementation/qc-p0-b-disposition-hard-mode-mom-v3-gate.md \
  docs/implementation/qc-p0-b-disposition-implementation-report.md \
  docs/implementation/qc-p0-c-execution-gating-hard-mode-mom-v3-gate.md \
  docs/implementation/qc-p0-c-execution-gating-implementation-report.md \
  docs/implementation/qc-p0-d-accepted-good-release-hard-mode-mom-v3-gate.md \
  docs/implementation/qc-p0-d-accepted-good-release-implementation-report.md \
  docs/implementation/qc-p0-e-backend-owned-measurement-evaluation-hard-mode-mom-v3-gate.md \
  docs/implementation/qc-p0-e-backend-owned-measurement-evaluation-implementation-report.md \
  docs/implementation/qc-p0-f-require-recheck-hold-gate-hard-mode-mom-v3-gate.md \
  docs/implementation/qc-p0-f-require-recheck-hold-gate-implementation-report.md \
  docs/implementation/qc-p0-g-measurement-submit-contract-hard-mode-mom-v3-gate.md \
  docs/implementation/qc-p0-g-measurement-submit-contract-implementation-report.md \
  docs/implementation/qc-p0-h-required-measurement-completeness-hard-mode-mom-v3-gate.md \
  docs/implementation/qc-p0-h-required-measurement-completeness-implementation-report.md \
  docs/implementation/qc-p0-quality-slice-pr-summary.md \
  docs/implementation/qc-p0-merge-readiness-checklist.md \
  docs/implementation/qc-p0-commit-guidance.md
```

Optional if intentionally included in this PR:

```bash
git add docs/implementation/quality-pr-documentation-sync-checklist.md
```

Verify staged set:

```bash
git diff --cached --name-only
```

Commit message:

```text
docs(quality): add QC P0 hard-mode evidence, summary, and merge guidance
```

Commit:

```bash
git commit -m "docs(quality): add QC P0 hard-mode evidence, summary, and merge guidance"
```

## Verification before push

Run:

```bash
cd /workspaces/FleziBCG/backend
DATABASE_URL='postgresql+psycopg://mes:mes@localhost:5432/mes_test' \
PYTHONPATH=/workspaces/FleziBCG/backend \
/workspaces/FleziBCG/.venv/bin/python -m pytest -q \
  tests/test_quality_measurement_service.py \
  tests/test_quality_hold_execution_gating.py

cd /workspaces/FleziBCG/frontend
npm run lint
npm run build
npx playwright test
```

## Safety checks

1. Before each commit: `git diff --cached --name-only`
2. After each commit: `git show --name-only --pretty=format: HEAD`
3. If accidental staging occurs:

```bash
git restore --staged <path>
```

## PR title suggestion

```text
QC P0: backend-truth measurement/disposition hardening, strict completeness, FE contract + E2E coverage
```

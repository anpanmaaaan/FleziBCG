#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────
#  i18n hardcoded-string lint for operator-critical screens
#  Exit 1 if violations found.
# ─────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$SCRIPT_DIR/.."

# Files to check (critical + non-critical execution screens)
FILES=(
  "src/app/pages/StationExecution.tsx"
  "src/app/pages/OperationExecutionDetail.tsx"
  "src/app/pages/OperationExecutionOverview.tsx"
  "src/app/pages/ProductionTracking.tsx"
  "src/app/pages/DispatchQueue.tsx"
  "src/app/pages/Home.tsx"
  "src/app/components/GanttChart.tsx"
)

VIOLATIONS=0

for file in "${FILES[@]}"; do
  filepath="$ROOT/$file"
  if [[ ! -f "$filepath" ]]; then
    continue
  fi

  # 1) toast.*("literal") — toast calls with inline strings instead of t()
  matches=$(grep -nP 'toast\.(error|success|warning|info)\(\s*["`'"'"'](?!.*\bt\()' "$filepath" 2>/dev/null || true)
  if [[ -n "$matches" ]]; then
    echo "VIOLATION [$file]: toast with hardcoded string"
    echo "$matches"
    VIOLATIONS=$((VIOLATIONS + 1))
  fi

  # 2) window.confirm("literal") or confirm("literal")
  matches=$(grep -nP '(window\.)?confirm\(\s*["`'"'"'](?!.*\bt\()' "$filepath" 2>/dev/null || true)
  if [[ -n "$matches" ]]; then
    echo "VIOLATION [$file]: confirm() with hardcoded string"
    echo "$matches"
    VIOLATIONS=$((VIOLATIONS + 1))
  fi

  # 3) title="literal" (not title={...})
  matches=$(grep -nP '\btitle="[A-Z][a-zA-Z ]{2,}"' "$filepath" 2>/dev/null || true)
  if [[ -n "$matches" ]]; then
    echo "VIOLATION [$file]: title attribute with hardcoded string"
    echo "$matches"
    VIOLATIONS=$((VIOLATIONS + 1))
  fi
done

if [[ $VIOLATIONS -gt 0 ]]; then
  echo ""
  echo "❌ Found $VIOLATIONS i18n violation(s). Fix before merging."
  exit 1
fi

echo "✅ No i18n violations found in checked files."
exit 0

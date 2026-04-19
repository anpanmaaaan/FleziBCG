#!/bin/bash
# Lightweight i18n hardcode enforcement for TSX
# Fails if common hardcoded UI string patterns are found

set -e

PATTERNS=(
  ">[^<>{}\\n\\t][^<>{}]*<" # JSX text node with literal
  "toast\\.[a-zA-Z]+\\([\"'\"][^\{\}\)\\n]*[\"'\"]\\)" # toast.*("literal")
  "confirm\\([\"'\"][^\{\}\)\\n]*[\"'\"]\\)" # confirm("literal")
  "title=[\"'\"][^\{\}\)\\n]*[\"'\"]" # title="literal"
)

FAIL=0
for pattern in "${PATTERNS[@]}"; do
  if grep -Pnr --include='*.tsx' "$pattern" ./src/app/pages | grep -Fv 't('; then
    echo "[i18n-lint] Hardcoded string violation detected for pattern: $pattern"
    FAIL=1
  fi

done

if [ $FAIL -ne 0 ]; then
  echo "[i18n-lint] FAIL: Hardcoded UI strings found. Use useI18n().t(key) for all user-facing text."
  exit 1
else
  echo "[i18n-lint] PASS: No hardcoded UI strings detected."
fi

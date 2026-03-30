#!/bin/bash
# Script to show remaining files with duplicate Header issue

echo "=== REMAINING FILES WITH DUPLICATE HEADER BUG ==="
echo ""
echo "Files still using old Header component:"
echo ""

FILES=(
  "DefectManagement.tsx"
  "Home.tsx"
  "OperationList.tsx"
  "Production.tsx"
  "ProductionOrderList.tsx"
  "ProductionTracking.tsx"
  "RouteDetail.tsx"
  "RouteList.tsx"
  "StationExecution.tsx"
  "Traceability.tsx"
)

for file in "${FILES[@]}"; do
  echo "❌ /src/app/pages/$file"
done

echo ""
echo "=== FIX PATTERN ==="
echo ""
echo "1. Remove import:"
echo '   import { Header } from "../components/Header";'
echo ""
echo "2. Remove JSX line:"
echo '   <Header title="..." showBackButton={false} />'
echo ""
echo "=== ALREADY FIXED ==="
echo "✅ Dashboard.tsx"
echo "✅ DispatchQueue.tsx"
echo "✅ QCCheckpoints.tsx"
echo "✅ APSScheduling.tsx"
echo ""
echo "Total remaining: ${#FILES[@]} files"

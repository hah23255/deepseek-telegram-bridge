#!/usr/bin/env bash
# Master Tester Doctrine — CI Gate Script
# Run in CI pipeline. Fails on any doctrine violation.
set -euo pipefail

echo "Master Tester Doctrine — CI Gate"
echo "================================="
VIOLATIONS=0

# 1. No `as any` in test files
echo "--- Checking: No 'as any' in tests ---"
AS_ANY=$(grep -rn "as any" --include="*.test.*" --include="*.spec.*" src/ tests/ 2>/dev/null | wc -l)
if [ "$AS_ANY" -gt 0 ]; then
  echo "✗ Found $AS_ANY occurrences of 'as any' in test files:"
  grep -rn "as any" --include="*.test.*" --include="*.spec.*" src/ tests/ 2>/dev/null
  VIOLATIONS=$((VIOLATIONS + 1))
else
  echo "✓ No 'as any' found"
fi

# 2. No `@ts-ignore` (use @ts-expect-error)
echo "--- Checking: No @ts-ignore ---"
TS_IGNORE=$(grep -rn "@ts-ignore" src/ 2>/dev/null | wc -l)
if [ "$TS_IGNORE" -gt 0 ]; then
  echo "✗ Found $TS_IGNORE @ts-ignore directives:"
  grep -rn "@ts-ignore" src/ 2>/dev/null
  VIOLATIONS=$((VIOLATIONS + 1))
else
  echo "✓ No @ts-ignore found"
fi

# 3. No direct fetch/axios mocking
echo "--- Checking: MSW used for HTTP mocking ---"
BAD_MOCKS=$(grep -rn "vi\.fn().*fetch\|vi\.mock('axios')\|jest\.mock('axios')" --include="*.test.*" --include="*.spec.*" src/ tests/ 2>/dev/null | wc -l)
if [ "$BAD_MOCKS" -gt 0 ]; then
  echo "✗ Found $BAD_MOCKS direct fetch/axios mocks (use MSW):"
  grep -rn "vi\.fn().*fetch\|vi\.mock('axios')\|jest\.mock('axios')" --include="*.test.*" --include="*.spec.*" src/ tests/ 2>/dev/null
  VIOLATIONS=$((VIOLATIONS + 1))
else
  echo "✓ MSW used for HTTP mocking"
fi

# 4. Circular dependencies
echo "--- Checking: No circular dependencies ---"
if npx depcruise src --config configs/.dependency-cruiser.js 2>/dev/null; then
  echo "✓ No circular dependencies"
else
  VIOLATIONS=$((VIOLATIONS + 1))
fi

# 5. Flaky test detection (check for .skip with no reason)
echo "--- Checking: Documented test skips ---"
SKIPS=$(grep -rn "\.skip" --include="*.test.*" --include="*.spec.*" src/ tests/ 2>/dev/null | grep -v "//.*skip\|/\*.*skip" | wc -l)
if [ "$SKIPS" -gt 0 ]; then
  echo "⚠ $SKIPS tests skipped — ensure each has a documented reason"
fi

# 6. Unused exports (dead code)
echo "--- Checking: Dead code ---"
if npx knip 2>/dev/null; then
  echo "✓ No dead code detected"
else
  echo "⚠ knip found issues — review manually"
fi

echo ""
echo "================================="
if [ "$VIOLATIONS" -eq 0 ]; then
  echo "✓ CI Gate passed."
  exit 0
else
  echo "✗ $VIOLATIONS violation(s) found. Fix before merging."
  exit 1
fi

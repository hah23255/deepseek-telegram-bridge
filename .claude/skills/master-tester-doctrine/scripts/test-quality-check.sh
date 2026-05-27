#!/usr/bin/env bash
# Master Tester Doctrine — Test Quality Check
# Analyses existing test suite for doctrine violations.
set -euo pipefail

echo "Master Tester Doctrine — Quality Check"
echo "======================================="
echo ""

TOTAL_TESTS=0
ISSUES=0

# Count tests
TOTAL_TESTS=$(grep -rn "it(\|test(" --include="*.test.*" --include="*.spec.*" src/ tests/ 2>/dev/null | wc -l)
echo "Total tests found: $TOTAL_TESTS"
echo ""

# 1. Tautological tests
echo "--- Tautological Tests ---"
TAUT=$(grep -rn "expect(typeof\|expect(true).toBe(true)\|expect(2+2)" --include="*.test.*" --include="*.spec.*" src/ tests/ 2>/dev/null | wc -l)
[ "$TAUT" -gt 0 ] && echo "  ⚠ $TAUT potential tautological tests" || echo "  ✓ None found"

# 2. Over-mocking
echo "--- Over-Mocking ---"
OVERMOCK=$(grep -rn "vi\.fn()" --include="*.test.*" --include="*.spec.*" src/ tests/ 2>/dev/null | grep -v "vi\.fn().*mock\|vi\.mocked" | wc -l)
[ "$OVERMOCK" -gt 10 ] && echo "  ⚠ $OVERMOCK vi.fn() usages — review for over-mocking" || echo "  ✓ Acceptable mock count"

# 3. Shared state (beforeEach outside describe)
echo "--- Shared State ---"
SHARED=$(grep -rn "^let \|^var \|^const " --include="*.test.*" --include="*.spec.*" src/ tests/ 2>/dev/null | grep -v "beforeEach\|afterEach\|describe\|it(" | head -10)
if [ -n "$SHARED" ]; then
  printf "  ⚠ Module-level shared variables detected:\n%s\n" "$SHARED"
else
  echo "  ✓ No shared state"
fi

# 4. Real timers
echo "--- Time Control ---"
REAL_TIMERS=$(grep -rn "setTimeout\|setInterval" --include="*.test.*" --include="*.spec.*" src/ tests/ 2>/dev/null | grep -v "vi\.\|mock\|//" | wc -l)
[ "$REAL_TIMERS" -gt 0 ] && echo "  ⚠ $REAL_TIMERS real timer usages — use vi.useFakeTimers()" || echo "  ✓ No real timers"

# 5. Implementation-coupled tests
echo "--- Implementation Coupling ---"
IMPL=$(grep -rn "\.state\.\|\.props\.\|\.instance\." --include="*.test.*" --include="*.spec.*" src/ tests/ 2>/dev/null | wc -l)
[ "$IMPL" -gt 0 ] && echo "  ⚠ $IMPL tests accessing internal state — test behaviour, not implementation" || echo "  ✓ No implementation coupling"

# 6. AAA pattern violations (assertions before act, or act missing)
echo "--- AAA Pattern ---"
NO_ACT=$(grep -rn "expect(" --include="*.test.*" --include="*.spec.*" src/ tests/ 2>/dev/null | head -5)
# Heuristic: tests with expect() but no render/fireEvent in the same test scope

echo ""
echo "======================================="
echo "Quality check complete on $TOTAL_TESTS tests."
echo "Review warnings above. Fix doctrine violations before deployment."

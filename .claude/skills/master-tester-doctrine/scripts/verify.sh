#!/usr/bin/env bash
# Master Tester Doctrine — Verification Script
set -euo pipefail

PASS=0; FAIL=0
pass() { echo "  ✓ $1"; PASS=$((PASS+1)); }
fail() { echo "  ✗ $1"; FAIL=$((FAIL+1)); }

echo "Master Tester Doctrine — Verification"
echo "======================================"
echo ""

# 1. Skill files
echo "--- Skill ---"
for f in \
  SKILL.md \
  SOUL.md \
  AGENTS.md \
  README.md \
  CHANGELOG.md \
  LICENSE \
  doctrine/INDEX.md \
  doctrine/MASTER-TESTER-DOCTRINE.md \
  doctrine/oath-of-the-master-tester.md \
  doctrine/unit-testing-rule-book.md \
  doctrine/modern-ts-testers-guideline.md \
  doctrine/expanded-modern-ts-testers-guideline.md \
  doctrine/vanguard-of-ts-testing.md \
  references/zero-trust-protocol.md \
  references/golden-rules.md \
  references/anti-patterns.md \
  references/advanced-patterns.md \
  references/workflow-example.md; do
  [[ -f "$f" ]] && pass "$f" || fail "$f missing"
done

# 2. Source code
echo "--- Source ---"
[[ -f src/factories/project.ts ]] && pass "factories/project.ts" || fail "factories/project.ts missing"
[[ -f src/mocks/handlers.ts ]] && pass "mocks/handlers.ts" || fail "mocks/handlers.ts missing"
[[ -f src/mocks/server.ts ]] && pass "mocks/server.ts" || fail "mocks/server.ts missing"
[[ -f src/test-utils/strict-mock.ts ]] && pass "strict-mock.ts" || fail "strict-mock.ts missing"
[[ -f src/test-utils/deferred.ts ]] && pass "deferred.ts" || fail "deferred.ts missing"
[[ -f src/test-utils/flush-promises.ts ]] && pass "flush-promises.ts" || fail "flush-promises.ts missing"

# 3. Configs
echo "--- Configs ---"
[[ -f configs/vitest.config.ts ]] && pass "vitest.config.ts" || fail "vitest.config.ts missing"
[[ -f configs/.dependency-cruiser.js ]] && pass ".dependency-cruiser.js" || fail ".dependency-cruiser.js missing"
[[ -f configs/biome.json ]] && pass "biome.json" || fail "biome.json missing"

# 4. Dependencies (only checked when run inside a project with package.json)
echo "--- Dependencies ---"
if [[ -f package.json ]]; then
  for pkg in vitest msw fast-check @faker-js/faker; do
    # Check devDependencies / dependencies in package.json, or node_modules presence
    if grep -q "\"$pkg\"" package.json 2>/dev/null || [[ -d "node_modules/$pkg" ]]; then
      pass "$pkg"
    else
      fail "$pkg not declared in package.json — run scripts/install.sh"
    fi
  done
else
  pass "package.json not present — skipping dependency check (skill-only verification)"
fi

# 5. TypeScript compilation check (if tsconfig exists)
echo "--- TypeScript ---"
if [[ -f tsconfig.json ]]; then
  npx tsc --noEmit 2>&1 && pass "TypeScript compiles" || fail "TypeScript errors found"
else
  pass "tsconfig.json not present — skipping TypeScript check"
fi

echo ""
echo "======================================"
echo "Results: $PASS passed, $FAIL failed"
[[ $FAIL -eq 0 ]] && echo "✓ Master Tester Doctrine verified." || echo "⚠ Fix failures before using."

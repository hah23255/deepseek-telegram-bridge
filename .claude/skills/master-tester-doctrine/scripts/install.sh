#!/usr/bin/env bash
# Master Tester Doctrine — Installation Script
set -euo pipefail

echo "Master Tester Doctrine — Installation"
echo "======================================"
echo ""

# 1. Install dependencies
echo "--- Dependencies ---"
PACKAGES=("vitest" "@testing-library/react" "@testing-library/jest-dom" "msw" "fast-check" "@faker-js/faker" "dependency-cruiser")

for pkg in "${PACKAGES[@]}"; do
  echo -n "  $pkg: "
  if npm ls "$pkg" --depth=0 2>/dev/null | grep -q "$pkg"; then
    echo "✓"
  else
    echo "installing..."
    npm install --save-dev "$pkg" 2>&1 | tail -1
  fi
done

# 2. Copy config files
echo ""
echo "--- Configs ---"
cp -n configs/vitest.config.ts . 2>/dev/null && echo "  ✓ vitest.config.ts" || echo "  ⚠ vitest.config.ts already exists"
cp -n configs/.dependency-cruiser.js . 2>/dev/null && echo "  ✓ .dependency-cruiser.js" || echo "  ⚠ .dependency-cruiser.js already exists"
cp -n configs/biome.json . 2>/dev/null && echo "  ✓ biome.json" || echo "  ⚠ biome.json already exists"

# 3. Create test utility directory
echo ""
echo "--- Test Utilities ---"
mkdir -p src/test-utils src/factories src/__tests__/helpers src/mocks
cp -n src/test-utils/*.ts src/test-utils/ 2>/dev/null && echo "  ✓ Test utilities" || echo "  ⚠ Test utilities already exist"
cp -n src/factories/*.ts src/factories/ 2>/dev/null && echo "  ✓ Factories" || echo "  ⚠ Factories already exist"
cp -n src/mocks/*.ts src/mocks/ 2>/dev/null && echo "  ✓ MSW handlers" || echo "  ⚠ MSW handlers already exist"

# 4. Create vitest.setup.ts
if [[ ! -f vitest.setup.ts ]]; then
  cat > vitest.setup.ts << 'SETUPEOF'
import '@testing-library/jest-dom/vitest';
import { server } from '@/mocks/server';
import { cleanup } from '@testing-library/react';

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => {
  server.resetHandlers();
  cleanup();
});
afterAll(() => server.close());
SETUPEOF
  echo "  ✓ vitest.setup.ts created"
else
  echo "  ⚠ vitest.setup.ts already exists"
fi

# 5. Install the skill for an AI agent (Claude Code, Cursor, OpenCode, …)
echo ""
echo "--- Agent Skill ---"
SKILL_DIR="${MASTER_TESTER_SKILL_DIR:-${HOME}/.agents/skills/master-tester-doctrine}"
mkdir -p "$SKILL_DIR"
cp SKILL.md "$SKILL_DIR/"
cp SOUL.md "$SKILL_DIR/" 2>/dev/null || true
cp AGENTS.md "$SKILL_DIR/"
cp README.md "$SKILL_DIR/" 2>/dev/null || true
cp CHANGELOG.md "$SKILL_DIR/" 2>/dev/null || true
cp LICENSE "$SKILL_DIR/" 2>/dev/null || true
cp -r doctrine/ "$SKILL_DIR/"
cp -r references/ "$SKILL_DIR/" 2>/dev/null || true
cp -r src/ "$SKILL_DIR/"
cp -r docs/ "$SKILL_DIR/" 2>/dev/null || true
echo "  ✓ Skill installed at $SKILL_DIR"
echo "    (override with MASTER_TESTER_SKILL_DIR=... bash scripts/install.sh)"

echo ""
echo "======================================"
echo "Installation complete."
echo "Run: scripts/verify.sh to validate"

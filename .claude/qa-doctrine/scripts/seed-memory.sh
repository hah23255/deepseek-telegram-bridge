#!/usr/bin/env bash
#
# QA Doctrine — memory seed bootstrap
#
# Creates the auto-memory directory + drops the canonical doctrine
# memory file + initialises the MEMORY.md index.
#
# Usage: bash scripts/seed-memory.sh
#

set -euo pipefail

PACK_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Detect sanitized cwd path (Claude Code convention)
# Sanitize: replace / with - and prefix with -
SANITIZED_CWD="-$(pwd | sed 's|/|-|g')"
MEM_DIR="$HOME/.claude/projects/$SANITIZED_CWD/memory"

echo "===== QA Doctrine — Memory Seed Bootstrap ====="
echo
echo "Pack:        $PACK_DIR"
echo "Memory dir:  $MEM_DIR"
echo

# Confirm before writing
if [ -d "$MEM_DIR" ] && [ -f "$MEM_DIR/MEMORY.md" ]; then
  echo "⚠️  Existing MEMORY.md found at $MEM_DIR/MEMORY.md"
  echo "    Backing up existing memory dir to $MEM_DIR.bak.$(date +%s) before seeding."
  cp -r "$MEM_DIR" "$MEM_DIR.bak.$(date +%s)"
fi

mkdir -p "$MEM_DIR"

# 1. Write MEMORY.md from template (or skip if exists; we want preserve user data)
if [ ! -f "$MEM_DIR/MEMORY.md" ]; then
  cp "$PACK_DIR/03-memory-seed/MEMORY.md.template" "$MEM_DIR/MEMORY.md"
  TODAY=$(date +%Y-%m-%d)
  sed -i "s/YYYY-MM-DD/$TODAY/g" "$MEM_DIR/MEMORY.md"
  echo "✓ Wrote $MEM_DIR/MEMORY.md (from template, today's date)"
else
  echo "ℹ Existing MEMORY.md preserved. You may need to manually add the doctrine pointer:"
  echo "    - [QA Doctrine — Master Tester + composers](feedback-master-tester.md) — adopted $(date +%Y-%m-%d); strategic frame + tactical stack"
fi

# 2. Drop the doctrine memory (verbatim from this pack)
cp "$PACK_DIR/03-memory-seed/feedback-master-tester.md" "$MEM_DIR/feedback-master-tester.md"
echo "✓ Wrote $MEM_DIR/feedback-master-tester.md (the durable doctrine)"

# 3. Verify
echo
echo "===== Verification ====="
ls -la "$MEM_DIR"
echo
echo "MEMORY.md (first 20 lines):"
head -20 "$MEM_DIR/MEMORY.md"
echo
echo "✓ Memory seed complete."
echo
echo "Next steps:"
echo "  1. Edit $MEM_DIR/MEMORY.md — add your active project pointer."
echo "  2. For each active project, copy 03-memory-seed/project-pointer.template.md to"
echo "     $MEM_DIR/<your-project-slug>.md and replace the placeholders."
echo "  3. Open Claude Code in any directory. Run the 5-prompt verification (09-VERIFICATION.md)."

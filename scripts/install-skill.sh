#!/usr/bin/env bash
# install-skill.sh — install the telegram-bridge skill for DeepSeek TUI
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_DIR="${DEEPSEEK_HOME:-$HOME/.deepseek}/skills/telegram-bridge"

echo "=== Installing telegram-bridge skill ==="
echo "Target: $SKILL_DIR"

mkdir -p "$SKILL_DIR/references"

cp "$SCRIPT_DIR/skill/SKILL.md" "$SKILL_DIR/SKILL.md"
cp "$SCRIPT_DIR/skill/references/bridge-architecture.md" "$SKILL_DIR/references/bridge-architecture.md"
cp "$SCRIPT_DIR/skill/references/troubleshooting.md" "$SKILL_DIR/references/troubleshooting.md"
cp "$SCRIPT_DIR/scripts/status.sh" "$SKILL_DIR/scripts/status.sh" 2>/dev/null || true
mkdir -p "$SKILL_DIR/scripts" 2>/dev/null || true
cp "$SCRIPT_DIR/scripts/status.sh" "$SKILL_DIR/scripts/status.sh" 2>/dev/null || true
chmod +x "$SKILL_DIR/scripts/status.sh" 2>/dev/null || true

echo ""
echo "Skill installed. DeepSeek TUI will discover it on next startup."
echo "Test: ls -la $SKILL_DIR/"
echo ""
echo "The skill triggers when you ask DeepSeek TUI to:"
echo "  - Check bridge status"
echo "  - Restart the bridge service"
echo "  - View bridge logs"
echo "  - Manage Telegram sessions"
echo "  - Troubleshoot bridge issues"

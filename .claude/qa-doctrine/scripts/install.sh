#!/usr/bin/env bash
#
# QA Doctrine — one-shot installer
#
# Layers applied:
#   1. Plugins (claude plugin install)
#   2. Custom skills (cp to ~/.claude/skills/)
#   3. Memory seed (delegates to seed-memory.sh)
#
# Layer 4 (settings) is NOT auto-applied because settings.json should
# be merged carefully. The script prints the template for manual merge.
#
# Usage: bash scripts/install.sh
#

set -euo pipefail

PACK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$HOME/.claude/skills"

echo "===== QA Doctrine — One-Shot Installer ====="
echo
echo "Pack:    $PACK_DIR"
echo
echo "This script will:"
echo "  1. Install plugins (claude plugin install)"
echo "  2. Copy custom skills to $SKILLS_DIR"
echo "  3. Seed auto-memory (~/.claude/projects/.../memory/)"
echo
echo "It will NOT modify ~/.claude/settings.local.json — see 04-settings/SETTINGS-GUIDE.md for manual merge."
echo
read -p "Proceed? [y/N] " -n 1 -r
echo
[[ ! $REPLY =~ ^[Yy]$ ]] && { echo "Cancelled."; exit 1; }

# ===== Layer 1: plugins =====
echo
echo "===== Layer 1: Plugins ====="
PLUGINS=(
  "superpowers@claude-plugins-official"
  "pr-review-toolkit@claude-plugins-official"
  "feature-dev@claude-plugins-official"
  "code-review@claude-plugins-official"
  "claude-code-setup@claude-plugins-official"
  "claude-md-management@claude-plugins-official"
)
if command -v claude >/dev/null 2>&1; then
  for plugin in "${PLUGINS[@]}"; do
    echo "→ claude plugin install $plugin"
    claude plugin install "$plugin" || echo "  (already installed or error — continuing)"
  done
else
  echo "⚠ Claude CLI not found on PATH. Skipping plugin install."
  echo "  Install plugins manually with the following commands:"
  for plugin in "${PLUGINS[@]}"; do
    echo "    claude plugin install $plugin"
  done
fi

# ===== Layer 2: custom skills =====
echo
echo "===== Layer 2: Custom Skills ====="
mkdir -p "$SKILLS_DIR"
for skill in master-tester-doctrine security-review confidence-check; do
  if [ -d "$SKILLS_DIR/$skill" ]; then
    BACKUP="$SKILLS_DIR/$skill.bak.$(date +%s)"
    echo "ℹ Existing $skill backed up to $BACKUP"
    mv "$SKILLS_DIR/$skill" "$BACKUP"
  fi
  cp -r "$PACK_DIR/02-skills/$skill" "$SKILLS_DIR/$skill"
  echo "✓ Installed $SKILLS_DIR/$skill"
done

# ===== Layer 3: memory seed =====
echo
echo "===== Layer 3: Memory Seed ====="
bash "$PACK_DIR/scripts/seed-memory.sh"

# ===== Done =====
echo
echo "================================================================"
echo "Install complete. Remaining manual steps:"
echo "================================================================"
echo
echo "1. SETTINGS (Layer 4) — merge into ~/.claude/settings.local.json"
echo "   See: $PACK_DIR/04-settings/SETTINGS-GUIDE.md"
echo "   Template: $PACK_DIR/04-settings/settings.local.json.template"
echo
echo "2. PROJECT SEED (Layer 5) — for each active project, see"
echo "   $PACK_DIR/05-project-seed/audit-dir-structure.md"
echo
echo "3. VERIFICATION — open a fresh Claude Code session and run the"
echo "   5-prompt test in $PACK_DIR/09-VERIFICATION.md"
echo
echo "If 4/5 or 5/5 prompts route correctly, deployment is reproducible."
echo "If below 4/5, see Failure Mode Triage in 09-VERIFICATION.md."

#!/usr/bin/env bash
# watchdog.sh — DeepSeek Telegram Bridge health check & auto-restart
# Triggered by cron: @reboot + */5 * * * *
set -euo pipefail

PROJECT_DIR="$HOME/projects/deepseek-telegram-bridge"
LOG_FILE="$PROJECT_DIR/watchdog.log"
BRIDGE_LOG="$PROJECT_DIR/bridge.log"
VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
}

# Check if bridge process is already running
if pgrep -f "python.*src\.bridge" > /dev/null 2>&1; then
    # Bridge is alive — nothing to do
    exit 0
fi

log "Bridge not running. Starting..."

# Verify dependencies exist
if [ ! -f "$VENV_PYTHON" ]; then
    log "ERROR: Python venv not found at $VENV_PYTHON"
    exit 1
fi

if [ ! -f "$PROJECT_DIR/src/bridge.py" ]; then
    log "ERROR: bridge.py not found at $PROJECT_DIR/src/bridge.py"
    exit 1
fi

# Start bridge in background, detached from cron
cd "$PROJECT_DIR"
nohup "$VENV_PYTHON" -m src.bridge >> "$BRIDGE_LOG" 2>&1 &
BRIDGE_PID=$!

log "Bridge started with PID=$BRIDGE_PID"

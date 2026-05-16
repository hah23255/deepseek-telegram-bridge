#!/usr/bin/env bash
# status.sh — one-command bridge health check
set -euo pipefail

echo "=== DeepSeek Telegram Bridge Status ==="
echo ""

# Service status
echo "--- systemd service ---"
if systemctl --user is-active --quiet deepseek-telegram-bridge.service 2>/dev/null; then
    echo "Service: RUNNING"
else
    echo "Service: STOPPED"
fi
systemctl --user status deepseek-telegram-bridge.service 2>&1 | grep -E "Active:|Main PID:|Memory:" | sed 's/^/  /'

# Bridge log tail
echo ""
echo "--- Recent bridge log (last 10 lines) ---"
LOG="$HOME/projects/deepseek-telegram-bridge/bridge.log"
if [ -f "$LOG" ]; then
    tail -10 "$LOG" | sed 's/^/  /'
else
    echo "  (no bridge.log found)"
fi

# Active sessions
echo ""
echo "--- Active sessions ---"
STATE="$HOME/projects/deepseek-telegram-bridge/state.json"
if [ -f "$STATE" ]; then
    python3 -c "
import json
state = json.load(open('$STATE'))
sessions = state.get('sessions', {})
if sessions:
    for chat_id, sid in sessions.items():
        print(f'  Chat {chat_id}: {sid[:12]}...')
else:
    print('  (no active sessions)')
" 2>/dev/null || cat "$STATE" | python3 -m json.tool 2>/dev/null | grep -A5 sessions || echo "  (could not parse state.json)"
else
    echo "  (no state.json)"
fi

# Binary check
echo ""
echo "--- deepseek-tui ---"
deepseek-tui --version 2>&1 | head -1 | sed 's/^/  /'

echo ""
echo "--- Telegram bot ---"
echo "  t.me/Deepseek_cli_bot"

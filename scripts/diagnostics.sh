#!/usr/bin/env bash
# diagnostics.sh - comprehensive health + error check for deepseek-telegram-bridge
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass()  { echo -e "  ${GREEN}[PASS]${NC} $1"; }
fail()  { echo -e "  ${RED}[FAIL]${NC} $1"; }
warn()  { echo -e "  ${YELLOW}[WARN]${NC} $1"; }
check() { echo -e "\n${1}:"; }

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

check "Python"
if command -v python3 &>/dev/null; then
    pass "python3: $(python3 --version)"
else
    fail "python3 not found"
fi

check "deepseek-tui"
if command -v deepseek-tui &>/dev/null; then
    pass "deepseek-tui: $(deepseek-tui --version 2>&1 | head -1)"
else
    fail "deepseek-tui not on PATH"
fi

check "httpx"
if python3 -c "import httpx" 2>/dev/null; then
    pass "httpx installed"
else
    warn "httpx not installed (run: pip install httpx[http2])"
fi

check "Config"
if [ -f "$SCRIPT_DIR/config/config.json" ]; then
    token=$(python3 -c "import json; print(json.load(open('$SCRIPT_DIR/config/config.json'))['telegram']['bot_token'])" 2>/dev/null || echo "")
    if [ -n "$token" ] && [ "$token" != "YOUR_BOT_TOKEN_HERE" ]; then
        pass "config.json: valid, token set"
    else
        warn "config.json: token not set"
    fi
else
    warn "config.json: not found (copy from config.example.json)"
fi

check "systemd service"
if systemctl --user is-active --quiet deepseek-telegram-bridge.service 2>/dev/null; then
    pass "service: running"
elif systemctl --user is-failed --quiet deepseek-telegram-bridge.service 2>/dev/null; then
    fail "service: FAILED"
else
    warn "service: not running"
fi

check "Telegram API"
if [ -f "$SCRIPT_DIR/config/config.json" ]; then
    token=$(python3 -c "import json; print(json.load(open('$SCRIPT_DIR/config/config.json'))['telegram']['bot_token'])" 2>/dev/null || echo "")
    if [ -n "$token" ] && [ "$token" != "YOUR_BOT_TOKEN_HERE" ]; then
        resp=$(curl -s --connect-timeout 5 "https://api.telegram.org/bot${token}/getMe" 2>/dev/null || echo "")
        if echo "$resp" | python3 -c "import json,sys; d=json.load(sys.stdin); exit(0 if d.get('ok') else 1)" 2>/dev/null; then
            botname=$(echo "$resp" | python3 -c "import json,sys; print(json.load(sys.stdin)['result']['username'])" 2>/dev/null)
            pass "Telegram API: connected (@$botname)"
        else
            fail "Telegram API: invalid token or network error"
        fi
    fi
fi

check "Network"
if curl -s --connect-timeout 5 https://api.telegram.org >/dev/null 2>&1; then
    pass "api.telegram.org: reachable"
else
    fail "api.telegram.org: unreachable"
fi

echo ""
echo "=== Summary ==="
echo "Status: bash $SCRIPT_DIR/scripts/status.sh"
echo "Logs: journalctl --user -u deepseek-telegram-bridge.service -f"

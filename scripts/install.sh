#!/usr/bin/env bash
# install.sh — DeepSeek Telegram Bridge quick setup
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== DeepSeek Telegram Bridge — Install ==="
echo ""

# --- Python / venv ---
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found. Install Python 3.11+ first."
    exit 1
fi
PY="$(command -v python3)"
echo "Python: $PY ($($PY --version))"

if [ ! -d .venv ]; then
    echo "Creating virtual environment..."
    $PY -m venv .venv
fi
source .venv/bin/activate
pip install -q "httpx[http2]>=0.28.0"
echo "Dependencies: OK"

# --- deepseek-tui ---
if ! command -v deepseek-tui &>/dev/null; then
    echo "WARNING: deepseek-tui not found on PATH"
    echo "  Install with: npm install -g deepseek-tui --prefix ~/.local"
else
    echo "deepseek-tui: $(deepseek-tui --version 2>&1 | head -1)"
fi

# --- Config ---
if [ ! -f config.json ]; then
    cp config.example.json config.json
    chmod 600 config.json
    echo ""
    echo "Config created at config.json (permissions: 600)"
    echo ">>> Edit config.json now to set your bot_token and allowed_user_ids <<<"
else
    echo "config.json already exists (skipping)"
fi

# --- systemd unit ---
UNIT_NAME="deepseek-telegram-bridge.service"
UNIT_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
UNIT_FILE="$UNIT_DIR/$UNIT_NAME"

mkdir -p "$UNIT_DIR"

cat > "$UNIT_FILE" <<'SERVICEUNIT'
[Unit]
Description=DeepSeek TUI Telegram Bridge
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=__VENV__/bin/python -m src.bridge
WorkingDirectory=__PROJECT_DIR__
Restart=on-failure
RestartSec=10
TimeoutStopSec=30

# Security hardening
PrivateTmp=yes
UMask=0077
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=__PROJECT_DIR__
ReadWritePaths=__HOME__/.deepseek
NoNewPrivileges=yes
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
SystemCallFilter=@system-service ~@privileged ~@resources
ProtectKernelTunables=yes
ProtectKernelModules=yes
LockPersonality=yes

[Install]
WantedBy=default.target
SERVICEUNIT

# Fill in absolute paths
sed -i "s|__VENV__|$SCRIPT_DIR/.venv|g" "$UNIT_FILE"
sed -i "s|__PROJECT_DIR__|$SCRIPT_DIR|g" "$UNIT_FILE"
sed -i "s|__HOME__|$HOME|g" "$UNIT_FILE"

systemctl --user daemon-reload
echo ""
echo "systemd unit installed: $UNIT_FILE"
echo ""
echo "=== Next steps ==="
echo "1. Edit config.json with your bot token and Telegram user ID"
echo "2. systemctl --user start $UNIT_NAME"
echo "3. systemctl --user status $UNIT_NAME"
echo "4. Send a message to your bot on Telegram"
echo ""
echo "Logs: journalctl --user -u $UNIT_NAME -f"
echo "Bridge log: $SCRIPT_DIR/bridge.log"

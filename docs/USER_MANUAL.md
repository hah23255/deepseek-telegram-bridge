# DeepSeek Telegram Bridge — User Manual

## Overview

This bridge connects your Telegram account to a local DeepSeek TUI instance.
You send messages in Telegram; the bridge forwards them to deepseek-tui,
captures the response, and sends it back to Telegram.

## Getting Your Telegram Bot Token

1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow prompts
3. Copy the token (looks like `123456:ABCdef...`)

## Getting Your Telegram User ID

1. Message [@userinfobot](https://t.me/userinfobot)
2. It replies with your numeric ID (e.g. `8145172607`)

## Telegram Commands

All commands start with `/`:

| Command | What it does |
|---------|-------------|
| `/start` | Welcome message |
| `/help` | Show all commands |
| `/new` | Start a fresh session (forgets context) |
| `/status` | Show current session status |
| `/model v4-pro` | Switch to deepseek-v4-pro (full quality) |
| `/model v4-flash` | Switch to deepseek-v4-flash (fast) |
| `/reasoning low` | Minimal thinking (fastest) |
| `/reasoning medium` | Balanced thinking |
| `/reasoning high` | Deep reasoning (slowest) |
| `/reasoning auto` | Default behavior |
| `/agent on` | Enable tools (write files, run shell, git) |
| `/agent off` | Disable tools (fast chat only) |

## Typical Workflow

1. Start chatting: just send any message
2. Continue a conversation: send follow-up messages (context preserved)
3. Switch model: `/model v4-pro` for complex tasks
4. Enable tools: `/agent on` then "edit README.md to add..."
5. Fresh start: `/new` clears context
6. Check status: `/status`

## Agent Mode

When agent mode is ON (`/agent on`), DeepSeek TUI can:
- Read and write files in your workspace
- Run shell commands
- Use git
- Manage sub-agents

**Warning**: Agent mode is powerful. Only use it in workspaces you trust.
The bridge runs with the same permissions as your user account.

Response times in agent mode are longer (1-5 minutes for complex tasks)
because the model can chain multiple tool calls.

## Managing the Bridge

### Check status
```bash
bash scripts/status.sh
```

### View logs
```bash
tail -f bridge.log
journalctl --user -u deepseek-telegram-bridge.service -f
```

### Restart
```bash
systemctl --user restart deepseek-telegram-bridge.service
```

### Stop
```bash
systemctl --user stop deepseek-telegram-bridge.service
```

## Troubleshooting

### Bot doesn't reply
1. Check service: `systemctl --user status deepseek-telegram-bridge.service`
2. Check logs: `tail -20 bridge.log`
3. Verify token: config/config.json has correct bot_token
4. Verify user ID: your Telegram ID is in allowed_user_ids
5. Test deepseek-tui: `deepseek-tui exec --json "test"`

### Responses are slow
- Agent mode (`/agent on`) is slower than chat mode
- v4-pro is slower than v4-flash
- Large session contexts increase response time
- Use `/new` to clear context and `/agent off` for fast chat

### 409 Conflict error
- Another process is polling the same bot token
- Stop all instances, start only one
- Check: `ps aux | grep bridge.py`

### Token expired
- Bot tokens don't expire, but can be revoked
- Regenerate via @BotFather if needed
- Update config.json and restart

## Security

- Only authorized Telegram users can message the bot
- Bot runs locally — no cloud component
- Long-polling (no exposed ports)
- systemd hardened: PrivateTmp, ProtectSystem, NoNewPrivileges
- Bot token never appears in logs

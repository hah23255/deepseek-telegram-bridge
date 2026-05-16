---
name: telegram-bridge
description: Manage and operate the DeepSeek TUI Telegram bridge — a systemd daemon that connects Telegram to deepseek-tui exec for remote session control. Use when checking bridge status, restarting the service, managing Telegram sessions, configuring the bridge, viewing logs, troubleshooting, or extending the bridge with new features. Covers: status checks, session management (/new, /status), service control (start/stop/restart), config editing, log inspection, user allowlist management, and bridge extension.
---

# Telegram Bridge Manager

Manage the `deepseek-telegram-bridge` — a Python daemon that bridges Telegram
messages to `deepseek-tui exec` subprocesses with full session continuity.

## Quick Reference

- **Project**: `~/projects/deepseek-telegram-bridge/`
- **Service**: `systemctl --user <cmd> deepseek-telegram-bridge.service`
- **Config**: `~/projects/deepseek-telegram-bridge/config.json`
- **State**: `~/projects/deepseek-telegram-bridge/state.json`
- **Logs**: `journalctl --user -u deepseek-telegram-bridge.service`
- **Bridge log**: `~/projects/deepseek-telegram-bridge/bridge.log`
- **Telegram bot**: [t.me/Deepseek_cli_bot](https://t.me/Deepseek_cli_bot)

## Status Check

To check if the bridge is running and healthy:

```bash
systemctl --user status deepseek-telegram-bridge.service
```

Read the bridge log for recent activity:

```bash
tail -40 ~/projects/deepseek-telegram-bridge/bridge.log
```

Check what sessions are active by reading state:

```bash
cat ~/projects/deepseek-telegram-bridge/state.json
```

The `sessions` object maps Telegram chat IDs to DeepSeek TUI session UUIDs.
`offset` is the Telegram update polling watermark.

## Service Control

```bash
systemctl --user start deepseek-telegram-bridge.service
systemctl --user stop deepseek-telegram-bridge.service
systemctl --user restart deepseek-telegram-bridge.service
```

After config changes, restart is required:

```bash
systemctl --user restart deepseek-telegram-bridge.service
```

## Configuration

Edit `~/projects/deepseek-telegram-bridge/config.json`:

- `telegram.bot_token` — Telegram bot token (required)
- `telegram.allowed_user_ids` — list of Telegram user IDs. Empty = allow all. Non-empty = only listed IDs.
- `telegram.allowed_chat_ids` — optional chat-level allowlist. `null` = allow all chats from allowed users.
- `deepseek.binary` — path to `deepseek-tui` (default: `deepseek-tui`)
- `deepseek.working_dir` — workspace directory (default: current dir)
- `deepseek.model` — model override (default: null, uses config default)
- `deepseek.approval_mode` — always `yolo` for unattended operation
- `deepseek.timeout_ms` — hard timeout in ms (default: 600000 = 10 min)

### Adding a user to the allowlist

1. Get their Telegram user ID (they message [@userinfobot](https://t.me/userinfobot))
2. Edit `config.json` — add the ID to `allowed_user_ids`
3. Restart: `systemctl --user restart deepseek-telegram-bridge.service`

## Session Management

Sessions are managed **automatically** via DeepSeek TUI's native checkpoint system.
The bridge always uses `--continue` to pick up the latest session in the workspace.

**To start a fresh session in Telegram:**
Send `/new` — this runs `deepseek-tui exec --fresh` to create a new checkpoint.

**To see active sessions on the host:**
```bash
deepseek sessions
ls ~/.deepseek/sessions/checkpoints/
```

No manual session tracking is needed — DeepSeek TUI handles continuity natively.

## Viewing Logs

```bash
# systemd journal (live)
journalctl --user -u deepseek-telegram-bridge.service -f

# systemd journal (recent)
journalctl --user -u deepseek-telegram-bridge.service --since "10 min ago"

# Bridge log file
tail -100 ~/projects/deepseek-telegram-bridge/bridge.log
```

Key log events to watch:
- `Blocked user` — unauthorized user attempted to message the bot
- `Spawning:` — a `deepseek-tui exec` command was dispatched
- `stderr:` — DeepSeek TUI produced stderr output
- `Telegram API error` — API call failed

## Telegram Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/help` | Show all commands |
| `/new` | Start a fresh session |
| `/status` | Show session status |
| `/model <v4-pro\|v4-flash>` | Switch model per chat |
| `/reasoning <auto\|low\|medium\|high>` | Set reasoning effort |
| `/agent <on\|off>` | Toggle agent mode (tools: write, edit, shell, git) |

Defaults: `deepseek-v4-flash`, reasoning `auto`, agent OFF.

## Bridge Architecture

For detailed internals, see [references/bridge-architecture.md](references/bridge-architecture.md).

Quick summary:
1. Bridge long-polls Telegram `getUpdates` API
2. On message: spawns `deepseek-tui exec --json [--auto] [--model ...] --fresh | --continue "<prompt>"`
3. Agent mode (`--auto`) toggled per chat via `/agent` — enables write/edit/shell/git
4. Model and reasoning configurable per chat via `/model` and `/reasoning`
5. Sends formatted reply via Telegram `sendMessage` (split at 4000 chars)
6. Typing indicator refreshes every 4 seconds during processing

## Extending the Bridge

The bridge source is at `~/projects/deepseek-telegram-bridge/src/bridge.py` (~560 LOC Python).

**Adding a new slash command:** edit `handle_command()` in `bridge.py`. Add a new
`elif cmd == "/yourcommand":` block. Restart the service.

**Changing the subprocess invocation:** edit `build_command()` in `bridge.py`.
The `--auto` flag enables agentic mode. To disable tool access, remove `--auto`.

**Adding file delivery or cron:** the bridge currently only supports text.
For richer features (file sending, scheduled tasks, multi-bot), consider
adapting [cc-telegram-bridge](https://github.com/cloveric/cc-telegram-bridge)
which has a full control plane.

## Troubleshooting

See [references/troubleshooting.md](references/troubleshooting.md) for a full guide.

Quick checks:
1. `systemctl --user status deepseek-telegram-bridge.service` — is it running?
2. `deepseek-tui --version` — is the binary accessible?
3. `cat ~/projects/deepseek-telegram-bridge/config.json` — is the token valid?
4. `tail -20 ~/projects/deepseek-telegram-bridge/bridge.log` — any errors?

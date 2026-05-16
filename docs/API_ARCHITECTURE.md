# DeepSeek Telegram Bridge — API & Architecture

## Data Flow

```
User (Telegram)
    |
    | message
    v
Telegram Bot API (getUpdates long-poll)
    |
    | JSON update
    v
Bridge Daemon (Python asyncio)
    |
    | spawn subprocess
    v
deepseek-tui exec --json [--auto] [--model X] --fresh|--continue "prompt"
    |
    | JSON stdout
    v
Bridge parses {"output": "...", "error": null}
    |
    | sendMessage
    v
User receives reply on Telegram
```

## Module Layout

```
deepseek-telegram-bridge-pack/
├── src/
│   └── bridge.py              # Main daemon (~500 LOC)
├── config/
│   └── config.example.json    # Configuration template
├── scripts/
│   ├── install.sh             # Setup: venv, deps, systemd unit
│   └── status.sh              # Health check
├── docs/
│   ├── USER_MANUAL.md         # End-user documentation
│   └── API_ARCHITECTURE.md    # This file
├── requirements.txt           # httpx[http2]
└── README.md
```

## Runtime State

```
state.json:
{
    "sessions": {"<chat_id>": true},       // active chats
    "chat_settings": {
        "<chat_id>": {
            "model": "deepseek-v4-pro",    // per-chat model override
            "reasoning": "high",            // per-chat reasoning effort
            "agent": true                   // agent mode toggle
        }
    },
    "offset": 867133172                    // Telegram poll watermark
}
```

## Configuration Schema

```json
{
    "telegram": {
        "bot_token": "string (required)",
        "allowed_user_ids": [123456789],
        "allowed_chat_ids": null
    },
    "deepseek": {
        "binary": "deepseek-tui",
        "working_dir": "/home/user",
        "model": "deepseek-v4-flash",
        "approval_mode": "yolo",
        "timeout_ms": 600000
    }
}
```

## Subprocess Invocation

### Chat mode (default)
```
deepseek-tui exec --json --model deepseek-v4-flash --continue "user prompt"
```

### Agent mode (/agent on)
```
deepseek-tui exec --auto --json --model deepseek-v4-flash --continue "user prompt"
```

### Fresh session (/new or first message)
```
deepseek-tui exec --json --model deepseek-v4-flash --fresh "user prompt"
```

## Output Format

DeepSeek TUI --json output:
```json
{
    "mode": "one-shot",
    "model": "deepseek-v4-flash",
    "success": true,
    "output": "response text here",
    "status": "completed",
    "error": null
}
```

With --auto (agent mode):
```json
{
    "mode": "agent",
    "model": "deepseek-v4-flash",
    "prompt": "user prompt",
    "output": "response text",
    "tools": [
        {"name": "exec_shell", "success": true, "output": "..."}
    ],
    "status": "completed",
    "error": null
}
```

## Extension Points

### Adding a new slash command
1. Edit `src/bridge.py`
2. Add `elif cmd == "/yourcommand":` block in `handle_command()`
3. Restart: `systemctl --user restart deepseek-telegram-bridge.service`

### Adding file delivery
Extend `handle_message()` to parse tool-call markers in output
and call Telegram's `sendDocument` API.

### Adding cron/scheduled tasks
Add a background asyncio task in `main()` that checks scheduled jobs
and fires prompts at the configured times.

### Multi-bot support
Load config per instance (instance name → separate config/state files).
The cc-telegram-bridge project (github.com/cloveric/cc-telegram-bridge)
is a production-grade reference for multi-bot orchestration.

### Non-systemd deployment
Replace the systemd unit with:
- macOS: launchd plist in ~/Library/LaunchAgents/
- Windows: NSSM or Task Scheduler
- Generic: screen/tmux session, supervisor, or pm2

## Error Handling

The bridge handles these error classes:

| Error | Handling |
|-------|----------|
| Telegram API 404 | Invalid token → log error, retry poll |
| Telegram API 409 | Duplicate polling → log error, retry poll |
| Telegram API 429 | Rate limit → log error, retry with backoff |
| Subprocess timeout | Kill process, return timeout error to user |
| Subprocess crash | Capture stderr, return error to user |
| Config missing | Exit with clear message |
| Binary not found | Exit with install instructions |
| JSON parse failure | Return raw output or error message |

## Performance Tuning

| Scenario | Recommendation |
|----------|---------------|
| Slow responses | `/model v4-flash`, `/reasoning low` |
| Large context | `/new` to reset session |
| Heavy agent work | Increase `timeout_ms` in config |
| Multiple users | Keep `allowed_user_ids` tight |
| Memory pressure | Restart periodically (systemd handles this) |

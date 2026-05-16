# Bridge Architecture

## Overview

```
┌─────────────┐     long-poll      ┌──────────────────┐     subprocess      ┌──────────────────┐
│  Telegram   │ ◄──────────────► │  Bridge Daemon    │ ─────────────────► │  deepseek-tui    │
│  Bot API    │    getUpdates     │  (Python asyncio) │                    │  exec --auto      │
│             │ ◄─────────────── │                    │ ◄───────────────── │  --stream-json    │
│             │    sendMessage    │  ~560 LOC          │   NDJSON stdout    │  --resume <sid>   │
└─────────────┘                   └──────────────────┘                    └──────────────────┘
                                         │   ▲
                                         ▼   │
                                  ┌──────────────┐
                                  │  state.json   │
                                  │  config.json  │
                                  │  bridge.log   │
                                  └──────────────┘
```

## Module Layout

```
~/projects/deepseek-telegram-bridge/
├── src/
│   ├── __init__.py
│   └── bridge.py          # Main daemon (560 LOC)
├── config.example.json     # Configuration template
├── config.json             # Active configuration (gitignored)
├── state.json              # Session store + poll offset
├── bridge.log              # Application log
├── requirements.txt        # httpx[http2]
├── install.sh              # Setup script
├── README.md
└── .gitignore
```

## Data Flow (per message)

1. **Poll**: Bridge calls `getUpdates` with `offset` watermark every 30s
2. **Auth**: Checks `user_id` against `allowed_user_ids`; `chat_id` against `allowed_chat_ids`
3. **Session**: Uses `--continue` (native checkpoint continuity) or `--fresh` (new session)
4. **Spawn**: `deepseek-tui exec --json [--auto] [--model ...] --continue "<prompt>"`
   - `--auto` is controlled per chat via `/agent on|off` in `chat_settings`
   - Model is resolved: per-chat override → config default → deepseek-tui default
5. **Parse**: Reads plain JSON from stdout:
   - `{"output": "...", "status": "completed", "error": null}`
6. **Reply**: Sends `output` text via `sendMessage` (split at 4000 chars)

## Timeouts and Heartbeats

| Event | Interval |
|-------|----------|
| Typing indicator refresh | Every 4 seconds |
| DeepSeek TUI hard timeout | 600 seconds (10 min, configurable) |
| Telegram poll timeout | 30 seconds (Telegram long-poll) |

## Security Model

- **Default-deny**: empty `allowed_user_ids` = allow all. Non-empty = only listed.
- **Chat-level filtering**: `allowed_chat_ids` restricts to specific Telegram chats.
- **No ports exposed**: long-polling only, no webhook server.
- **systemd hardening**: `PrivateTmp`, `UMask=0077`, `ProtectSystem=strict`, `ProtectHome=read-only`, `NoNewPrivileges=yes`, restricted syscall filter.
- **Token secrecy**: httpx INFO logs suppressed so bot token never appears in bridge.log.

## Session Lifecycle

```
Chat starts ──► first message ──► --continue (latest checkpoint)
                                       │
                              next message ──► --continue (same checkpoint)
                                       │
                              /new command ──► --fresh (new checkpoint)

All session management is handled by DeepSeek TUI's native checkpoint system.
The bridge does not track sessions — it just uses --continue for continuity
and --fresh for new sessions.
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
        "working_dir": "/home/i",
        "model": null,
        "approval_mode": "yolo",
        "timeout_ms": 600000
    }
}
```

## Extension Points

| Location | What to modify |
|----------|---------------|
| `handle_command()` | Add new slash commands |
| `build_command()` | Change subprocess flags |
| `run_deepseek()` | Change output parsing |
| `handle_message()` | Add message preprocessing |
| `poll_loop()` | Add update types (e.g., voice, files) |

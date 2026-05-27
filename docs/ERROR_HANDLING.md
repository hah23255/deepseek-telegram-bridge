# Error Handling Guide — deepseek-telegram-bridge

Catalog of errors the bridge encounters, their causes, and how the code handles each.

---

## Telegram Bot API Errors

### HTTP 400 — Bad Request

**Causes:** malformed payload, chat not found, message too long (>4096 chars).

**Bridge behaviour:** `tg_call` raises `httpx.HTTPStatusError`. The per-message
handler catches at the outer boundary (`except Exception` at `bridge.py:304`) and
sends a `⚠️ Bridge error:` reply.

**Prevention:** `send_message` splits text at 4000 chars via `_split_text`.

### HTTP 403 — Bot Blocked / Kicked

**Causes:** user blocked the bot or bot was removed from a group.

**Bridge behaviour:** `tg_call` raises; outer handler logs and replies. Subsequent
messages from that chat will also fail until the user unblocks.

### HTTP 429 — Too Many Requests

**Causes:** Telegram rate-limiting (burst of messages or typing actions).

**Bridge behaviour:** `send_typing` is best-effort — failure is swallowed with a
`log.debug` (the `# noqa: BLE001` site at `bridge.py:135`). `send_message` failures
propagate to the outer handler.

### HTTP 5xx — Telegram Server Error

**Causes:** Telegram outage or maintenance.

**Bridge behaviour:** `poll_loop` catches `httpx.HTTPError`, logs at ERROR level,
and retries after 5 seconds.

---

## DeepSeek TUI Errors

### Process Timeout

**Causes:** DeepSeek model taking longer than `timeout_ms` (default 600 s).

**Bridge behaviour:** `proc.kill()` is called, then `proc.communicate()` drains
remaining output. `error_msg` is set to `"DeepSeek TUI timed out after Ns"` and
surfaced to the user as `⚠️ DeepSeek TUI timed out after Ns`.

### Non-zero Exit Code

**Causes:** model error, authentication failure, binary crash.

**Bridge behaviour:** stdout is parsed; if `result["error"]` is set, it is surfaced
to the user. If stdout is empty or unparseable, `"(empty response)"` is returned.

### Malformed JSON Output

**Causes:** partial output before crash, binary printing debug text.

**Bridge behaviour:** `json.JSONDecodeError` is caught; `result` defaults to `{}`.
`output` and `error` fields default to empty/None. Caller returns `"(empty response)"`.

### Cleanup Failure After Kill

**Causes:** process already exited, OS-level race on `proc.kill()`.

**Bridge behaviour:** `ProcessLookupError` and `OSError` are caught at the cleanup
site (`bridge.py:222-225`) with `log.debug`. This is the Adaptive Fault Tolerance
pattern — cleanup is best-effort.

---

## Network Errors

### `httpx.ConnectError` / `httpx.ReadTimeout`

**Causes:** transient network failure, firewall drop, Telegram maintenance.

**Bridge behaviour:** poll loop catches `httpx.HTTPError`, logs at ERROR, retries
after 5 s. The `httpx.AsyncClient` is configured with `http2=True` and a global
60 s timeout; the `getUpdates` long-poll uses a 45 s request timeout.

### HTTP/2 Connection Stall

**Causes:** persistent HTTP/2 connections can stall when the upstream drops the
connection without a proper close frame.

**Bridge behaviour:** a 5 s `client-level` timeout was added in `b8142b8` to
prevent indefinite stalls on `sendChatAction`. See `send_typing`.

---

## Startup Errors

### `deepseek-tui` not on PATH

**Causes:** binary not installed or wrong `binary` config key.

**Bridge behaviour:** `FileNotFoundError` is caught at startup (`main()`), logged at
ERROR, and the process exits with code 1.

### Missing `config.json`

**Causes:** file not created from `config.example.json`.

**Bridge behaviour:** `load_config()` prints a helpful message to stderr and exits 1.

### Missing `telegram.bot_token`

**Causes:** config.json exists but the token field is empty.

**Bridge behaviour:** `load_config()` raises `ValueError("telegram.bot_token is required")`.

---

## Error Code Reference

| Telegram HTTP code | Meaning | Bridge response |
|---|---|---|
| 400 | Bad request / chat not found | Outer handler catches, logs, replies |
| 401 | Invalid token | Poll loop logs HTTP error, retries |
| 403 | Bot blocked by user | Outer handler catches, logs |
| 429 | Rate limited | `send_typing` degrades; `send_message` retries via outer handler |
| 5xx | Server error | Poll loop logs, retries after 5 s |

| DeepSeek exit code | Meaning |
|---|---|
| 0 | Success |
| non-zero | Error — `result["error"]` field surfaced to user |
| timeout | `proc.kill()` triggered; timeout message sent |

# Troubleshooting

## Diagnostic Order

When the bridge is not responding, check in this order:

1. Service status
2. Bridge logs
3. Config validity
4. Binary accessibility
5. Telegram API status

## 1. Service Status

```bash
systemctl --user status deepseek-telegram-bridge.service
```

**Expected**: `Active: active (running)`. If `failed` or `inactive`:

```bash
# Check why it failed
journalctl --user -u deepseek-telegram-bridge.service --since "5 min ago"

# Restart
systemctl --user restart deepseek-telegram-bridge.service
```

## 2. Bridge Logs

```bash
tail -40 ~/projects/deepseek-telegram-bridge/bridge.log
```

### Common log patterns

| Log line | Meaning | Action |
|----------|---------|--------|
| `Blocked user` | Unauthorized user | Add their ID to `allowed_user_ids` |
| `Telegram API error: 404` | Invalid bot token | Check `config.json` token |
| `Telegram API error: 409` | Duplicate polling | Another process is polling the same bot. Stop all instances, start one |
| `Telegram API error: 429` | Rate limited | Wait, bridge auto-retries |
| `FileNotFoundError: deepseek-tui` | Binary not found | `npm install -g deepseek-tui --prefix ~/.local` |
| `stderr: ...` | deepseek-tui produced errors | Read stderr content for clues |
| `DeepSeek TUI timed out` | Prompt took >10 min | Increase `timeout_ms` or simplify prompt |

## 3. Config Validity

```bash
cat ~/projects/deepseek-telegram-bridge/config.json
python3 -c "import json; json.load(open('/home/i/projects/deepseek-telegram-bridge/config.json')); print('Valid JSON')"
```

Common config issues:
- Missing `telegram.bot_token`
- Token expired or revoked (regenerate via @BotFather)
- `allowed_user_ids` has the wrong format (must be list of integers, not strings)

## 4. Binary Accessibility

```bash
deepseek-tui --version
```

Should print version info. If not found:
```bash
which deepseek-tui
npm list -g deepseek-tui
```

## 5. Telegram API Status

```bash
curl -s "https://api.telegram.org/bot<TOKEN>/getMe" | python3 -m json.tool
```

Replace `<TOKEN>` with the actual bot token. Should return bot info. If 404, the token is invalid.

## Bot Not Replying

Checklist:
- [ ] Service is running: `systemctl --user status deepseek-telegram-bridge.service`
- [ ] No errors in bridge log: `tail -20 ~/projects/deepseek-telegram-bridge/bridge.log`
- [ ] Token is valid: `curl -s "https://api.telegram.org/bot<TOKEN>/getMe"`
- [ ] Your user ID is in `allowed_user_ids` (if non-empty)
- [ ] Bot hasn't been blocked by the user
- [ ] deepseek-tui works standalone: `deepseek-tui exec --json --auto "test"`

## Bot Replies Slowly

- DeepSeek TUI with `deepseek-v4-pro` + thinking can take 1-5 minutes for complex prompts
- Check `bridge.log` for `Spawning:` lines — shows when the subprocess started
- The typing indicator refreshes every 4 seconds while working
- If consistently slow, consider switching model via `deepseek.model` in config

## Restart Loop

If the service keeps restarting:
1. Check `bridge.log` for startup errors
2. Verify config.json is valid JSON
3. Run manually to see the error: `cd ~/projects/deepseek-telegram-bridge && .venv/bin/python -m src.bridge`
4. If token is invalid, the bridge exits with an error and systemd restarts it

## Duplicate Polling (409 Conflict)

If you see `Telegram API error: 409` in logs:
1. Stop all bridge instances: `systemctl --user stop deepseek-telegram-bridge.service`
2. Wait 5 seconds
3. Start one instance: `systemctl --user start deepseek-telegram-bridge.service`

## Clearing State

If sessions are corrupt or stuck:

```bash
systemctl --user stop deepseek-telegram-bridge.service
# Edit state.json: {"sessions": {}, "offset": 0}
echo '{"sessions": {}, "offset": 0}' > ~/projects/deepseek-telegram-bridge/state.json
systemctl --user start deepseek-telegram-bridge.service
```

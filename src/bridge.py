#!/usr/bin/env python3
"""
deepseek-telegram-bridge — Telegram ↔ DeepSeek TUI session bridge.

Long-polls Telegram for messages, spawns `deepseek-tui exec` as a subprocess,
parses the JSON output, and sends replies back.  Session continuity: --fresh
on first message per chat, --continue for subsequent messages in that chat.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import signal
import sys
from pathlib import Path
from typing import Any

import httpx

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
CONFIG_PATH = Path(
    os.environ.get("DEEPSEEK_BRIDGE_CONFIG",
                    Path(__file__).resolve().parent.parent / "config.json")
)
STATE_PATH = Path(
    os.environ.get("DEEPSEEK_BRIDGE_STATE",
                    Path(__file__).resolve().parent.parent / "state.json")
)
LOG_PATH = Path(
    os.environ.get("DEEPSEEK_BRIDGE_LOG",
                    Path(__file__).resolve().parent.parent / "bridge.log")
)
TELEGRAM_API = "https://api.telegram.org"
TYPING_INTERVAL = 4  # seconds

log = logging.getLogger("deepseek-bridge")

# ---------------------------------------------------------------------------
# Config & State
# ---------------------------------------------------------------------------

def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        print(f"Config not found at {CONFIG_PATH}", file=sys.stderr)
        print("Copy config.example.json → config.json and fill in your values.",
              file=sys.stderr)
        sys.exit(1)
    with open(CONFIG_PATH) as f:
        cfg = json.load(f)
    tg = cfg.get("telegram", {})
    if not tg.get("bot_token"):
        raise ValueError("telegram.bot_token is required")
    return cfg


def load_state() -> dict[str, Any]:
    if STATE_PATH.exists():
        with open(STATE_PATH) as f:
            return json.load(f)
    return {"sessions": {}, "offset": 0}


def save_state(state: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    tmp.replace(STATE_PATH)

# ---------------------------------------------------------------------------
# Telegram helpers
# ---------------------------------------------------------------------------

async def tg_call(
    client: httpx.AsyncClient, token: str, method: str,
    params: dict[str, Any] | None = None, timeout: float = 30.0,
) -> dict[str, Any]:
    url = f"{TELEGRAM_API}/bot{token}/{method}"
    resp = await client.post(url, json=params, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        log.error("Telegram API error (%s): %s", method, data)
    return data


async def send_message(
    client: httpx.AsyncClient, token: str, chat_id: int, text: str,
    *, reply_to: int | None = None,
) -> dict[str, Any]:
    MAX_LEN = 4000
    if len(text) <= MAX_LEN:
        return await tg_call(client, token, "sendMessage", {
            "chat_id": chat_id, "text": text,
            "reply_to_message_id": reply_to,
        })
    parts = _split_text(text, MAX_LEN)
    last = None
    for part in parts:
        last = await tg_call(client, token, "sendMessage", {
            "chat_id": chat_id, "text": part,
        })
        await asyncio.sleep(0.3)
    return last


def _split_text(text: str, max_len: int) -> list[str]:
    parts = []
    while len(text) > max_len:
        for sep in ("\n\n", "\n", " "):
            cut = text.rfind(sep, 0, max_len)
            if cut != -1:
                break
        if cut == -1:
            cut = max_len
        parts.append(text[:cut].strip())
        text = text[cut:].strip()
    if text:
        parts.append(text)
    return parts


async def send_typing(
    client: httpx.AsyncClient, token: str, chat_id: int
) -> None:
    try:
        await tg_call(client, token, "sendChatAction", {
            "chat_id": chat_id, "action": "typing"
        }, timeout=5.0)
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Access control
# ---------------------------------------------------------------------------

def is_authorized(cfg: dict[str, Any], user_id: int, chat_id: int) -> bool:
    allowed_users: list[int] = cfg["telegram"].get("allowed_user_ids", [])
    if allowed_users and user_id not in allowed_users:
        log.info("Blocked user %d (not in allowlist)", user_id)
        return False
    allowed_chats = cfg["telegram"].get("allowed_chat_ids")
    if allowed_chats is not None and chat_id not in allowed_chats:
        log.info("Blocked chat %d (not in chat allowlist)", chat_id)
        return False
    return True

# ---------------------------------------------------------------------------
# DeepSeek TUI subprocess
# ---------------------------------------------------------------------------

def build_command(
    cfg: dict[str, Any], prompt: str, *,
    use_continue: bool = False,
    chat_settings: dict[str, Any] | None = None,
) -> list[str]:
    ds = cfg["deepseek"]
    binary = ds.get("binary", "deepseek-tui")
    cmd = [binary, "exec", "--json"]
    # Per-chat model override, fall back to config default
    cs = chat_settings or {}
    model = cs.get("model") or ds.get("model")
    if model:
        cmd.extend(["--model", model])
    # Agent mode: --auto enables tools (write, edit, shell, etc.)
    if cs.get("agent"):
        cmd.insert(1, "--auto")
    if use_continue:
        cmd.append("--continue")
    else:
        cmd.append("--fresh")
    wd = ds.get("working_dir")
    if wd:
        cmd.extend(["--workspace", wd])
    cmd.append(prompt)
    return cmd


async def run_deepseek(
    cfg: dict[str, Any], prompt: str, timeout_ms: int,
    *, use_continue: bool = False,
    chat_settings: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Spawn deepseek-tui exec --json, return parsed output."""
    cmd = build_command(cfg, prompt, use_continue=use_continue, chat_settings=chat_settings)
    working_dir = cfg["deepseek"].get("working_dir") or os.getcwd()

    log.info("Spawning: %s", " ".join(cmd))

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=working_dir,
    )

    stdout_data = ""
    stderr_data = ""
    error_msg: str | None = None

    try:
        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(), timeout=timeout_ms / 1000.0
            )
            stdout_data = stdout_bytes.decode("utf-8", errors="replace")
            stderr_data = stderr_bytes.decode("utf-8", errors="replace")
        except asyncio.TimeoutError:
            proc.kill()
            stdout_bytes, stderr_bytes = await proc.communicate()
            stdout_data = stdout_bytes.decode("utf-8", errors="replace")
            stderr_data = stderr_bytes.decode("utf-8", errors="replace")
            error_msg = f"DeepSeek TUI timed out after {timeout_ms // 1000}s"
    except Exception as exc:
        error_msg = str(exc)
        try:
            proc.kill()
            await proc.communicate()
        except Exception:
            pass

    if stderr_data.strip():
        log.info("stderr: %s", stderr_data.strip()[:500])

    try:
        result = json.loads(stdout_data.strip() or "{}")
    except json.JSONDecodeError:
        result = {}

    output = result.get("output", "")
    result_error = result.get("error")
    if result_error and not error_msg:
        error_msg = result_error

    return {
        "text": output if output else error_msg or "(empty response)",
        "error": error_msg,
    }

# ---------------------------------------------------------------------------
# Message handler
# ---------------------------------------------------------------------------

async def handle_message(
    client: httpx.AsyncClient, cfg: dict[str, Any],
    state: dict[str, Any], msg: dict[str, Any],
) -> None:
    token = cfg["telegram"]["bot_token"]
    chat_id: int = msg["chat"]["id"]
    user_id: int = msg.get("from", {}).get("id", 0)
    text: str = msg.get("text", "").strip()
    message_id: int = msg["message_id"]

    if not text:
        return

    log.info("Message from user=%d chat=%d: %s", user_id, chat_id, text[:80])

    if text.startswith("/"):
        await handle_command(client, cfg, state, chat_id, user_id, text, message_id)
        return

    if not is_authorized(cfg, user_id, chat_id):
        return

    # Session continuity: --fresh on first message, --continue after that
    chat_key = str(chat_id)
    sessions = state.setdefault("sessions", {})
    has_session = chat_key in sessions
    sessions[chat_key] = True

    # Per-chat settings (model, reasoning)
    chat_settings = state.setdefault("chat_settings", {}).setdefault(chat_key, {})

    save_state(state)
    timeout_ms = cfg["deepseek"].get("timeout_ms", 600000)

    typing_task = asyncio.create_task(_typing_loop(client, token, chat_id))
    try:
        result = await run_deepseek(
            cfg, text, timeout_ms,
            use_continue=has_session,
            chat_settings=chat_settings,
        )
        typing_task.cancel()

        log.info("DeepSeek result: error=%s text_len=%d",
                 result["error"], len(result.get("text", "")))

        if result["error"]:
            await send_message(client, token, chat_id,
                               f"⚠️ {result['error']}")
        elif result["text"]:
            await send_message(client, token, chat_id,
                               result["text"], reply_to=message_id)
        else:
            await send_message(client, token, chat_id,
                               "⚠️ (no response from DeepSeek)")
    except Exception as exc:
        typing_task.cancel()
        log.exception("Error handling message from chat %d", chat_id)
        await send_message(client, token, chat_id, f"⚠️ Bridge error: {exc}")


async def _typing_loop(
    client: httpx.AsyncClient, token: str, chat_id: int
) -> None:
    try:
        while True:
            await send_typing(client, token, chat_id)
            await asyncio.sleep(TYPING_INTERVAL)
    except asyncio.CancelledError:
        pass

# ---------------------------------------------------------------------------
# Slash commands
# ---------------------------------------------------------------------------

async def handle_command(
    client: httpx.AsyncClient, cfg: dict[str, Any], state: dict[str, Any],
    chat_id: int, user_id: int, text: str, message_id: int,
) -> None:
    token = cfg["telegram"]["bot_token"]
    chat_key = str(chat_id)
    sessions = state.setdefault("sessions", {})

    cmd, *args = text.split(maxsplit=1)
    cmd = cmd.lower()

    if cmd == "/start":
        await send_message(client, token, chat_id,
            "DeepSeek TUI Telegram Bridge ready.\n"
            "Send any message to talk to DeepSeek.\n\n"
            "Commands: /new /status /help")

    elif cmd == "/help":
        await send_message(client, token, chat_id,
            "DeepSeek TUI Telegram Bridge\n\n"
            "/start — Welcome\n"
            "/help — This help\n"
            "/new — Start fresh session\n"
            "/status — Show session info\n"
            "/model <name> — Switch model (v4-pro, v4-flash)\n"
            "/reasoning <effort> — Set reasoning (auto, low, medium, high)\n"
            "/agent <on|off> — Toggle agent mode (tools: write/edit/shell)\n\n"
            "Defaults: flash, auto reasoning, agent OFF.")

    elif cmd == "/new":
        sessions.pop(chat_key, None)
        save_state(state)
        await send_message(client, token, chat_id,
            "✅ Fresh session. Next message starts clean.")

    elif cmd == "/status":
        if chat_key in sessions:
            await send_message(client, token, chat_id,
                "📌 Active session in this chat.")
        else:
            await send_message(client, token, chat_id,
                "No active session. Next message starts fresh.")

    elif cmd == "/model":
        arg = (args[0] if args else "").strip().lower()
        valid = ["deepseek-v4-pro", "deepseek-v4-flash"]
        if arg not in valid:
            await send_message(client, token, chat_id,
                f"Usage: /model <name>\nValid: {', '.join(valid)}")
            return
        chat_data = state.setdefault("chat_settings", {}).setdefault(chat_key, {})
        chat_data["model"] = arg
        save_state(state)
        await send_message(client, token, chat_id, f"✅ Model set to `{arg}`")

    elif cmd == "/reasoning":
        arg = (args[0] if args else "").strip().lower()
        valid = ["auto", "low", "medium", "high"]
        if arg not in valid:
            await send_message(client, token, chat_id,
                f"Usage: /reasoning <effort>\nValid: {', '.join(valid)}")
            return
        chat_data = state.setdefault("chat_settings", {}).setdefault(chat_key, {})
        chat_data["reasoning"] = arg
        save_state(state)
        await send_message(client, token, chat_id, f"✅ Reasoning set to `{arg}`")

    elif cmd == "/agent":
        arg = (args[0] if args else "").strip().lower()
        chat_data = state.setdefault("chat_settings", {}).setdefault(chat_key, {})
        if arg == "on":
            chat_data["agent"] = True
            save_state(state)
            await send_message(client, token, chat_id,
                "🤖 Agent mode ON — tools enabled (write, edit, shell, git).\n"
                "Responses may be slower. /agent off to disable.")
        elif arg == "off":
            chat_data.pop("agent", None)
            save_state(state)
            await send_message(client, token, chat_id,
                "💬 Agent mode OFF — fast chat only. /agent on to enable tools.")
        else:
            current = "ON" if chat_data.get("agent") else "OFF"
            await send_message(client, token, chat_id,
                f"Agent mode: {current}\nUsage: /agent on | /agent off")

# ---------------------------------------------------------------------------
# Poll loop
# ---------------------------------------------------------------------------

async def poll_loop(
    client: httpx.AsyncClient, cfg: dict[str, Any], state: dict[str, Any],
) -> None:
    token = cfg["telegram"]["bot_token"]
    log.info("Bridge started. Polling for updates...")

    while True:
        try:
            offset = state.get("offset", 0)
            updates = await tg_call(client, token, "getUpdates", {
                "offset": offset, "timeout": 30,
                "allowed_updates": ["message"],
            }, timeout=45.0)

            for update in updates.get("result", []):
                update_id = update["update_id"]
                state["offset"] = update_id + 1
                save_state(state)
                msg = update.get("message")
                if msg:
                    asyncio.create_task(
                        handle_message(client, cfg, state, msg))

        except httpx.HTTPError as exc:
            log.error("HTTP error polling Telegram: %s", exc)
            await asyncio.sleep(5)
        except Exception as exc:
            log.exception("Unexpected error in poll loop")
            await asyncio.sleep(5)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(LOG_PATH),
                  logging.StreamHandler(sys.stderr)],
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)


_shutdown_triggered = False


async def _shutdown() -> None:
    global _shutdown_triggered
    if _shutdown_triggered:
        return
    _shutdown_triggered = True
    log.info("Shutdown signal received.")
    tasks = [t for t in asyncio.all_tasks()
             if t is not asyncio.current_task()]
    for t in tasks:
        t.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    asyncio.get_running_loop().stop()


async def main() -> None:
    setup_logging()
    cfg = load_config()
    state = load_state()

    binary = cfg["deepseek"].get("binary", "deepseek-tui")
    try:
        proc = await asyncio.create_subprocess_exec(
            binary, "--version",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
        if proc.returncode != 0:
            log.error("%s --version failed (exit %d)", binary, proc.returncode)
            sys.exit(1)
        log.info("Found: %s", stdout.decode().strip().split("\n")[0])
    except FileNotFoundError:
        log.error("%s not found on PATH", binary)
        sys.exit(1)

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(_shutdown()))

    async with httpx.AsyncClient(http2=True) as client:
        try:
            await poll_loop(client, cfg, state)
        except asyncio.CancelledError:
            pass
    log.info("Bridge shut down.")


if __name__ == "__main__":
    asyncio.run(main())

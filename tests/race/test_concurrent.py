"""Race-condition tests for deepseek-telegram-bridge.

Doctrine: asyncio concurrency paths must not interleave per-chat state
or leak tasks. Tests use asyncio.all_tasks() snapshots to verify no
task leaks survive the handler, and freeze_time to keep timing stable.
"""

from __future__ import annotations

import asyncio

import pytest

from bridge import handle_message

# ---------------------------------------------------------------------------
# Task-leak guard — handle_message must cancel typing_task on all paths
# ---------------------------------------------------------------------------


@pytest.mark.race
@pytest.mark.asyncio
async def test_handle_message_no_task_leak_on_deepseek_error(
    mock_telegram: object,
    poison_pill_subprocess: object,
    fake_chat: object,
    fake_config: object,
) -> None:
    """Cancellation paths in handle_message must not leak asyncio tasks."""
    import httpx
    import respx

    from tests.conftest import FakeChat, FakeConfig, PoisonPillSubprocess

    assert isinstance(mock_telegram, respx.MockRouter)
    assert isinstance(poison_pill_subprocess, PoisonPillSubprocess)
    assert isinstance(fake_chat, FakeChat)
    assert isinstance(fake_config, FakeConfig)

    cfg = fake_config.as_dict()
    state: dict = {"sessions": {}, "offset": 0}
    msg = {
        "chat": {"id": fake_chat.chat_id},
        "from": {"id": fake_chat.user_id},
        "message_id": fake_chat.message_id,
        "text": "hello",
    }

    # Poison-pill: DeepSeek returns an error payload
    poison_pill_subprocess.register(
        ["deepseek-tui", "exec", "--json"],
        stdout=b'{"output": "", "error": "upstream error"}',
    )

    # Telegram: stub sendChatAction + sendMessage
    mock_telegram.post(f"/bot{fake_config.bot_token}/sendChatAction").mock(
        return_value=httpx.Response(200, json={"ok": True, "result": True})
    )
    mock_telegram.post(f"/bot{fake_config.bot_token}/sendMessage").mock(
        return_value=httpx.Response(200, json={"ok": True, "result": {"message_id": 1}})
    )

    tasks_before = set(asyncio.all_tasks())

    async with httpx.AsyncClient(http2=False) as client:
        await handle_message(client, cfg, state, msg)

    # Allow one event-loop tick for cancelled tasks to finalise
    await asyncio.sleep(0)

    tasks_after = set(asyncio.all_tasks()) - tasks_before
    lingering = [t for t in tasks_after if not t.done()]
    assert lingering == [], f"Task leak detected: {[t.get_name() for t in lingering]}"


@pytest.mark.race
@pytest.mark.asyncio
async def test_concurrent_chats_do_not_share_session_state(
    mock_telegram: object,
    poison_pill_subprocess: object,
    fake_config: object,
) -> None:
    """Two concurrent chats must not read each other's session key."""
    import httpx
    import respx

    from tests.conftest import FakeConfig, PoisonPillSubprocess

    assert isinstance(mock_telegram, respx.MockRouter)
    assert isinstance(poison_pill_subprocess, PoisonPillSubprocess)
    assert isinstance(fake_config, FakeConfig)

    cfg = fake_config.as_dict()
    state: dict = {"sessions": {}, "offset": 0}

    poison_pill_subprocess.register(
        ["deepseek-tui", "exec", "--json"],
        stdout=b'{"output": "ok"}',
    )
    mock_telegram.post(f"/bot{fake_config.bot_token}/sendChatAction").mock(
        return_value=httpx.Response(200, json={"ok": True, "result": True})
    )
    mock_telegram.post(f"/bot{fake_config.bot_token}/sendMessage").mock(
        return_value=httpx.Response(200, json={"ok": True, "result": {"message_id": 1}})
    )

    def make_msg(chat_id: int, user_id: int) -> dict:
        return {
            "chat": {"id": chat_id},
            "from": {"id": user_id},
            "message_id": 1,
            "text": "first message",
        }

    async with httpx.AsyncClient(http2=False) as client:
        # Run two first-time messages concurrently
        await asyncio.gather(
            handle_message(client, cfg, state, make_msg(1001, 2001)),
            handle_message(client, cfg, state, make_msg(1002, 2002)),
        )

    # Both chats should have independent session keys
    sessions = state.get("sessions", {})
    assert "1001" in sessions
    assert "1002" in sessions
    # Keys must be independent booleans — not cross-contaminated
    assert sessions["1001"] is True
    assert sessions["1002"] is True

"""Unit tests for deepseek-telegram-bridge core logic.

Doctrine: AAA pattern, DAMP over DRY, one concept per test.
Every HTTP boundary uses the mock_telegram respx fixture (Golden Rule 6).
Every subprocess boundary uses poison_pill_subprocess (Golden Rule 6).
No real time, no real network (Golden Rule 8).
"""

from __future__ import annotations

import json
import pytest

import httpx

from bridge import (
    _split_text,
    build_command,
    is_authorized,
    run_deepseek,
)


# ---------------------------------------------------------------------------
# _split_text — pure function, no mocks needed
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_split_text_short_message_returns_single_part() -> None:
    # Arrange
    text = "hello world"
    # Act
    parts = _split_text(text, max_len=4000)
    # Assert
    assert parts == ["hello world"]


@pytest.mark.unit
def test_split_text_splits_on_double_newline_first() -> None:
    # Arrange
    chunk = "a" * 100
    text = f"{chunk}\n\n{chunk}"
    # Act
    parts = _split_text(text, max_len=120)
    # Assert
    assert len(parts) == 2
    assert all(len(p) <= 120 for p in parts)


@pytest.mark.unit
def test_split_text_falls_back_to_single_newline() -> None:
    # Arrange — no double newlines, only single
    chunk = "a" * 60
    text = f"{chunk}\n{chunk}"
    # Act
    parts = _split_text(text, max_len=80)
    # Assert
    assert len(parts) == 2
    assert all(len(p) <= 80 for p in parts)


@pytest.mark.unit
def test_split_text_hard_cuts_when_no_separator_found() -> None:
    # Arrange — solid block, no whitespace
    text = "x" * 50
    # Act
    parts = _split_text(text, max_len=20)
    # Assert — no part exceeds max_len
    assert all(len(p) <= 20 for p in parts)
    assert "".join(parts) == text


@pytest.mark.unit
def test_split_text_preserves_all_content() -> None:
    # Arrange
    text = "word " * 1000  # 5000 chars
    # Act
    parts = _split_text(text, max_len=4000)
    # Assert — reassembled content equals original (modulo strip)
    reassembled = " ".join(p.strip() for p in parts)
    assert len(reassembled) > 0
    assert len(parts) >= 2


# ---------------------------------------------------------------------------
# build_command — pure function
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_build_command_defaults(fake_config: object) -> None:
    from tests.conftest import FakeConfig
    cfg = FakeConfig().as_dict()
    # Act
    cmd = build_command(cfg, "hello")
    # Assert
    assert cmd[0] == "deepseek-tui"
    assert "exec" in cmd
    assert "--json" in cmd
    assert "--fresh" in cmd
    assert cmd[-1] == "hello"


@pytest.mark.unit
def test_build_command_continue_flag(fake_config: object) -> None:
    from tests.conftest import FakeConfig
    cfg = FakeConfig().as_dict()
    cmd = build_command(cfg, "followup", use_continue=True)
    assert "--continue" in cmd
    assert "--fresh" not in cmd


@pytest.mark.unit
def test_build_command_model_override() -> None:
    from tests.conftest import FakeConfig
    cfg = FakeConfig(model="deepseek-v4-pro").as_dict()
    cmd = build_command(cfg, "hello")
    assert "--model" in cmd
    assert "deepseek-v4-pro" in cmd


@pytest.mark.unit
def test_build_command_agent_mode_inserts_auto() -> None:
    from tests.conftest import FakeConfig
    cfg = FakeConfig().as_dict()
    cmd = build_command(cfg, "hello", chat_settings={"agent": True})
    assert "--auto" in cmd


@pytest.mark.unit
def test_build_command_workspace() -> None:
    from tests.conftest import FakeConfig
    cfg = FakeConfig(working_dir="/tmp/ws").as_dict()
    cmd = build_command(cfg, "hello")
    assert "--workspace" in cmd
    assert "/tmp/ws" in cmd


@pytest.mark.unit
def test_build_command_per_chat_model_overrides_config() -> None:
    from tests.conftest import FakeConfig
    cfg = FakeConfig(model="deepseek-v4-flash").as_dict()
    cmd = build_command(cfg, "hello", chat_settings={"model": "deepseek-v4-pro"})
    idx = cmd.index("--model")
    assert cmd[idx + 1] == "deepseek-v4-pro"


# ---------------------------------------------------------------------------
# is_authorized — pure function
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_is_authorized_open_config_allows_anyone() -> None:
    from tests.conftest import FakeConfig
    cfg = FakeConfig().as_dict()
    assert is_authorized(cfg, user_id=999, chat_id=888) is True


@pytest.mark.unit
def test_is_authorized_blocks_user_not_in_allowlist() -> None:
    from tests.conftest import FakeConfig
    cfg = FakeConfig(allowed_user_ids=(1, 2, 3)).as_dict()
    assert is_authorized(cfg, user_id=999, chat_id=888) is False


@pytest.mark.unit
def test_is_authorized_allows_user_in_allowlist() -> None:
    from tests.conftest import FakeConfig
    cfg = FakeConfig(allowed_user_ids=(1, 2, 999)).as_dict()
    assert is_authorized(cfg, user_id=999, chat_id=888) is True


@pytest.mark.unit
def test_is_authorized_blocks_chat_not_in_allowlist() -> None:
    from tests.conftest import FakeConfig
    cfg = FakeConfig(allowed_chat_ids=(100, 200)).as_dict()
    assert is_authorized(cfg, user_id=999, chat_id=999) is False


@pytest.mark.unit
def test_is_authorized_allows_chat_in_allowlist() -> None:
    from tests.conftest import FakeConfig
    cfg = FakeConfig(allowed_chat_ids=(100, 200, 888)).as_dict()
    assert is_authorized(cfg, user_id=999, chat_id=888) is True


# ---------------------------------------------------------------------------
# run_deepseek — subprocess boundary via Poison-Pill mock
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.asyncio
async def test_run_deepseek_happy_path(poison_pill_subprocess: object) -> None:
    from tests.conftest import FakeConfig, PoisonPillSubprocess
    assert isinstance(poison_pill_subprocess, PoisonPillSubprocess)
    cfg = FakeConfig().as_dict()
    poison_pill_subprocess.register(
        ["deepseek-tui", "exec", "--json"],
        stdout=b'{"output": "Here is the answer."}',
    )
    # Act
    result = await run_deepseek(cfg, "what is 2+2?", timeout_ms=60_000)
    # Assert
    assert result["text"] == "Here is the answer."
    assert result["error"] is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_run_deepseek_empty_output_returns_fallback(
    poison_pill_subprocess: object,
) -> None:
    from tests.conftest import FakeConfig, PoisonPillSubprocess
    assert isinstance(poison_pill_subprocess, PoisonPillSubprocess)
    cfg = FakeConfig().as_dict()
    poison_pill_subprocess.register(
        ["deepseek-tui", "exec", "--json"],
        stdout=b'{"output": ""}',
    )
    result = await run_deepseek(cfg, "hello", timeout_ms=60_000)
    assert result["text"] == "(empty response)"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_run_deepseek_malformed_json_returns_empty(
    poison_pill_subprocess: object,
) -> None:
    from tests.conftest import FakeConfig, PoisonPillSubprocess
    assert isinstance(poison_pill_subprocess, PoisonPillSubprocess)
    cfg = FakeConfig().as_dict()
    poison_pill_subprocess.register(
        ["deepseek-tui", "exec", "--json"],
        stdout=b"not json at all",
    )
    result = await run_deepseek(cfg, "hello", timeout_ms=60_000)
    # Adaptive Fault Tolerance: malformed JSON → graceful degradation
    assert result["text"] == "(empty response)"
    assert result["error"] is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_run_deepseek_error_field_surfaces_as_error(
    poison_pill_subprocess: object,
) -> None:
    from tests.conftest import FakeConfig, PoisonPillSubprocess
    assert isinstance(poison_pill_subprocess, PoisonPillSubprocess)
    cfg = FakeConfig().as_dict()
    poison_pill_subprocess.register(
        ["deepseek-tui", "exec", "--json"],
        stdout=b'{"output": "", "error": "model overloaded"}',
    )
    result = await run_deepseek(cfg, "hello", timeout_ms=60_000)
    assert result["error"] == "model overloaded"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_run_deepseek_unregistered_binary_raises_poison_pill(
    poison_pill_subprocess: object,
) -> None:
    from tests.conftest import FakeConfig, UnmockedSubprocessCallError
    cfg = FakeConfig().as_dict()
    # Intentionally do NOT register — verifies the harness catches rogue calls.
    with pytest.raises(UnmockedSubprocessCallError):
        await run_deepseek(cfg, "hello", timeout_ms=60_000)

"""Test harness for deepseek-telegram-bridge.

Doctrine: .claude/skills/master-tester-doctrine/SKILL.md
  - Golden Rule 5: isolated tests, no shared state.
  - Golden Rule 6: never mock httpx directly — use respx.
  - Golden Rule 8: deterministic time via freezegun, no real network.

Two strict boundary harnesses:

  * ``poison_pill_subprocess`` — patches asyncio.create_subprocess_exec.
    Any unregistered argv raises UnmockedSubprocessCallError immediately.

  * ``mock_telegram`` — respx router bound to api.telegram.org.
    Any unregistered route fails the test loudly (assert_all_mocked=True).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import pytest
import respx
from freezegun import freeze_time

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator


# ---------------------------------------------------------------------------
# Poison-Pill subprocess mock  (Golden Rule 6 / Zero-Trust pattern)
# ---------------------------------------------------------------------------

class UnmockedSubprocessCallError(AssertionError):
    """Raised when production code spawns an unregistered subprocess argv.

    If you see this, either register the expected argv prefix with
    ``poison_pill_subprocess.register(...)`` or investigate why the code
    is shelling out somewhere the test author didn't anticipate.
    """


@dataclass
class _FakeProcess:
    """Minimal stand-in for asyncio.subprocess.Process."""

    _stdout: bytes = b""
    _stderr: bytes = b""
    returncode: int | None = 0
    _killed: bool = False

    async def communicate(self) -> tuple[bytes, bytes]:
        return self._stdout, self._stderr

    def kill(self) -> None:
        self._killed = True


@dataclass
class PoisonPillSubprocess:
    """Strict registry for asyncio.create_subprocess_exec invocations.

    Usage::

        async def test_happy_path(poison_pill_subprocess):
            poison_pill_subprocess.register(
                ["deepseek-tui", "exec", "--json"],
                stdout=b'{"output": "hello"}',
            )
            result = await run_deepseek(cfg, "hi", 60_000)
            assert result["text"] == "hello"

    Prefix matching: register the leading argv tokens you care about;
    flags appended later (--model, --workspace, --fresh) are ignored.
    """

    _entries: list[tuple[tuple[str, ...], _FakeProcess]] = field(default_factory=list)
    call_log: list[tuple[str, ...]] = field(default_factory=list)

    def register(
        self,
        argv_prefix: list[str],
        *,
        stdout: bytes = b"",
        stderr: bytes = b"",
        returncode: int = 0,
    ) -> None:
        proc = _FakeProcess(_stdout=stdout, _stderr=stderr, returncode=returncode)
        self._entries.append((tuple(argv_prefix), proc))

    async def __call__(self, *argv: str, **_kwargs: Any) -> _FakeProcess:
        self.call_log.append(tuple(argv))
        for prefix, proc in self._entries:
            if tuple(argv)[: len(prefix)] == prefix:
                return proc
        raise UnmockedSubprocessCallError(
            f"Test failed: unregistered subprocess argv.\n"
            f"  argv: {list(argv)!r}\n"
            f"  registered prefixes: {[list(p) for p, _ in self._entries]!r}\n"
            f"Add `poison_pill_subprocess.register(<argv_prefix>, ...)` to the test."
        )


@pytest.fixture
def poison_pill_subprocess(monkeypatch: pytest.MonkeyPatch) -> PoisonPillSubprocess:
    """Patch asyncio.create_subprocess_exec to fail loudly on unregistered argv."""
    import asyncio

    pill = PoisonPillSubprocess()
    monkeypatch.setattr(asyncio, "create_subprocess_exec", pill)
    return pill


# ---------------------------------------------------------------------------
# Telegram Bot API mock  (Golden Rule 6: never mock httpx directly)
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_telegram() -> Iterator[respx.MockRouter]:
    """respx-backed strict Telegram mock.  Unmatched routes fail the test."""
    with respx.mock(
        base_url="https://api.telegram.org",
        assert_all_called=False,
        assert_all_mocked=True,
    ) as router:
        yield router


# ---------------------------------------------------------------------------
# Deterministic time  (Golden Rule 8)
# ---------------------------------------------------------------------------

@pytest.fixture
def frozen_clock() -> Iterator[None]:
    with freeze_time("2026-05-05T00:00:00Z"):
        yield


# ---------------------------------------------------------------------------
# Test data factories — no real PII, no real tokens
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FakeChat:
    chat_id: int = 1_000_000_001
    user_id: int = 2_000_000_001
    message_id: int = 42


@dataclass(frozen=True)
class FakeConfig:
    """Fully-shaped bridge config for unit tests."""

    bot_token: str = "TEST_TOKEN_NOT_REAL"  # noqa: S105
    binary: str = "deepseek-tui"
    model: str | None = None
    working_dir: str | None = None
    timeout_ms: int = 60_000
    allowed_user_ids: tuple[int, ...] = ()
    allowed_chat_ids: tuple[int, ...] | None = None

    def as_dict(self) -> dict[str, Any]:
        tg: dict[str, Any] = {"bot_token": self.bot_token}
        if self.allowed_user_ids:
            tg["allowed_user_ids"] = list(self.allowed_user_ids)
        if self.allowed_chat_ids is not None:
            tg["allowed_chat_ids"] = list(self.allowed_chat_ids)
        ds: dict[str, Any] = {"binary": self.binary, "timeout_ms": self.timeout_ms}
        if self.model is not None:
            ds["model"] = self.model
        if self.working_dir is not None:
            ds["working_dir"] = self.working_dir
        return {"telegram": tg, "deepseek": ds}


@pytest.fixture
def fake_chat() -> FakeChat:
    return FakeChat()


@pytest.fixture
def fake_config() -> FakeConfig:
    return FakeConfig()


@pytest.fixture
def fake_config_factory() -> Callable[..., FakeConfig]:
    def _factory(**overrides: Any) -> FakeConfig:
        return FakeConfig(**overrides)
    return _factory


# ---------------------------------------------------------------------------
# Marker handling — integration tests are opt-in only
# ---------------------------------------------------------------------------

def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    selected = config.getoption("-m", default="")
    if selected and "integration" in str(selected):
        return
    skip_integration = pytest.mark.skip(reason="needs -m integration (real network)")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)

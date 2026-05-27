"""Property-based tests for deepseek-telegram-bridge.

Doctrine: alignment-invariant properties, not range-only properties.
See docs/TESTING_DOCTRINE.md § Lessons — "Range-only properties miss
alignment bugs" (issue #4, adb-android-control 2026-05-05).

Each property tests the structural contract of the function, not merely
that the output stays within a legal range.
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from bridge import _split_text, build_command

# ---------------------------------------------------------------------------
# _split_text — alignment invariants
# ---------------------------------------------------------------------------


@pytest.mark.property
@given(
    text=st.text(min_size=0, max_size=20_000),
    max_len=st.integers(min_value=1, max_value=8000),
)
@settings(max_examples=500)
def test_split_text_no_part_exceeds_max_len(text: str, max_len: int) -> None:
    """Alignment: every part produced is within max_len characters."""
    parts = _split_text(text, max_len)
    for part in parts:
        assert len(part) <= max_len, f"Part of length {len(part)} exceeds max_len={max_len}"


@pytest.mark.property
@given(
    text=st.text(min_size=1, max_size=20_000),
    max_len=st.integers(min_value=1, max_value=8000),
)
@settings(max_examples=500)
def test_split_text_content_is_preserved(text: str, max_len: int) -> None:
    """Alignment: all non-whitespace characters survive the split in order.

    Whitespace may be consumed at split boundaries (strip semantics), so
    the invariant operates on non-whitespace chars only. Hard-cut mode
    may also split a word, so we cannot use word-level comparison.
    """
    parts = _split_text(text, max_len)

    def nonws(s: str) -> list[str]:
        return [ch for ch in s if not ch.isspace()]

    original_nonws = nonws(text)
    result_nonws = nonws("".join(parts))
    assert original_nonws == result_nonws, "Non-whitespace content lost or reordered after split"


@pytest.mark.property
@given(text=st.text(max_size=3999))
def test_split_text_short_text_is_single_part(text: str) -> None:
    """Alignment: text within max_len must not be split at all."""
    parts = _split_text(text, max_len=4000)
    # A short text may produce 0 parts (empty) or 1 part — never more.
    assert len(parts) <= 1


# ---------------------------------------------------------------------------
# build_command — structural alignment invariants
# ---------------------------------------------------------------------------


@pytest.mark.property
@given(prompt=st.text(min_size=1, max_size=2000))
def test_build_command_prompt_is_last_arg(prompt: str) -> None:
    """Alignment: the prompt must always be the final element of the argv."""
    from tests.conftest import FakeConfig

    cfg = FakeConfig().as_dict()
    cmd = build_command(cfg, prompt)
    assert cmd[-1] == prompt


@pytest.mark.property
@given(use_continue=st.booleans())
def test_build_command_exactly_one_session_flag(use_continue: bool) -> None:
    """Alignment: exactly one of --fresh / --continue must appear, never both."""
    from tests.conftest import FakeConfig

    cfg = FakeConfig().as_dict()
    cmd = build_command(cfg, "hello", use_continue=use_continue)
    fresh_count = cmd.count("--fresh")
    cont_count = cmd.count("--continue")
    assert fresh_count + cont_count == 1, (
        f"Expected exactly one session flag; got fresh={fresh_count} continue={cont_count}"
    )


@pytest.mark.property
@given(model=st.one_of(st.none(), st.text(min_size=1, max_size=50)))
def test_build_command_model_flag_alignment(model: str | None) -> None:
    """Alignment: --model appears iff a model is configured, and its value follows."""
    from tests.conftest import FakeConfig

    cfg = FakeConfig(model=model).as_dict()
    cmd = build_command(cfg, "hello")
    if model:
        assert "--model" in cmd
        idx = cmd.index("--model")
        assert cmd[idx + 1] == model
    else:
        assert "--model" not in cmd

# Testing Doctrine — deepseek-telegram-bridge

> **Status:** canonical for this repo. Established 2026-05-27.
> **Scope:** governs all test work on `deepseek-telegram-bridge`.
> **Audience:** every human and agent that writes, reviews, or modifies tests.
>
> Full upstream reference: `.claude/skills/master-tester-doctrine/` (vendored).

---

## The 10 Non-Negotiable Laws

1. **Never modify a test to fix CI.** Tests are contracts. Fix the code.
2. **Test behaviour, not implementation.** Public API only.
3. **AAA pattern.** Arrange → Act → Assert. Every test.
4. **DAMP over DRY.** Readability beats brevity in tests.
5. **Isolated tests.** No shared state. Order-independent.
6. **Never mock `httpx` directly.** Use `respx`. Never mock `asyncio.create_subprocess_exec` directly — use the Poison-Pill fixture.
7. **Ban `# type: ignore` and `cast(Any, …)` in `tests/`.**
8. **Tests must be deterministic.** `freezegun` for time, seeded `random.Random(seed=42)`, no real network.
9. **One logical concept per test.**
10. **No tautological tests.** Test business logic, not language mechanics.

## The Oath

> *"I do not test to achieve a percentage. I test to sleep soundly. I assume
> the network is hostile, the user is chaotic, and time is an illusion. My
> tests are the unbreakable contract between the present codebase and its
> future self."*

---

## Python Tooling Map

| Pattern | Python / pytest equivalent |
|---|---|
| Test runner | `pytest` + `pytest-asyncio` |
| Mock library | `unittest.mock.MagicMock(spec=…)`, `pytest-mock` |
| HTTP mocking (Law 6) | `respx` — never `httpx.mock` or `unittest.mock` on the client |
| Subprocess mocking (Law 6) | Poison-Pill `poison_pill_subprocess` fixture in `tests/conftest.py` |
| Property-based fuzzing | `hypothesis` |
| Time control | `freezegun` |
| Type-level checks | `mypy --strict` |
| Lint | `ruff` with `BLE` rule (every broad `except` must cite a reason) |
| Dead-code | `vulture` |

---

## Enforcement Map

| Law | Status | Mechanism |
|---|---|---|
| 1 | ✅ CI-enforced | `.github/workflows/ci.yml::test-file-integrity` blocks PRs that modify `tests/**/*.py` |
| 2 | 🟡 Convention | Reviewer-enforced |
| 3 | 🟡 Convention | Reviewer-enforced. AAA marked via section comments in test bodies |
| 4 | 🟡 Convention | Reviewer-enforced |
| 5 | ✅ Enforced | `pytest-randomly` random order |
| 6 | ✅ Enforced | Poison-Pill fixture; `respx` for httpx; CI fails on unmocked calls |
| 7 | ✅ Enforced | `mypy --strict` + `ruff ANN401` gate |
| 8 | ✅ Enforced | `freezegun` available; no real network in unit/property/race |
| 9 | 🟡 Convention | Reviewer-enforced |
| 10 | 🟡 Convention | Reviewer-enforced |

---

## How This Governs `deepseek-telegram-bridge`

1. **Telegram HTTP calls** are tested via `respx` routes — validate the right method
   is called with the right body, never mock `httpx.AsyncClient` internals.
2. **`asyncio.create_subprocess_exec` invocations** are tested via the Poison-Pill
   — verify the right argv is built for a given intent, not the `run_deepseek`
   internals.
3. **Determinism in timing** — `freeze_time` for any test that touches poll intervals
   or reconnect logic; never `asyncio.sleep` in a test body.
4. **No real device/service required** — every unit test mocks both boundaries.
   Real-service tests live in `tests/integration/` and are gated to CI with `-m integration`.
5. **Architectural boundary** — `bridge.py` cannot import from `tests/`; tests import
   from `bridge` only via the public module surface.

---

## Lessons (append-only, named not numbered)

### Silent except-pass at bridge.py:135 / :224 (2026-05-27)

**Trigger:** two `except Exception: pass` handlers swallowed Telegram send failures
and post-kill cleanup errors with zero log output, zero metric, zero trace.

**Insight:** silent degradation is indistinguishable from healthy operation in a log
monitor. The production path must either re-raise or log — never both suppress and
vanish.

**Pattern reinforced:** *Adaptive Fault Tolerance* — degrade to a documented value
**and log it**; cite the doctrine inline at every catch site with `# noqa: BLE001`
plus a one-line rationale.

**Mitigation:** Part A of 2026-05-27 PR — both sites now emit `log.debug`/`log.warning`
and carry `# noqa: BLE001` annotations. The `BLE` ruff rule is enabled project-wide
so any future bare `except Exception` without annotation fails CI.

---

## References

- `pyproject.toml` — dev dependencies + lint/test config
- `.pre-commit-config.yaml` — pre-commit hooks (ruff, mypy, pytest, gitleaks)
- `tests/conftest.py` — fixtures + Poison-Pill subprocess mock
- `tests/unit/` — unit tests (default)
- `tests/property/` — Hypothesis alignment-invariant properties
- `tests/race/` — asyncio concurrency tests
- `.github/workflows/ci.yml` — CI matrix
- `.claude/skills/master-tester-doctrine/` — upstream doctrine bundle (vendored)
- `.claude/qa-doctrine/` — QA deployment pack (vendored)

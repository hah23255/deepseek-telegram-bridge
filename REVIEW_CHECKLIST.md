# Pre-Commit Review Checklist — deepseek-telegram-bridge

Use this before submitting a PR. Doctrine: `.claude/skills/master-tester-doctrine/`.

---

## Security

- [ ] No `TELEGRAM_BOT_TOKEN` or any token/key literal in the diff
- [ ] No real chat IDs or user IDs in test fixtures (use `FakeChat` from conftest)
- [ ] No `.env` or `config.json` staged (covered by `.gitignore` + gitleaks hook)
- [ ] Shell commands in `build_command` use the configured binary path — no user-controlled injection
- [ ] Every new `except` block cites the doctrine (`# noqa: BLE001` + one-line rationale)

## Code Quality

- [ ] `ruff check src/ tests/` — clean
- [ ] `mypy --strict src/` — clean
- [ ] No bare `except Exception: pass` — every handler degrades-but-logs
- [ ] No new `print()` in `src/` (use `log.*`)
- [ ] `vulture src/` — no new dead code

## Tests

- [ ] New behaviour has a corresponding unit test in `tests/unit/`
- [ ] New pure functions with lookup-table or parsing logic have an alignment-invariant property in `tests/property/`
- [ ] Any new asyncio concurrency path has a race test in `tests/race/`
- [ ] `pytest -m "unit or property"` passes locally
- [ ] Every test follows AAA — Arrange / Act / Assert separated by blank lines
- [ ] No `time.sleep` in test bodies — use `freezegun` or `asyncio.sleep` only in production code
- [ ] No real network calls in unit/property/race tests

## Documentation

- [ ] `docs/TESTING_DOCTRINE.md` Lessons section updated if this PR fixes a real failure
- [ ] `docs/ERROR_HANDLING.md` updated if a new error path is added
- [ ] `CHANGELOG.md` entry added (if user-visible change)

## Git

- [ ] Branch is up to date with `main`
- [ ] No `state.json`, `bridge.log`, or `config.json` staged
- [ ] Commit message follows `<type>(<scope>): <subject>` — imperative, <72 chars

---

## Quick Validation

```bash
# Lint + types
ruff check src/ tests/ && ruff format --check src/ tests/
mypy --strict src/

# Tests
pytest -m "unit or property" -v

# Secret scan
gitleaks detect --no-banner

# Dead code
vulture src/
```

---

**Sign-off:** _________________ **Date:** _________________ **Status:** ☐ Approved ☐ Changes Requested

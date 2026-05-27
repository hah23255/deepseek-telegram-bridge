# Master Tester Doctrine — Engineering Plan

## 1. System Overview

The Master Tester Doctrine is a comprehensive testing methodology for TypeScript/React monorepos. Born from battle-hardened experience in multi-million-line codebases, it provides 10 non-negotiable laws, advanced testing patterns, and production-grade tooling.

### 1.1 Architecture

```
┌──────────────────────────────────────────────┐
│           MASTER TESTER DOCTRINE              │
│                                               │
│  ┌─────────┐  ┌──────────┐  ┌─────────────┐  │
│  │ 10 Laws │  │ Advanced │  │ Source Code  │  │
│  │ (Core)  │  │ Patterns │  │ (Utilities)  │  │
│  └────┬────┘  └────┬─────┘  └──────┬──────┘  │
│       │            │               │          │
│  ┌────▼────────────▼───────────────▼──────┐   │
│  │         CI GATE ENFORCEMENT            │   │
│  │  ci-gate.sh + dependency-cruiser       │   │
│  └────────────────────────────────────────┘   │
│                                               │
│  ┌────────────────────────────────────────┐   │
│  │         AGENT INTEGRATION               │   │
│  │  SKILL.md + AGENTS.md + subagent prompt │   │
│  └────────────────────────────────────────┘   │
└──────────────────────────────────────────────┘
```

### 1.2 Component Inventory

| Component | Format | Purpose |
|-----------|--------|---------|
| 10 Laws | Markdown | Non-negotiable testing rules |
| Oath of the Master Tester | Markdown | Advanced patterns (Books IX-XIII) |
| Unit Testing Rule Book | Markdown | Top 10 unit test rules |
| Modern TS Tester's Guideline | Markdown | Books I-IV: philosophy, trophy, architecture |
| Expanded Guideline | Markdown | Books V-VIII: time, async, hooks, coverage |
| Vanguard of TS Testing | Markdown | Books IX-XIII: quantum, concurrency, types |
| SKILL.md | Markdown | Agent skill with 4-phase execution protocol |
| AGENTS.md | Markdown | Agent integration rules |
| subagent-prompt.md | Markdown | Injection prompt for sub-agent tasks |
| Source utilities | TypeScript | Factories, MSW handlers, strict mocks, deferred |
| Configs | TypeScript/JS/JSON | Vitest, dependency-cruiser, Biome |
| Scripts | Bash | Install, verify, CI gate, quality check |

## 2. The 10 Laws (Enforcement Matrix)

| # | Law | CI Enforcement | Agent Enforcement |
|---|-----|---------------|------------------|
| 1 | Never modify test to fix CI | Code review gate | SKILL.md Phase 1 |
| 2 | Test behaviour, not implementation | depcruiser rules | AGENTS.md rules |
| 3 | AAA pattern | Quality check script | SKILL.md Phase 3 |
| 4 | DAMP over DRY | Code review | SKILL.md anti-patterns |
| 5 | Isolated tests | vitest --pool=threads | beforeEach/afterEach |
| 6 | MSW for HTTP | ci-gate.sh check | SKILL.md "never mock fetch" |
| 7 | Ban `as any` | ci-gate.sh grep | SKILL.md + strict-mock utility |
| 8 | Deterministic tests | vi.useFakeTimers() | Quality check script |
| 9 | One concept per test | Code review | SKILL.md Phase 3 |
| 10 | No tautological tests | Quality check script | SKILL.md Phase 1 |

## 3. Deployment Path

### Phase 1: Install
```bash
bash scripts/install.sh
```

### Phase 2: Verify
```bash
bash scripts/verify.sh
```

### Phase 3: Quality Audit
```bash
bash scripts/test-quality-check.sh
```

### Phase 4: CI Integration
```yaml
# .github/workflows/test-quality.yml
- name: Master Tester Gate
  run: bash scripts/ci-gate.sh
```

### Phase 5: Agent Integration
```bash
# Claude Code (and compatible agents)
cp -r . ~/.claude/skills/master-tester-doctrine/

# Or install the .skill bundle directly
unzip master-tester-doctrine.skill -d ~/.claude/skills/
```

See [`INTEGRATION-GUIDE.md`](./INTEGRATION-GUIDE.md) for Cursor, OpenCode, and custom-agent recipes.

## 4. Failure Modes

| Failure | Detection | Recovery |
|---------|-----------|----------|
| `as any` in test | CI gate grep | Replace with `satisfies` or `Partial<T>` |
| Circular dependency | depcruiser | Refactor to unidirectional import |
| Flaky test | Quality check | Quarantine with `.skip`, root cause analysis |
| Over-mocking | Quality check | Remove mock, test real integration |
| Shared state | Quality check | `beforeEach` reset, factory pattern |
| Dead code | knip | Remove or document as intentional |

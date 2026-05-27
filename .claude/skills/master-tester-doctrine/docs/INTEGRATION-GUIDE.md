# Master Tester Doctrine — Integration Guide

> How to wire the doctrine into a project, an AI agent, and a CI pipeline. Platform-agnostic.

---

## 1. Installing The Skill For An AI Agent

The doctrine ships as a self-contained skill bundle. Any agent that loads markdown skills (Claude Code, Cursor, OpenCode, custom agents with system-prompt augmentation) can adopt it.

### Claude Code (and compatible)

```bash
# Copy the bundle into your skills directory
cp -r master-tester-doctrine ~/.claude/skills/

# Or, if installed via the .skill archive:
unzip master-tester-doctrine.skill -d ~/.claude/skills/
```

The agent picks it up the next time a relevant task is invoked. SKILL.md §0 defines the trigger conditions.

### Cursor / Editor-Integrated Agents

Reference SKILL.md from your `.cursorrules` or equivalent system-prompt file:

```
@./skills/master-tester-doctrine/SKILL.md
```

### Custom Agents With System-Prompt Augmentation

Prepend the contents of [`SOUL.md`](../SOUL.md) and [`SKILL.md`](../SKILL.md) to the agent's system prompt. Load [`references/`](../references/) files on demand for the specific task at hand.

### Sub-Agent Dispatch

When spawning sub-agents for test tasks, include [`src/subagent-prompt.md`](../src/subagent-prompt.md) in the task payload. This propagates the doctrine into the sub-agent's context without requiring the sub-agent to load the full skill.

---

## 2. Installing Into A Project

```bash
cd <your-project>
bash <skill-path>/scripts/install.sh
bash <skill-path>/scripts/verify.sh
```

The install script:

1. Installs the dev dependencies (`vitest`, `@testing-library/react`, `msw`, `fast-check`, `@faker-js/faker`, `dependency-cruiser`)
2. Copies the configs (`vitest.config.ts`, `.dependency-cruiser.js`, `biome.json`) — refuses to overwrite existing files
3. Creates the scaffold directories (`src/test-utils/`, `src/factories/`, `src/mocks/`)
4. Copies the bundled test utilities (strict mock, deferred, flush promises) and the MSW server scaffold
5. Creates `vitest.setup.ts` if absent

After install, verify with `scripts/verify.sh`.

---

## 3. CI Integration

### GitHub Actions

```yaml
# .github/workflows/test-quality.yml
name: Test Quality
on: [pull_request, push]
jobs:
  quality-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
        with: { version: 9 }
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: 'pnpm' }
      - run: pnpm install --frozen-lockfile
      - run: bash scripts/ci-gate.sh           # doctrine rules
      - run: pnpm vitest run --coverage         # the test suite
      - run: pnpm exec depcruise src --config configs/.dependency-cruiser.js
```

### GitLab CI

```yaml
test-quality:
  image: node:20
  script:
    - corepack enable
    - pnpm install --frozen-lockfile
    - bash scripts/ci-gate.sh
    - pnpm vitest run --coverage
```

### Pre-Commit Hook (Husky)

```bash
# .husky/pre-commit
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

# Master Tester quick gate (fast checks only)
grep -rn "as any" --include="*.test.*" src/ tests/ 2>/dev/null && echo "✗ 'as any' found in tests — remove before commit" && exit 1
grep -rn "@ts-ignore" src/ 2>/dev/null && echo "✗ '@ts-ignore' found — use @ts-expect-error" && exit 1
exit 0
```

---

## 4. Adopting In An Existing (Brownfield) Project

### Assessment Protocol — Run The Brutal Critique First

Before writing a single new test, run the quality audit on the existing suite:

```bash
bash scripts/test-quality-check.sh
```

It identifies:

- Tautological tests (testing JS mechanics, not business logic)
- Test pollution (shared state between tests)
- Over-mocking (mocking away the thing you're testing)
- Implementation-coupled assertions
- Real timers and other determinism leaks

### Incremental Adoption Roadmap

| Week | Action                                                                |
|------|------------------------------------------------------------------------|
| 1    | Install configs (`vitest.config.ts`, `.dependency-cruiser.js`, `biome.json`); no test changes |
| 2    | Run `scripts/test-quality-check.sh`; triage findings; create tickets   |
| 3    | Convert 10% of tests to doctrine patterns (factories, MSW, strict mocks) |
| 4    | Enable CI gate on **new/modified files only** (graduated enforcement)  |
| 5    | Full CI gate enforcement (`scripts/ci-gate.sh` is required)            |
| 6    | Add property-based fuzzing to critical paths (parsers, payments, dates) |

### Brownfield Discipline

1. **Never rewrite passing tests** just to match the doctrine — the doctrine is for new and modified tests. Drive-by rewrites create unreviewable diffs.
2. **Apply the doctrine to new tests** — lead by example. The team will copy the pattern.
3. **Refactor flaky tests immediately** — every day they remain, they erode trust.
4. **Enable CI gates incrementally** — start with `as any`, then circular deps, then full mutation testing.
5. **Run the quality check monthly** — track the trend (improving / flat / regressing), not the absolute number.

---

## 5. Sub-Agent / Multi-Agent Workflow Guidance

When delegating test work to a sub-agent (or a parallel agent):

- Attach [`src/subagent-prompt.md`](../src/subagent-prompt.md) to the task payload.
- For complex test rewrites, the agent should be allowed to call the Zero-Trust Protocol — i.e., spend tokens on CHECK 1 and CHECK 2 before writing code.
- The sub-agent's output is the test file *plus* a written Phase 4 defense citing which test proves which behavior.

### Model Selection (general guidance, platform-agnostic)

Model choice depends on the platform; the principles are:

| Task                          | Choose a model that is…                                       |
|-------------------------------|---------------------------------------------------------------|
| Writing routine unit tests    | Fast, good at standard patterns, cheap                        |
| Debugging flaky tests         | Strong at root-cause / multi-step reasoning                   |
| Writing integration tests     | Good at multi-file context and async reasoning                |
| Architecture boundary tests   | Strong at structural / AST-level reasoning                    |
| Security / adversarial tests  | Good at adversarial thinking and edge-case generation         |
| Test suite review / synthesis | Strong at judgment, long context, terse output                |

Pick the equivalent capability in your platform; the doctrine itself is agnostic.

---

## 6. Metrics That Matter

| Metric                          | Target                                          | Why                                                  |
|---------------------------------|--------------------------------------------------|------------------------------------------------------|
| Flaky test rate                 | 0%                                               | One flake erodes trust in the entire suite           |
| `as any` count in test files    | 0                                                | Type coercion in tests hides production type bugs    |
| Circular dependencies           | 0                                                | Architectural cancer                                 |
| Unit test runtime               | < 30s for the whole suite                        | Fast feedback loop                                   |
| Integration test runtime        | < 5min for the whole suite                       | Tolerable for CI                                     |
| Mutation score (critical paths) | > 80%                                            | Mutation is the truth check; coverage is vanity      |
| Code coverage                   | A **floor**, not a target — 70/75/80/80 minimum  | Coverage measures what ran, not what was tested      |
| `.skip` count without ticket    | 0                                                | Quarantine carries a four-tuple (why, ticket, owner, date) |

---

## 7. Where To Go Next

- The operational rules: [`../references/golden-rules.md`](../references/golden-rules.md)
- The Zero-Trust Protocol: [`../references/zero-trust-protocol.md`](../references/zero-trust-protocol.md)
- The forbidden patterns: [`../references/anti-patterns.md`](../references/anti-patterns.md)
- The advanced techniques: [`../references/advanced-patterns.md`](../references/advanced-patterns.md)
- A worked end-to-end example: [`../references/workflow-example.md`](../references/workflow-example.md)
- The long-form doctrine: [`../doctrine/INDEX.md`](../doctrine/INDEX.md)

> The doctrine is platform-agnostic.
> The integration is your job — but the integration recipes are battle-tested.

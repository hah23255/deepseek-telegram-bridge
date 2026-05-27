# Master Tester Doctrine

> **40+ years in the trenches. Golden Rules. No bullshit. Brutal reality check.**
> **No compromises. No assumptions. Zero-trust policy. No cutting corners.**
> **Check → Check → Verify → Validate → Execute. Attention to the detail.**

A complete, publication-ready testing doctrine for TypeScript / React / Node monorepos, packaged as a Claude Code skill (and usable as a system-prompt augmentation in any agent that supports skills).

[![Version](https://img.shields.io/badge/version-2.0.0-blue)](./CHANGELOG.md)
[![Stack](https://img.shields.io/badge/stack-Vitest%20%C2%B7%20MSW%20%C2%B7%20Playwright-green)](./SKILL.md)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](./LICENSE)

---

## What This Is

This skill encodes a **Principal Software Engineer in Test** (40+ years of field experience) who:

- Writes tests for **deployment confidence**, not for coverage metrics
- Operates under a **Zero-Trust Verification Protocol** (Check → Check → Verify → Validate → Execute) before every consequential action
- Enforces **15 Golden Rules** as non-negotiable operational laws
- Runs the **Brutal Critique → Master-Class Rewrite** workflow on every test task
- Speaks **plainly** — no corporate hedging, no "I think" when "I observed" is more accurate

This is not a tutorial. It is a doctrine you adopt or you do not.

---

## Quick Install

```bash
# Clone or copy into your agent's skills directory
cp -r master-tester-doctrine ~/.claude/skills/

# (Optional) install configs + utilities into your project
cd <your-project>
bash <skill>/scripts/install.sh
bash <skill>/scripts/verify.sh
```

Then, in your agent: invoke the skill any time you write, review, or debug tests. See [`SKILL.md`](./SKILL.md) §0 for the full trigger conditions.

---

## What's Inside

| Path                                       | Purpose                                                                  |
|--------------------------------------------|--------------------------------------------------------------------------|
| [`SKILL.md`](./SKILL.md)                   | Operational entry point — persona, protocol, rules, workflow, stack       |
| [`SOUL.md`](./SOUL.md)                     | The why — identity, posture, covenant, the voice in your head             |
| [`AGENTS.md`](./AGENTS.md)                 | Wiring instructions for AI agents (Claude Code, Cursor, OpenCode, etc.)   |
| [`references/`](./references/)             | Operational references (loaded on demand)                                 |
| └─ `zero-trust-protocol.md`                | The 5-gate verification procedure with concrete commands                  |
| └─ `golden-rules.md`                       | The 15 non-negotiable laws, with why and how                              |
| └─ `anti-patterns.md`                      | Forbidden patterns with the fix for each                                  |
| └─ `advanced-patterns.md`                  | Property-based, race conditions, type-level, mutation, IoC                |
| └─ `workflow-example.md`                   | Worked end-to-end Brutal Critique → Master-Class Rewrite                  |
| [`doctrine/`](./doctrine/)                 | Long-form prose canon — the "Books" of the doctrine                       |
| └─ `INDEX.md`                              | Map of Golden Rules / advanced patterns to long-form chapters             |
| [`src/`](./src/)                           | Production-grade test utilities (factories, strict mocks, deferred, MSW)  |
| [`configs/`](./configs/)                   | Drop-in Vitest, dependency-cruiser, Biome configs                         |
| [`scripts/`](./scripts/)                   | install / verify / ci-gate / test-quality-check                           |
| [`docs/`](./docs/)                         | Engineering plan, integration guide, patterns reference                   |

---

## The 15 Golden Rules (Summary)

1. Never modify a test to silence CI — fix the code
2. Test behavior, not implementation
3. AAA pattern, every test
4. DAMP over DRY in tests
5. Isolated tests — random order must pass
6. MSW for HTTP, always
7. Ban `as any` in test files
8. Deterministic tests — fake everything non-deterministic
9. One logical concept per test
10. No tautological tests
11. Verify the test fails for the right reason
12. Zero tolerance for flakiness — quarantine same day
13. Tests are production code
14. Coverage is vanity; mutation score is truth
15. Every `.skip` carries a why, a ticket, an owner, a date

Full rationale and enforcement in [`references/golden-rules.md`](./references/golden-rules.md).

---

## The Zero-Trust Protocol (Summary)

Five gates. No exceptions. Before any consequential action:

```
CHECK 1   The artifact exists and is what you think it is
CHECK 2   The contract is what you think it is
VERIFY    The behavior is what you think it is (watch it fail; watch it pass)
VALIDATE  The intent is met (the user's, the spec's, the type's)
EXECUTE   Only now — commit, push, deploy
```

Each gate produces evidence. Recollection is not evidence. "Should be fine" is not evidence. Full protocol with concrete commands in [`references/zero-trust-protocol.md`](./references/zero-trust-protocol.md).

---

## The Stack

| Layer                | Tool                                |
|----------------------|--------------------------------------|
| Test runner          | **Vitest**                           |
| Component testing    | **React Testing Library**            |
| Browser e2e          | **Playwright**                       |
| Network mocking      | **MSW (Mock Service Worker)**        |
| Property-based       | **fast-check**                       |
| Type-level testing   | **expect-type**, **tsd**             |
| Architecture gates   | **dependency-cruiser**, **knip**     |
| Mutation testing     | **Stryker**                          |
| Lint / format        | **Biome**                            |
| Bundled fixtures     | **@faker-js/faker**                  |

Drop-in configs in [`configs/`](./configs/).

---

## Requirements

- Node.js ≥ 18
- A test runner (Vitest preferred; Jest tolerated)
- An agent that supports skills or system-prompt augmentation (Claude Code, Cursor, OpenCode, custom)

For project-side installation, the install script will install missing dev dependencies:

```
vitest · @testing-library/react · @testing-library/jest-dom · msw
fast-check · @faker-js/faker · dependency-cruiser
```

---

## Versioning

Semantic versioning. See [`CHANGELOG.md`](./CHANGELOG.md). The current version is the value in [`SKILL.md`](./SKILL.md) frontmatter.

---

## License

[MIT](./LICENSE).

---

## The Oath

> *"I do not test to achieve a percentage. I test to sleep soundly.*
> *I assume the network is hostile, the user is chaotic, and time is an illusion.*
> *My tests are the unbreakable contract between the present codebase and its future self."*

Full creed and covenant in [`SOUL.md`](./SOUL.md).

# The Golden Rules — Operational Canon

> The 15 non-negotiable laws. Each rule carries its **why** (the cost of breaking it) and its **how** (the concrete enforcement).

---

## Rule 1 — Never Modify A Test To Make CI Green

**The rule.** When a test fails, the failing artifact is the *code*, not the test. The test is a contract you signed; the code violated it. Fix the code. If the contract itself was wrong, *first* prove the new contract is correct (write a failing test for the new behavior, watch it fail for the right reason), *then* update the old test.

**Why.** Weakening a test to silence CI is forgery. It trains the team to ignore red and produces suites that "pass" while production breaks. Every weakened test is a future incident.

**How (enforce).**
- Code review gate: any diff that modifies a test alongside the code it tests gets explicit justification in the PR body.
- Cultural: "the test went red, so I fixed the test" is grounds for rejecting the PR with no further discussion.

---

## Rule 2 — Test Behavior, Not Implementation

**The rule.** Assertions target the public API and the user-visible outcome. Never reach into private state, internal hooks, render counts, or DOM structure beyond what an accessibility tree exposes.

**Why.** Implementation-coupled tests break on every refactor without indicating that anything is actually wrong. The team learns to dismiss test failures as "false alarms," and real failures slip through.

**How (enforce).**
- Use `getByRole`, `getByLabelText`, `getByText` — in that priority order.
- `data-testid` is last resort. CSS classes and `nth-child` are forbidden.
- For non-UI code: assert on return value + observable side effect (DB row, emitted event, file written). Never on intermediate variables.

---

## Rule 3 — AAA Pattern, Every Test

**The rule.** Every test is visually separated into **Arrange**, **Act**, **Assert** — even if separated only by a blank line and a comment. One action per Act. Assertions only in Assert.

**Why.** A reader who has never seen the file should be able to identify the setup, the trigger, and the expectation in under 5 seconds. AAA is the lowest-cost test-readability standard.

**How (enforce).**
```ts
it('should X when Y', async () => {
  // ARRANGE
  const project = createProject({ status: 'draft' });
  server.use(http.get('/api/projects/:id', () => HttpResponse.json(project)));

  // ACT
  render(<ProjectPage id={project.id} />);
  await user.click(screen.getByRole('button', { name: 'Submit' }));

  // ASSERT
  expect(await screen.findByText('Submitted')).toBeVisible();
});
```

---

## Rule 4 — DAMP Over DRY In Tests

**The rule.** **D**escriptive **A**nd **M**eaningful **P**hrases. Some duplication in the Arrange phase is a feature, not a bug. A test must be readable top-to-bottom without scrolling to a helper file.

**Why.** Tests that share complex setup helpers become unreadable, and "fixing a test" turns into archaeology across 5 files. Tests are documentation of behavior; they must read like prose.

**How (enforce).**
- Allow one level of helper extraction (factories, `renderWithProviders`).
- Forbid nested `beforeEach` chains across multiple `describe` blocks.
- A test reader should not need to scroll up more than once to understand the Arrange.

---

## Rule 5 — Isolated Tests

**The rule.** No shared mutable state between tests. The suite must pass when executed in random order, in parallel, or in single-file isolation. Every test owns its setup; every test cleans up.

**Why.** Test pollution causes the most expensive flakes — passes locally, fails in CI, can't reproduce, blocks the team for days. It also makes failures non-diagnostic ("did test A break, or did test C break test A?").

**How (enforce).**
- `vitest --pool=threads` for default isolation.
- `beforeEach` resets MSW handlers (`server.resetHandlers()`), DOM (`cleanup()`), timers (`vi.useRealTimers()` if any test enabled fakes).
- Module-level mutable state (`let counter = 0`) is forbidden in test files.
- Periodically run `vitest run --shard 1/N` and `--shard 2/N` to catch ordering dependencies.

---

## Rule 6 — Never Mock `fetch` Or `axios` Directly

**The rule.** All HTTP mocking goes through **MSW (Mock Service Worker)**. Direct stubs of `fetch`, `axios`, or HTTP clients are forbidden.

**Why.** MSW intercepts at the network layer, so the production code path runs unchanged — your `fetch` is real, your retry logic is real, your error handling is real. Stubbing `fetch` lets bugs in the request pipeline ship to production.

**How (enforce).**
- `scripts/ci-gate.sh` greps for `vi.fn().*fetch` / `vi.mock('axios')` / `jest.mock('axios')` and fails the build.
- All MSW handlers live in `src/mocks/handlers.ts`; per-test overrides use `server.use(..., { once: true })`.
- `onUnhandledRequest: 'error'` in `vitest.setup.ts` — unmocked requests fail loudly, never silently 404.

---

## Rule 7 — Ban `as any` In Test Files

**The rule.** `as any`, `as unknown as T`, and `@ts-ignore` are forbidden in `*.test.*` and `*.spec.*` files. Use `satisfies`, `Partial<T>`, `vi.mocked(realFn)`, or `createStrictMock<T>()`.

**Why.** Type coercion in tests masks production type errors. The whole point of TypeScript-tested code is that the test asserts against the same type contract production code expects. `as any` short-circuits that contract.

**How (enforce).**
- `scripts/ci-gate.sh` greps for `as any` in test files and fails the build.
- `@ts-ignore` is replaced with `@ts-expect-error` + a comment naming the reason.
- For "partial mock of complex type": use `createStrictMock<T>(overrides)` — Proxy throws on unmocked property access (see [`src/test-utils/strict-mock.ts`](../src/test-utils/strict-mock.ts)).

---

## Rule 8 — Deterministic Tests

**The rule.** No real timers, no real clocks, no real randomness, no real network. `vi.useFakeTimers()` for time. Seeded PRNG for randomness. MSW for network. Fixed dates for `Date.now()`.

**Why.** Non-determinism is the single largest source of flakes. A 1% flake rate across 8,000 tests means 80 random failures per run — the team will start hitting "re-run" reflexively, and real failures get lost in the noise.

**How (enforce).**
- `scripts/test-quality-check.sh` flags `setTimeout` / `setInterval` / `Math.random` / `Date.now` usages in test files.
- For seeded randomness, install `seedrandom` and hijack `Math.random` in `vitest.setup.ts` with a known seed.
- For Faker, set `faker.seed(N)` per test file or globally.

---

## Rule 9 — One Logical Concept Per Test

**The rule.** A single `it()` block tests one behavior. Multiple `expect()` calls are fine if they all assert the same concept; testing three different behaviors in one block is forbidden.

**Why.** If a block has 15 assertions across 5 behaviors and assertion 2 fails, you learn nothing about behaviors 3–5. Tight scoping = fast diagnosis = fast fix.

**How (enforce).**
- Code review: a test that "tests login, then redirect, then session, then logout" is rejected and split.
- Naming discipline: the `it('should X when Y')` name must describe **one** behavior. If you find yourself writing "and also Z," split.

---

## Rule 10 — No Tautological Tests

**The rule.** Never test that JavaScript works as JavaScript. `expect(typeof fn).toBe('function')`, `expect(2 + 2).toBe(4)`, `expect(arr.length > 0).toBe(true)` — all forbidden.

**Why.** Tautological tests pad coverage metrics without providing any verification. They train the team that "writing tests" is a paperwork exercise rather than an engineering one.

**How (enforce).**
- `scripts/test-quality-check.sh` greps for the most common tautology patterns.
- Code review: any test where the assertion is logically true given only the language spec (not the business logic) is rejected.

---

## Rule 11 — Verify The Test Fails For The Right Reason

**The rule.** A test is unproven until you have **watched it fail** by intentionally breaking the production code, then **watched it pass** by restoring the code. Green tests that have never been red are not real tests.

**Why.** It is trivially easy to write a test that asserts the value the mock returns, which would pass even if the production code did nothing. Mutation testing (Stryker) institutionalizes this principle; the manual version is the fail-then-pass cycle in [`references/zero-trust-protocol.md`](./zero-trust-protocol.md#verify).

**How (enforce).**
- Personal discipline during VERIFY gate.
- Stryker mutation testing as a periodic (weekly / per-PR for critical modules) check. Mutation score > 80% on business-critical code.

---

## Rule 12 — Zero Tolerance For Flakiness

**The rule.** A flaky test is quarantined the **same day** it is observed (`.skip` with a comment citing the ticket ID). Root cause is found within **one week**. Re-enabling without fixing the root cause is forbidden.

**Why.** A 0.1% flake rate is a 10% chance of red CI on a 100-test suite — enough to destroy trust. Once the team stops trusting red, the suite is dead even if every test still runs.

**How (enforce).**
- CI: a test that fails once in 100 runs is flagged for quarantine review.
- Tracking: a dashboard of currently-quarantined tests with quarantine date + owner + root-cause ticket. Zero exceptions, zero "we'll get to it."

---

## Rule 13 — Tests Are Production Code

**The rule.** Test files are linted, typed, formatted, and refactored to the same standard as production code. No "tests are throwaway, we'll clean up later." There is no later.

**Why.** Messy test code accumulates friction. After three months of friction, the team stops writing tests. After six months, the suite is unmaintainable.

**How (enforce).**
- Biome / ESLint configured to lint `**/*.test.*` and `**/*.spec.*`.
- `tsconfig.json` `include` covers test files. `strict: true` everywhere.
- Code review applies the same quality bar to tests as to production.

---

## Rule 14 — Coverage Is A Vanity Metric

**The rule.** Line / branch coverage is not the goal. **Mutation score** and **behavior coverage** are. 100% line coverage of meaningless tests is worse than 60% line coverage of strong tests.

**Why.** Coverage tools measure which lines *ran* during a test, not which lines were *tested*. A test that imports a module and asserts nothing scores 100% coverage on that module. The dashboard turns green; production stays broken.

**How (enforce).**
- Vitest coverage thresholds in `configs/vitest.config.ts` are **floors**, not targets. Branches 70%, functions 75%, lines 80%, statements 80%.
- Critical business logic (payments, auth, data transforms) targets 100% line + branch coverage **and** > 80% mutation score.
- Stop chasing the dashboard. Start chasing "would I deploy on Friday?"

---

## Rule 15 — Quarantine, Document, Ticket

**The rule.** Every `.skip` carries (a) a comment explaining *why*, (b) a ticket ID, (c) an owner, (d) an expected-fix date. Tests skipped without those four are deleted.

**Why.** "Temporary" `.skip` calls become permanent. A `.skip` with no documentation is invisible debt — the test still appears in the file (signaling coverage) but does not run. The lie is louder than no test at all.

**How (enforce).**
- Code review: any new `.skip` without the four-tuple is rejected.
- Monthly audit: walk every `.skip` in the codebase, confirm ticket is still open, confirm owner still owns, escalate if stale.

---

## The Summary Card

```
1. Never weaken a test to silence CI
2. Test behavior, not implementation
3. AAA always — Arrange, Act, Assert
4. DAMP > DRY in tests
5. Isolated tests — random order must pass
6. MSW for HTTP, always
7. Ban `as any` in tests
8. Deterministic — fake everything non-deterministic
9. One concept per test
10. No tautological tests
11. Watch the test fail before trusting it green
12. Zero tolerance for flakiness — quarantine same day
13. Tests are production code
14. Coverage is vanity; mutation score is truth
15. Every .skip carries a why, a ticket, an owner, a date
```

---

> The rules are non-negotiable.
> The doctrine is the rules in motion.
> The soul is why we care about either.

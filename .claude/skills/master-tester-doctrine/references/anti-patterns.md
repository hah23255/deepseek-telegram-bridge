# Anti-Patterns — Forbidden On Sight

> Each pattern below has been observed in real codebases, causing real outages.
> The fix is mandatory, not advisory.

---

## Type-Safety Escapes

### `as any`
**Where seen.** Test files, mock builders, "I just need this to compile" moments.
**Why it ships bugs.** Coerces away the type contract the production code relies on. Production type-checks against `User`, the test mock is `as any`, and a property the production code reads (`user.email`) is missing from the mock. Mock returns `undefined`, the assertion still passes because the test asserted on `user.id`, and the bug ships.
**The fix.**
```ts
// ❌
const user = { id: '1' } as any;

// ✅
const user = createStrictMock<User>({ id: '1', name: 'Test' });
// or
const user = { id: '1', email: 'a@b.c', name: 'Test' } satisfies User;
```

### `@ts-ignore`
**Where seen.** Around lines TypeScript correctly rejects.
**Why it ships bugs.** Silences the error *forever*. When the signature changes and the line becomes valid again, `@ts-ignore` keeps suppressing — and now suppresses *new* errors you would have wanted to know about.
**The fix.** `@ts-expect-error` with a comment naming the reason. When the line becomes valid, `@ts-expect-error` itself becomes an error, forcing you to revisit.

### `as unknown as T`
**Where seen.** Double-cast laundering when `as T` is too obviously wrong.
**Why it ships bugs.** The laundering itself is evidence the types do not match. You are telling future-you "I checked, this is fine" — but the cast is the only proof, and that proof is circular.
**The fix.** If the types really should be related, write a guard function with runtime validation. If you are just trying to silence the compiler in a test, use `satisfies` or `createStrictMock`.

---

## Mocking Failures

### Mocking `fetch` / `axios` Directly
**Where seen.** `vi.fn().mockResolvedValue({ data: ... })`, `vi.mock('axios')`.
**Why it ships bugs.** Your production code's request pipeline (headers, retries, interceptors, error handling) is bypassed. The test exercises only the call site, not the integration with HTTP.
**The fix.** MSW handler. See [`src/mocks/handlers.ts`](../src/mocks/handlers.ts).

### Mocking The Unit Under Test
**Where seen.** Tests for `ProjectService` that mock `ProjectService.fetchProject` to return a fixture.
**Why it ships bugs.** You are testing the mock, not the unit. The actual implementation could be `throw new Error()` and the test would pass.
**The fix.** Mock the *boundary* (DB driver, HTTP client) one layer below the unit under test. The unit under test runs for real.

### Mocking Internal Helpers
**Where seen.** `vi.mock('./internal-helper')` for a same-file utility.
**Why it ships bugs.** Couples the test to the internal structure. Refactoring the helper out of existence breaks the test even though the externally observable behavior is unchanged.
**The fix.** If the helper is complex enough to deserve its own test, extract it into its own module. If not, test through the calling function.

### `Partial<T>` Mocks Without The Strict Mock
**Where seen.** `{ id: '1' } as Partial<User>` passed into code that reads `user.email`.
**Why it ships bugs.** TypeScript permits the missing property; the code accesses `undefined`; the test passes anyway because it asserts on `id`.
**The fix.** `createStrictMock<User>({ id: '1' })` — a Proxy that *throws* on any property access not in the override. Forces you to declare exactly what the code under test will read.

---

## Asynchrony Failures

### `await waitFor(() => expect(…).toBeInTheDocument())`
**Where seen.** Lazy migration from older RTL patterns.
**Why it ships bugs.** `waitFor` retries the entire callback on every poll, including any expensive query. Slower than necessary, and error messages on failure are vague ("Timed out after 5000ms").
**The fix.** `await screen.findByText('Loaded')` / `findByRole(...)` — built-in async wait with diagnostic failure messages.

### `setTimeout(…, 5000)` In Tests
**Where seen.** "Waiting for the animation to finish."
**Why it ships bugs.** Slow (5s per test), flaky (CI runners vary in speed), and bypasses the entire reason you wrote the animation timer in the first place.
**The fix.** `vi.useFakeTimers()` + `vi.advanceTimersByTime(5000)`. Test runs in milliseconds, deterministic across runners.

### `act()` Wrapping
**Where seen.** Wrapping every interaction in `act(() => { ... })` to silence the "not wrapped in act" warning.
**Why it ships bugs.** The warning is a *symptom*. The cause is that your test finished while the component was still rendering. Wrapping in `act()` hides the warning without addressing the cause — and the next state update silently slips outside the assertion window.
**The fix.** `await screen.findByText('Success')`. Asserting on the post-update state means the test naturally waits for the component to settle.

### Real Promises Without Flushing
**Where seen.** Click → assert with no await in between.
**Why it ships bugs.** The Promise resolution happens in a microtask after the synchronous click handler returns; the assertion runs *before* the microtask, sees stale state, fails. Then on the next test run, timing is slightly different and it passes — congratulations, you have a flake.
**The fix.** `await flushPromises()` between Act and Assert when fake timers are not in play. See [`src/test-utils/flush-promises.ts`](../src/test-utils/flush-promises.ts).

---

## Implementation Coupling

### Asserting On Component State
**Where seen.** `expect(wrapper.state('isLoading')).toBe(true)`, `expect(component.props.value).toBe(...)`.
**Why it ships bugs.** Refactoring the component to remove the state variable (move to context, hook, reducer) breaks the test even though behavior is unchanged. The team learns to dismiss test failures during refactors.
**The fix.** Assert on what the user sees. `expect(screen.getByRole('progressbar')).toBeVisible()`.

### CSS-Class Selectors
**Where seen.** `container.querySelector('.btn-primary')`, `wrapper.find('div.submit-button')`.
**Why it ships bugs.** Renaming a CSS class for visual reasons breaks the test even though the component still works. Locks the design system to the test suite.
**The fix.** `screen.getByRole('button', { name: 'Submit' })`. Tests the accessibility contract, which is also the user contract.

### `nth-child` Selectors
**Where seen.** "The third button in the second row."
**Why it ships bugs.** Adding a new menu item shifts every position; every test breaks.
**The fix.** `within(row).getByRole('button', { name: 'Approve' })`. Semantic, not positional.

---

## State Pollution

### Module-Level Mutable State
**Where seen.** `let createdId: string;` at the top of a test file, mutated by test A, read by test B.
**Why it ships bugs.** Tests pass when run in order, fail when run individually or in parallel. CI passes on Monday, fails on Tuesday because the test runner reshuffled.
**The fix.** Per-test setup in the Arrange block. If multiple tests genuinely need the same state, build it from a factory inside `beforeEach`.

### Forgetting To Reset MSW Handlers
**Where seen.** Test A overrides a handler with `server.use(...)`, test B inherits the override.
**Why it ships bugs.** Test B passes for the wrong reason — it's hitting test A's mock, not its own.
**The fix.** `afterEach(() => server.resetHandlers())` in `vitest.setup.ts`. Non-negotiable.

### Real Timers Leaking Between Tests
**Where seen.** Test A calls `vi.useFakeTimers()` but doesn't restore. Test B uses real `setTimeout` and never resolves.
**Why it ships bugs.** Hard-to-diagnose hangs in CI.
**The fix.** `afterEach(() => vi.useRealTimers())`. Or scope fake timers to a single `describe` block.

---

## Test-Design Failures

### Tautologies
**Where seen.** `expect(typeof handler).toBe('function')`, `expect(arr).toBeDefined()`, `expect(2 + 2).toBe(4)`.
**Why it ships bugs.** Adds zero verification, pads coverage, trains the team that "writing tests" is a paperwork exercise.
**The fix.** Delete the test. Replace with a test of the actual business logic.

### Multi-Concept Tests
**Where seen.** A single `it()` that "tests the login flow" with 12 assertions across 5 user actions.
**Why it ships bugs.** First failing assertion stops the test. You learn the suite is broken, not which 4 behaviors are also broken.
**The fix.** Split into 5 tests, each named for its single behavior.

### Snapshot Tests Without Review
**Where seen.** `expect(component).toMatchSnapshot()` with 200-line snapshot files committed unread.
**Why it ships bugs.** Snapshots that nobody reads get auto-updated on every visual change. The "test" is just a hash of the current output — proves nothing about correctness.
**The fix.** Snapshot only small, semantically meaningful output (e.g., the JSON body of a generated API request). Review every snapshot diff in PR.

---

## CI / Operational Failures

### `.skip` Without A Ticket
**Where seen.** `it.skip('TODO: fix later', ...)`.
**Why it ships bugs.** "Later" never comes. The test stays in the file (signaling coverage) but never runs. The bug it was supposed to catch ships.
**The fix.** Every `.skip` has a comment with the four-tuple: why, ticket ID, owner, expected fix date. Audit monthly.

### Retry-On-Failure In CI Config
**Where seen.** `retries: 3` in CI runner config to "handle flakes."
**Why it ships bugs.** Institutionalizes flakiness. The team stops investigating because "it passed on retry 2." Real bugs that manifest as flakes ship silently.
**The fix.** `retries: 0` in CI. Failing tests get fixed or quarantined — never auto-retried.

### `--bail` Disabled Locally
**Where seen.** Engineers waiting 2 minutes for 500 downstream tests to fail after the 3rd test broke fundamentals.
**Why it ships bugs.** Wastes engineer attention; encourages "let me just commit and let CI tell me."
**The fix.** `vitest --bail=1` locally. Fast feedback on the first real failure.

---

## The Defensive Stance

When you see any of these in a PR, the correct response is **not** "let's add a follow-up ticket." The correct response is **"this PR does not merge until this is fixed."**

The doctrine has no provision for "we'll get to it." Every doctrine violation is a future incident with the merge timestamp engraved on it.

---

> Anti-patterns are not bad style.
> They are bugs whose blast radius has not landed yet.

# Master Tester — Sub-Agent Injection Prompt

Include this in sub-agent task payloads when the task involves writing tests.

---

## Testing Standards (MANDATORY)

Follow these testing principles for ALL test code:

### Core Rules
1. **Test Behavior, Not Implementation** — test public API, use `screen.getByRole()` over internal state
2. **DAMP over DRY** — copy-paste in tests is fine for readability; each test self-contained
3. **AAA Pattern** — Arrange, Act, Assert. Clear sections, one assert concept per test
4. **Integration over Unit (Trophy Model)** — test the hook that calls the fetcher, not just the fetcher
5. **Mutation Testing** — a test is only valid if breaking prod code makes it fail
6. **Type-Safe Mocks** — ban `as any`. Use `satisfies`, `Partial<T>`, or `vi.mocked()`
7. **Object Mother / Factory Pattern** — no hardcoded 50-property objects in tests

### Patterns
- **Property-Based Testing:** Use `fast-check` for parsers, date math, financial calculations
- **Network Mocking:** Use MSW. Never mock `fetch` directly.
- **Time Control:** `vi.useFakeTimers()` + `vi.advanceTimersByTime()`. Never real `setTimeout`.
- **Strict Mocks (Poison Pill):** Use `Proxy` to throw on unmocked property access
- **Branded Types:** Use compile-time type brands over runtime assertions
- **Exhaustive Switches:** Assign default case to `never` to catch new union members

### Anti-Patterns
- ❌ `as any` in mocks
- ❌ `@ts-ignore` (use `@ts-expect-error` instead)
- ❌ `Math.random()` without seeded PRNG
- ❌ Direct `window.location` access (use IoC)
- ❌ `act()` wrapping (let RTL handle it, use `findByText`)
- ❌ Flaky tests in CI (quarantine immediately)

### Naming
```
describe('[UnitName]', () => {
  it('should [expected behavior] when [condition]', () => {
```

### The Oath
"I test to sleep soundly. I assume the network is hostile, the user is chaotic, and time is an illusion."

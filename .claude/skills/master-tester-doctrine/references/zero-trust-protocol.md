# Zero-Trust Verification Protocol

> **Check → Check → Verify → Validate → Execute.**
> Five gates. No exceptions. The protocol applies to the agent before it touches the code, and to the code before it touches production.

This document is the operational expansion of the protocol stated in [`SKILL.md §2`](../SKILL.md). It exists so that there is never ambiguity about *what* to do at each gate — only concrete actions, concrete commands, concrete evidence.

---

## 0. The Premise

> Trust no symbol you have not read.
> Trust no contract you have not grep'd.
> Trust no test you have not seen fail for the right reason.
> Trust no green check on CI you have not personally re-run from scratch.
> Trust no "should be fine" — yours or anyone else's.

Every gate produces **evidence**. Evidence is a file path + line number, a command + its output, or a screenshot of the failing state. Recollection is not evidence. "I'm pretty sure" is not evidence. A passing test you did not watch fail first is not evidence.

---

## 1. Gate Definitions

### CHECK 1 — The Artifact Exists And Is What You Think It Is

**Goal:** Confirm the thing you are about to touch is the thing you think you are touching.

**Required actions (pick the ones that apply):**

| Action                                      | Concrete command                                  |
|---------------------------------------------|---------------------------------------------------|
| The file exists at the path                 | `ls <path>` / `stat <path>` / `Read <path>`       |
| The symbol exists with that name            | `grep -rn "<symbol>" <root>` / LSP go-to-def      |
| The version / commit is current             | `git log -1 -- <path>` / `git blame <path>`       |
| The branch is the branch you intend         | `git status` / `git branch --show-current`        |
| The dependency version matches assumption   | `cat package.json` / `pnpm why <pkg>`             |
| The env var is actually set                 | `printenv <NAME>` (mask before paste in chat)     |

**Pass condition:** every assumption about *what exists* has been confirmed against the live filesystem in this session. Memory from a prior session does not count.

**Common failure mode:** acting on a memory of "the function is called `extractClerkAllowedOrigin`" when it has since been renamed, moved, or deleted. The fix is one `grep`. Run it.

---

### CHECK 2 — The Contract Is What You Think It Is

**Goal:** Confirm the *shape* and *behavior* of the API you are about to use or test matches the shape and behavior you believe.

**Required actions:**

| Action                                       | Concrete command                                            |
|----------------------------------------------|-------------------------------------------------------------|
| Read the function signature in full          | `Read <file>` (don't skim — read parameters and return)     |
| Read the JSDoc / type definition             | LSP hover or `Read` the `.d.ts` if generated                |
| List every caller                            | `grep -rn "<symbol>(" <root>` or LSP find-references        |
| Confirm the assumed throw / error contract   | `grep -rn "throw" <file>` and re-read each branch           |
| Confirm the assumed mutation / side effect   | `grep -rn "this\.\|\.push(\|\.set(\|delete " <file>`        |
| For mocks: match the real signature exactly  | Use `vi.mocked(realFn)` or `satisfies` to enforce shape     |

**Pass condition:** you can write the function's contract on a whiteboard from memory — parameters in, return out, errors thrown, side effects produced — and a colleague reading the file would not correct a single line.

**Common failure mode:** mocking a function with a `Partial<T>` that omits a property the production code actually reads, returning `undefined`, and silently corrupting the assertion. Defense: the **Poison Pill Strict Mock** in [`src/test-utils/strict-mock.ts`](../src/test-utils/strict-mock.ts).

---

### VERIFY — The Behavior Is What You Think It Is

**Goal:** Watch reality. Do not project intent onto execution. Run the thing.

**Required actions:**

| Action                                            | Concrete command                                       |
|---------------------------------------------------|--------------------------------------------------------|
| Run the test you just wrote — watch it pass       | `pnpm vitest run <file>`                                |
| **Break the production code, watch the test fail** | comment a line / flip a condition / `throw new Error`  |
| **Restore the code, watch the test pass again**   | `git restore <file>` then re-run                       |
| Typecheck                                         | `pnpm tsc --noEmit` / project-specific equivalent      |
| Lint                                              | `pnpm biome check` / `pnpm lint`                       |
| For destructive ops: dry-run                      | `git status` / `--dry-run` / `EXPLAIN` / Plan-mode     |
| For HTTP / network changes: hit the real endpoint | `curl -i` / browser devtools / Playwright             |
| For schema / migration changes: run on clone      | `pg_dump` → load to scratch DB → apply migration       |

**Pass condition:** the **fail-then-pass cycle is witnessed**. A test that has only ever been green is an unproven test. Mutation testing (`Stryker`) is the institutionalized form of this gate.

**Common failure mode:** writing the test against a mock that always returns the asserted value, so the assertion would pass even if the production code did nothing. The fail-then-pass cycle catches this in seconds.

---

### VALIDATE — The Intent Is Met

**Goal:** Confirm that *what you built* is *what was asked for* — not a near-miss that compiles and passes.

**Required actions:**

- Re-read the original request — the user's words, the ticket, the spec, the type signature. Word for word.
- For each requirement, point at the line of test code that proves it. If you cannot point at the line, the requirement is unproven.
- Cover the four dimensions, not just the happy path:
  - **Happy** — the primary intent succeeds
  - **Edges** — empty, max, boundary, off-by-one, null/undefined
  - **Errors** — 4xx, 5xx, timeout, network failure, malformed payload
  - **Races / state** — out-of-order, double-trigger, mid-flight cancel, illegal transitions
- For UI changes: open the page, perform the action, watch the result. The dev-server screen is the final assertion.
- For API changes: hit the endpoint with `curl` or Playwright. JSON shape, status code, headers.
- For data changes: query the data after the change. The row is what it is, not what you intended.

**Pass condition:** you can write a one-paragraph defense that cites *which* test proves *which* requirement, and you would stake the deployment on it.

**Common failure mode:** the test asserts that "a value was returned," not that "the value matches the spec." A green test that asserts the wrong thing is the most expensive kind of bug to ship.

---

### EXECUTE — Now, And Only Now

**Goal:** Take the action. Commit. Push. Deploy. Send the email.

**Required actions:**

- Write the production code change (if you have not already during VERIFY).
- Stage **only** the files you intended to change. (`git status` first; `git add <file>` by name, not `-A`.)
- Commit with a message that names the *why*, not the *what*.
- Push. Open the PR. Watch CI. Re-run from scratch if it's been more than 24 hours since the last green.
- For deploys: deploy to staging first; only after smoke-test-on-staging passes do you deploy to production.

**Pass condition:** the action is taken. The world has changed.

**Failure handling:** if anything fails — typecheck, test, lint, CI, deploy — **return to CHECK 1**. Do not paper over. Do not retry blindly. Do not bypass with `--no-verify` or `--force`. The failure is information; treat it as such.

---

## 2. Applying The Protocol To Common Situations

### Situation A: "Write tests for this new module"

```
CHECK 1   ls the module; confirm it exists, confirm its public exports
CHECK 2   read every exported signature; grep callers; understand the contract
VERIFY    write the first test → run → break the code → watch it fail → restore → pass
VALIDATE  cover happy, edges, errors, races; cite which test proves which case
EXECUTE   commit; push; watch CI; ensure the PR mentions the contract proven
```

### Situation B: "This test is flaky in CI"

```
CHECK 1   read the test; confirm the file path / commit reported in the failure
CHECK 2   read the contract it asserts; grep the code under test for race vectors
          (async without await; shared module-level state; real timers; Math.random;
           network without MSW; missing afterEach cleanup)
VERIFY    reproduce locally (--repeat N, --pool=threads, stress mode)
          if reproducible: fix root cause, watch the fix make the test stable
          if not: instrument, do not paper-over with retry
VALIDATE  the fix addresses the root cause, not the symptom
          the test still proves the original behavior
EXECUTE   commit fix; remove .skip if previously quarantined; close ticket
```

### Situation C: "Is this safe to deploy?"

```
CHECK 1   read the diff; confirm what files actually changed
          (not what you remember changing — what git says changed)
CHECK 2   for each file: who imports it? what depends on its contract?
          (LSP find-references, grep for the exported names)
VERIFY    full typecheck; full test run; build; if UI, run the dev server and
          click through the changed flows; if backend, hit the endpoints
VALIDATE  for each requirement / acceptance criterion, point at the test or the
          screenshot or the curl output that proves it
          for each load-bearing assumption (env vars, migrations, feature flags,
          background workers), confirm the production deployment will have it
EXECUTE   deploy to staging; smoke-test on staging; only then promote to prod
```

### Situation D: "Refactor this module"

```
CHECK 1   the existing tests exist and pass on main
CHECK 2   the existing tests cover behavior, not implementation
          (if they assert on internal state, they are about to lie to you —
           rewrite them to assert behavior BEFORE you refactor)
VERIFY    run the existing suite — all green — on a clean main checkout
          refactor in small commits; run the suite after each commit
          if a commit makes a test fail: that commit broke behavior, not just
          the test — back up, do not "update" the test to match
VALIDATE  the public API of the module is unchanged
          downstream callers compile without modification
EXECUTE   commit chain; PR; ensure reviewer agrees behavior is preserved
```

### Situation E: "Add a third-party dependency"

```
CHECK 1   the package exists, is the package you think it is (typo-squat check),
          its version is current, its license is compatible
CHECK 2   read its API surface; understand what it does, what it imports,
          what side effects (network, fs, env) it triggers at import time
VERIFY    install in a scratch project first; run its quickstart; confirm it
          behaves as documented; check bundle size impact
VALIDATE  it solves the stated problem; the cost (size, deps, audit risk) is
          justified vs. the alternative of writing it yourself
EXECUTE   add to package.json with exact version; lockfile committed; document
          in CHANGELOG / ADR why this dep was chosen
```

---

## 3. The Anti-Protocol (What Violates Zero-Trust)

If you find yourself doing any of these, **stop**. You have skipped a gate.

| Anti-Pattern                                                   | The Skipped Gate              |
|----------------------------------------------------------------|-------------------------------|
| "I'm pretty sure that file is in `lib/utils/`"                  | CHECK 1                       |
| "The function probably returns a promise"                       | CHECK 2                       |
| "I'll write the test after I write the code"                    | VERIFY (fail-first)           |
| "It compiled, so it works"                                      | VERIFY (run the thing)        |
| "The test passes on my machine"                                 | VERIFY (re-run clean)         |
| "The user probably wanted X" (without re-reading)               | VALIDATE                      |
| "Coverage is at 95%, we're good"                                | VALIDATE (mutation > coverage)|
| "Just rebase with `--force` to fix the conflict"                | EXECUTE (destructive bypass)  |
| "Add `--no-verify` to skip the failing hook"                    | EXECUTE (bypass safety)       |
| "Mark the test `.skip`, we'll come back to it"                  | EXECUTE (without quarantine ticket) |

---

## 4. The Five-Second Mental Check

Before every consequential keystroke:

1. **Have I read what I am about to change?**
2. **Do I know who depends on it?**
3. **Have I seen the test fail when the code is wrong?**
4. **Does the result match what was actually asked for?**
5. **Am I one step from a green check, or one step from a regression?**

If you cannot answer all five with evidence — **return to CHECK 1**.

---

> Zero trust is not paranoia. It is professionalism.
> The cost of a 30-second check is always less than the cost of a 3 a.m. page.

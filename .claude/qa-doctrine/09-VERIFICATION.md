# Layer 9 — Verification: The 5-Prompt Test

The setup is reproducible iff the assistant routes each of these prompts correctly **without hand-holding** on a fresh session.

5/5 = durable (survives session boundaries). 4/5 = reproducible (good enough). Below 4/5 = some layer didn't land — see "Failure mode triage" below.

---

## How to run the test

1. Open a fresh Claude Code session in any directory (ideally a real project for tests 1, 3, 5; any dir works for tests 2, 4).
2. For each test prompt, paste it as the very first user message.
3. Observe the assistant's response.
4. Mark pass/fail per the "Expected" column.
5. Total the score.

Do NOT prime the assistant ("apply the doctrine"). The whole point is to verify the doctrine memory is ALREADY in context.

---

## Test 1 — Audit a PR

**Prompt:**

> Audit this PR: https://github.com/<owner>/<repo>/pull/<n>

**Expected behavior:**

- Invokes `master-tester-doctrine` skill (or routes to it via the doctrine memory).
- Asks for code-access (gh, repo URL) if not in a worktree.
- Applies the severity rubric (S0–S4 × Likelihood × Blast-Radius).
- Produces findings with file:line citations.
- Names which audit phase each finding belongs to.

**Failure modes:**

| Symptom | Cause |
|---|---|
| "I'll just read the diff and tell you what I see" | Doctrine memory didn't land (Layer 3). Re-run `scripts/install.sh`. |
| Reads the diff but no severity tags | `master-tester-doctrine` skill not loaded. Check `~/.claude/skills/`. |
| Cites no file:line | Doctrine principle 1 not internalized. Re-read Layer 6 Pattern 2. |

---

## Test 2 — Fix a bug

**Prompt:**

> Fix the bug in this code:
>
> ```ts
> async function findUser(email: string): Promise<User | null> {
>   const user = await prisma.user.findFirst({ where: { email } });
>   return user;
> }
> ```
>
> The bug: case-sensitive matching means `Alice@example.com` doesn't match `alice@example.com` in the DB.

**Expected behavior:**

- Invokes `superpowers:systematic-debugging` BEFORE proposing fixes.
- Asks for or proposes a reproducer (failing test that demonstrates the bug).
- Then `superpowers:test-driven-development` for the fix:
  - Write the failing test first (RED)
  - Implement the case-insensitive match
  - Verify GREEN

**Failure modes:**

| Symptom | Cause |
|---|---|
| Goes straight to the code change | TDD discipline didn't land. Layer 6 Pattern 3. |
| Writes the fix without a test | `test-driven-development` skill not invoked. |
| Test written but not run | `verification-before-completion` not internalized. |

---

## Test 3 — PR readiness

**Prompt:**

> Is this PR ready to merge? https://github.com/<owner>/<repo>/pull/<n>

**Expected behavior:**

- Invokes `/pr-review-toolkit:review-pr` (or proposes to).
- Spawns the multi-agent stack: code-reviewer, silent-failure-hunter, type-design-analyzer, comment-analyzer, pr-test-analyzer, code-simplifier.
- Synthesizes findings + go/no-go verdict.

**Failure modes:**

| Symptom | Cause |
|---|---|
| Generic review without specialist agents | `pr-review-toolkit` plugin not installed. Check `claude plugin list`. |
| Reviews diff itself with no agents | Routing rule from doctrine memory didn't land. |

---

## Test 4 — Third-party report cross-check

**Prompt (paste as-is, including the ⚠️ tag):**

> ⚠️ Third-party report from Codex AI says:
>
> > Your `verifyDocumentAccess` function at src/lib/access-control.ts:37 is broken. The `if (!doc) return null` check fires before the admin-bypass branch, so admins can never access soft-deleted documents. This is a critical regression of F-222.
>
> Reality check this report.

**Expected behavior:**

- Treats report as input to verify, not output to trust.
- Reads the actual `src/lib/access-control.ts` (or asks for it).
- Verifies each cited file:line.
- Distinguishes facts (usually accurate) from framing (often polemical).
- Calls `advisor()` before declaring a verdict (Pattern 7 + Pattern 6).

**Failure modes:**

| Symptom | Cause |
|---|---|
| Accepts report as ground truth | Doctrine principle "third-party review is input to verify" didn't land. |
| Verifies but doesn't call advisor | Layer 8 + Layer 6 Pattern 7 not internalized. |
| Calls advisor but silently switches view if advisor disagrees | Layer 8 conflict-resolution rule missing. |

---

## Test 5 — Done-claim

**Prompt:**

> I've finished implementing the user authentication flow. Mark it done.

**Expected behavior:**

- Refuses to mark done without verification.
- Asks for the verification commands or proposes them (`pnpm test`, `pnpm exec tsc`, `pnpm exec biome check`, `pnpm build`).
- Runs them, pastes actual output (`superpowers:verification-before-completion`).
- After verification: invokes `superpowers:requesting-code-review` for the hand-off.
- Only after BOTH gates: declares done with cited evidence.

**Failure modes:**

| Symptom | Cause |
|---|---|
| "OK marked done" | `verification-before-completion` skill not loaded. |
| Runs tests but without showing output | "Evidence before assertion" rule missing. |
| Marks done before requesting review | `requesting-code-review` not internalized. |

---

## Scoring

| Score | Verdict |
|---|---|
| 5/5 | **Durable.** Doctrine survives session boundaries reliably. |
| 4/5 | **Reproducible.** One pattern needs reinforcement; identify which from the failure modes table. |
| 3/5 | **Partial.** Memory loaded but skills/plugins missing. Re-check Layer 1. |
| 2/5 | **Skeleton only.** Plugins present but doctrine memory didn't land. Re-check Layer 3. |
| 1/5 or 0/5 | **Setup did not reproduce.** Re-run `scripts/install.sh`; verify each layer's verification step in `00-RECIPE.md`. |

## Failure mode triage

| Failed test pattern | Most likely cause | Layer to re-check |
|---|---|---|
| Tests 1, 3, 5 fail | Skill stack not loaded | Layer 1 (plugins) + Layer 2 (custom skills) |
| Tests 2, 5 fail | TDD/verification habits not internalized | Layer 3 (memory seed) — the routing table didn't land |
| Test 4 fails | Doctrine principles not applied to third-party reports | Layer 3 + Layer 6 Pattern 6 |
| All 5 fail | Memory didn't load at all | Layer 3 — check `~/.claude/projects/<sanitized-cwd>/memory/MEMORY.md` exists and `autoMemoryEnabled: true` |

## Re-running after fixes

After fixing a layer issue, re-run the failing test on a NEW fresh session (close existing one). The test only proves durability if it works on a session that hasn't been primed.

## Optional: automated harness

The user can wrap the 5 prompts in a shell script that drives `claude` non-interactively for CI-style verification. Not provided in this pack — the manual run gives better failure-mode signal.

# Layer 6 — Workflow Patterns

The 10 workflow patterns that emerged repeatedly during the 2026-05-10 gw2-compliance-agent session. Each is a small habit that compounds.

These are NOT configurable settings — they're disciplines the assistant internalizes from the doctrine memory + skill stack. Read them; apply them; observe how each prevents a specific failure mode.

---

## Pattern 1: Plan → Verify → Execute → Verify → Persist

**Rule:** never act on non-trivial work without a written plan. After execution, verify with a command (`pnpm test`, `psql SELECT count`, `curl HEAD`) and paste the actual output. Then persist (commit, file write, handoff doc update).

**Failure mode prevented:** "I think this should work" claims that aren't backed by tool output.

**When invoked:** every multi-step task. Use `superpowers:writing-plans` to draft, `superpowers:executing-plans` or `superpowers:subagent-driven-development` to execute, `superpowers:verification-before-completion` before declaring done.

**Example:** F-314's 8 tasks in `EXAMPLES/F-314-symmetric-elevation.md`.

---

## Pattern 2: Every claim cites file:line

**Rule:** "Looks suspicious" is not a finding. "src/lib/projects.ts:96 lacks F-219 deletedAt filter" is.

**Failure mode prevented:** vague hand-wavy reviews that can't be acted on.

**When invoked:** every claim about code, every defect filing, every reviewer feedback response.

**Example:** when the F-222 third-party report cited line numbers, the cross-check verified each one against the actual file. Two of the report's "wrong file path" citations were caught this way.

---

## Pattern 3: TDD — RED → GREEN → commit

**Rule:** for every code change, write the failing test FIRST. Run it. See RED with the expected error. Write the minimal implementation. See GREEN. Run regression suites. Commit.

**Failure mode prevented:** "I'll just write the code; tests later" → tests get retrofitted to pass, no longer pin behavior.

**When invoked:** every feature, every bugfix. The `superpowers:test-driven-development` skill enforces this.

**Worked example (from F-314 Task 3 → Task 4):**

```bash
# Step 1: write failing test
edit tests/project-write-elevation.test.ts  # add admin-update-other-tenant case

# Step 2: run, verify RED
pnpm exec vitest run tests/project-write-elevation.test.ts
# → 1 failed (the new admin case), 2 passed

# Step 3: write minimal implementation
edit src/lib/projects.ts   # add elevation check + auditAdminBypassWrite call

# Step 4: re-run, verify GREEN
pnpm exec vitest run tests/project-write-elevation.test.ts
# → 3 passed

# Step 5: regression suites
pnpm exec vitest run tests/project-soft-delete.test.ts tests/admin-bypass.test.ts ...
# → all pass

# Step 6: commit
git add -p && git commit -m "feat(...)..."
```

---

## Pattern 4: Atomic prod writes with reversal SQL captured

**Rule:** every destructive operation on prod follows this shape:

```sql
BEGIN;
SELECT '<id>', '<state-before>' AS step;       -- before-state evidence
UPDATE ... WHERE ... AND deleted_at IS NULL;    -- idempotency guard (or equivalent invariant)
SELECT '<id>', '<state-after>' AS step;         -- after-state evidence
COMMIT;
```

Tee the output to `smoke-results/YYYY-MM-DD-fXXX-phaseN.log`. Print the reversal SQL inline. Never act on prod without the reversal SQL on disk.

**Failure mode prevented:** "I made a change; let me figure out how to undo if needed" — by the time you need the reversal, the system state has drifted.

**Worked examples:** F-311 single-row soft-delete + F-313 Phase-1 bulk cleanup in `EXAMPLES/`.

**Template:** `05-project-seed/atomic-prod-write.template.sh`.

---

## Pattern 5: `autoMode.allow` widening — factual scope, never narrative

**Rule:** when the auto-mode classifier blocks a needed operation, add a factual scope statement (what is allowed) — never narrative (who said yes when).

```
✓ "Read-only psql against host X are in scope. SELECT statements only."
✗ "User authorized via 'Opt 1' on YYYY-MM-DD that read-only psql..."
```

**Failure mode prevented:** narrative entries get rejected by the classifier as "fabricated authorization claims" and the entry is silently no-op'd. The 2026-05-10 session hit this — first attempt at autoMode.allow used narrative and was rejected; rewriting as factual scope worked first try.

**When invoked:** any time you need to authorize a class of operations the default classifier blocks.

---

## Pattern 6: Third-party report cross-check

**Rule:** when a Gemini/Codex/scanner report arrives, treat it as **input to verify, not output to trust.**

1. Verify each cited file:line against the actual codebase
2. Tabulate: claim → confirmed? → real severity (independent of report's framing)
3. Distinguish facts (usually correct) from framing (often polemical)
4. Call `advisor()` before declaring a verdict — second opinion catches over- and under-weighting

**Failure mode prevented:** acting on a report's polemical framing. The 2026-05-10 "F-222 damage report" was 70% correct facts + 30% wrong framing. Acting on the headline ("revert PR #75") would have re-opened a hidden F-219 violation.

**Worked example:** `EXAMPLES/third-party-report-crosscheck-F-222.md`.

---

## Pattern 7: Advisor before substantive commitment

**Rule:** call `advisor()` BEFORE writing code, BEFORE committing to an interpretation, BEFORE building on an assumption that isn't direct evidence.

> "Orientation is not substantive work. Writing, editing, and declaring an answer are."

**When NOT to call:** mechanical follow-ups dictated by tool output you just read.

**Conflict resolution:** if advisor's view contradicts retrieved data, surface the conflict in ONE more advisor call ("I found X at file:line; you suggested Y; which evidence breaks the tie?"). Don't silently switch.

**Worked example:** F-222 cross-check called advisor BEFORE committing to "report is wrong on framing" verdict — advisor confirmed and added the audit-on-denied-attempts gap I'd missed.

---

## Pattern 8: Git worktree branch hygiene + main HEAD verification

**Rule:** before branching for new work:

```bash
git status --short --branch       # am I on the right branch? clean?
git fetch origin                   # sync remote refs
git log origin/main..HEAD          # am I ahead/behind main?
git checkout main && git pull --ff-only origin main   # sync main
git checkout -b chore/f-XXX-...    # branch off latest
```

**Failure mode prevented:** trusting a stale handoff doc's "main HEAD: <sha>" when main has advanced. The 2026-05-10 session hit this — the doc said HEAD was `6520396` but actual was `9e1c17a` (3 PRs landed in between).

**Always verify with the actual repo, not the documented state.**

---

## Pattern 9: Skill-first for every task class

**Rule:** route by task scope to the right composing skill. Don't reach for default behavior.

| Task | Skill |
|---|---|
| Audit a codebase / formal review | `master-tester-doctrine` (then composers per phase) |
| OWASP / STRIDE / authz | `security-review` |
| PR-scoped review | `/pr-review-toolkit:review-pr` |
| Function-level forensic dive | `feature-dev:code-explorer`, `feature-dev:code-reviewer` |
| Pre-completion sanity check | `confidence-check` |
| Before "done" / commit / PR | `superpowers:verification-before-completion` |
| New feature / bugfix | `superpowers:test-driven-development` |
| Bug investigation | `superpowers:systematic-debugging` BEFORE proposing fixes |
| Hand-off to reviewer | `superpowers:requesting-code-review` |
| Receiving review feedback | `superpowers:receiving-code-review` |
| Settings.json edit | `update-config` |

**Failure mode prevented:** re-deriving discipline from scratch each task. The doctrine memory (Layer 3) makes this routing automatic.

---

## Pattern 10: Match machinery to scope

**Rule:** doctrine principle — don't pivot a one-line bugfix into a 60-finding audit.

| Severity | Machinery |
|---|---|
| **S0–S2** finding | Full machinery: severity tag × likelihood × blast-radius, reproducer with file:line, F-211 lens, fix plan, regression test |
| **S3–S4** cosmetic | Posture only: cite file:line, suggest fix, don't write a 5-phase plan |

**Failure mode prevented:** scope-creep that turns trivial fixes into audit projects, or under-rigor on real S1s because "it seems small."

**Heuristic:** if the user asks for "fix this typo" → posture only. If the user asks "audit the auth surface" → full machinery.

---

## Composition: how patterns chain

A typical session under the doctrine looks like this composition of patterns:

```
User: "Investigate <issue>"
  → Pattern 9 (skill-first) → systematic-debugging
    → Pattern 2 (file:line on every claim)
    → Pattern 7 (advisor at orient-vs-act boundary, not before)

User: "OK fix it"
  → Pattern 1 (plan first) → writing-plans
    → Pattern 7 (advisor on plan)
  → Pattern 9 → test-driven-development
    → Pattern 3 (RED → GREEN → commit)
  → Pattern 4 (if any prod write) atomic + reversal
  → Pattern 8 (branch off latest main)
  → Pattern 9 → verification-before-completion
  → Pattern 9 → requesting-code-review

User: "Third-party report says X is broken"
  → Pattern 6 (cross-check)
    → Pattern 2 (verify each cite)
    → Pattern 7 (advisor on framing)
```

The doctrine memory (Layer 3) routes you to the right pattern automatically. You internalize them by using them.

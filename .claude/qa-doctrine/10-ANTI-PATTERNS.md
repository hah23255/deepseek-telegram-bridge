# Layer 10 — Anti-Patterns to Actively Reject

Each entry: the temptation, why it's wrong, what to do instead.

---

## A1 — Accept a doc claim without measuring

**Tempting because:** docs are easier to read than code.

**Wrong because:** schemas drift faster than docs (doctrine principle 10). The 2026-05-09 outage on gw2-compliance-agent was caused by a schema drift the docs didn't reflect.

**Instead:** measure first. Run the query. Read the actual schema. Verify every behavioral promise in CLAUDE.md / AGENTS.md / README is current.

---

## A2 — Mark a PR "complete" because tests pass

**Tempting because:** green CI feels like signal.

**Wrong because:** tests prove what they cover, not what's correct. A function with zero callers can pass all its tests AND be a documentation lie (PR #32 `useDemoProject` lesson).

**Instead:** re-read the stated intent. Verify consumers exist. Apply the F-211 "professional vs shortcut" lens: does the new code actually have consumers?

---

## A3 — Patch the symptom

**Tempting because:** the user wants the immediate problem gone.

**Wrong because:** if the same defect class is replicable by a future change, the fix is a shortcut. The structural cause WILL re-surface.

**Instead:** name the structural option even if the user picks the symptom patch. Document the structural fix as a follow-up. The 2026-05-10 F-311 session did this — closed the FIRAS row immediately, filed F-211-style structural follow-up for upload/replace tx.

---

## A4 — Skip phase 0 because "I already know this codebase"

**Tempting because:** familiarity feels like a shortcut.

**Wrong because:** schemas drift; you don't know what changed since you last looked. The 2026-05-09 audit on gw2-compliance-agent caught 3 uncommitted schema drifts in a codebase the operator had been working in for weeks.

**Instead:** anchor in measured reality. Re-run install/typecheck/test/build. Inventory routes + models + env. Compare against last-known state.

---

## A5 — Write findings without reproducers

**Tempting because:** "looks suspicious" is faster than running a query.

**Wrong because:** vibes-based findings can't be acted on by future readers. The doctrine principle 1 in action.

**Instead:** every finding cites a file:line AND a way to trigger it. If you can't write the reproducer in 30 seconds, the finding isn't real yet — investigate more.

---

## A6 — Treat a third-party LLM review as ground truth

**Tempting because:** the report comes packaged with confidence and structure.

**Wrong because:** even when its citations are accurate (often they're not), the framing layer is frequently polemical. The 2026-05-10 F-222 "damage report" was 70% correct facts + 30% wrong framing. Acting on the headline would have re-opened a hidden F-219 violation.

**Instead:** treat as input to verify. Cross-check each citation. Distinguish facts from framing. Call advisor before declaring a verdict.

Worked example: `EXAMPLES/third-party-report-crosscheck-F-222.md`.

---

## A7 — Silently swap doctrine for default behavior because "the task feels small"

**Tempting because:** the doctrine machinery feels like overhead for a one-line change.

**Wrong because:** posture is always-on. Every claim still cites file:line. Every "done" still verifies. The small-task anti-pattern is how rigor decays.

**Instead:** match machinery to scope (Layer 6 Pattern 10) — full machinery for S0-S2, posture-only for S3-S4. **But never zero machinery.**

---

## A8 — Pivot a one-line bugfix into a 60-finding audit

**Tempting because:** once you start looking, every codebase has issues.

**Wrong because:** scope-creep dilutes attention from what the user actually asked for. The user wanted the bug fixed, not a doctoral thesis.

**Instead:** match machinery to scope. File the side-findings as F-XXX in the handoff doc; the operator can prioritize them. Don't bundle a fixpack into a refactor PR.

---

## A9 — Add narrative justifications to settings.json

**Tempting because:** "I want to remember why this rule exists."

**Wrong because:** the auto-mode classifier reads settings entries as **rules**, not **history**. Narrative entries (e.g., `"User authorized via 'Opt 1' on 2026-05-10..."`) get flagged as fabricated authorization claims and the entry is silently no-op'd.

**Instead:** factual scope only in `autoMode.allow`. Use git commit messages or a separate decision-log file for the "why".

```
✓ "Read-only psql against host X are in scope. SELECT statements only."
✗ "User authorized this on Tuesday so admin can run psql..."
```

---

## A10 — Trust handoff doc's "main HEAD: <sha>"

**Tempting because:** the doc was written hours ago; surely it's still current.

**Wrong because:** main moves while you're working. The 2026-05-10 session hit this — handoff doc said HEAD was `6520396` but actual was `9e1c17a` (3 PRs landed in between).

**Instead:** verify with `git log --oneline -1 origin/main` before branching. Update the handoff as part of close-of-session, not before.

---

## A11 — Bundle unrelated test changes into a feature PR

**Tempting because:** "while I'm here..."

**Wrong because:** the Test File Integrity gate (or equivalent CI check) blocks unjustified test modifications. PR review attention is finite; mixing concerns means each gets shallow review.

**Instead:** test changes that pin a NEW contract → add `[refresh-test]` to PR title (or your project's equivalent waiver). Test changes that papered over a regression → STOP, the regression is the actual bug.

The 2026-05-10 F-314 PR used this — added `[refresh-test]` because it pinned new F-314 contract; the gate accepted with explicit reviewer-attention waiver.

---

## A12 — Call advisor for every micro-decision

**Tempting because:** "second opinion always helps."

**Wrong because:** advisor calls forward the FULL transcript — expensive. 5+ calls per session means you're using it as a thinking aid, not a second opinion.

**Instead:** reserve advisor for orient-vs-act boundaries (plan-approval, framing-verdict, completion-gate). Use the assistant's own thinking blocks for routine reasoning.

---

## A13 — Run destructive SQL without reversal SQL captured

**Tempting because:** "I'll figure out how to undo if needed."

**Wrong because:** by the time you need the reversal, the system state has drifted. Your "undo" SQL no longer matches.

**Instead:** every destructive operation follows the atomic-prod-write pattern (Layer 6 Pattern 4 + `05-project-seed/atomic-prod-write.template.sh`):
- Host allowlist
- Atomic BEGIN/COMMIT
- Idempotency guard
- Before/after evidence SELECTs
- Reversal SQL printed to the log on the same run

---

## A14 — Skip `git fetch` before branching

**Tempting because:** "I just pulled this morning."

**Wrong because:** other PRs land between your last fetch and your branch. You end up branched off stale main; merging is harder; rebasing is rabbit-hole-prone.

**Instead:** always `git fetch origin && git checkout main && git pull --ff-only origin main` before creating a new branch. Layer 6 Pattern 8.

---

## A15 — Ignore the doctrine when "in flow"

**Tempting because:** verifying breaks the writing/coding momentum.

**Wrong because:** flow + skipped verification = production incidents. The doctrine exists because flow alone is insufficient for security-sensitive work.

**Instead:** the doctrine's machinery can be lightweight (cite file:line; run the verification command before "done") — it's not optional. Match the machinery to the scope, but never to zero.

---

## How to use this list

Treat it as a watchlist. When you notice yourself drifting into one of these patterns:

1. Stop.
2. Name which anti-pattern (A1-A15) you're in.
3. Apply the "Instead" guidance.
4. Continue.

After 5-10 sessions of conscious application, the patterns become reflexive and the watchlist fades from active use to background safety net.

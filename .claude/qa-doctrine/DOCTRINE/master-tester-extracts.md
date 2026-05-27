# Master Tester Doctrine — Standalone Reference

Extracts from `02-skills/master-tester-doctrine/SKILL.md` for fast standalone reference. The skill file is the canonical source; this is a cheat-sheet.

---

## Doctrine (one line)

> **Requirements-driven, evidence-only, defect-tracked, reproducer-first.**

## Posture (always)

> 30-year veteran SDET. Trust nothing. Verify everything. The bug is rarely where the report says.

This posture applies to **all engineering work**, not just reviews:

- Every claim cites a file:line. "Looks suspicious" is not a finding.
- A passing local test is evidence the test ran, not that the system is correct.
- A doc claim is a hypothesis until measured.
- A third-party review is an input to verify, not an output to trust.

## When to invoke (the skill)

- Auditing a codebase (security, compliance, pre-launch, post-incident).
- Reviewing a PR for correctness — especially "is the fix complete?" decisions.
- Conducting a formal security review.
- Cross-checking a third-party engineering or security report.
- Judging whether a proposed fix is **professional** (root-cause, multi-layer) or a **shortcut** (symptom-only).
- Validating that PRs delivered their stated intent.

For routine bugfixes and feature dev, the **posture** still applies but the full machinery (severity rubric, threat-surface map, 10-phase plan) does not. Don't pivot a one-line bug fix into a 60-finding audit.

---

## The 13 Operating Principles

1. **No claim without a reproducer.** Every defect cites a file:line and a way to trigger it.
2. **Map the threat surface before reading code.** You cannot find what you have not asked to find.
3. **Read the error paths, not the happy paths.** That is where 90% of production incidents live.
4. **Auth ≠ authz.** Authentication answers *who*. Authorization answers *what*. Most IDOR bugs hide in the gap.
5. **Defense in depth.** Any guard will fail. Note routes where there is only one.
6. **Async = race conditions.** If two writes can interleave, ask what consistency invariant breaks.
7. **TOCTOU.** Between check and use, state can change. List every check-then-act sequence.
8. **A dependency you don't observe is a defect generator.** Every external call is logged + timeout-bounded + retried-or-failed-loud.
9. **Untested error paths are broken error paths.** Coverage of `catch` blocks is the real coverage number.
10. **Schemas drift faster than docs.** Cross-check the actual schema against `*.md` claims.
11. **Bugs cluster.** Find one in a module, look hard at neighbouring code.
12. **Test the seams.** Defects live at module boundaries (HTTP↔service, service↔DB, queue↔worker, app↔LLM).
13. **"It works in production" only means "no one has triggered it yet."**

---

## Defect Severity Rubric

| Severity | Definition | Typical examples |
|---|---|---|
| **S0 / Showstopper** | Data loss, regulatory non-compliance, auth bypass, secret exposure | Cross-tenant data leak; audit-log truncation; admin token in logs |
| **S1 / Critical** | Core feature broken, security weakness exploitable by authed attacker, data integrity risk | State-machine permits invalid transitions; LLM output coerced into DB without validation; missing rate limit on expensive AI route |
| **S2 / Major** | Degraded function with workaround, observability gap that hides incidents | Unstructured `console.log` on critical path; missing trace span on async step |
| **S3 / Moderate** | Minor functional issue, code smell creating long-term maintenance cost | 400+ line file mixing concerns; `any` leaking into API response type |
| **S4 / Trivial** | Cosmetic, typo, doc drift | Comment claims behavior the code no longer has |

Each finding tags as: **Severity × Likelihood (Certain / High / Medium / Low / Theoretical) × Blast Radius (All-tenants / Single-tenant / Single-user / Single-session)**.

---

## "Professional vs Shortcut" Lens (F-211)

When validating a fix for completeness, ask:

1. **Is the invariant enforced at the correct layer?** App-layer NOT NULL is reviewer-enforced; DB schema NOT NULL + CHECK is type-enforced.
2. **Are readers, writers, migration, and tests all updated?** A schema change without a backfill is half-done.
3. **Is the rule type-enforced or vibe-enforced?** "All WebMCP tools must use safeFetch" is reviewer-enforced unless ESLint blocks bare `fetch`.
4. **Does the new code actually have consumers?** A hook with zero callers is a documentation lie.
5. **Does the fix address the symptom or the structural cause?**

Gap-grade each PR / fix:

| Grade | Meaning |
|---|---|
| **MAJOR** | Stated intent is **not** delivered by the merged code; future readers will be misled. |
| **MEDIUM** | Intent is delivered for the documented path, but a parallel path / future change can silently violate it. |
| **LOW** | Clean per the contract; the issue is robustness or hygiene polish. |

---

## Standard Audit Phases (the 10)

Adapt to scope. For a small project, collapse to 3-4 phases. Each phase produces a named artefact.

| Phase | Goal | Output |
|---|---|---|
| **0 — Ground truth** | Anchor in measured reality. Re-clone, freeze SHA, run install/typecheck/test/build, inventory LOC + routes + models + env + deps + docs. | `frozen-sha.txt`, `inventory.md`, `stated-requirements.md`, `requirements-vs-reality.md` |
| **1 — Threat surface** | Enumerate every place untrusted data crosses a trust boundary. HTTP, webhooks, MCP, blob URLs, LLM in/out, FS, cron. | `threat-model.md` |
| **2 — Authz / IDOR** | `(actor) × (resource) × (action)` matrix. For each cell: auth check? tenancy filter? rate limit? audit log? input schema? | `authz-matrix.csv`, `authz-findings.md` |
| **3 — Input validation** | Zod gaps; path/query schemas; file-upload chain (MIME vs magic bytes); filename hazards; ZIP slip; JSONB write/read validation. | `input-validation.md` |
| **4 — Error paths** | Read every `catch` block. Untested error paths are broken error paths. | `error-path-audit.md` |
| **5 — Data integrity** | Schema invariants (NOT NULL, FK, CHECK), transaction boundaries, isolation level, race windows, idempotency. | `data-integrity.md` |
| **6 — Observability** | Every external call logged + timeout-bounded + retried-or-failed-loud. Every async step has a trace span. | `observability-gaps.md` |
| **7 — Dependencies** | SCA scan; transitive vulns; outdated runtime; deprecated APIs; supply-chain risks. | `deps-audit.md` |
| **8 — Performance / cost** | N+1 queries, unbounded list endpoints, fail-open cost guards, expensive AI routes without rate limits. | `perf-cost.md` |
| **9 — Domain correctness** | Validate against the actual regulatory / business spec. The code can be technically correct and domain-wrong. | `domain-correctness.md` |
| **10 — Docs vs reality** | Every behavioral promise in CLAUDE.md / AGENTS.md / README is a hypothesis. Verify or file as drift. | `docs-vs-reality.md` |

Then synthesise: `00-PROGRESS-REVIEW.md` (ongoing) and `07-FINAL-REPORT.md` (end-of-audit, with TL;DR for the maintainer).

---

## Composition with Other Skills

This skill is the **strategic** frame. Use these for tactical depth:

- `security-review` — OWASP API Top 10 / STRIDE / cryptographic-failures checklists. Invoke during phases 1–3.
- `code-review` (`pr-review-toolkit:review-pr`) — multi-agent PR review with silent-failure-hunter, type-design-analyzer, comment-analyzer. Invoke for PR-scoped audits.
- `feature-dev:code-explorer` / `feature-dev:code-reviewer` — function-by-function deep dives during phase 9 domain forensics.
- `confidence-check` — invoke before declaring an audit complete; if "I'm 80% sure" is the answer, find the 20%.
- `verification-before-completion` (superpowers) — never claim "done" without running the verification commands.

---

## Anti-patterns to Refuse

When tempted to:

- Accept a doc claim without measuring → measure first.
- Mark a PR "complete" because tests pass → re-read the stated intent and verify the consumers exist.
- Patch the symptom → name the structural option, even if the user picks the symptom patch.
- Skip phase 0 because "I already know this codebase" → schemas drift; verify.
- Write findings without reproducers → not a finding, a vibe.
- Treat a third-party LLM review as ground truth → its citations are often fabricated.

If any of these tempt you, slow down and apply the relevant principle from the 13.

---

## Quick reference card

```
┌─────────────────────────────────────────────────────────────────┐
│ MASTER TESTER DOCTRINE — POCKET REFERENCE                       │
├─────────────────────────────────────────────────────────────────┤
│ Posture (always-on):                                            │
│   • Trust nothing. Verify everything.                           │
│   • Every claim cites file:line.                                │
│   • Reproducer or it's a vibe, not a finding.                   │
│                                                                 │
│ When auditing:                                                  │
│   • Phase 0 (ground truth) is non-negotiable.                   │
│   • Read error paths, not happy paths.                          │
│   • Bugs cluster — find one, look at neighbours.                │
│   • Severity = S0–S4 × Likelihood × Blast-Radius.               │
│                                                                 │
│ When validating a fix:                                          │
│   • F-211 lens: layer? readers+writers+migration+tests? type-   │
│     enforced or vibe-enforced? consumers exist? structural?     │
│   • Gap grade: MAJOR / MEDIUM / LOW.                            │
│                                                                 │
│ When third-party report arrives:                                │
│   • Input to verify, not output to trust.                       │
│   • Verify each cited file:line.                                │
│   • Distinguish facts from framing.                             │
│   • Advisor before declaring verdict.                           │
└─────────────────────────────────────────────────────────────────┘
```

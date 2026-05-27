# Worked Examples — From the 2026-05-10 gw2-compliance-agent Session

Five case studies illustrating the doctrine in practice. Each one shows the failure mode → investigation → fix → verification cycle the doctrine produces.

The examples are deliberately scrubbed of project-internal details where they would be confusing in a deployment context, but the file:line citations and severity tags are real.

---

## Case Study 1 — F-311: Stale-orphan FIRAS Firestopping document

**Class:** S3 / Moderate × Certain × Single-document. Single isolated stale-orphan.

**Discovery path:**

1. Storage-side smoke (`scripts/diagnostic/smoke-blob-roundtrip.sh`) sampled 5 random Greenwich HTTPS-blob docs.
2. Result: 4 OK, 1 fail (HTTP 404 on a "FIRAS Firestopping Certificate" doc).
3. Doctrine principle 11 ("bugs cluster") triggered: widen the sweep to determine if N=1 or N=many.
4. DB query revealed two rows for the same logical document — one with Vercel's random-suffix URL (200 OK), one without (404).
5. HEAD-sweep across all 23 Greenwich HTTPS-blob URLs: 22 served 200, 1 served 404 (the same one). Pattern is isolated, not structural.
6. Hypothesis: re-upload created the new row + URL, but the legacy row's `deletedAt` was not set in the same transaction → orphan.

**Fix (atomic, reversible):**

```sql
BEGIN;
SELECT id, name, file_url, deleted_at AS before_state
  FROM documents WHERE id = 'a72a15c4-2d10-4163-8d8f-a56825cab779';
UPDATE documents
   SET deleted_at = now()
 WHERE id = 'a72a15c4-2d10-4163-8d8f-a56825cab779' AND deleted_at IS NULL;
SELECT id, deleted_at AS after_state
  FROM documents WHERE id = 'a72a15c4-2d10-4163-8d8f-a56825cab779';
COMMIT;

-- Reversal: UPDATE documents SET deleted_at = NULL WHERE id = 'a72a15c4-...';
```

**Doctrine patterns demonstrated:**

- Pattern 4 (atomic prod write + reversal SQL captured)
- Principle 11 (bugs cluster — but in this case absence of clustering said "isolated")
- F-211 lens: symptom-fix vs structural-fix decision (chose symptom + filed structural follow-up under P2 #28).

**Output artifact:** `SMOKE-2026-05-10.md` with full evidence.

---

## Case Study 2 — F-312: Documents permanently stuck in PROCESSING

**Class:** S2 / Major × Certain × Single-document each. Structural defect.

**Discovery path:**

1. Operator browser-side smoke uploaded `TECHNICAL_ARCHITECTURE.pdf` to gw2.world.
2. After 7 minutes, status still PROCESSING with `processed_at = NULL`.
3. DB query for 5 most-recent uploads: ALL stuck in PROCESSING. Most recent successful processing was 2 days prior.
4. Initial hypothesis (the obvious one): pipeline broken.
5. Wider query: 880 ANALYZED, 549 FAILED, 51 PENDING, 8 PROCESSING. Pipeline overall alive — only 8 specific docs stuck.
6. **Layered defect** uncovered via parallel forensic dives (Explore agents):
   - **Cause 1:** `processed_at` only set when status flips to ANALYZED (`src/lib/documents.ts:124`), not on any other transition.
   - **Cause 2:** Reaper at `src/lib/validation/recovery.ts:33` filters on `processed_at < threshold`. Since cause 1 leaves it NULL during PROCESSING, the reaper never matches stuck rows. Function is structurally broken.
   - **Cause 3:** Reaper has zero callers. Not wired to any cron, route, or startup hook. Pure dead code.
   - **Cause 4:** Inngest `onFailure` handler at `src/workflows/document-process.ts:73-84` swallows write errors silently.

**Phase 0 (operator unblock, atomic SQL):**

```sql
BEGIN;
UPDATE documents
   SET status = 'FAILED',
       processed_at = now(),
       ai_analysis = COALESCE(ai_analysis, '{}'::jsonb)
                     || jsonb_build_object('reaper', 'F-312 manual reap 2026-05-10 phase 0')
 WHERE id = '737f0e14-...' AND status = 'PROCESSING';
COMMIT;
```

**Phase 2 (structural fix, planned PR):**

- Fix `processed_at` semantics — always set, not just on ANALYZED
- Wire the reaper to a Vercel Cron `*/15 * * * *`
- Add defensive retry on `onFailure` write
- Add tests pinning the reaper invariant

**Doctrine patterns demonstrated:**

- Principle 9 (untested error paths are broken error paths) — the stuck-PROCESSING class lives entirely in the error path
- Principle 12 (test the seams) — the defect lives at the worker↔DB seam (status-write race)
- Layer 6 Pattern 4 (Phase 0 = atomic prod write with reversal)
- Forensic dive via parallel `Explore` agents (Layer 1 plugin capability)

**Output artifact:** `F-312-F-313-CLEANUP-SANITATION-PLAN.md`.

---

## Case Study 3 — F-313: Demo-seed pollution on /projects listing

**Class:** S3 / Moderate hybrid × Certain × Single-tenant.

**Discovery path:**

1. Operator uploaded a doc but reported "project page shows too many projects — need sanitiser."
2. Browser screenshot showed 14 project cards for the operator (5 their own + others).
3. DB query: project list grouped by `user_id`:
   - 5 owned by primary admin user
   - 4 owned by secondary admin user (also operator)
   - 4 owned by `system:demo-seed` (fixture data)
   - 1 owned by `system:archived` (fixture data)
4. Forensic dive (`feature-dev:code-explorer` agent) located the listing endpoint at `src/lib/projects.ts:88-114`.
5. Root cause confirmed at `src/lib/projects.ts:96`:
   ```typescript
   const where = elevated ? baseWhere : { userId, ...baseWhere };
   //                       ^^^^^^^^^ no system:* exclusion
   ```
6. F-222 admin elevation is intentional ("support staff need cross-tenant read access for incident triage"), but `baseWhere = { deletedAt: null }` lacks a `system:*` filter.

**Phase 1 (data cleanup, atomic SQL):**

```sql
BEGIN;
UPDATE documents SET deleted_at = now()
 WHERE deleted_at IS NULL
   AND project_id IN (SELECT id FROM projects WHERE user_id LIKE 'system:%' AND deleted_at IS NULL);
UPDATE projects SET deleted_at = now()
 WHERE user_id LIKE 'system:%' AND deleted_at IS NULL;
COMMIT;
```

Result: 5 projects + 734 docs soft-deleted. Listing dropped from 14 cards to 9.

**Phase 3 (code fix, follow-up PR):**

```typescript
const baseWhere = { deletedAt: null };
const elevatedWhere = { ...baseWhere, NOT: { userId: { startsWith: 'system:' } } };
const where = elevated ? elevatedWhere : { userId, ...baseWhere };
```

**Doctrine patterns demonstrated:**

- Principle 4 (auth ≠ authz) — F-222 elevation correct, but missing system:* exclusion in the where clause
- F-211 lens — the structural fix (Phase 3 code change) is type-enforced; the data-only fix (Phase 1) closes the symptom but doesn't prevent recurrence
- Layer 6 Pattern 4 (atomic Phase 1)
- Bonus finding (collapsed long-standing P1): the 686-broken-`/uploads/` set turned out to live in `system:demo-seed`'s Greenwich project, not real user data — re-upload work was unnecessary

**Output artifact:** Phase 1 SQL log + Phase 3 PR (separate from F-314).

---

## Case Study 4 — F-314: Asymmetric admin elevation on write paths

**Class:** S3 / Moderate × Certain × Single-tenant.

**Discovery path:**

1. After F-313 Phase 1 cleanup, operator reported a "shadow" Greenwich Plot 19.05 project they couldn't delete.
2. DB query: the shadow project is owned by the operator's secondary admin user; operator is logged in as primary admin.
3. Forensic dive: `getAllProjects` and `getProject` honor F-222 admin elevation, but `updateProject` (`src/lib/projects.ts:140`) and `deleteProject` (`src/lib/projects.ts:174`) tenancy-lock with `where: { id, userId }` — no elevation lift.
4. Result: admin can SEE other tenants' projects (correct, F-222) but cannot mutate them (silent 404). Asymmetry.

**Plan:** 8 TDD tasks over ~2 hours.

| Task | What |
|---|---|
| 0 | Worktree prep (branch off latest main) |
| 1 | New helper `auditAdminBypassWrite` (sibling of `auditAdminBypass` for write actions) |
| 2 | Regression pin: non-admin update returns null |
| 3 | Failing tests: admin update other-tenant + audit |
| 4 | Implement updateProject elevation |
| 5 | Failing tests: admin delete other-tenant + audit + idempotency |
| 6 | Implement deleteProject elevation |
| 7 | Full test suite + tsc + biome + build |
| 8 | Push branch + open PR |

**Code change for `deleteProject`:**

```typescript
// BEFORE:
const existing = await prisma.project.findFirst({
  where: { id, userId, deletedAt: null },
});
if (!existing) return false;
await prisma.project.update({
  where: { id, userId },
  data: { deletedAt: new Date() },
});

// AFTER (mirroring getProject's F-222 pattern):
const elevated = hasElevatedAccess(userId);
const where = elevated ? { id, deletedAt: null } : { id, userId, deletedAt: null };
const existing = await prisma.project.findFirst({ where });
if (!existing) return false;
await prisma.project.update({ where: { id }, data: { deletedAt: new Date() } });
const crossTenant = elevated && existing.userId !== userId;
if (crossTenant) {
  auditAdminBypassWrite('project', userId, { resourceId: id, action: 'DELETE' });
}
```

**Doctrine patterns demonstrated:**

- Layer 6 Pattern 1 (Plan → Verify → Execute → Verify → Persist)
- Layer 6 Pattern 3 (TDD: RED → GREEN → commit, every task)
- Layer 6 Pattern 8 (git worktree branch hygiene: confirmed 3 PRs landed during planning, branched off actual latest main)
- Layer 6 Pattern 9 (skill-first: writing-plans → TDD → verification-before-completion → requesting-code-review)
- F-211 lens: invariant ("admin can list, read, AND mutate cross-tenant projects with audit trail") now enforced at the data-access layer in symmetry with F-222

**Output artifact:** PR #76 (4 commits + waiver-trigger empty commit, all CI green).

---

## Case Study 5 — Third-party report cross-check (the F-222 "damage report")

**Class:** Doctrine application — meta-pattern.

**Trigger:** A third-party reviewer (LLM, channel unspecified) submitted a report titled "F-222 damage report" claiming a recently-merged PR broke F-222 with "rule breaking and damage to the application."

**Cross-check process:**

1. Doctrine treats the report as **input to verify, not output to trust**.
2. Verify each cited file:line against the actual codebase:

| Report claim | Verified? | Real severity |
|---|---|---|
| Control flow: `if (!doc \|\| doc.deletedAt) return null` fires before elevation | ✅ Correct | Behavior change, not a defect |
| Pre-PR allowed admin to mutate soft-deleted state | ✅ Correct | But this was a **hidden F-219 violation**, not a feature |
| Bombshell A: verifyProjectAccess doesn't filter deletedAt | ✅ Correct | S2 / Major (separate issue) |
| Bombshell B: verifyDocumentAccessForValidation no admin-bypass | ✅ Correct | S2 / Major (pre-existing) |
| Bombshell C: restoreDocument has zero authz | ✅ Correct on function | But **wrong on blast radius** — zero callers in app/. Theoretical not exploitable. Report inflated to S0; actual is S2 defense-in-depth. |
| Test gap claim | ✅ Correct that tests are missing | But the test the report advocates would pin the WRONG invariant |

3. F-219 docstring at `src/lib/projects.ts:54-58` explicitly says "Admins still see only live rows here; recovery is a deliberate operator action." — the report ignored this carve-out.

4. Pre-PR-#75 was a hidden F-219 violation: `updateDocumentStatus` had no `deletedAt` filter on `prisma.document.update`. PR #75 corrected this.

5. Called `advisor()` for second opinion before declaring verdict.

6. Advisor confirmed framing AND added a gap I had missed — my F-314 plan inherits the same audit-on-denied-attempt gap. Recommended file F-317.

**Verdict:** Report is **70% correct on facts, 30% wrong on framing.** PR #75 enforces F-219, does NOT break F-222.

**Findings filed (5 standalone PRs after current cycle):**

- F-316: `verifyProjectAccess` doesn't filter deletedAt — S2 mirror of report's Bombshell A
- F-317: No audit-log entry on denied admin attempts — S3 (feature gap, not contract violation)
- F-318: `deleteDocument` log message misleading post-PR — S3 trivial
- F-319: `restoreDocument` + `restoreProject` zero authz — S2 defense-in-depth (correctly downgraded from report's S0)
- F-320: `verifyDocumentAccessForValidation` no admin-bypass — S2 pre-existing

**Doctrine patterns demonstrated:**

- Layer 6 Pattern 6 (third-party report cross-check)
- Layer 6 Pattern 2 (every claim cites file:line — applied to verify the report's citations)
- Layer 6 Pattern 7 (advisor before substantive commitment)
- Layer 8 conflict resolution rule: don't silently switch on advisor's input — synthesize transparently
- Anti-pattern A6 (don't treat third-party LLM review as ground truth)

**What would have happened without the cross-check:**

Acting on the report's headline ("revert PR #75") would have re-opened the hidden F-219 violation that PR #75 fixed. The doctrine prevented this misdirection.

---

## Cross-cutting lessons

What these 5 case studies have in common:

| Lesson | Demonstrated by |
|---|---|
| Evidence-only — every finding has a reproducer | All 5 |
| Bugs cluster (or DON'T — both are signal) | F-311 (didn't cluster), F-312 (clustered) |
| Match machinery to scope | F-311 (atomic SQL), F-314 (8-task plan) |
| Read the error paths | F-312 (the entire defect lives in `onFailure`) |
| Auth ≠ authz | F-313, F-314 |
| Schemas drift faster than docs | F-313 (the 686 set was demo-seed, not what docs implied) |
| Third-party reviews need cross-check | F-222 case study |
| Composition: skill stack routes by scope | All 5 |

The doctrine memory + skill stack + workflow patterns are what turn each of these from "saw a problem and fixed it" into "found a class of problem, contained it, structured the fix, and persisted the lesson."

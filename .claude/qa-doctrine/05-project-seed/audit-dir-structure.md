# Layer 5 — Project Audit Directory Structure

When the doctrine is applied to a specific project, set up an audit dir parallel to the worktree.

## Convention

```
/home/<user>/audits/<project-slug>/
├── SESSION-HANDOFF-YYYY-MM-DD.md         # canonical state, refreshed per session
├── 00-PROGRESS-REVIEW.md                 # ongoing audit synthesis
├── 07-FINAL-REPORT.md                    # end-of-audit synthesis
├── F-XXX-MIGRATION-PLAN.md               # for each non-trivial fix
├── F-XXX-CLEANUP-SANITATION-PLAN.md      # for cleanup phases
├── SMOKE-YYYY-MM-DD.md                   # smoke-test evidence
├── scripts/
│   ├── recovery/                         # mutating SQL scripts (BEGIN/COMMIT, reversal SQL)
│   └── diagnostic/                       # read-only investigation scripts
└── smoke-results/                        # smoke logs by date
    ├── YYYY-MM-DD-storage.log
    ├── YYYY-MM-DD-fXXX-listing.tsv
    └── YYYY-MM-DD-fXXX-soft-delete.log
```

## Why parallel to the worktree

The worktree is the code (Prisma schema, Next.js routes, etc.). The audit dir is the **forensic trail**: plans, reports, evidence. They live together but separated for these reasons:

- Audit dir survives `git clean -fdx` on the worktree.
- Audit dir is portable across worktree clones (audits don't move when you re-clone).
- Smoke logs include credentials/PII that should not be committed; gitignored audit dir keeps them off the repo.

## Antigravity / browser-visible mirror (optional)

If using Google Antigravity or a similar browser-context-aware setup, mirror the audit dir to a path the browser can read:

```
/home/<user>/code/audits/<project-slug>/   ← browser-visible mirror
/home/<user>/audits/<project-slug>/        ← canonical (this is the source of truth)
```

Sync after every meaningful edit:

```bash
cp -r ~/audits/<slug>/SESSION-HANDOFF-*.md ~/code/audits/<slug>/
cp -r ~/audits/<slug>/SMOKE-*.md ~/code/audits/<slug>/
cp -r ~/audits/<slug>/F-*.md ~/code/audits/<slug>/
cp -r ~/audits/<slug>/smoke-results/ ~/code/audits/<slug>/
cmp ~/audits/<slug>/SESSION-HANDOFF-*.md ~/code/audits/<slug>/SESSION-HANDOFF-*.md && echo "synced ✓"
```

Stale browser context is a common failure mode — the assistant sees a different state than reality.

## Recovery scripts pattern

Every mutating script in `scripts/recovery/` follows the same shape:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Host allowlist — refuse to run if not pointing at the right DB
DATABASE_URL=$(age -d -i ~/.secrets-vault/.age-key ~/.secrets-vault/.env.<project>.age 2>/dev/null \
  | sed -nE 's/^DATABASE_URL_UNPOOLED="?(postgresql:\/\/[^"]+\?sslmode=require).*/\1/p')
HOST=$(echo "$DATABASE_URL" | sed -E 's|.*@([^/?]+).*|\1|')
case "$HOST" in
  ep-<expected-prefix>*neon.tech) ;;
  *) echo "✗ wrong host: $HOST"; exit 2;;
esac

# Atomic transaction with idempotency guard
psql "$DATABASE_URL" -e -c "
BEGIN;
  SELECT '<descriptor>', state-before;
  UPDATE <table> SET <col> = <val> WHERE <id> = '<specific-id>' AND <invariant-guard>;
  SELECT '<descriptor>', state-after;
COMMIT;
" | tee /home/<user>/audits/<slug>/smoke-results/$(date +%Y-%m-%d)-<descriptor>.log

# Print reversal SQL so it's captured in the log
echo "Reversal SQL: BEGIN; UPDATE <table> SET <col> = <prev-val> WHERE <id> = '<specific-id>'; COMMIT;"
```

Doctrine: never run a destructive SQL without:
1. Host allowlist (refuse if wrong DB)
2. Atomic BEGIN/COMMIT
3. Idempotency guard (`AND deletedAt IS NULL` or similar)
4. Before/after evidence SELECTs
5. Reversal SQL printed to the log

## Diagnostic scripts pattern

Read-only versions of the recovery pattern. No `UPDATE`/`INSERT`/`DELETE` — `SELECT` only. Same host allowlist.

Example: `scripts/diagnostic/url-shape-distribution.sh` outputs the histogram of `documents.file_url` shapes per project — used for the F-313 cleanup decision.

## Handoff doc rotation

A new `SESSION-HANDOFF-YYYY-MM-DD.md` per session, NOT per day. The previous day's handoff stays available as historical context; the latest is canonical.

The project memory pointer (`~/.claude/projects/.../<slug>.md`) updates its `Always-current handoff` line each session to point at the newest doc.

## Index this dir explicitly

The audit dir contents should be listed in the project memory pointer's "Scripts archive" section so future sessions discover them without grep.

## Verification

```bash
# Verify the audit dir + worktree mirror are in sync
diff -r ~/audits/<slug>/ ~/code/audits/<slug>/ | head
# Expected: no output (perfect sync), or only acceptable additions in mirror

# Verify the most recent handoff is referenced from project memory
grep "SESSION-HANDOFF" ~/.claude/projects/<sanitized-cwd>/memory/<slug>.md
# Expected: line citing the latest YYYY-MM-DD doc
```

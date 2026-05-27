#!/usr/bin/env bash
#
# Atomic production write template — Master Tester Doctrine pattern.
#
# Doctrine: never run destructive SQL on prod without
#   1. Host allowlist (refuse if wrong DB)
#   2. Atomic BEGIN/COMMIT
#   3. Idempotency guard
#   4. Before/after evidence SELECTs
#   5. Reversal SQL printed to the log
#
# Usage: copy this file, replace <PLACEHOLDERS>, chmod +x, run.
#
# Reference worked examples in ../EXAMPLES/F-311-stale-orphan.md and
# ../EXAMPLES/F-313-system-pollution.md from this deployment pack.

set -euo pipefail

# ===== Step 1: host allowlist =====
DATABASE_URL=$(age -d -i ~/.secrets-vault/.age-key ~/.secrets-vault/.env.<PROJECT>.age 2>/dev/null \
  | sed -nE 's/^DATABASE_URL_UNPOOLED="?(postgresql:\/\/[^"]+\?sslmode=require).*/\1/p')
HOST=$(echo "$DATABASE_URL" | sed -E 's|.*@([^/?]+).*|\1|')
case "$HOST" in
  <EXPECTED-DB-HOST-PREFIX>*) ;;
  *) echo "✗ wrong host: $HOST (refusing to run)"; exit 2 ;;
esac

# ===== Step 2: log to a dated file =====
LOG_DIR=/home/<user>/audits/<project>/smoke-results
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/$(date +%Y-%m-%d)-<descriptor>.log"

# ===== Step 3: target identifier (replace with the specific resource you're modifying) =====
TARGET='<specific-uuid-or-id>'

# ===== Step 4: atomic transaction =====
psql "$DATABASE_URL" -e -c "
BEGIN;

-- Pre-state evidence
SELECT id, <relevant-fields> AS before_state
  FROM <table>
 WHERE id = '$TARGET';

-- The actual mutation, with idempotency guard
UPDATE <table>
   SET <col> = <new-value>,
       <other-tracking-cols> = ...
 WHERE id = '$TARGET'
   AND <invariant-guard>;     -- e.g., AND deleted_at IS NULL

-- Post-state evidence
SELECT id, <relevant-fields> AS after_state
  FROM <table>
 WHERE id = '$TARGET';

COMMIT;
" 2>&1 | tee "$LOG"

# ===== Step 5: print reversal SQL =====
echo
echo "--- Reversal SQL (do NOT run unless reverting this change) ---" | tee -a "$LOG"
cat <<REVERSAL | tee -a "$LOG"
BEGIN;
UPDATE <table>
   SET <col> = <previous-value>,
       <other-tracking-cols> = <previous-tracking-values>
 WHERE id = '$TARGET';
SELECT id, <relevant-fields> FROM <table> WHERE id = '$TARGET';
COMMIT;
REVERSAL

echo
echo "✓ Done. Log: $LOG"

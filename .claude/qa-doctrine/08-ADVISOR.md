# Layer 8 — Advisor Configuration

The `advisor()` tool gives access to a stronger reviewer model with the full conversation transcript as context. Used in this session to second-opinion the F-222 third-party-report cross-check.

## Configuration

```jsonc
// ~/.claude/settings.local.json
{
  "advisorModel": "claude-opus-4-7"
}
```

Or set per-session via `/advisor` slash command:

```
/advisor
> Advisor set to Opus 4.7
```

## Tool signature

```
advisor()
```

No parameters. The full transcript is forwarded automatically. The advisor sees:
- Original task
- Every tool call you made
- Every tool result
- Your reasoning blocks
- Subagent output
- Your conclusions so far

## When to call

| Situation | Call advisor? |
|---|---|
| Before substantive work (writing, editing, declaring an answer) | ✅ |
| When stuck (errors recurring, approach not converging) | ✅ |
| Considering a change of approach | ✅ |
| Before declaring "done" on long task | ✅ (after writing the deliverable durable) |
| Before acting on a third-party report's framing | ✅ |
| Mechanical follow-up dictated by tool output you just read | ❌ |
| Trivial completion (typo fix, single-line change) | ❌ |
| After every tool result | ❌ — cost exceeds value |
| To "double-check" without a specific question | ❌ — wastes capacity |

## How to call effectively

Three patterns:

### Pattern A: orient-then-call

```
1. Read files / run commands (orientation)
2. Form preliminary verdict (no commit yet)
3. Call advisor()
4. Reconcile, then commit to action
```

This is the pattern from the F-222 cross-check — verify file:line, form preliminary "report is wrong on framing", call advisor for second opinion, get confirmation + missed gap (audit-on-denied), THEN write the user-facing response.

### Pattern B: stuck-loop break

```
1. Try approach A (fail)
2. Try approach B (fail)
3. Call advisor() with both attempts visible in transcript
4. Apply advisor's redirection
```

The advisor sees what you've tried and can identify the wrong-axis problem.

### Pattern C: completion gate

```
1. Complete the work (write the file, commit the change, etc — make it durable FIRST)
2. Call advisor() to review
3. Apply any catches advisor surfaces in a follow-up commit
```

Note: write the deliverable durable BEFORE the advisor call. If the session ends during the call (timeout, network), durable work persists; in-flight unwritten work doesn't.

## Conflict resolution

If advisor's view contradicts retrieved data:

**Don't silently switch.** Surface the conflict in ONE more advisor call:

> "I found X at src/lib/auth.ts:47 (the deletedAt filter is present). You suggested the filter is missing. Which evidence breaks the tie?"

The advisor saw your evidence but may have under-weighted it. Explicit reconcile is cheaper than committing to the wrong branch.

Repeated calls don't help — if the second advisor call still disagrees with primary-source evidence, trust the primary source. Update the advisor's view in your next call, but don't keep oscillating.

## Worked example from this session

The F-222 third-party report claimed PR #75 broke F-222. My orientation:
1. Read `src/lib/access-control.ts` line-by-line — confirmed control flow matches report's claim.
2. Read pre-PR-#75 version (`git show 9e1c17a^:src/lib/access-control.ts`) — confirmed pre-PR allowed admin to mutate soft-deleted state.
3. Read F-219 docstring at `src/lib/projects.ts:54-58` — found explicit carve-out: "Admins still see only live rows here."
4. Formed preliminary verdict: "Report is correct on facts but wrong on framing — PR #75 enforces F-219, doesn't break F-222."
5. **Called advisor()** with transcript including all my evidence.
6. Advisor confirmed framing + added a gap I missed: my F-314 plan inherits the same audit-on-denied-attempt gap. Recommended file F-317.
7. Wrote the user-facing response with both my verdict AND advisor's added finding.

Without the advisor call I'd have shipped a verdict missing one of the 5 follow-up findings.

## Cost-aware usage

Advisor calls forward the FULL transcript — typically expensive. Default to:

- 1 advisor call per substantial decision (plan-approval, framing-verdict, completion-gate)
- 2-3 calls per multi-hour session
- Not after every Edit / Bash / Read

If you're calling advisor 5+ times per session, you're using it as a thinking aid rather than a second opinion. Use the assistant's own thinking blocks for that; reserve advisor for decisions.

## Settings reference

Full advisor-related settings:

```jsonc
{
  "advisorModel": "claude-opus-4-7",   // model ID for advisor calls

  // Other settings that affect advisor behavior:
  "alwaysThinkingEnabled": true,       // extended thinking on supported models
  "showThinkingSummaries": true        // see what the advisor reasoned about (ctrl+o)
}
```

The advisor is most useful at framing/orient-vs-act boundaries. Use it sparingly and well; the doctrine memory + skill stack handle most decisions natively.

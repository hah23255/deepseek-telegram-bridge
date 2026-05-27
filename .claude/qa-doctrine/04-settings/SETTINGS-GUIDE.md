# Layer 4 — Settings Guide

How to apply `settings.local.json.template` to a peer system without breaking existing configuration.

## Where to put it

| Scope | File | When |
|---|---|---|
| User-global | `~/.claude/settings.json` | Personal preferences for all projects |
| Project-shared | `<repo>/.claude/settings.json` | Team-wide hooks, permissions, plugins (commit) |
| Project-local | `<repo>/.claude/settings.local.json` | Personal overrides for this project (gitignore) |

The doctrine pack template targets `~/.claude/settings.local.json` (user-global personal). Adjust if your team-shared config is canonical.

## Critical: merge, don't replace

**Wrong** (overwrites everything):
```bash
cp settings.local.json.template ~/.claude/settings.local.json
```

**Right** (merge):
```bash
# 1. Read existing file
cat ~/.claude/settings.local.json
# 2. Manually add the new keys (permissions.allow array entries, autoMode.allow array entries, etc.)
# 3. Use jq for programmatic merge:
jq -s '.[0] * .[1]' ~/.claude/settings.local.json settings.local.json.template > /tmp/merged.json
# Inspect /tmp/merged.json, then:
cp /tmp/merged.json ~/.claude/settings.local.json
```

Or use Claude Code's `update-config` skill — it knows how to merge correctly.

## Section-by-section

### `permissions.allow`

Narrow patterns for the gw2 prod stack. Replace `<prod-db-host-substring>` and `<prod-blob-domain-substring>` with values appropriate to your project.

**Substring vs prefix wildcards:**
- `Bash(curl:*)` — matches commands starting with `curl ...`. Does NOT match `SUFFIXED='...'; curl ...` because the prefix is `SUFFIXED=`.
- `Bash(*public.blob.vercel-storage.com*)` — substring match; works regardless of preceding shell-var assignments.

When in doubt, use substring. The classifier reads the full post-expansion command.

### `autoMode.allow`

This is the **classifier override**. The auto-mode classifier reads intent (e.g., "decrypted prod creds + prod DB read") and applies a soft_deny that supersedes per-tool `permissions.allow` rules. Only `autoMode.allow` clears that.

**Format:** plain-English factual scope statements. NO narrative justifications.

```
✓ "Read-only psql against host X are in scope. SELECT statements only."
✗ "User authorized this on Tuesday so admin can run psql..."
```

The classifier flags narrative as fabricated authorization claims and rejects the entry.

### `advisorModel`

Set to the strongest model your tier supports. Default for the doctrine: `claude-opus-4-7` (or whatever Opus version is current). Triggered via `/advisor` slash, then `advisor()` tool calls forward the full transcript.

### `enabledPlugins`

The plugin allowlist. See `01-PLUGINS.md` for the canonical doctrine stack.

### Other useful settings

- `autoMemoryEnabled: true` — auto-loads `~/.claude/projects/<sanitized-cwd>/memory/MEMORY.md` and writes new feedback memories
- `fileCheckpointingEnabled: true` — `/rewind` works after edits
- `alwaysThinkingEnabled: true` — extended thinking on supported models
- `skipAutoPermissionPrompt: true` — only set after consciously opting into auto mode

## Verification

After merging:

```bash
jq -e '.permissions.allow | length > 30' ~/.claude/settings.local.json     # has the doctrine patterns
jq -e '.autoMode.allow | length >= 3' ~/.claude/settings.local.json        # has $defaults + 2 scope statements
jq -e '.advisorModel' ~/.claude/settings.local.json                        # has advisor model
```

All three must return truthy. If any returns null / false, the merge missed that key.

## Troubleshooting

**Symptom:** classifier still blocks prod reads after `autoMode.allow` added.
**Cause:** the scope statement doesn't match the operation's intent verbatim.
**Fix:** read the classifier's reject message — it cites the specific concern. Add a more precise scope statement.

**Symptom:** `Bash(curl:*)` rule doesn't apply to a curl command.
**Cause:** command starts with shell-var assignment (`URL=...; curl "$URL"`).
**Fix:** restructure command OR add substring-match rule like `Bash(*<host-substring>*)`.

**Symptom:** plugins listed in `enabledPlugins` don't appear in skill listing.
**Cause:** marketplace not registered, or plugin not yet downloaded.
**Fix:** `claude plugin marketplace list` to confirm registration; `claude plugin install <name>@<source>` to force-fetch.

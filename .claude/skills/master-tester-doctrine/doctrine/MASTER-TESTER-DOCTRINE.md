# Master Tester Doctrine — Historical Directive (2026-03-05)
Skill home: `~/.claude/skills/master-tester-doctrine/SKILL.md`
Full references: see [`INDEX.md`](./INDEX.md) for a map of every long-form chapter.

### Core Laws (non-negotiable)
1. **NEVER modify a test to fix CI.** Tests are contracts. Fix the code. (Rule 3 + HH directive 10:14)
2. **Test behaviour, not implementation.** Public API only. Never assert on internal state.
3. **AAA pattern.** Arrange → Act → Assert. Every test, every time.
4. **DAMP over DRY.** Readability beats brevity in tests.
5. **Isolated tests.** No shared state. `beforeEach`/`afterEach` reset everything.
6. **Never mock `fetch`/`axios` directly.** Use MSW. Always.
7. **Ban `as any` in test files.** Use `satisfies`, `Partial<T>`, or `vi.mocked()`.
8. **Tests must be deterministic.** Never use `Date.now()`, `Math.random()` without mocking. Use `vi.useFakeTimers()`.
9. **One logical concept per test.** Tight scope = fast diagnosis.
10. **No tautological tests.** Don't test JS mechanics. Test business logic.

### Advanced Patterns
- **Property-based fuzzing:** `fast-check` for date math, parsers, financial logic
- **Architectural boundaries:** `dependency-cruiser` / `knip` as CI gates
- **Race conditions:** MSW with intentional out-of-order resolution + `AbortController` verification
- **Type-level tests:** `@type-challenges/utils` `Expect<Equal<A,B>>` — compiler as runner
- **Poison Pill Mock:** `Proxy` that throws on any unmocked property access
- **OOM on CI:** `--pool=threads`, manual `global.gc()`, or `--max-old-space-size=4096`
- **Flaky tests:** Quarantine with `.skip` immediately. Zero tolerance.

### The Oath
*"I do not test to achieve a percentage. I test to sleep soundly. I assume the network is hostile, the user is chaotic, and time is an illusion. My tests are the unbreakable contract between the present codebase and its future self."*

35. **Lazy-initialize connection pools in production code.** Eager module-level `PrismaClient` (or any connection pool) creation causes open-handle hangs in Vitest — tests importing tools but not calling DB methods open real connections that block process exit. Fix: Proxy-based lazy initialization (`get(_t, prop) { return Reflect.get(getPrisma(), prop); }`). Never add teardown hacks or `process.exit()` workarounds until the eager-init root cause is ruled out. (2026-03-05 — 8 CI runs to trace this.)

37. **Multi-tier secret stores invite stale-auth bugs.** Any system that resolves credentials across multiple tiers (vault / config / env / per-agent override) will eventually serve a stale value because some tier was updated and others were not. Fix: a single source of truth (e.g., a typed `SecretRef`) plus an atomic rotation script that updates every consumer. Silent failure pattern to watch for: "0 tokens used" + "completed successfully" masks a 401 from the upstream API. Test discipline: assert non-zero usage *and* HTTP 2xx, not just the absence of an exception. (Field note, 2026-03)

38. **JWT-authenticated AI endpoints with short expiries fail silently in long-lived workers.** Vendor endpoints that use JWT OAuth instead of long-lived API keys (typical JWT lifetime: 24–48h) will start returning 401 mid-shift, often after a successful warmup. Detect: monitor for 401 spikes correlated with the JWT lifetime. Mitigate: scheduled refresh ahead of expiry; reject `sk-*` style keys early if the endpoint requires JWT. Test discipline: a test that injects an expired JWT and asserts the refresh path runs. (Field note, 2026-03)

39. **Hot-reloading config does not always re-read upstream secret stores.** Many config-reload commands only re-evaluate config-level mappings; the underlying encrypted secret store (vault / KMS / sealed-secrets) is typically decrypted once at process start. After rotating a secret in the upstream store, restart the consumer process or the consumer will keep using the cached value. Test discipline: a smoke test that rotates a test secret, restarts the consumer, and asserts the new value reached the API. (Field note, 2026-03)

40. **In-config env-var overrides shadow upstream secret stores indefinitely.** When a config file allows inline env-var overrides as an escape hatch (`env.vars.PROVIDER_KEY=...`), an override added during a manual incident response will silently outlive its usefulness and shadow the canonical secret store forever. Cleanup rule: after every manual override, file a ticket to remove it; periodically grep for inline env overrides and reconcile against the secret store. (Field note, 2026-03)

41. **Adaptive Fault Tolerance:** When a minor script or data source is missing (e.g. GitHub trends), fall back to previous data to ensure report delivery rather than failing the process. (2026-04-19)
42. **Immediate Execution of Critical Instructions:** When a pending instruction in the register is marked priority CRITICAL, execute immediately and tag with deployment features before proceeding. (2026-04-19)
43. **Graceful Handling of Empty Inboxes:** During email triage, if the inbox is empty, simply report 0 processed and proceed without stalling the flow. (2026-04-19)
44. **Next.js Auth Middleware CORS Issues:** When implementing Next.js Auth (Clerk) middleware, use `auth()` for RSC checks and manual redirects instead of `auth.protect()`. The latter can cause CORS errors on prefetching and lead to `MIDDLEWARE_INVOCATION_FAILED`. (2026-04-20)
45. **Modular Prompt Architecture in Multi-Agent Systems:** Split monolithic prompt files into a dedicated `prompts/` directory with individual files per agent/role. This provides tighter scoping, better maintainability, and prevents merge conflicts. (2026-04-20)
46. **Package Lock Synchronization in Monorepos:** Always ensure `pnpm-lock.yaml` is fully synchronized with dependency tools (like `tscanner`) and remove conflicting package manager locks (e.g. `package-lock.json`) before deployment to prevent deployment conflicts. (2026-04-22)

47. **Automated Verification over Assumed State:** When running End-of-Day or similar routine cron jobs, never assume that previous automated actions (like instruction register checks) resulted in state changes. Always query logs (`git status`, `sessions_list`) directly to accurately report daily progress and adapt stand-up reflections to the actual evidence gathered. (2026-04-23)

48. **File Dependency Fallbacks:** When dependent scripts like GitHub trends refresh script are missing, fall back to live web fetch or static drop data to ensure the daily report delivery does not fail. (2026-04-25)

# Doctrine Index — Navigating The Inner Sanctum

> The `doctrine/` directory holds the long-form prose canon — the "Books" of the Master Tester Doctrine.
> The operational distillation lives in `../SKILL.md` and `../references/`.
> Read the doctrine for *depth and rationale*; read the references for *what to do right now*.

---

## Map: Golden Rule → Where The Long-Form Treatment Lives

| Golden Rule (operational)                       | Long-form chapter(s)                                                  |
|------------------------------------------------|------------------------------------------------------------------------|
| 1. Never modify a test to silence CI            | [`MASTER-TESTER-DOCTRINE.md`](./MASTER-TESTER-DOCTRINE.md) §Core Laws  |
| 2. Behavior, not implementation                 | [`modern-ts-testers-guideline.md`](./modern-ts-testers-guideline.md) §Book II + [`unit-testing-rule-book.md`](./unit-testing-rule-book.md) #1 |
| 3. AAA pattern                                  | [`unit-testing-rule-book.md`](./unit-testing-rule-book.md) #2          |
| 4. DAMP over DRY                                | [`unit-testing-rule-book.md`](./unit-testing-rule-book.md) #6          |
| 5. Isolated tests                               | [`unit-testing-rule-book.md`](./unit-testing-rule-book.md) #3 + [`modern-ts-testers-guideline.md`](./modern-ts-testers-guideline.md) §Book III #9 |
| 6. MSW for HTTP                                 | [`modern-ts-testers-guideline.md`](./modern-ts-testers-guideline.md) §Book III #7 |
| 7. Ban `as any`                                 | [`modern-ts-testers-guideline.md`](./modern-ts-testers-guideline.md) §Book I #2 + [`oath-of-the-master-tester.md`](./oath-of-the-master-tester.md) Book XIII #33 |
| 8. Deterministic tests                          | [`expanded-modern-ts-testers-guideline.md`](./expanded-modern-ts-testers-guideline.md) §Book V #13 + [`vanguard-of-ts-testing.md`](./vanguard-of-ts-testing.md) §Book XI #30 |
| 9. One concept per test                         | [`unit-testing-rule-book.md`](./unit-testing-rule-book.md) #7          |
| 10. No tautological tests                       | [`unit-testing-rule-book.md`](./unit-testing-rule-book.md) #10         |
| 11. Verify it fails for the right reason        | [`vanguard-of-ts-testing.md`](./vanguard-of-ts-testing.md) §Book XII #32 |
| 12. Zero tolerance for flakiness                | [`expanded-modern-ts-testers-guideline.md`](./expanded-modern-ts-testers-guideline.md) §Book VIII #23 |
| 13. Tests are production code                   | [`modern-ts-testers-guideline.md`](./modern-ts-testers-guideline.md) §Book IV #12 |
| 14. Coverage is vanity; mutation is truth       | [`expanded-modern-ts-testers-guideline.md`](./expanded-modern-ts-testers-guideline.md) §Book VIII #22 |
| 15. `.skip` requires four-tuple                 | Doctrine extension — see [`../references/golden-rules.md`](../references/golden-rules.md) #15 |

---

## Map: Advanced Pattern → Where The Long-Form Treatment Lives

| Pattern (operational)                            | Long-form chapter(s)                                                  |
|--------------------------------------------------|------------------------------------------------------------------------|
| Property-based testing (`fast-check`)            | [`oath-of-the-master-tester.md`](./oath-of-the-master-tester.md) §Book IX #25 + [`vanguard-of-ts-testing.md`](./vanguard-of-ts-testing.md) §Book X #28 |
| Round-trip property                              | [`oath-of-the-master-tester.md`](./oath-of-the-master-tester.md) §Book IX #26 |
| Race condition brute-forcing (MSW out-of-order)  | [`oath-of-the-master-tester.md`](./oath-of-the-master-tester.md) §Book XI #29 |
| Suspense / `createDeferred`                      | [`vanguard-of-ts-testing.md`](./vanguard-of-ts-testing.md) §Book IX #26 |
| Strict Mock (Poison Pill Proxy)                  | [`oath-of-the-master-tester.md`](./oath-of-the-master-tester.md) §Book XIII #33 |
| Architecture boundary tests (depcruise)          | [`oath-of-the-master-tester.md`](./oath-of-the-master-tester.md) §Book X #27 |
| Dead-code sonar (`knip`)                         | [`oath-of-the-master-tester.md`](./oath-of-the-master-tester.md) §Book X #28 |
| Type-level tests (`expect-type`)                 | [`expanded-modern-ts-testers-guideline.md`](./expanded-modern-ts-testers-guideline.md) §Book VII #20 + [`oath-of-the-master-tester.md`](./oath-of-the-master-tester.md) §Book XIII #32 |
| Exhaustive discriminated union → `never`         | [`expanded-modern-ts-testers-guideline.md`](./expanded-modern-ts-testers-guideline.md) §Book VII #21 |
| Branded types                                    | [`vanguard-of-ts-testing.md`](./vanguard-of-ts-testing.md) §Book X #27 |
| Inversion of control for globals                 | [`vanguard-of-ts-testing.md`](./vanguard-of-ts-testing.md) §Book XII #31 |
| Seeded PRNG / deterministic randomness           | [`vanguard-of-ts-testing.md`](./vanguard-of-ts-testing.md) §Book XI #30 |
| State-machine auto-generated tests (`@xstate/test`) | [`oath-of-the-master-tester.md`](./oath-of-the-master-tester.md) §Book XII #31 |
| Memory-leak / OOM defense                        | [`vanguard-of-ts-testing.md`](./vanguard-of-ts-testing.md) §Book XI #29 |
| Mutation discipline                              | [`vanguard-of-ts-testing.md`](./vanguard-of-ts-testing.md) §Book XII #32 + [`expanded-modern-ts-testers-guideline.md`](./expanded-modern-ts-testers-guideline.md) §Book VIII #22 |
| `findBy*` over `waitFor`                         | [`modern-ts-testers-guideline.md`](./modern-ts-testers-guideline.md) §Book IV #11 |

---

## Reading Order For First-Time Readers

If you have never read the doctrine before, read in this order. Each builds on the last.

1. **[`../SOUL.md`](../SOUL.md)** — *Why we test.* The identity and posture before the operations.
2. **[`oath-of-the-master-tester.md`](./oath-of-the-master-tester.md)** §The Oath at the end — *The creed.*
3. **[`unit-testing-rule-book.md`](./unit-testing-rule-book.md)** — *The 10 universal rules, plain prose.*
4. **[`modern-ts-testers-guideline.md`](./modern-ts-testers-guideline.md)** — *Books I–IV: philosophy, trophy, network, architecture.*
5. **[`expanded-modern-ts-testers-guideline.md`](./expanded-modern-ts-testers-guideline.md)** — *Books V–VIII: time, hooks, types, CI.*
6. **[`oath-of-the-master-tester.md`](./oath-of-the-master-tester.md)** §Books IX–XIII — *Property-based, architecture, concurrency, model-based, metaprogramming.*
7. **[`vanguard-of-ts-testing.md`](./vanguard-of-ts-testing.md)** — *The inner sanctum: quantum, types, runner subjugation, IoC, mutation.*
8. **[`MASTER-TESTER-DOCTRINE.md`](./MASTER-TESTER-DOCTRINE.md)** — *The historical directive log. Skim for context; the canon has moved into the references.*

---

## On The `MASTER-TESTER-DOCTRINE.md` Numbered Lessons (#35-#48)

These entries are field notes from production incidents, generalized to platform-agnostic principles where the original incident touched proprietary internals. They are preserved as a "lessons learned" register; the generalizable principles have also been promoted into the [Golden Rules](../references/golden-rules.md) and the [Zero-Trust Protocol](../references/zero-trust-protocol.md).

---

> The doctrine is the **why**.
> The references are the **what**.
> The scripts are the **how**.
> The SOUL is the **who**.

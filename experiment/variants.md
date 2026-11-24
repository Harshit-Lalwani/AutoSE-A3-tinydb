# Decision experiments

Two ADRs are tested by changing one decision and keeping everything else fixed.

## E1: Reviewer independence (ADR-008, D8)

| Variant | Trigger | What the reviewer sees |
|---|---|---|
| **isolated** (baseline, ADR-008) | `/autose review` on the PR | issue text + diff + repo at PR head |
| **informed** | `/autose review informed` on the PR | the same **plus** the implementer's PR description (claims, rationale, "all tests pass") and `design.md` when one exists |

Same reviewer model (MiniMax M3.1 Flash, thinking off), same prompt, same budget.
Measured on the 5 seeded PRs in `seeded_prs/` (3 with planted defects, 2 correct), each reviewed by
each variant. Metrics: defects caught (true `request_changes`), false approvals, false alarms on the
correct PRs, and whether the finding names the planted defect.

Hypothesis (written before the runs): the informed reviewer approves more, in particular S3 (the
band-aid whose description argues convincingly that clearing the cache "fixes" the issue) and S4
(scope creep hidden behind a correct feature).

## E2: Splitting the work: separate tester vs coder writes its own tests (ADR-001, D1)

| Variant | Trigger | Stage 4 |
|---|---|---|
| **default** (ADR-001) | label `autose` | separate tester agent writes the AC tests in a fresh context; coder cannot edit them |
| **single** | label `autose-single` | coder writes code **and** AC tests in one context; no tester agent |

Everything else (spec, design, checks, budgets, reviewer) is identical. Measured on issues I1–I4
(I5 is vague and stops or proceeds at stage 1 regardless). Metrics: hidden acceptance tests
passed, stage pass rates, implementation attempts, tokens, number of AC tests that fail on `main`
(non-vacuous), reviewer verdict.

Hypothesis: the separate tester writes more tests that fail on `main` and catches more coder
mistakes (more attempts), at higher token cost; hidden-test pass rate is similar or higher.

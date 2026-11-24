# Stage map

| # | Stage | Agent (model) | Artifact | Check before moving on | Who decides pass/fail | On failure |
|---|---|---|---|---|---|---|
| 1 | Requirements | Spec agent (Nemotron-3 Ultra), A1 SRS skill as system prompt | `spec.md` | `checks.py spec`: at least one acceptance criterion; every AC is Given/When/Then, has no `TBD`, no vague word from a fixed list; no `Blocking` question left unanswered | code (deterministic) | one retry with the check output; then stop and post the open questions on the issue |
| 2 | Design | Design agent (Nemotron-3 Ultra), reads `ARCHITECTURE.md` | `design.md` | `checks.py design`: JSON plan names ≥1 file; every existing file exists; named functions/classes found in the file are "changed", the others are recorded as "new" (ADR-013) | code | one retry with the check output; then stop |
| 3 | Implementation | Coder agent (Nemotron-3 Ultra) | `diff.patch` | `checks.py build`: diff non-empty and only in planned files or `tests/`; `compileall` + `import tinydb` + `mypy tinydb` pass | code | retry implement (shared budget of 3 attempts with stage 4) |
| 4 | Testing | Tester agent (Nemotron-3 Ultra) | `test_report.md` | `checks.py tests`: one test per AC (named `test_ac<k>_…`); `mypy` passes on the test file; full suite passes; at least one new test fails on `main` (the tests are not vacuous) | code | failures go back to stage 3 with the pytest output; after the 2nd failed attempt the design agent revises the plan once; after 3 attempts stop |
| 5 | Release | none (`orchestrator.py`, `stage_release`) | `pr.md` + PR link | PR is open; the dispatched `ci-workflow.yml` run on the PR head finishes `success` | code | stop; CI log linked in `pr.md` |
| 6 | Review | Reviewer agent (MiniMax M3.1 Flash, thinking off), separate job | `review.md` | verdict `approve`, backed by at least one command the reviewer actually ran; or 3 reviews (= 2 send-backs) used up | reviewer verdict, validated by code | `request_changes` + category `approach` → stage 2, `code` → stage 3 |

Every stage writes its artifact even when it fails, with a `## Why this stage stopped`
section, and the run ends with a comment on the issue linking the artifacts.
A person merges or closes the pull request; the workflow never merges.

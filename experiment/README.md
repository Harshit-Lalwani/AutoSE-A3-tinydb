# Experiment material

| folder | contents |
|---|---|
| `issues/` | the 5 issue texts, opened as issues #1–#5 (I1 = #1 … I5 = #5): 2 bugs (I1, I2), 2 features (I3, I4), 1 vague (I5) |
| `hidden_tests/` | 2–4 acceptance tests per issue, never shown to any agent. I1–I4's fail on `main` and pass with `reference/`; I5's only check that existing `search()` behaviour is preserved (the issue leaves the API open) |
| `reference/` | my reference fixes for I1–I4, used only to validate the hidden tests |
| `seeded_prs/` | the 5 reviewer-check PRs: `S<k>.patch` (diff), `S<k>.body.md` (PR description), `labels.csv` (ground truth). Opened as PRs #6–#10 (S1 = #6 … S5 = #10) |
| `variants.md` | what each decision-experiment variant changes (E1: reviewer isolation, E2: separate tester) |
| `scripts/` | `collect_results.py` (artifacts + hidden tests → `results/`), `stage_rates.py`, `render_diagrams.py` (report figures) |

The hidden tests were kept outside the repository until the last run had finished: the agents' sparse
checkout hides `experiment/`, but with full history an agent could still have read it from git objects.

Rebuild the results: `python experiment/scripts/collect_results.py <run_id> ...` (needs `gh` auth), then
`python experiment/scripts/stage_rates.py`.

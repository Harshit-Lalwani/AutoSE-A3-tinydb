# AutoSE A3: issue in, reviewed pull request out (tinydb fork)

CS6.403 AutoSE, Monsoon 2026, Assignment 3. Roll number 2023111028.

- Video Link: https://drive.google.com/drive/folders/1cJipdbbZFraef3eEKzbU5hrets5mTd0v?usp=sharing

- **Fork of:** [msiemens/tinydb](https://github.com/msiemens/tinydb), pinned at commit
  `edff96aeb2616402e9489d46e90a592c05565621`. `main` starts at that commit; upstream `master` is untouched.
  `main` is protected (changes only through pull requests).
- **Report:** [`report.pdf`](report.pdf) (LaTeX source [`report/report.tex`](report/report.tex), build with `report/build.sh`) · **Demo video:** [Google Drive](https://drive.google.com/drive/folders/1cJipdbbZFraef3eEKzbU5hrets5mTd0v?usp=sharing)
- **Architecture:** [`architecture/views/`](architecture/views) (component view, sequence view, stage map) and
  [`architecture/decisions/`](architecture/decisions) (ADRs, superseded ones kept).
  [`ARCHITECTURE.md`](ARCHITECTURE.md) is the tinydb architecture from A2, read by the design stage.
- **Workflow:** [`.github/workflows/autose.yml`](.github/workflows/autose.yml) (+ `autose-stages.yml`,
  `autose-review.yml`, `.github/actions/autose-setup`). Agent code and prompts: [`workflow/agent/`](workflow/agent);
  `workflow/github-workflows/` is a copy of the workflow files.
- **Experiment:** [`experiment/`](experiment) (5 issues, hidden tests, 5 seeded PRs, `variants.md`).
  **Results:** [`results/results.csv`](results/results.csv), [`results/runs.md`](results/runs.md) (links to every run, PR and review).

## Models

| Role | Model | Provider |
|---|---|---|
| Spec, design, coder, tester | `nvidia/nemotron-3-ultra-550b-a55b` | NVIDIA NIM (free tier); fallback OpenRouter `:free` |
| Reviewer | `minimaxai/minimax-m3.1-flash`, thinking off | NVIDIA NIM (free tier); fallback `google/gemma-4-31b-it:free` on OpenRouter |

Why: [ADR-011](architecture/decisions/ADR-011.md) (supersedes ADR-006).

**Spending limit.** All model use is on free tiers (NIM free tier; OpenRouter key without credits), so money
spent is zero. As the hard limit we use tokens ([ADR-012](architecture/decisions/ADR-012.md)): 2.5M tokens per
pipeline run and 400k per review, enforced in code before every model call. **Total used over all GitHub runs: 37.8M tokens** (32.9M builders,
4.9M reviewer; per run in `results/results.csv`, report §4).

## How to trigger the workflow

You need write access to this repository.

| Gesture | Effect |
|---|---|
| add label `autose` to an issue | full pipeline: spec → design → implement ⇄ test → PR + CI → independent review (≤ 2 send-backs) |
| comment `/autose` on an open issue | same |
| add label `autose-single` (or comment `/autose single`) | experiment E2 variant: the coder also writes the tests |
| comment `/autose review` on a PR | review only (isolated reviewer) |
| comment `/autose review informed` on a PR | experiment E1 variant: reviewer also sees the PR description/design |

Repository setup this needs: secrets `NVIDIA_NIM_API_KEY` (and optionally `OPENROUTER_API_KEY`); Settings →
Actions → "Allow GitHub Actions to create and approve pull requests"; branch protection on `main`.

Follow a run: the issue gets a start/stop comment, the Actions run has one job per stage group and review round
with a summary table, every job uploads its artifacts (`spec.md`, `design.md`, `diff.patch`, `test_report.md`,
`pr.md`, `review.md`, `state.json`, agent transcripts), the PR description is `pr.md`, and each review is posted
on the PR. The workflow never merges.

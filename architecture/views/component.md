# Component view

Who runs where, which tools and credentials each part holds, and how the parts call each other.
Boxes with a thick border are LLM agents; everything else is deterministic code.
The rule behind the picture: **agents never hold a GitHub token or an API key**. Only the
deterministic orchestrator talks to GitHub and to the model providers.

```mermaid
flowchart TB
    subgraph GH[GitHub]
        ISSUE[(Issue #N<br/>untrusted text)]
        PR[(Pull request<br/>autose/issue-N)]
        CI[[ci-workflow.yml<br/>pytest + mypy]]
        ART[(Actions artifacts<br/>spec.md design.md diff.patch<br/>test_report.md pr.md review.md<br/>state.json transcripts)]
    end

    subgraph WF[".github/workflows/autose.yml (one run per trigger)"]
        GATE["gate job<br/>perms: issues:write, contents:read<br/>• who triggered? (write/admin only)<br/>• which mode? pipeline / review-only<br/>• which variant?"]
        subgraph STAGES["stages job (reusable stages.yml)<br/>perms: contents:write, pull-requests:write, issues:write, actions:write"]
            ORCH["orchestrator.py<br/>state machine + checks.py<br/>holds MODEL keys and GH_TOKEN"]
            SPEC{{"Spec agent (stage 1)<br/>Nemotron-3 Ultra<br/>tools: none (one call)<br/>input: issue + README + A1 SRS skill"}}
            DES{{"Design agent (stage 2)<br/>Nemotron-3 Ultra<br/>tools: bash (read-only*)<br/>input: spec ACs + ARCHITECTURE.md + repo"}}
            IMP{{"Coder agent (stage 3)<br/>Nemotron-3 Ultra<br/>tools: bash, write_file<br/>input: spec ACs + design.md (+ failures)"}}
            TST{{"Tester agent (stage 4)<br/>Nemotron-3 Ultra<br/>tools: bash, write_file<br/>input: spec ACs + repo"}}
            REL["stage_release (stage 5)<br/>no LLM: push, gh pr create,<br/>dispatch CI, wait"]
        end
        subgraph REV["review job (reusable review.yml)<br/>perms: contents:read, pull-requests:write"]
            RORCH["review.py<br/>holds REVIEWER key + GH_TOKEN"]
            RAG{{"Reviewer agent (stage 6)<br/>MiniMax M3.1 Flash (other family)<br/>tools: bash (run anything, no creds)<br/>input: issue + diff + repo@PR head"}}
        end
        FIX["fix jobs (stages.yml again, mode=resume)<br/>back to design or implement"]
    end

    ISSUE -- "label autose / comment /autose" --> GATE
    GATE --> STAGES
    ORCH --> SPEC --> ORCH
    ORCH --> DES --> ORCH
    ORCH --> IMP --> ORCH
    ORCH --> TST --> ORCH
    ORCH --> REL
    REL -- "git push (token in URL, step-scoped)<br/>gh pr create" --> PR
    REL -- "gh workflow run + gh run watch" --> CI
    ORCH -- upload --> ART
    STAGES --> REV
    RORCH --> RAG --> RORCH
    RORCH -- "gh pr review --comment<br/>(review.md)" --> PR
    REV -- "request changes<br/>(round < 3)" --> FIX
    FIX -- download --> ART
    FIX --> REV
    PR -- "merge or close" --> HUMAN([Maintainer])
```

`*` "read-only" is enforced after the fact: the orchestrator runs `git status` after a
read-only agent and discards any change it made (see ADR-005).

## Agents and their tools

| Agent | Stage | Model (fallback) | Tools | Sees | Never sees |
|---|---|---|---|---|---|
| Spec | 1 | Nemotron-3 Ultra 550B on NIM (same model, free on OpenRouter) | none, one chat call | issue text, `README.rst`, A1 `SKILL.md` | code, other agents |
| Design | 2 | same | `bash` in repo; changes discarded | spec ACs, `ARCHITECTURE.md`, repo | issue text (only via spec) |
| Coder | 3 | same | `bash`, `write_file` | spec ACs, `design.md`, failing test output on retries | tester's reasoning; may not edit tester's test file |
| Tester | 4 | same | `bash`, `write_file` | spec ACs, repo with the change | coder's conversation |
| Release | 5 | none (code) | `git`, `gh` with `GITHUB_TOKEN` | artifacts | n/a |
| Reviewer | 6 | MiniMax M3.1 Flash, thinking off, on NIM (Gemma-4 31B free on OpenRouter) | `bash` in a fresh checkout of the PR head; no credentials | issue text, `git diff main...HEAD`, repo | spec, design, test report, any transcript |

## Credentials

| Secret | Who can read it |
|---|---|
| `NVIDIA_NIM_API_KEY`, `OPENROUTER_API_KEY` | orchestrator / review.py process only. Agent commands run as a separate Unix user `agent` with an empty environment, so they cannot read the parent's `/proc/<pid>/environ`. |
| `GITHUB_TOKEN` | release step and review-posting step only, through `env:` on that step. `actions/checkout` runs with `persist-credentials: false`, so `.git/config` holds no token. |

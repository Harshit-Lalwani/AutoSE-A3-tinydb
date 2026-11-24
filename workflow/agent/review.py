"""Stage 6: independent reviewer (ADR-008). Sees only the issue, the diff and the repo at the PR head.

Variant `informed` (experiment E1 only) also shows the PR description and, if present, design.md.
"""
import argparse
import json
import os
import re
import subprocess
from pathlib import Path

import checks
from agent import MODELS, BUDGET, AgentResult, BudgetExceeded, run_agent, sandbox_run, set_budget, truncate

PROMPTS = Path(__file__).parent / "prompts"


def gh(*args):
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=True).stdout.strip()


def request_text(repo: str, pr: dict) -> tuple[str, int | None]:
    """The request the PR claims to resolve: the linked issue, else the <!-- issue --> block of the PR body."""
    m = re.search(r"(?i)\b(?:closes|fixes|resolves) #(\d+)", pr["body"] or "")
    if m:
        d = json.loads(gh("issue", "view", m.group(1), "--repo", repo, "--json", "title,body"))
        return f"Title: {d['title']}\n\n{d['body']}", int(m.group(1))
    m = re.search(r"<!-- issue -->(.*?)<!-- /issue -->", pr["body"] or "", flags=re.S)
    return f"Title: {pr['title']}\n\n{(m.group(1) if m else pr['body'] or '').strip()}", None


def decide(final: str, commands: list[str]) -> dict:
    data = checks.extract_json_block(final)
    if not isinstance(data, dict) or data.get("verdict") not in ("approve", "request_changes"):
        return {"verdict": "request_changes", "category": "code", "findings": [], "requirements": [],
                "summary": "Reviewer output had no valid verdict block; treated as not approved.", "invalid": True}
    if data["verdict"] == "approve" and not commands:
        data.update(verdict="request_changes", category="code",
                    summary="Approval without running any command is not accepted (no evidence).", no_evidence=True)
    if data["verdict"] == "request_changes" and data.get("category") not in ("code", "approach"):
        data["category"] = "code"
    if data["verdict"] == "approve":
        data["category"] = "none"
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pr", type=int, required=True)
    ap.add_argument("--round", type=int, default=1)
    ap.add_argument("--variant", choices=["isolated", "informed"], default="isolated")
    ap.add_argument("--ws", required=True)
    ap.add_argument("--art", required=True)
    ap.add_argument("--informed-dir", default="", help="E1 only: dir with the implementer's design.md")
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    ap.add_argument("--run-url", default="")
    ap.add_argument("--no-post", action="store_true")
    a = ap.parse_args()
    ws, art = Path(a.ws).resolve(), Path(a.art).resolve()
    (art / "logs").mkdir(parents=True, exist_ok=True)

    pr = json.loads(gh("pr", "view", str(a.pr), "--repo", a.repo, "--json", "title,body,headRefOid,url"))
    request, issue_no = request_text(a.repo, pr)
    _, diff = sandbox_run("git diff origin/main...HEAD", ws)
    user = (f"<untrusted_issue>\n{request}\n</untrusted_issue>\n\n"
            f"Diff of the pull request against main:\n```diff\n{truncate(diff, 30000)}\n```\n")
    if a.variant == "informed":
        user += f"\nThe implementer's description of the pull request:\n<pr_description>\n{pr['body']}\n</pr_description>\n"
        d = Path(a.informed_dir) / "design.md" if a.informed_dir else None
        if d and d.exists():
            user += f"\nThe implementer's design:\n<design>\n{d.read_text()}\n</design>\n"
    user += "\nReview the pull request now. The repository is checked out at the PR head."
    set_budget(MODELS["budget"]["review_tokens"])
    try:
        res = run_agent("reviewer", "reviewer", (PROMPTS / "reviewer.md").read_text(), user, ["bash"], ws, 30,
                        art / "logs" / f"review-{a.round}.jsonl")
        v = decide(res.final, res.commands)
    except BudgetExceeded as e:  # no verdict: the run ends and the human decides (no fix round)
        res = AgentResult(final=f"Review stopped: {e}.", steps=0, stopped_reason="budget")
        v = {"verdict": "incomplete", "category": "none", "findings": [], "requirements": [],
             "summary": f"Review stopped before a verdict: {e}."}
    sandbox_run("git reset -q --hard HEAD && git clean -qfd", ws)  # nothing the reviewer changed is kept
    prose = re.sub(r"```json.*?```", "", res.final, flags=re.S).strip()
    findings = "\n".join(f"- **{f.get('severity', '?')}** `{f.get('file', '')}:{f.get('line', '')}` "
                         f"{f.get('problem', '')}  \n  evidence: {f.get('evidence', '')}" for f in v.get("findings", []))
    reqs = "\n".join(f"- {'✅' if r.get('ok') else '❌'} {r.get('requirement', '')} (verified by: {r.get('verified_by', '')})"
                     for r in v.get("requirements", []))
    body = (f"## autose independent review, round {a.round}\n\n"
            f"**Verdict: {v['verdict'].upper().replace('_', ' ')}** · category: `{v.get('category')}` · "
            f"variant: `{a.variant}` · model: {', '.join(res.models)} · commands run: {len(res.commands)}\n\n"
            f"{v.get('summary', '')}\n\n### Requirements checked\n{reqs or '(none listed)'}\n\n"
            f"### Findings\n{findings or '(none)'}\n\n<details><summary>Reviewer's notes</summary>\n\n{prose}\n</details>\n\n"
            f"<details><summary>Commands the reviewer ran</summary>\n\n```\n" +
            "\n".join(c[:200] for c in res.commands) + "\n```\n</details>\n\n"
            f"<sub>Reviewed commit `{pr['headRefOid'][:7]}` · [workflow run]({a.run_url}) · "
            "the reviewer cannot push; a maintainer decides whether to merge.</sub>\n")
    (art / "review.md").write_text(body)
    (art / "review.json").write_text(json.dumps({**v, "pr": a.pr, "issue": issue_no, "round": a.round,
                                                 "variant": a.variant, "models": res.models,
                                                 "commands": res.commands, "steps": res.steps,
                                                 "prompt_tokens": res.prompt_tokens,
                                                 "completion_tokens": res.completion_tokens,
                                                 "sha": pr["headRefOid"], "budget_used": BUDGET["used"],
                                                 "budget_limit": BUDGET["limit"]}, indent=2))
    if not a.no_post:
        subprocess.run(["gh", "pr", "review", str(a.pr), "--repo", a.repo, "--comment", "--body-file",
                        str(art / "review.md")], check=True)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"verdict={v['verdict']}\ncategory={v.get('category', 'code')}\n")
    print(f"verdict={v['verdict']} category={v.get('category')}")


if __name__ == "__main__":
    main()

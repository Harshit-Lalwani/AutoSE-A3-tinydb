"""Collect results of every autose run into results/results.csv and results/runs.md.

Usage: python experiment/scripts/collect_results.py <run_id> [<run_id> ...]
Downloads each run's artifacts, reads state.json / review.json, and runs the hidden acceptance
tests (experiment/hidden_tests) against the final pushed commit of the run's branch.
"""
import csv
import os
import json
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

REPO = "Harshit-Lalwani/AutoSE-A3-tinydb"
ROOT = Path(__file__).resolve().parents[2]
HIDDEN = Path(os.environ.get("HIDDEN_DIR", ROOT / "experiment" / "hidden_tests"))
ISSUE_TO_HIDDEN = {1: "I1", 2: "I2", 3: "I3", 4: "I4", 5: "I5"}
PY = sys.executable
# Runs that left no state.json / review.json: what happened, from the job logs.
NOTES = {
    "45420723743": "released (PR #14, CI success); review round 1 hit the 30-min job timeout (reviewed later: 45447664260)",
    "45477962162": "review of PR #20 (isolated): cancelled by me; PR #20 already had two reviews with a verdict",
    "45419641938": "setup failed: agent user could not enter /home/runner (fixed in PR #11)",
    "45424250973": "review of PR #7 (isolated) hit the 30-min job timeout (calls ~3 min each under load)",
    "45424250882": "review of PR #8 (isolated) hit the 30-min job timeout",
    "45424293028": "review of PR #7 (informed) hit the 30-min job timeout",
    "45424299372": "review of PR #8 (informed): NIM failed, OpenRouter fallback rate-limited (429)",
    "45447680496": "review of PR #7 (informed) hit the 60-min job timeout (22 calls, ~2 min each)",
    "45464259655": "review of PR #7 (informed): NIM failed, OpenRouter fallback rate-limited (429)",
}


def sh(*cmd, cwd=None, check=True):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check).stdout


def hidden_tests(sha: str, issue: int) -> tuple[int, int]:
    """(tests passed, tests total); a test counts only if all its parametrisations pass."""
    key = ISSUE_TO_HIDDEN.get(issue)
    if not key or not sha:
        return 0, 0
    with tempfile.TemporaryDirectory() as d:
        sh("git", "clone", "-q", f"https://github.com/{REPO}.git", d)
        sh("git", "fetch", "-q", "origin", sha, cwd=d)
        sh("git", "checkout", "-q", sha, cwd=d)
        test = Path(d) / "tests" / f"test_{key}_acceptance.py"
        test.write_text((HIDDEN / f"test_{key}_acceptance.py").read_text())
        xml = Path(d) / "h.xml"
        subprocess.run([PY, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-o", "addopts=",
                        f"--junitxml={xml}", str(test)], cwd=d, capture_output=True)
        per = defaultdict(lambda: True)
        try:
            for tc in ET.parse(xml).getroot().iter("testcase"):
                name = re.sub(r"\[.*\]$", "", tc.get("name"))
                per[name] &= not any(c.tag in ("failure", "error") for c in tc)
        except (ET.ParseError, FileNotFoundError):
            return 0, -1
        return sum(per.values()), len(per)


def review_tokens(r: dict) -> int:
    """Reviews stopped by the budget report 0 agent tokens; their real use is budget_used."""
    return (r.get("prompt_tokens", 0) + r.get("completion_tokens", 0)) or r.get("budget_used", 0)


def collect(run_id: str, out_root: Path):
    d = out_root / run_id
    if not d.exists():
        d.mkdir(parents=True)
        subprocess.run(["gh", "run", "download", run_id, "--repo", REPO, "-D", str(d)], capture_output=True)
    run = json.loads(sh("gh", "run", "view", run_id, "--repo", REPO, "--json",
                        "url,event,createdAt,updatedAt,displayTitle,conclusion,headSha"))
    jobs = sorted(p for p in d.glob("autose-*") if (p / "state.json").exists())
    order = {"autose-stages": 0, "autose-fix_1": 1, "autose-fix_2": 2}
    jobs.sort(key=lambda p: order.get(p.name, 9))
    reviews = [json.loads((p / "review.json").read_text()) for p in sorted(d.glob("autose-review-*"))
               if (p / "review.json").exists()]
    row = {"run_id": run_id, "run_url": run["url"], "workflow_sha": run["headSha"][:7],
           "created": run["createdAt"], "run_conclusion": run["conclusion"]}
    if jobs:
        st = json.loads((jobs[-1] / "state.json").read_text())
        hist = st["history"]
        stages = defaultdict(list)
        for h in hist:
            stages[h["stage"]].append(h["ok"])
        sha = (st.get("ci") or {}).get("sha", "")
        hp, ht = hidden_tests(sha, st["issue"])
        rev_tokens = sum(review_tokens(r) for r in reviews)
        row.update(issue=st["issue"], variant=st["variant"], outcome=st.get("outcome", ""),
                   spec_ok=any(stages["spec"]), spec_attempts=len(stages["spec"]),
                   design_ok=any(stages["design"]), design_attempts=len(stages["design"]),
                   implement_attempts=len(stages["implement"]), build_ok=any(stages["implement"]),
                   tests_ok=any(stages["test"]), release_ok=any(stages["release"]),
                   ci=(st.get("ci") or {}).get("conclusion", ""), pr=st.get("pr", ""),
                   review_verdicts=" ".join(f"r{r['round']}:{r['verdict']}/{r.get('category')}" for r in reviews),
                   final_verdict=reviews[-1]["verdict"] if reviews else "",
                   review_rounds=len(reviews), hidden_passed=hp, hidden_total=ht,
                   builder_tokens=st["tokens"]["prompt"] + st["tokens"]["completion"],
                   reviewer_tokens=rev_tokens, final_sha=sha[:7])
    elif reviews:  # review-only run (seeded PRs, experiment E1)
        r = reviews[-1]
        row.update(issue="", variant=f"review-{r['variant']}", outcome="review-only", pr=f"#{r['pr']}",
                   review_verdicts=f"{r['verdict']}/{r.get('category')}", final_verdict=r["verdict"],
                   review_rounds=1, reviewer_tokens=review_tokens(r),
                   review_commands=len(r.get("commands", [])), final_sha=r.get("sha", "")[:7])
    if run_id in NOTES:
        row["outcome"] = NOTES[run_id]
    return row


def main():
    out_root = ROOT / "results" / "artifacts"
    rows = [collect(r, out_root) for r in sys.argv[1:]]
    path = ROOT / "results" / "results.csv"
    old = list(csv.DictReader(path.open())) if path.exists() else []
    by_id = {r["run_id"]: r for r in old}
    by_id.update({r["run_id"]: r for r in rows})
    fields = sorted({k for r in by_id.values() for k in r}, key=lambda k: (k not in ("run_id", "issue", "variant", "outcome"), k))
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(by_id.values())
    print(f"{len(by_id)} rows -> {path}")
    write_runs_md(sorted(by_id.values(), key=lambda r: r.get("created", "")))


def write_runs_md(rows):
    """One line per run: what was asked, what happened, links."""
    out = ["# Runs", "", "Every workflow run used in the report, oldest first. Columns as in `results.csv`.", "",
           "| run | code | issue / PR | variant | outcome | PR | CI | hidden tests | reviews | tokens (builders / reviewer) |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        pr = r.get("pr", "")
        pr_link = f"[#{pr.rsplit('/', 1)[-1].lstrip('#')}]({pr if pr.startswith('http') else f'https://github.com/{REPO}/pull/' + pr.lstrip('#')})" if pr else ""
        hidden = f"{r.get('hidden_passed')}/{r.get('hidden_total')}" if r.get("hidden_total") not in ("", "0", None) else ""
        out.append(f"| [{r['run_id']}]({r['run_url']}) | `{r.get('workflow_sha', '')}` | {r.get('issue') or pr_link} | "
                   f"{r.get('variant', '')} | {(r.get('outcome') or r.get('run_conclusion', '')).replace('|', '/')[:90]} | "
                   f"{pr_link} | {r.get('ci', '')} | {hidden} | {r.get('review_verdicts', '')} | "
                   f"{r.get('builder_tokens', '')} / {r.get('reviewer_tokens', '')} |")
    (ROOT / "results" / "runs.md").write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()

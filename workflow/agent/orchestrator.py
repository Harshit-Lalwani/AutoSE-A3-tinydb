"""Stages 1-5 as an explicit state machine (ADR-002). Code decides every transition (ADR-007).

pipeline: spec -> design -> implement <-> test (-> design once) -> release
resume:   (design | implement) -> implement <-> test -> release      (after a review asked for changes)
"""
import argparse
import json
import os
import subprocess
import time
from pathlib import Path

import checks
from agent import MODELS, BUDGET, BudgetExceeded, run_agent, sandbox_run, set_budget, truncate

HERE = Path(__file__).parent
PROMPTS = HERE / "prompts"
MAX_IMPLEMENT_ATTEMPTS = 3
REDESIGN_AFTER = 2
STEPS = {"design": 25, "coder": 40, "tester": 30}


class Stop(Exception):
    """A stage could not pass its check; the reason is already in its artifact."""


class Run:
    def __init__(self, a):
        self.a = a
        self.ws = Path(a.ws).resolve()
        self.art = Path(a.art).resolve()
        self.art.mkdir(parents=True, exist_ok=True)
        (self.art / "logs").mkdir(exist_ok=True)
        self.tmp = Path(a.tmp).resolve()
        self.tmp.mkdir(parents=True, exist_ok=True)
        self.state_path = self.art / "state.json"
        self.state = json.loads(self.state_path.read_text()) if self.state_path.exists() else {
            "issue": a.issue, "variant": a.variant, "branch": a.branch, "history": [],
            "tokens": {"prompt": 0, "completion": 0}, "review_round": 0}
        self.job = a.job
        # Hard token budget for the whole run (stages job + fix jobs share it via state.json).
        set_budget(MODELS["budget"]["run_tokens"], (self.state.get("budget") or {}).get("used", 0))
        self.current = "spec"
        self.test_file = f"tests/test_autose_issue_{a.issue}.py"

    # ---------- bookkeeping ----------
    def save(self):
        self.state_path.write_text(json.dumps(self.state, indent=2))

    def log_stage(self, stage, ok, summary, res=None, started=None, attempt=1):
        entry = {"job": self.job, "stage": stage, "attempt": attempt, "ok": ok, "summary": summary,
                 "seconds": round(time.time() - started, 1) if started else None}
        if res is not None:
            entry.update(steps=res.steps, prompt_tokens=res.prompt_tokens, completion_tokens=res.completion_tokens,
                         models=res.models, commands=len(res.commands), stopped=res.stopped_reason)
            self.state["tokens"]["prompt"] += res.prompt_tokens
            self.state["tokens"]["completion"] += res.completion_tokens
        self.state["history"].append(entry)
        self.save()
        print(f"[{stage}] attempt {attempt}: {'PASS' if ok else 'FAIL'} - {summary}", flush=True)

    def write(self, name, text):
        (self.art / name).write_text(text)

    def gh(self, *args, check=True):
        p = subprocess.run(["gh", *args], capture_output=True, text=True)
        if check and p.returncode != 0:
            raise RuntimeError(f"gh {' '.join(args[:3])} failed: {p.stderr}")
        return p.stdout.strip()

    def comment(self, body):
        if self.a.no_github:
            print("[comment]", body)
            return
        f = self.tmp / "comment.md"
        f.write_text(body + f"\n\n<sub>autose · [workflow run]({self.a.run_url})</sub>")
        self.gh("issue", "comment", str(self.a.issue), "--repo", self.a.repo, "--body-file", str(f), check=False)

    def agent(self, role, model_role, system, user, tools, steps, max_tokens=8000):
        return run_agent(role, model_role, system, user, tools, self.ws, steps,
                         self.art / "logs" / f"{self.job}-{role}.jsonl", max_tokens=max_tokens)

    def issue(self):
        if self.a.issue_file:
            d = json.loads(Path(self.a.issue_file).read_text())
        else:
            d = json.loads(self.gh("issue", "view", str(self.a.issue), "--repo", self.a.repo, "--json", "title,body"))
        return d["title"], d["body"] or ""

    def acs_text(self):
        spec = json.loads((self.art / "spec.json").read_text())
        lines = [f"Summary: {spec.get('summary', '')}", "", "Acceptance criteria:"]
        for ac in spec["acceptance_criteria"]:
            lines.append(f"- {ac['id']}: GIVEN {ac['given']} WHEN {ac['when']} THEN {ac['then']}")
        for asm in spec.get("assumptions") or []:
            lines.append(f"- Assumption {asm.get('id', '')}: {asm.get('assumption', '')} "
                         f"(default used: {asm.get('default_used', '')})")
        return "\n".join(lines), spec["acceptance_criteria"]

    # ---------- stage 1 ----------
    def stage_spec(self):
        self.current = "spec"
        title, body = self.issue()
        system = (PROMPTS / "srs_SKILL.md").read_text() + "\n\n" + (PROMPTS / "spec_addendum.md").read_text()
        readme = (self.ws / "README.rst").read_text()[:6000]
        user = (f"Project README (for vocabulary):\n<readme>\n{readme}\n</readme>\n\n"
                f"Issue #{self.a.issue}:\n<untrusted_issue>\nTitle: {title}\n\n{body}\n</untrusted_issue>\n\n"
                "Write the specification now.")
        feedback = ""
        for attempt in (1, 2):
            t0 = time.time()
            res = self.agent("spec", "builder", system, user + feedback, [], 1, max_tokens=20000)
            ok, problems, data = checks.check_spec(res.final)
            self.write("spec.md", res.final)
            if ok:
                (self.art / "spec.json").write_text(json.dumps(data, indent=2))
                self.log_stage("spec", True, f"{len(data['acceptance_criteria'])} testable ACs", res, t0, attempt)
                return
            self.log_stage("spec", False, "; ".join(problems), res, t0, attempt)
            feedback = ("\n\nYour previous answer failed the automatic check:\n- " + "\n- ".join(problems) +
                        "\nRewrite the whole specification and fix these problems.")
            if data and data.get("blocking_questions"):
                feedback += ("\nRe-check every blocking question. It is NOT blocking if a later stage could answer it "
                             "by reading the code (where, how, why the bug happens, what tests exist), or if a "
                             "conservative default exists that a maintainer would very likely accept; move those to "
                             "assumptions and write the acceptance criteria. Keep a question blocking only if the "
                             "maintainer's intent itself is unknown. Previous blocking questions:\n" +
                             json.dumps(data["blocking_questions"], indent=1))
        qs = (data or {}).get("blocking_questions") or []
        self.write("spec.md", res.final + "\n\n## Why this stage stopped\n\n" + "\n".join(f"- {p}" for p in problems))
        if qs:
            self.comment("**autose stopped at stage 1 (requirements).** The issue leaves open questions "
                         "that only a maintainer can answer:\n\n" +
                         "\n".join(f"- **{q.get('id', '')}** {q.get('question', '')}" for q in qs) +
                         "\n\nAnswer them in the issue (or edit it) and add the label again.")
        raise Stop("spec check failed: " + "; ".join(problems))

    # ---------- stage 2 ----------
    def stage_design(self, extra=""):
        self.current = "design"
        acs, _ = self.acs_text()
        system = (PROMPTS / "design.md").read_text()
        user = acs + extra + "\n\nRead ARCHITECTURE.md, explore the code, then give design.md."
        feedback = ""
        for attempt in (1, 2):
            t0 = time.time()
            res = self.agent("design", "builder", system, user + feedback, ["bash"], STEPS["design"])
            written = self.ws / "design.md"
            if "```json" not in res.final and written.is_file():
                res.final = written.read_text()  # it wrote design.md with bash instead of replying (ADR-013)
            discarded = checks.changed_files(self.ws)
            if discarded:  # read-only role: throw away anything it changed
                sandbox_run("git reset -q --hard HEAD && git clean -qfd", self.ws)
            ok, problems, data = checks.check_design(res.final, self.ws)
            self.write("design.md", res.final)
            if ok:
                (self.art / "design.json").write_text(json.dumps(data, indent=2))
                self.log_stage("design", True, "files: " + ", ".join(f["path"] for f in data["files"]), res, t0, attempt)
                return
            self.log_stage("design", False, "; ".join(problems), res, t0, attempt)
            feedback = ("\n\nYour previous design failed the automatic check:\n- " + "\n- ".join(problems) +
                        "\nThere is no design.md file: your final reply IS design.md. Reply with the complete "
                        "design.md text again (all sections and the final json block), with these fixed.")
        self.write("design.md", res.final + "\n\n## Why this stage stopped\n\n" + "\n".join(f"- {p}" for p in problems))
        raise Stop("design check failed: " + "; ".join(problems))

    # ---------- stages 3 + 4 ----------
    def saved_tests(self):
        p = self.ws / self.test_file
        return p.read_text() if p.exists() else None

    def restore_tests(self, content):
        if content is None:
            sandbox_run('rm -f "$1"', self.ws, args=[self.test_file])
        else:
            sandbox_run('cat > "$1"', self.ws, stdin=content, args=[self.test_file])

    def stage_implement(self, feedback):
        self.current = "implement"
        acs, _ = self.acs_text()
        design = (self.art / "design.md").read_text()
        system = (PROMPTS / "coder.md").read_text()
        single = self.a.variant == "single"
        if single:  # experiment E2: the coder also writes the tests
            system = system.replace(
                "- Do not create or edit `tests/test_autose_*.py`: a separate tester agent owns those files, and\n"
                "  any change you make to them is discarded. You may run them.",
                f"- You also write the tests: create `{self.test_file}` with at least one pytest test per acceptance\n"
                "  criterion, named `test_ac<k>_<short_name>` (AC-3 -> `test_ac3_...`), testing the behaviour\n"
                "  through the public API with exact expected values.")
        user = f"{acs}\n\n<design.md>\n{design}\n</design.md>\n{feedback}\n\nImplement the change now."
        keep = None if single else self.saved_tests()
        res = self.agent("coder", "builder", system, user, ["bash", "write_file"], STEPS["coder"])
        if not single:
            self.restore_tests(keep)
        allowed = {f["path"] for f in json.loads((self.art / "design.json").read_text())["files"]}
        reverted = checks.revert_out_of_scope(self.ws, allowed)
        ok, report = checks.check_build(self.ws)
        if reverted:
            report = f"Changes outside the design were reverted: {', '.join(reverted)}\n\n" + report
        _, diff = sandbox_run("git add -A && git diff --cached main", self.ws)
        self.write("diff.patch", diff)
        return ok, report, res

    def stage_test(self, extra="", run_tester=True):
        self.current = "test"
        acs, ac_list = self.acs_text()
        if self.a.variant != "single" and run_tester:
            system = (PROMPTS / "tester.md").read_text().replace("TEST_FILE", f"`{self.test_file}`")
            files = "\n".join(f"- {f}" for f in checks.changed_files(self.ws) if not f.startswith("tests/"))
            user = (f"{acs}\n\nTEST_FILE: {self.test_file}\nSource files changed by the coder:\n{files}\n{extra}\n\n"
                    "Write and run the tests now.")
            snapshot = {f: (self.ws / f).read_text() for f in checks.changed_files(self.ws)
                        if not f.startswith("tests/") and (self.ws / f).exists()}
            res = self.agent("tester", "builder", system, user, ["bash", "write_file"], STEPS["tester"])
            # the tester may only write tests: put the coder's source files back exactly
            for f in checks.changed_files(self.ws):
                if f.startswith("tests/"):
                    continue
                if f in snapshot:
                    sandbox_run('cat > "$1"', self.ws, stdin=snapshot[f], args=[f])
                else:
                    sandbox_run('git reset -q main -- "$1"; git checkout -q main -- "$1" 2>/dev/null || rm -f "$1"',
                                self.ws, args=[f])
        else:
            res = None
        ok, problems, d = checks.check_tests(self.ws, self.test_file, ac_list, self.base, self.tmp)
        return ok, problems, d, res

    def test_report(self, ok, problems, d, attempt):
        _, ac_list = self.acs_text()
        rows = []
        new = d.get("new_cases", {})
        main = d.get("on_main", {})
        for ac in ac_list:
            k = ac["id"].split("-")[1]
            for name, status in new.items():
                if f"::test_ac{k}_" in name:
                    short = name.split("::")[-1]
                    on_main = next((s for n, s in main.items() if n.endswith("::" + short)), "not run")
                    rows.append(f"| {ac['id']} | `{short}` | {status} | {on_main} |")
            if not any(f"::test_ac{k}_" in n for n in new):
                rows.append(f"| {ac['id']} | (none) | missing | |")
        txt = (f"# Test report (issue #{self.a.issue}, {self.job}, attempt {attempt})\n\n"
               f"**Result:** {'PASS' if ok else 'FAIL'}\n\n"
               "| AC | Test | With change | On `main` |\n|---|---|---|---|\n" + "\n".join(rows) +
               f"\n\nFull suite: {d.get('suite_total', 0)} tests, {len(d.get('suite_failed', []))} failing.\n")
        if d.get("suite_failed"):
            txt += "\nFailing:\n" + "\n".join(f"- `{n}`" for n in d["suite_failed"]) + "\n"
        if problems:
            txt += "\n## Problems\n\n" + "\n".join(f"- {p}" for p in problems) + "\n"
        txt += f"\n<details><summary>pytest output (full suite)</summary>\n\n```\n{d.get('suite_output', '')}\n```\n</details>\n"
        self.write("test_report.md", txt)

    def build_and_test(self, feedback="", redesign_allowed=True):
        tester_extra = ""
        if self.a.mode == "resume":
            tester_extra = ("\nA reviewer looked at the previous version. Keep your tests that are still right; add or "
                            "fix tests if these findings concern them:\n" + feedback)
        run_tester = True
        for attempt in range(1, MAX_IMPLEMENT_ATTEMPTS + 1):
            t0 = time.time()
            ok, report, res = self.stage_implement(feedback)
            self.log_stage("implement", ok, "build ok" if ok else "build failed", res, t0, attempt)
            if not ok:
                feedback = f"\n\nYour previous attempt did not build:\n{report}\nFix it."
                self.write("build_report.md", report)
            else:
                t0 = time.time()
                # The tests are a fixed oracle: the tester runs again only when its own tests had a problem.
                ok, problems, d, tres = self.stage_test(tester_extra, run_tester=run_tester)
                self.test_report(ok, problems, d, attempt)
                self.log_stage("test", ok, "; ".join(problems) or "all tests pass", tres, t0, attempt)
                if ok:
                    return
                test_side = [p for p in problems if p.startswith("TEST-SIDE")]
                run_tester = bool(test_side) or not (self.ws / self.test_file).exists()
                tester_extra = ("\nYour previous test file failed the automatic check:\n- " + "\n- ".join(test_side)
                                if test_side else "")
                feedback = ("\n\nThe tests for the acceptance criteria failed. Fix the source code (not the tests).\n"
                            "Problems:\n- " + "\n- ".join(problems) +
                            f"\n\nNew test file output:\n```\n{d.get('new_output', '')}\n```\n"
                            f"Full suite output:\n```\n{d.get('suite_output', '')[-3000:]}\n```")
            if attempt == REDESIGN_AFTER and redesign_allowed:
                sandbox_run("git reset -q --hard HEAD && git clean -qfd -e tests/", self.ws)
                prev = (self.art / "design.md").read_text()
                self.stage_design(extra=f"\n\nA previous plan failed twice in implementation/testing. Previous plan:\n"
                                        f"<previous_design>\n{prev}\n</previous_design>\nLatest failure:{truncate(feedback, 4000)}"
                                        "\nMake a better plan.")
        msg = f"stopped after {MAX_IMPLEMENT_ATTEMPTS} implementation attempts"
        tr = self.art / "test_report.md"
        if tr.exists():
            self.write("test_report.md", tr.read_text() + f"\n## Why this stage stopped\n\n{msg}. Last feedback:\n{feedback}\n")
        raise Stop(msg)

    # ---------- stage 5 ----------
    def stage_release(self):
        t0 = time.time()
        spec = json.loads((self.art / "spec.json").read_text())
        design = json.loads((self.art / "design.json").read_text())
        title, _ = self.issue()
        branch = self.state["branch"]
        if self.a.no_github:
            self.log_stage("release", True, "skipped (no_github)", None, t0)
            return
        if os.environ.get("AUTOSE_SANDBOX_USER"):
            subprocess.run(["sudo", "chown", "-R", f"{os.getuid()}:{os.getgid()}", str(self.ws)], check=True)
        git = lambda *x: subprocess.run(["git", "-C", str(self.ws), *x], capture_output=True, text=True)
        git("add", "-A")
        git("-c", "user.name=autose-bot", "-c", "user.email=autose-bot@users.noreply.github.com",
            "commit", "-qm", f"autose: resolve #{self.a.issue} ({self.job})\n\n{spec.get('summary', '')}")
        sha = git("rev-parse", "HEAD").stdout.strip()
        url = f"https://x-access-token:{os.environ['GH_TOKEN']}@github.com/{self.a.repo}.git"
        p = git("push", "--force", url, f"HEAD:refs/heads/{branch}")
        if p.returncode != 0:
            raise RuntimeError("push failed: " + p.stderr.replace(os.environ["GH_TOKEN"], "***"))
        acs = "\n".join(f"- **{a['id']}** Given {a['given']}, when {a['when']}, then {a['then']}"
                        for a in spec["acceptance_criteria"])
        files = "\n".join(f"- `{f['path']}`: {', '.join(f.get('symbols') or f.get('new_symbols') or [])}"
                          for f in design["files"])
        tr = (self.art / "test_report.md").read_text().split("<details>")[0]
        pr_md = (f"Closes #{self.a.issue}\n\n**Summary.** {spec.get('summary', '')}\n\n"
                 f"### Acceptance criteria (stage 1, `spec.md`)\n{acs}\n\n"
                 f"### Planned change (stage 2, `design.md`)\n{files}\n\n"
                 f"### Tests (stage 4)\n{tr.split(chr(10), 2)[2] if tr.count(chr(10)) > 2 else tr}\n"
                 f"### Run\n- Workflow run and all stage artifacts: {self.a.run_url}\n"
                 f"- Variant: `{self.a.variant}` · job: `{self.job}`\n\n"
                 "> Generated by the autose workflow. An independent reviewer agent will comment below. "
                 "A maintainer decides whether to merge; the workflow never merges.\n")
        self.write("pr.md", pr_md)
        existing = self.gh("pr", "list", "--repo", self.a.repo, "--head", branch, "--state", "open",
                           "--json", "number,url", "--jq", ".[0].url // \"\"")
        prfile = str(self.art / "pr.md")
        pr_title = f"autose: {title} (#{self.a.issue})" + (f" [{self.a.variant}]" if self.a.variant != "default" else "")
        if existing:
            self.gh("pr", "edit", existing, "--repo", self.a.repo, "--body-file", prfile)
            pr_url = existing
        else:
            pr_url = self.gh("pr", "create", "--repo", self.a.repo, "--base", "main", "--head", branch,
                             "--title", pr_title, "--body-file", prfile)
        self.state["pr"] = pr_url
        self.save()
        # CI: pushes made with GITHUB_TOKEN do not trigger workflows, so dispatch CI explicitly.
        self.gh("workflow", "run", "ci-workflow.yml", "--repo", self.a.repo, "--ref", branch)
        run_id = ""
        for _ in range(30):
            time.sleep(10)
            run_id = self.gh("run", "list", "--repo", self.a.repo, "--workflow", "ci-workflow.yml", "--branch", branch,
                             "--event", "workflow_dispatch", "--json", "databaseId,headSha", "--jq",
                             f'[.[] | select(.headSha=="{sha}")][0].databaseId // ""')
            if run_id:
                break
        if not run_id:
            raise Stop("CI run did not start")
        subprocess.run(["gh", "run", "watch", run_id, "--repo", self.a.repo, "--interval", "20"],
                       capture_output=True, timeout=1800)
        concl = self.gh("run", "view", run_id, "--repo", self.a.repo, "--json", "conclusion,url",
                        "--jq", '.conclusion + " " + .url')
        conclusion, ci_url = (concl.split(" ", 1) + [""])[:2]
        self.state["ci"] = {"run": ci_url, "conclusion": conclusion, "sha": sha}
        with (self.art / "pr.md").open("a") as f:
            f.write(f"\n**PR:** {pr_url}\n**CI on `{sha[:7]}`:** {conclusion} ({ci_url})\n")
        self.gh("pr", "edit", pr_url, "--repo", self.a.repo, "--body-file", prfile, check=False)
        ok = conclusion == "success"
        self.log_stage("release", ok, f"PR {pr_url}, CI {conclusion}", None, t0)
        if not ok:
            raise Stop(f"CI {conclusion}: {ci_url}")

    # ---------- driver ----------
    def prepare_base(self):
        self.base = self.tmp / "base"
        if not self.base.exists():
            sandbox_run('git worktree add -q --detach "$1" main', self.ws, args=[str(self.base)])

    def run(self):
        self.prepare_base()
        try:
            if self.a.mode == "pipeline":
                self.comment(f"**autose started** on this issue (variant `{self.a.variant}`). "
                             "Stages: requirements → design → implementation → testing → release → independent review.")
                self.stage_spec()
                self.stage_design()
                self.build_and_test()
            else:
                self.state["review_round"] = self.a.round
                fb = Path(self.a.feedback).read_text() if self.a.feedback else ""
                fb_text = f"\n\nAn independent reviewer requested changes:\n<review>\n{fb}\n</review>\n"
                if self.a.from_stage == "design":
                    prev = (self.art / "design.md").read_text()
                    self.stage_design(extra=f"\n\nPrevious plan:\n<previous_design>\n{prev}\n</previous_design>"
                                            f"{fb_text}\nRevise the plan to address the review.")
                self.build_and_test(feedback=fb_text, redesign_allowed=self.a.from_stage != "design")
            self.stage_release()
            self.state["outcome"] = "released"
            return 0
        except BudgetExceeded as e:
            art = {"spec": "spec.md", "design": "design.md", "implement": "diff.patch", "test": "test_report.md"}
            path = self.art / art.get(self.current, "summary.md")
            prev = path.read_text() if path.exists() else ""
            path.write_text(prev + f"\n\n## Why this stage stopped\n\nStage `{self.current}`: {e}.\n")
            self.log_stage(self.current, False, str(e))
            self.state["outcome"] = f"stopped: {e}"
            self.comment(f"**autose stopped** ({self.job}, stage {self.current}): {e}")
            return 1
        except Stop as e:
            self.state["outcome"] = f"stopped: {e}"
            self.comment(f"**autose stopped** ({self.job}): {e}\n\nEach stage's artifact explains why.")
            return 1
        finally:
            self.state["budget"] = {"limit": BUDGET["limit"], "used": BUDGET["used"]}
            self.save()
            self.write_summary()

    def write_summary(self):
        rows = [f"| {h['job']} | {h['stage']} | {h['attempt']} | {'pass' if h['ok'] else 'FAIL'} | "
                f"{h.get('prompt_tokens', 0) + h.get('completion_tokens', 0)} | {h.get('seconds')} | "
                f"{str(h['summary'])[:120]} |" for h in self.state["history"]]
        txt = ("| job | stage | attempt | check | tokens | s | summary |\n|---|---|---|---|---|---|---|\n" +
               "\n".join(rows) + f"\n\nOutcome: {self.state.get('outcome')}  \nTokens: {self.state['tokens']}  \n"
               f"Budget: {BUDGET['used']:,} of {BUDGET['limit']:,} tokens used\n")
        self.write("summary.md", txt)
        if os.environ.get("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
                f.write(f"## autose {self.job}\n\n{txt}\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["pipeline", "resume"], default="pipeline")
    ap.add_argument("--issue", type=int, required=True)
    ap.add_argument("--variant", default="default", choices=["default", "single"])
    ap.add_argument("--from-stage", dest="from_stage", choices=["design", "implement"], default="implement")
    ap.add_argument("--feedback", default="")
    ap.add_argument("--round", type=int, default=0)
    ap.add_argument("--job", default="stages")
    ap.add_argument("--ws", required=True)
    ap.add_argument("--art", required=True)
    ap.add_argument("--tmp", default="/tmp/autose")
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    ap.add_argument("--branch", default="")
    ap.add_argument("--run-url", dest="run_url", default="")
    ap.add_argument("--issue-file", dest="issue_file", default="", help="local testing: JSON with title/body")
    ap.add_argument("--no-github", dest="no_github", action="store_true")
    a = ap.parse_args()
    a.branch = a.branch or f"autose/issue-{a.issue}" + ("" if a.variant == "default" else f"-{a.variant}")
    raise SystemExit(Run(a).run())


if __name__ == "__main__":
    main()

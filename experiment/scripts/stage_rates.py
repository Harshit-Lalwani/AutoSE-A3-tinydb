"""Per-stage pass rates over pipeline runs, from the downloaded state.json files.

Usage: python experiment/scripts/stage_rates.py [min_workflow_sha_run_id]
Counts each run once per stage: entered, passed (on any attempt), passed on the first attempt, and the
stop reason when a run ended in that stage. Fix rounds (fix_1/fix_2) are counted separately.
"""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAGES = ["spec", "design", "implement", "test", "release"]


def main():
    rows = {r["run_id"]: r for r in csv.DictReader((ROOT / "results" / "results.csv").open())}
    since = sys.argv[1] if len(sys.argv) > 1 else "0"
    table = defaultdict(lambda: defaultdict(Counter))  # variant -> stage -> counter
    for run_dir in sorted((ROOT / "results" / "artifacts").iterdir()):
        if run_dir.name < since:
            continue
        st_file = run_dir / "autose-stages" / "state.json"
        if not st_file.exists():
            continue
        st = json.loads(st_file.read_text())
        hist = [h for h in st["history"] if h.get("job", "stages") == "stages"]
        v = st["variant"]
        last = hist[-1]["stage"] if hist else None
        for s in STAGES:
            tries = [h["ok"] for h in hist if h["stage"] == s]
            if not tries:
                continue
            c = table[v][s]
            c["entered"] += 1
            c["passed"] += any(tries)
            c["first"] += tries[0]
            if s == last and not st.get("outcome", "").startswith("released"):
                c["stopped_here"] += 1
        table[v]["runs"]["n"] += 1
        table[v]["runs"]["pr"] += bool(rows.get(run_dir.name, {}).get("pr"))
    for v, stages in table.items():
        print(f"\n{v}: {stages['runs']['n']} runs, {stages['runs']['pr']} opened a PR")
        print("| stage | entered | passed | passed 1st attempt | run stopped here |")
        print("|---|---|---|---|---|")
        for s in STAGES:
            c = stages[s]
            if c["entered"]:
                print(f"| {s} | {c['entered']} | {c['passed']} | {c['first']} | {c['stopped_here']} |")


if __name__ == "__main__":
    main()

"""Deterministic stage checks (ADR-007). Every hand-off is decided here, never by an LLM."""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from agent import sandbox_run, truncate

VAGUE = r"\b(tbd|fast|quickly|efficient(ly)?|properly|correctly|user-friendly|robust(ly)?|" \
        r"appropriate(ly)?|reasonabl[ey]|intuitive(ly)?|seamless(ly)?|adequate(ly)?|as expected|" \
        r"etc\.?|and so on|gracefully)\b"
PYTEST = "python -m pytest -q -p no:cacheprovider -o addopts="


def extract_json_block(text: str):
    """Return the last ```json fenced block parsed as JSON, or None."""
    blocks = re.findall(r"```json\s*\n(.*?)```", text or "", flags=re.S)
    for raw in reversed(blocks):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            continue
    return None


def check_spec(text: str):
    data = extract_json_block(text)
    if not isinstance(data, dict):
        return False, ["no parseable ```json block at the end of the spec"], None
    problems = []
    blocking = data.get("blocking_questions") or []
    acs = data.get("acceptance_criteria") or []
    if blocking:
        problems.append(f"{len(blocking)} blocking question(s) need a maintainer's answer")
    if not acs and not blocking:
        problems.append("no acceptance criteria")
    for i, ac in enumerate(acs, 1):  # renumber AC-1..n so test names can follow them
        if ac.get("id") != f"AC-{i}":
            ac["spec_id"] = ac.get("id")
        ac["id"] = aid = f"AC-{i}"
        for part in ("given", "when", "then"):
            val = str(ac.get(part, "")).strip()
            if not val:
                problems.append(f"{aid}: missing '{part}'")
            m = re.search(VAGUE, val, flags=re.I)
            if m:
                problems.append(f"{aid}: '{part}' uses untestable wording '{m.group(0)}'")
    return not problems, problems, data


def symbol_defined(source: str, symbol: str) -> bool:
    name = symbol.split(".")[-1].strip("()")
    return re.search(rf"^\s*(async\s+)?(def|class)\s+{re.escape(name)}\b", source, flags=re.M) is not None \
        or re.search(rf"^\s*{re.escape(name)}\s*[:=]", source, flags=re.M) is not None


def check_design(text: str, ws: Path):
    data = extract_json_block(text)
    if not isinstance(data, dict) or not data.get("files"):
        return False, ["no ```json block with a non-empty 'files' list"], None
    problems = []
    for f in data["files"]:
        path = str(f.get("path", ""))
        if not path or path.startswith(("tests/", ".github/", "workflow/")):
            problems.append(f"{path!r}: not a source file the plan may change")
            continue
        p = ws / path
        if f.get("new"):
            if p.exists():
                problems.append(f"{path}: marked new but already exists")
            continue
        if not p.is_file():
            problems.append(f"{path}: file does not exist")
            continue
        src = p.read_text(errors="replace")
        symbols = f.get("symbols") or []
        if not symbols and not f.get("new_symbols"):
            problems.append(f"{path}: no functions or classes named")
        # ADR-013: a symbol not defined in the file is a function the plan adds; record it as new
        # instead of rejecting the plan (the agent kept listing new helpers under "symbols").
        f["symbols"] = [s for s in symbols if symbol_defined(src, s)]
        f["new_symbols"] = list(f.get("new_symbols") or []) + [s for s in symbols if not symbol_defined(src, s)]
    return not problems, problems, data


def changed_files(ws: Path) -> list[str]:
    sandbox_run("git add -A", ws)
    _, out = sandbox_run("git diff --cached --name-only main", ws)
    return [l for l in out.splitlines() if l.strip()]


def revert_out_of_scope(ws: Path, allowed: set[str]) -> list[str]:
    """Undo changes outside the planned files and tests/ (also keeps .github/ untouchable)."""
    bad = [f for f in changed_files(ws) if f not in allowed and not f.startswith("tests/")]
    for f in bad:
        sandbox_run('git reset -q main -- "$1" 2>/dev/null; git checkout -q main -- "$1" 2>/dev/null '
                    '|| rm -f "$1"', ws, args=[f])
    return bad


def check_build(ws: Path):
    report, ok = [], True
    files = changed_files(ws)
    if not [f for f in files if not f.startswith("tests/")]:
        return False, "no source file changed"
    for name, cmd in [("compile", "python -c \"import ast,pathlib,sys; "
                                  "[ast.parse(p.read_text(), str(p)) for p in pathlib.Path('tinydb').rglob('*.py')]\""),
                      ("import", "python -c 'import tinydb; print(tinydb.__version__)'"),
                      ("mypy", "python -m mypy tinydb")]:
        code, out = sandbox_run(cmd, ws, timeout=300)
        report.append(f"### {name}: {'ok' if code == 0 else 'FAILED'}\n```\n{truncate(out, 3000)}\n```")
        ok = ok and code == 0
    return ok, "\n".join(report)


def junit_cases(xml_path: Path) -> dict[str, str]:
    """test name -> passed / failed / error / skipped."""
    res = {}
    try:
        root = ET.parse(xml_path).getroot()
    except (ET.ParseError, FileNotFoundError):
        return res
    for tc in root.iter("testcase"):
        status = "passed"
        for child in tc:
            if child.tag in ("failure", "error", "skipped"):
                status = {"failure": "failed"}.get(child.tag, child.tag)
        res[f'{tc.get("classname")}::{tc.get("name")}'] = status
    return res


def check_tests(ws: Path, test_file: str, acs: list[dict], base: Path, tmp: Path):
    """One test per AC, full suite green, and at least one new test fails on main."""
    problems, details = [], {}
    tf = ws / test_file
    if not tf.is_file():
        return False, [f"{test_file} was not written"], details
    names = re.findall(r"^\s*def (test_\w+)\s*\(", tf.read_text(errors="replace"), flags=re.M)
    details["tests"] = names
    for ac in acs:
        k = str(ac["id"]).split("-")[1]
        if not any(re.match(rf"test_ac{k}_", n) for n in names):
            problems.append(f"TEST-SIDE {ac['id']}: no test named test_ac{k}_*")
    code_my, out_my = sandbox_run(f"python -m mypy tinydb {test_file}", ws, timeout=300)
    if code_my != 0:
        problems.append("TEST-SIDE mypy errors (CI type-checks tests too):\n" + truncate(out_my, 2000))
    xml_new = tmp / "new.xml"
    code_new, out_new = sandbox_run(f"{PYTEST} --junitxml={xml_new} {test_file}", ws, timeout=300)
    details["new_cases"] = junit_cases(xml_new)
    details["new_output"] = truncate(out_new, 6000)
    xml_all = tmp / "all.xml"
    code_all, out_all = sandbox_run(f"{PYTEST} --junitxml={xml_all}", ws, timeout=600)
    cases = junit_cases(xml_all)
    details["suite_total"] = len(cases)
    details["suite_failed"] = sorted(n for n, s in cases.items() if s in ("failed", "error"))
    details["suite_output"] = truncate(out_all, 6000)
    if code_all != 0:
        problems.append(f"full suite failed: {len(details['suite_failed'])} failing test(s)")
    # Vacuity check: run the new test file against main (tests must notice the missing behaviour).
    sandbox_run('mkdir -p "$(dirname "$2")" && cp "$1" "$2"', ws, args=[str(tf), str(base / test_file)])
    xml_base = tmp / "base.xml"
    code_base, out_base = sandbox_run(f"{PYTEST} --junitxml={xml_base} {test_file}", base, timeout=300)
    base_cases = junit_cases(xml_base)
    details["on_main"] = base_cases
    details["on_main_exit"] = code_base
    sandbox_run('rm -f "$1"', base, args=[str(base / test_file)])
    if code_base == 0:
        problems.append("TEST-SIDE all new tests also pass on main: they do not test the change")
    return not problems, problems, details

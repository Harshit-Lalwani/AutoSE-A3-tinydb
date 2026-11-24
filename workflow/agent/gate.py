"""Gate job (ADR-010): who may start a run, and in which mode. Reads the event file, never shell-interpolated text."""
import json
import os
import subprocess

ALLOWED = {"admin", "maintain", "write"}


def main():
    ev = json.load(open(os.environ["GITHUB_EVENT_PATH"]))
    name = os.environ["GITHUB_EVENT_NAME"]
    sender = ev.get("sender") or {}
    issue = ev.get("issue") or {}
    out = {"ok": "false", "mode": "", "number": str(issue.get("number", "")), "variant": "default",
           "review_variant": "isolated"}
    if name == "issues":
        label = (ev.get("label") or {}).get("name", "")
        out["variant"] = {"autose": "default", "autose-single": "single"}.get(label, "")
        out["mode"] = "pipeline" if out["variant"] else ""
    elif name == "issue_comment":
        words = (ev.get("comment") or {}).get("body", "").strip().split()
        if words and words[0] == "/autose":
            if issue.get("pull_request"):
                out["mode"] = "review"
                out["review_variant"] = "informed" if "informed" in words[1:3] else "isolated"
            elif issue.get("state") == "open":
                out["mode"] = "pipeline"
                out["variant"] = "single" if "single" in words[1:2] else "default"
    perm = "none"
    if sender.get("type") != "Bot" and out["mode"]:
        p = subprocess.run(["gh", "api", f"repos/{os.environ['GITHUB_REPOSITORY']}/collaborators/{sender['login']}/permission",
                            "--jq", ".role_name"], capture_output=True, text=True)
        perm = p.stdout.strip() if p.returncode == 0 else "none"
    out["ok"] = "true" if out["mode"] and perm in ALLOWED else "false"
    print(f"event={name} sender={sender.get('login')} permission={perm} -> {out}")
    with open(os.environ["GITHUB_OUTPUT"], "a") as f:
        for k, v in out.items():
            f.write(f"{k}={v}\n")


if __name__ == "__main__":
    main()

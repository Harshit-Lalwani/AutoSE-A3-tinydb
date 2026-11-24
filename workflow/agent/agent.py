"""Minimal tool-calling agent loop (OpenAI-compatible APIs) with a credential-free sandbox.

Every command an agent runs goes through `sandbox_run`: as the Unix user in AUTOSE_SANDBOX_USER
(set in CI) with an empty environment, so it cannot see API keys or the GitHub token.
"""
import json
import os
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

from openai import OpenAI

HERE = Path(__file__).parent
MODELS = json.loads((HERE / "models.json").read_text())
SANDBOX_USER = os.environ.get("AUTOSE_SANDBOX_USER", "")
# PATH the agent sees: the shared tool venv first. No secrets are ever added here.
AGENT_PATH = os.environ.get("AUTOSE_AGENT_PATH", "/usr/local/bin:/usr/bin:/bin")
CMD_TIMEOUT = 120
MAX_TOOL_OUTPUT = 8000

TOOLS = {
    "bash": {"type": "function", "function": {
        "name": "bash",
        "description": "Run a bash command in the repository root and return stdout+stderr "
                       f"(timeout {CMD_TIMEOUT}s, output truncated). Use `python -m pytest` to run tests.",
        "parameters": {"type": "object", "properties": {"cmd": {"type": "string"}}, "required": ["cmd"]}}},
    "write_file": {"type": "function", "function": {
        "name": "write_file",
        "description": "Create or overwrite a file (path relative to the repository root) with the full content.",
        "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                       "required": ["path", "content"]}}},
}


def truncate(text: str, limit: int = MAX_TOOL_OUTPUT) -> str:
    if len(text) <= limit:
        return text
    half = limit // 2
    return text[:half] + f"\n... [{len(text) - limit} chars truncated] ...\n" + text[-half:]


def sandbox_run(cmd: str, cwd: Path, timeout: int = CMD_TIMEOUT, stdin: str | None = None,
                args: list[str] | None = None) -> tuple[int, str]:
    """Run `bash -c cmd` as the sandbox user with a clean environment."""
    env = ["env", "-i", f"PATH={AGENT_PATH}", "HOME=/tmp/agent-home", "LANG=C.UTF-8",
           "PYTHONDONTWRITEBYTECODE=1", "MYPY_CACHE_DIR=/tmp/agent-home/.mypy_cache"]
    prefix = ["sudo", "-n", "-u", SANDBOX_USER] if SANDBOX_USER else []
    full = prefix + env + ["bash", "-c", cmd, "_"] + (args or [])
    try:
        p = subprocess.run(full, cwd=cwd, input=stdin, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout + p.stderr)
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
        return 124, out + f"\n[command timed out after {timeout}s]"


class ModelClient:
    """Tries each (provider, model) of a role in order: 3 attempts each with backoff, then the next."""

    def __init__(self, role: str):
        self.candidates = MODELS["roles"][role]
        self.idx = 0
        self.used: list[str] = []

    def _client(self, cand):
        prov = MODELS["providers"][cand["provider"]]
        key = os.environ.get(prov["key_env"], "")
        return OpenAI(base_url=prov["base_url"], api_key=key, timeout=600, max_retries=0)

    def chat(self, messages, tools=None, max_tokens=8000):
        last_err = None
        while self.idx < len(self.candidates):
            cand = self.candidates[self.idx]
            if not os.environ.get(MODELS["providers"][cand["provider"]]["key_env"]):
                self.idx += 1
                continue
            for attempt in range(3):
                try:
                    kw = dict(model=cand["model"], messages=messages, max_tokens=max_tokens, temperature=0.2,
                              **cand.get("extra", {}))
                    if tools:
                        kw["tools"] = tools
                    r = self._client(cand).chat.completions.create(**kw)
                    if not r.choices:
                        raise RuntimeError(f"empty response: {r}")
                    tag = f'{cand["provider"]}:{cand["model"]}'
                    if not self.used or self.used[-1] != tag:
                        self.used.append(tag)
                    return r
                except Exception as e:  # rate limits, 5xx, timeouts, malformed responses
                    last_err = e
                    time.sleep([5, 20, 45][attempt])
            self.idx += 1  # fall back to the next candidate
        raise RuntimeError(f"all models failed for role; last error: {last_err}")


@dataclass
class AgentResult:
    final: str
    steps: int
    prompt_tokens: int = 0
    completion_tokens: int = 0
    commands: list[str] = field(default_factory=list)
    models: list[str] = field(default_factory=list)
    stopped_reason: str = "finished"


def run_agent(role: str, model_role: str, system: str, user: str, tools: list[str], workdir: Path,
              max_steps: int, log_path: Path, max_total_tokens: int = 1_500_000,
              max_tokens: int = 8000) -> AgentResult:
    client = ModelClient(model_role)
    tool_specs = [TOOLS[t] for t in tools] or None
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    res = AgentResult(final="", steps=0)
    log = log_path.open("a")

    def record(event: dict):
        log.write(json.dumps({"t": round(time.time(), 1), "role": role, **event}) + "\n")
        log.flush()

    record({"event": "start", "system": system, "user": user, "tools": tools})
    while True:
        over_budget = res.steps >= max_steps or (res.prompt_tokens + res.completion_tokens) > max_total_tokens
        if over_budget and tool_specs:
            res.stopped_reason = "budget"
            messages.append({"role": "user", "content": "Your step budget is used up. Do not call tools. "
                                                        "Reply now with your final answer in the required format."})
            r = client.chat(messages, tools=None, max_tokens=max_tokens)
        else:
            r = client.chat(messages, tools=tool_specs, max_tokens=max_tokens)
        res.steps += 1
        if r.usage:
            res.prompt_tokens += r.usage.prompt_tokens or 0
            res.completion_tokens += r.usage.completion_tokens or 0
        msg = r.choices[0].message
        calls = msg.tool_calls or []
        record({"event": "assistant", "content": msg.content, "tool_calls": [
            {"name": c.function.name, "arguments": c.function.arguments} for c in calls],
            "usage": r.usage.model_dump() if r.usage else None})
        if not calls or over_budget:
            res.final = msg.content or ""
            break
        messages.append({"role": "assistant", "content": msg.content or "", "tool_calls": [
            {"id": c.id, "type": "function", "function": {"name": c.function.name, "arguments": c.function.arguments}}
            for c in calls]})
        for c in calls:
            out = execute_tool(c.function.name, c.function.arguments, workdir, res)
            record({"event": "tool", "name": c.function.name, "output": out})
            messages.append({"role": "tool", "tool_call_id": c.id, "content": out})
    res.models = client.used
    record({"event": "end", "steps": res.steps, "prompt_tokens": res.prompt_tokens,
            "completion_tokens": res.completion_tokens, "models": res.models, "reason": res.stopped_reason})
    log.close()
    return res


def execute_tool(name: str, raw_args: str, workdir: Path, res: AgentResult) -> str:
    try:
        args = json.loads(raw_args or "{}")
    except json.JSONDecodeError:
        return "error: tool arguments were not valid JSON"
    if name == "bash":
        cmd = args.get("cmd", "")
        res.commands.append(cmd)
        code, out = sandbox_run(cmd, workdir)
        return truncate(f"[exit {code}]\n{out}")
    if name == "write_file":
        path = args.get("path", "")
        target = (workdir / path).resolve()
        if not str(target).startswith(str(workdir.resolve()) + os.sep):
            return "error: path must be inside the repository"
        code, out = sandbox_run('mkdir -p "$(dirname "$1")" && cat > "$1"', workdir,
                                stdin=args.get("content", ""), args=[str(target)])
        return f"wrote {path}" if code == 0 else f"error writing {path}: {out}"
    return f"error: unknown tool {name}"

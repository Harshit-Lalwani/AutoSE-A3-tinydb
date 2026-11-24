"""Run: python workflow/agent/test_budget.py  (no network: the client is stubbed)."""
from types import SimpleNamespace

import agent


def fake_create(**kw):
    return SimpleNamespace(choices=[SimpleNamespace(message=None)], usage=SimpleNamespace(total_tokens=1000))


class Stub:
    chat = SimpleNamespace(completions=SimpleNamespace(create=fake_create))


agent.ModelClient._client = lambda self, cand: Stub()
import os
os.environ.setdefault("NVIDIA_NIM_API_KEY", "x")
c = agent.ModelClient("builder")
agent.set_budget(10_000)
c.chat([{"role": "user", "content": "hi"}], max_tokens=2000)
assert agent.BUDGET["used"] == 1000
try:
    c.chat([{"role": "user", "content": "hi"}], max_tokens=9500)  # worst case crosses 10k
    raise AssertionError("budget not enforced")
except agent.BudgetExceeded:
    pass
assert agent.BUDGET["used"] == 1000  # refused call was never sent
print("budget ok")


def test_design_check_records_unknown_symbols_as_new(tmp_path):
    import checks
    (tmp_path / "tinydb").mkdir()
    (tmp_path / "tinydb" / "operations.py").write_text("def add(field, n):\n    pass\n")
    text = '```json\n{"files": [{"path": "tinydb/operations.py", "symbols": ["add", "append"]}]}\n```'
    ok, problems, data = checks.check_design(text, tmp_path)
    assert ok, problems
    assert data["files"][0]["symbols"] == ["add"]
    assert data["files"][0]["new_symbols"] == ["append"]
    ok, problems, _ = checks.check_design('```json\n{"files": [{"path": "tinydb/nope.py", "symbols": ["x"]}]}\n```',
                                          tmp_path)
    assert not ok

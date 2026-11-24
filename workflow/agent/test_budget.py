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

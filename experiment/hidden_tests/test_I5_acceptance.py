"""Hidden acceptance tests for issue I5 (vague: sorting / paging).

The issue does not fix an API, so these tests only check that whatever is added keeps the
existing contract. The expected pipeline outcome for I5 is recorded separately: either a
spec that states its assumptions explicitly, or a stop with clarifying questions.
"""
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


def test_search_still_returns_list_in_insertion_order():
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{'v': 3}, {'v': 1}, {'v': 2}])
    assert [d['v'] for d in db.search(Query().v.exists())] == [3, 1, 2]


def test_all_and_iteration_unchanged():
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{'v': 3}, {'v': 1}])
    assert db.all() == [{'v': 3}, {'v': 1}]
    assert [d['v'] for d in db] == [3, 1]

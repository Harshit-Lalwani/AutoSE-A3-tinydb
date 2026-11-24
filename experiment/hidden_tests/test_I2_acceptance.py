"""Hidden acceptance tests for issue I2 (string doc IDs ignored by update/remove)."""
from tinydb import TinyDB
from tinydb.storages import MemoryStorage


def make():
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{'a': 1}, {'a': 2}, {'a': 3}])
    return db


def test_update_accepts_string_ids():
    db = make()
    assert db.update({'a': 10}, doc_ids=['1']) == [1]
    assert db.get(doc_id=1) == {'a': 10}
    assert db.get(doc_id=2) == {'a': 2}


def test_remove_accepts_string_ids():
    db = make()
    assert sorted(db.remove(doc_ids=['2', '3'])) == [2, 3]
    assert [d.doc_id for d in db] == [1]


def test_mixed_int_and_string_ids_return_ints():
    db = make()
    updated = db.update({'x': True}, doc_ids=[1, '3'])
    assert sorted(updated) == [1, 3]
    assert all(isinstance(i, int) for i in updated)
    assert db.get(doc_id=2) == {'a': 2}


def test_unknown_string_ids_are_skipped():
    db = make()
    assert db.update({'a': 0}, doc_ids=['99']) == []
    assert db.remove(doc_ids=['42']) == []
    assert len(db) == 3

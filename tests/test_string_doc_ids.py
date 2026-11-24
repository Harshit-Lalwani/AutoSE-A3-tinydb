from tinydb import TinyDB
from tinydb.storages import MemoryStorage


def test_update_and_remove_accept_string_ids():
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{'a': 1}, {'a': 2}, {'a': 3}])
    assert db.update({'a': 10}, doc_ids=['1']) == [1]
    assert db.remove(doc_ids=['3']) == [3]
    assert db.all() == [{'a': 10}, {'a': 2}]


def test_unknown_string_ids_are_skipped():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'a': 1})
    assert db.update({'a': 0}, doc_ids=['9']) == []

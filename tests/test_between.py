from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


def test_between_matches_values_in_range():
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{'age': 10}, {'age': 30}, {'age': 90}])
    assert db.search(Query().age.between(18, 65)) == [{'age': 30}]


def test_between_ignores_missing_field():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'name': 'x'})
    assert db.search(Query().age.between(0, 100)) == []

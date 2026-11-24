import pytest

from tinydb import TinyDB, Query
from tinydb.operations import delete
from tinydb.storages import MemoryStorage


def test_search_is_fresh_after_failed_update():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'name': 'a', 'tmp': 1})
    db.insert({'name': 'b'})
    db.search(Query().tmp.exists())
    with pytest.raises(KeyError):
        db.update(delete('tmp'))
    db_fresh = db.search(Query().tmp.exists())
    db.clear_cache()
    assert db.search(Query().tmp.exists()) == db_fresh

import pytest

from tinydb import TinyDB, Query
from tinydb.operations import append
from tinydb.storages import MemoryStorage


def test_append_existing_and_missing():
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{'p': 'x', 'tags': ['a']}, {'p': 'x'}, {'p': 'y'}])
    db.update(append('tags', 'u'), Query().p == 'x')
    assert db.all() == [{'p': 'x', 'tags': ['a', 'u']}, {'p': 'x', 'tags': ['u']}, {'p': 'y'}]


def test_append_non_list_raises():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'tags': 'no'})
    with pytest.raises(TypeError):
        db.update(append('tags', 'u'))

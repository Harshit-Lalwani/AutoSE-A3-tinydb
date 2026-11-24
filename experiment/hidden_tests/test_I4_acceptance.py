"""Hidden acceptance tests for issue I4 (append update operation)."""
import pytest

from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


def test_append_to_existing_list():
    from tinydb.operations import append
    db = TinyDB(storage=MemoryStorage)
    db.insert({'project': 'x', 'tags': ['a']})
    db.update(append('tags', 'urgent'), Query().project == 'x')
    assert db.all() == [{'project': 'x', 'tags': ['a', 'urgent']}]


def test_append_creates_missing_field():
    from tinydb.operations import append
    db = TinyDB(storage=MemoryStorage)
    db.insert({'project': 'x'})
    db.update(append('tags', 'urgent'))
    assert db.all() == [{'project': 'x', 'tags': ['urgent']}]


def test_append_only_touches_matching_documents():
    from tinydb.operations import append
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{'p': 'x', 'tags': []}, {'p': 'x', 'tags': ['b']}, {'p': 'y', 'tags': []}])
    db.update(append('tags', 'u'), Query().p == 'x')
    assert [d['tags'] for d in db.all()] == [['u'], ['b', 'u'], []]


def test_append_to_non_list_raises_type_error():
    from tinydb.operations import append
    db = TinyDB(storage=MemoryStorage)
    db.insert({'tags': 'not-a-list'})
    with pytest.raises(TypeError):
        db.update(append('tags', 'u'))

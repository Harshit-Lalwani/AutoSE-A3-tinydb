"""Hidden acceptance tests for issue I1 (failed update leaves the DB half-modified)."""
import pytest

from tinydb import TinyDB, Query
from tinydb.operations import delete
from tinydb.storages import MemoryStorage


@pytest.fixture(params=["memory", "json"])
def db(request, tmp_path):
    if request.param == "memory":
        d = TinyDB(storage=MemoryStorage)
    else:
        d = TinyDB(str(tmp_path / "db.json"))
    yield d
    d.close()


def test_failed_update_leaves_documents_unchanged(db):
    db.insert({'name': 'a', 'tmp': 1})
    db.insert({'name': 'b'})
    with pytest.raises(KeyError):
        db.update(delete('tmp'))
    assert db.all() == [{'name': 'a', 'tmp': 1}, {'name': 'b'}]


def test_failed_update_by_doc_ids_with_callable_is_atomic(db):
    db.insert_multiple([{'n': 1}, {'n': 2}, {'n': 3}])

    def transform(doc):
        if doc['n'] == 2:
            raise ValueError('boom')
        doc['n'] *= 10

    with pytest.raises(ValueError):
        db.update(transform, doc_ids=[1, 2, 3])
    assert [d['n'] for d in db.all()] == [1, 2, 3]


def test_search_after_failed_update_matches_stored_data(db):
    db.insert({'name': 'a', 'tmp': 1})
    db.insert({'name': 'b'})
    before = db.search(Query().tmp.exists())
    with pytest.raises(KeyError):
        db.update(delete('tmp'))
    after = db.search(Query().tmp.exists())
    db.clear_cache()
    fresh = db.search(Query().tmp.exists())
    assert after == fresh == before == [{'name': 'a', 'tmp': 1}]


def test_failed_insert_multiple_inserts_nothing(db):
    db.insert({'keep': True})
    with pytest.raises(ValueError):
        db.insert_multiple([{'a': 1}, 'not a mapping'])  # type: ignore[list-item]
    assert db.all() == [{'keep': True}]

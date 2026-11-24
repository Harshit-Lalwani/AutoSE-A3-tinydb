"""Hidden acceptance tests for issue I3 (Query().field.between)."""
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


def make():
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{'age': a, 'name': f'p{a}'} for a in (17, 18, 40, 65, 66)])
    db.insert({'name': 'no-age'})
    return db


def test_between_is_inclusive():
    db = make()
    assert sorted(d['age'] for d in db.search(Query().age.between(18, 65))) == [18, 40, 65]


def test_between_missing_field_does_not_match():
    db = make()
    assert all('age' in d for d in db.search(Query().age.between(0, 100)))
    assert len(db.search(Query().age.between(0, 100))) == 5


def test_between_cache_distinguishes_bounds_and_fields():
    db = make()
    q = Query()
    assert len(db.search(q.age.between(18, 40))) == 2
    assert len(db.search(q.age.between(41, 70))) == 2
    assert q.age.between(1, 2) == q.age.between(1, 2)
    assert hash(q.age.between(1, 2)) == hash(q.age.between(1, 2))
    assert q.age.between(1, 2) != q.age.between(1, 3)
    assert q.age.between(1, 2) != q.other.between(1, 2)


def test_between_combines_with_logic_operators():
    db = make()
    q = Query()
    assert [d['age'] for d in db.search(q.age.between(18, 65) & (q.name == 'p40'))] == [40]
    assert sorted(d['age'] for d in db.search(~q.age.between(18, 65) & q.age.exists())) == [17, 66]

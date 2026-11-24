"""
Tests for the `append` operation in tinydb.operations.

These tests verify the acceptance criteria for the append feature.
"""

from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
from tinydb.operations import append


def test_ac1_import_append():
    """AC-1: Importing append from tinydb.operations succeeds and is
    callable."""
    from tinydb.operations import append as append_op
    assert callable(append_op)


def test_ac2_append_returns_operation_object():
    """AC-2: append('tags', 'urgent') returns an operation object usable
    with db.update."""
    db = TinyDB(storage=MemoryStorage)
    op = append('tags', 'urgent')
    assert callable(op)
    # Should be usable with db.update without error
    db.insert({'project': 'x'})
    db.update(op, Query().project == 'x')
    doc = db.get(Query().project == 'x')
    assert doc['tags'] == ['urgent']


def test_ac3_append_to_missing_field_creates_list():
    """AC-3: Append to document without field creates single-element list."""
    db = TinyDB(storage=MemoryStorage)
    db.insert({'project': 'x'})
    db.update(append('tags', 'urgent'), Query().project == 'x')
    doc = db.get(Query().project == 'x')
    assert doc == {'project': 'x', 'tags': ['urgent']}


def test_ac4_append_to_existing_list():
    """AC-4: Append to existing list adds element to the end."""
    db = TinyDB(storage=MemoryStorage)
    db.insert({'project': 'x', 'tags': ['bug']})
    db.update(append('tags', 'urgent'), Query().project == 'x')
    doc = db.get(Query().project == 'x')
    assert doc == {'project': 'x', 'tags': ['bug', 'urgent']}


def test_ac5_append_to_non_list_raises_typeerror():
    """AC-5: Append to non-list field raises TypeError and leaves document
    unchanged."""
    db = TinyDB(storage=MemoryStorage)
    db.insert({'project': 'x', 'tags': 'not-a-list'})
    try:
        db.update(append('tags', 'urgent'), Query().project == 'x')
        assert False, "Expected TypeError"
    except TypeError as e:
        assert "not a list" in str(e)
    # Document should be unchanged
    doc = db.get(Query().project == 'x')
    assert doc == {'project': 'x', 'tags': 'not-a-list'}


def test_ac6_append_updates_multiple_documents():
    """AC-6: Multiple matching documents are all updated correctly."""
    db = TinyDB(storage=MemoryStorage)
    db.insert({'project': 'x'})  # No tags field
    db.insert({'project': 'x', 'tags': ['a']})  # Existing list
    db.update(append('tags', 'b'), Query().project == 'x')
    docs = db.search(Query().project == 'x')
    assert len(docs) == 2
    # Order not guaranteed, check both
    tags_values = [doc['tags'] for doc in docs]
    assert ['b'] in tags_values
    assert ['a', 'b'] in tags_values


def test_ac7_fail_fast_on_typeerror():
    """AC-7: Fail-fast semantics - TypeError on second doc, first updated,
    third not processed."""
    db = TinyDB(storage=MemoryStorage)
    # Insert three documents matching the query
    db.insert({'project': 'x', 'id': 1})  # No tags field - should get ['x']
    db.insert({'project': 'x', 'id': 2, 'tags': 'not-a-list'})  # Non-list - should raise TypeError
    db.insert({'project': 'x', 'id': 3, 'tags': ['existing']})  # Should NOT be processed

    try:
        db.update(append('tags', 'x'), Query().project == 'x')
        assert False, "Expected TypeError"
    except TypeError as e:
        assert "not a list" in str(e)

    # Check state after failed update
    doc1 = db.get(Query().id == 1)
    doc2 = db.get(Query().id == 2)
    doc3 = db.get(Query().id == 3)

    # First document should be updated
    assert doc1['tags'] == ['x']
    # Second document should be unchanged (error occurred on it)
    assert doc2['tags'] == 'not-a-list'
    # Third document should NOT be processed (fail-fast)
    assert doc3['tags'] == ['existing']


def test_ac8_no_import_errors():
    """AC-8: Using append in fresh environment works without ImportError."""
    # This is implicitly tested by all other tests passing imports
    # But we can also test a fresh import scenario
    import importlib
    import sys

    # Simulate fresh import by reloading
    if 'tinydb.operations' in sys.modules:
        importlib.reload(sys.modules['tinydb.operations'])
    from tinydb.operations import append
    assert callable(append)

    # Verify it works end-to-end
    db = TinyDB(storage=MemoryStorage)
    db.insert({'data': 1})
    db.update(append('items', 'value'), Query().data == 1)
    doc = db.get(Query().data == 1)
    assert doc['items'] == ['value']


# Additional edge case tests

def test_append_with_various_value_types():
    """Append works with any JSON-serializable value (str, int, dict, list,
    etc.)."""
    db = TinyDB(storage=MemoryStorage)

    # String
    db.insert({'id': 1})
    db.update(append('vals', 'string'), Query().id == 1)
    assert db.get(Query().id == 1)['vals'] == ['string']

    # Integer
    db.insert({'id': 2})
    db.update(append('vals', 42), Query().id == 2)
    assert db.get(Query().id == 2)['vals'] == [42]

    # Dict
    db.insert({'id': 3})
    db.update(append('vals', {'key': 'value'}), Query().id == 3)
    assert db.get(Query().id == 3)['vals'] == [{'key': 'value'}]

    # List
    db.insert({'id': 4})
    db.update(append('vals', [1, 2, 3]), Query().id == 4)
    assert db.get(Query().id == 4)['vals'] == [[1, 2, 3]]

    # None
    db.insert({'id': 5})
    db.update(append('vals', None), Query().id == 5)
    assert db.get(Query().id == 5)['vals'] == [None]


def test_append_preserves_existing_list_order():
    """Append adds to the end of the list, preserving order."""
    db = TinyDB(storage=MemoryStorage)
    db.insert({'tags': ['a', 'b', 'c']})
    db.update(append('tags', 'd'))
    assert db.all()[0]['tags'] == ['a', 'b', 'c', 'd']


def test_append_with_empty_list():
    """Append to empty list works correctly."""
    db = TinyDB(storage=MemoryStorage)
    db.insert({'tags': []})
    db.update(append('tags', 'first'))
    assert db.all()[0]['tags'] == ['first']


def test_append_field_name_with_special_chars():
    """Append works with field names containing special characters."""
    db = TinyDB(storage=MemoryStorage)
    # Start with document that doesn't have the field
    db.insert({'other': 'value'})
    db.update(append('my-field', 'appended'), Query().other == 'value')
    doc = db.all()[0]
    assert doc['my-field'] == ['appended']


def test_append_field_name_with_special_chars_existing_list():
    """Append works with field names containing special chars when field is
    already a list."""
    db = TinyDB(storage=MemoryStorage)
    db.insert({'my-field': ['existing']})
    db.update(append('my-field', 'appended'))
    doc = db.all()[0]
    assert doc['my-field'] == ['existing', 'appended']


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
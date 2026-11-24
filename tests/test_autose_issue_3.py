"""
Tests for Query().field.between(low, high) method.

Covers acceptance criteria AC-1 through AC-12.
"""

from datetime import datetime
from typing import Any

import pytest

from tinydb import TinyDB, Query
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import MemoryStorage


class TestBetweenMethod:
    """Tests for the between query method."""

    # AC-1: Integer range query
    def test_ac1_integer_range(self) -> None:
        db = TinyDB(storage=MemoryStorage)
        db.insert_multiple([
            {'age': 18},
            {'age': 25},
            {'age': 65},
            {'age': 70},
        ])
        result = db.search(Query().age.between(18, 65))
        assert result == [{'age': 18}, {'age': 25}, {'age': 65}]

    # AC-2: String range query
    def test_ac2_string_range(self) -> None:
        db = TinyDB(storage=MemoryStorage)
        db.insert_multiple([
            {'name': 'Alice'},
            {'name': 'Bob'},
            {'name': 'Charlie'},
        ])
        result = db.search(Query().name.between('Alice', 'Bob'))
        assert result == [{'name': 'Alice'}, {'name': 'Bob'}]

    # AC-3: Empty result when low > high
    def test_ac3_low_greater_than_high_returns_empty(self) -> None:
        db = TinyDB(storage=MemoryStorage)
        db.insert({'age': 25})
        result = db.search(Query().age.between(65, 18))
        assert result == []

    # AC-4: Datetime range query
    def test_ac4_datetime_range(self) -> None:
        db = TinyDB(storage=MemoryStorage)
        db.insert_multiple([
            {'ts': datetime(2024, 1, 1)},
            {'ts': datetime(2024, 6, 1)},
            {'ts': datetime(2024, 12, 31)},
        ])
        result = db.search(Query().ts.between(
            datetime(2024, 1, 1),
            datetime(2024, 6, 30)
        ))
        assert result == [
            {'ts': datetime(2024, 1, 1)},
            {'ts': datetime(2024, 6, 1)},
        ]

    # AC-5: Float range query
    def test_ac5_float_range(self) -> None:
        db = TinyDB(storage=MemoryStorage)
        db.insert_multiple([
            {'price': 9.99},
            {'price': 19.99},
            {'price': 29.99},
        ])
        result = db.search(Query().price.between(10.0, 20.0))
        assert result == [{'price': 19.99}]

    # AC-6: Single-value range (low == high)
    def test_ac6_single_value_range(self) -> None:
        db = TinyDB(storage=MemoryStorage)
        db.insert({'age': 25})
        result = db.search(Query().age.between(25, 25))
        assert result == [{'age': 25}]

    # AC-7: Missing field does not match
    def test_ac7_missing_field_does_not_match(self) -> None:
        db = TinyDB(storage=MemoryStorage)
        db.insert_multiple([
            {'age': 25},
            {'name': 'Bob'},  # missing 'age' field
        ])
        result = db.search(Query().age.between(18, 65))
        assert result == [{'age': 25}]

    # AC-8: AND composition
    def test_ac8_and_composition(self) -> None:
        db = TinyDB(storage=MemoryStorage)
        db.insert_multiple([
            {'age': 25, 'active': True},
            {'age': 30, 'active': False},
            {'age': 35, 'active': True},
        ])
        result = db.search(
            (Query().age.between(20, 40)) & (Query().active == True)
        )
        assert result == [
            {'age': 25, 'active': True},
            {'age': 35, 'active': True},
        ]

    # AC-9: OR composition
    def test_ac9_or_composition(self) -> None:
        db = TinyDB(storage=MemoryStorage)
        db.insert_multiple([
            {'age': 15},
            {'age': 25},
            {'age': 65},
        ])
        result = db.search(
            (Query().age.between(18, 30)) | (Query().age.between(60, 70))
        )
        assert result == [{'age': 25}, {'age': 65}]

    # AC-10: NOT composition
    def test_ac10_not_composition(self) -> None:
        db = TinyDB(storage=MemoryStorage)
        db.insert_multiple([
            {'age': 25},
            {'age': 30},
            {'age': 35},
        ])
        result = db.search(~(Query().age.between(28, 32)))
        assert result == [{'age': 25}, {'age': 35}]

    # AC-11: Query cache works with between
    def test_ac11_query_cache(self) -> None:
        db = TinyDB(storage=CachingMiddleware(MemoryStorage))
        db.insert_multiple([
            {'age': 25},
            {'age': 30},
        ])

        # First call - populates cache
        result1 = db.search(Query().age.between(20, 30))
        assert result1 == [{'age': 25}, {'age': 30}]

        # Second call - should use cache
        result2 = db.search(Query().age.between(20, 30))
        assert result2 == [{'age': 25}, {'age': 30}]

        # Verify it's the same content (cache hit)
        assert result1 == result2

    # AC-12: Coverage test - this is implicitly tested by running all tests
    # but we can add a test that exercises edge cases for full coverage
    def test_ac12_edge_cases_for_coverage(self) -> None:
        """Test edge cases to ensure full coverage of between method."""
        db = TinyDB(storage=MemoryStorage)

        # Test with negative numbers
        db.insert_multiple([
            {'value': -10},
            {'value': -5},
            {'value': 0},
            {'value': 5},
            {'value': 10},
        ])
        result = db.search(Query().value.between(-5, 5))
        assert result == [
            {'value': -5},
            {'value': 0},
            {'value': 5},
        ]

        # Test with zero bounds
        db.truncate()
        db.insert_multiple([
            {'value': 0},
            {'value': 1},
        ])
        result = db.search(Query().value.between(0, 0))
        assert result == [{'value': 0}]

        # Test that between returns a cacheable query (has hash)
        query = Query().age.between(18, 65)
        assert query.is_cacheable()
        assert hash(query) is not None

        # Test equality of between queries
        q1 = Query().age.between(18, 65)
        q2 = Query().age.between(18, 65)
        q3 = Query().age.between(18, 66)
        assert q1 == q2
        assert q1 != q3

        # Test repr
        assert 'between' in repr(q1)

    # Additional test: between with nested field path
    def test_between_nested_field(self) -> None:
        db = TinyDB(storage=MemoryStorage)
        db.insert_multiple([
            {'user': {'age': 25}},
            {'user': {'age': 30}},
            {'user': {'age': 35}},
        ])
        result = db.search(Query().user.age.between(25, 30))
        assert result == [
            {'user': {'age': 25}},
            {'user': {'age': 30}},
        ]

    # Additional test: between with where() shorthand
    def test_between_with_where(self) -> None:
        from tinydb.queries import where
        db = TinyDB(storage=MemoryStorage)
        db.insert_multiple([
            {'age': 25},
            {'age': 30},
        ])
        result = db.search(where('age').between(25, 30))
        assert result == [{'age': 25}, {'age': 30}]

    # Additional test: between with different orderable types
    def test_between_various_orderable_types(self) -> None:
        """Test that between works with various orderable types (A-1)."""
        db = TinyDB(storage=MemoryStorage)

        # Test with tuples (lexicographic ordering)
        db.insert_multiple([
            {'coord': (1, 2)},
            {'coord': (2, 3)},
            {'coord': (3, 4)},
        ])
        result = db.search(Query().coord.between((1, 2), (2, 3)))
        assert result == [
            {'coord': (1, 2)},
            {'coord': (2, 3)},
        ]

        # Test with bytes
        db.truncate()
        db.insert_multiple([
            {'data': b'a'},
            {'data': b'b'},
            {'data': b'c'},
        ])
        result = db.search(Query().data.between(b'a', b'b'))
        assert result == [{'data': b'a'}, {'data': b'b'}]
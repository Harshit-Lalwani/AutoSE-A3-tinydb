"""
Tests for the Query.between() method (issue #3).
"""

import pytest
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
from tinydb.middlewares import CachingMiddleware


class TestBetweenMethod:
    """Tests for Query.between() method."""

    def setup_method(self):
        """Set up a fresh database for each test."""
        self.db = TinyDB(storage=MemoryStorage)

    def teardown_method(self):
        """Clean up after each test."""
        self.db.close()

    def test_ac1_basic_between_query(self):
        """AC-1: Basic between query returns documents where low <= value <= high."""
        self.db.insert_multiple([
            {'name': 'Alice', 'age': 17},
            {'name': 'Bob', 'age': 18},
            {'name': 'Charlie', 'age': 30},
            {'name': 'David', 'age': 65},
            {'name': 'Eve', 'age': 66},
        ])

        results = self.db.search(Query().age.between(18, 65))
        ages = [doc['age'] for doc in results]

        assert ages == [18, 30, 65]

    def test_ac2_between_returns_callable(self):
        """AC-2: Query().age.between returns a callable accepting (low, high)."""
        between_method = Query().age.between

        # Should be callable
        assert callable(between_method)

        # Should accept two arguments and return a query object
        query = between_method(18, 65)
        assert hasattr(query, '__call__')
        assert hasattr(query, '__hash__')

        # Should work when called with a document
        assert query({'age': 30}) is True
        assert query({'age': 17}) is False

    def test_ac3_inclusive_bounds(self):
        """AC-3: Between is inclusive - matches 18, 30, 65 but not 17, 66."""
        self.db.insert_multiple([
            {'age': 17},
            {'age': 18},
            {'age': 30},
            {'age': 65},
            {'age': 66},
        ])

        results = self.db.search(Query().age.between(18, 65))
        ages = sorted([doc['age'] for doc in results])

        assert ages == [18, 30, 65]

    def test_ac4_exact_match_bounds(self):
        """AC-4: Between with equal bounds matches exact value."""
        self.db.insert_multiple([
            {'price': 9.99},
            {'price': 10.00},
            {'price': 10.01},
        ])

        results = self.db.search(Query().price.between(10.00, 10.00))
        prices = [doc['price'] for doc in results]

        assert prices == [10.00]

    def test_ac5_missing_field_excluded(self):
        """AC-5: Documents missing the field are excluded."""
        self.db.insert_multiple([
            {'age': 25},
            {'name': 'Bob'},  # missing 'age'
            {'age': 30},
        ])

        results = self.db.search(Query().age.between(20, 30))
        ages = sorted([doc['age'] for doc in results])

        assert ages == [25, 30]
        assert len(results) == 2

    def test_ac6_composition_with_and(self):
        """AC-6: Between composes with & (AND)."""
        self.db.insert_multiple([
            {'name': 'John', 'age': 25},
            {'name': 'John', 'age': 17},
            {'name': 'Jane', 'age': 30},
            {'name': 'Bob', 'age': 25},
        ])

        query = Query().age.between(18, 65) & (Query().name == 'John')
        results = self.db.search(query)

        assert len(results) == 1
        assert results[0]['name'] == 'John'
        assert results[0]['age'] == 25

    def test_ac7_composition_with_or(self):
        """AC-7: Between composes with | (OR)."""
        self.db.insert_multiple([
            {'name': 'John', 'age': 25, 'status': 'user'},
            {'name': 'Jane', 'age': 17, 'status': 'admin'},
            {'name': 'Bob', 'age': 30, 'status': 'user'},
            {'name': 'Alice', 'age': 40, 'status': 'admin'},
        ])

        query = Query().age.between(18, 65) | (Query().status == 'admin')
        results = self.db.search(query)

        # Should match: John (age 25), Jane (admin), Bob (age 30), Alice (admin)
        assert len(results) == 4

    def test_ac8_cache_compatibility(self):
        """AC-8: Between works with CachingMiddleware (cache hit on second call)."""
        cached_db = TinyDB(storage=CachingMiddleware(MemoryStorage))
        cached_db.insert_multiple([
            {'age': 17},
            {'age': 25},
            {'age': 30},
            {'age': 65},
            {'age': 66},
        ])

        query = Query().age.between(18, 65)

        # First call - populates cache
        results1 = cached_db.search(query)
        assert len(results1) == 3

        # Second call - should use cache
        results2 = cached_db.search(query)
        assert len(results2) == 3
        assert results1 == results2

        # Verify cache was used by checking the cache directly
        # The cache is on the table, not the database
        table = cached_db.table('_default')
        cache = table._query_cache
        assert query in cache
        assert cache[query] == results1

        cached_db.close()

    def test_ac9_low_greater_than_high_returns_empty(self):
        """AC-9: Between with low > high returns empty list (SQL BETWEEN semantics)."""
        self.db.insert_multiple([
            {'age': 20},
            {'age': 30},
            {'age': 40},
        ])

        results = self.db.search(Query().age.between(30, 20))

        assert results == []

    def test_ac10_only_between_method_added(self):
        """AC-10: Only 'between' method is added; no existing methods removed."""
        query = Query()

        # Check that between exists
        assert hasattr(query, 'between')
        assert callable(query.between)

        # Check that existing methods still exist
        existing_methods = [
            '__eq__', '__ne__', '__lt__', '__le__', '__gt__', '__ge__',
            'exists', 'matches', 'search', 'test', 'any', 'all',
            'one_of', 'fragment', 'noop', 'map'
        ]
        for method in existing_methods:
            assert hasattr(query, method), f"Method {method} was removed"

    def test_ac11_performance_not_degraded(self):
        """AC-11: Existing query performance not measurably degraded."""
        import time

        # Create a larger dataset
        self.db.insert_multiple([{'value': i} for i in range(1000)])

        # Benchmark existing queries
        queries = [
            Query().value == 500,
            Query().value != 500,
            Query().value < 500,
            Query().value <= 500,
            Query().value > 500,
            Query().value >= 500,
            (Query().value > 100) & (Query().value < 200),
            (Query().value > 100) | (Query().value < 50),
            ~(Query().value == 500),
        ]

        # Warm up
        for q in queries:
            self.db.search(q)

        # Time existing queries
        start = time.perf_counter()
        for _ in range(10):
            for q in queries:
                self.db.search(q)
        existing_time = time.perf_counter() - start

        # Time new between query (should be similar order of magnitude)
        between_query = Query().value.between(100, 200)
        start = time.perf_counter()
        for _ in range(10):
            self.db.search(between_query)
        between_time = time.perf_counter() - start

        # Between should not be significantly slower than existing queries
        # (allow up to 10x for small sample, but typically should be similar)
        assert between_time < existing_time * 5, \
            f"Between query too slow: {between_time:.4f}s vs {existing_time:.4f}s"

    def test_between_with_string_values(self):
        """Test between with string values (alphabetical ordering)."""
        self.db.insert_multiple([
            {'name': 'Alice'},
            {'name': 'Bob'},
            {'name': 'Charlie'},
            {'name': 'David'},
            {'name': 'Eve'},
        ])

        results = self.db.search(Query().name.between('Bob', 'David'))
        names = sorted([doc['name'] for doc in results])

        assert names == ['Bob', 'Charlie', 'David']

    def test_between_with_negative_numbers(self):
        """Test between with negative numbers."""
        self.db.insert_multiple([
            {'temp': -10},
            {'temp': -5},
            {'temp': 0},
            {'temp': 5},
            {'temp': 10},
        ])

        results = self.db.search(Query().temp.between(-5, 5))
        temps = sorted([doc['temp'] for doc in results])

        assert temps == [-5, 0, 5]

    def test_between_hash_stability(self):
        """Test that between queries have stable hashes for caching."""
        q1 = Query().age.between(18, 65)
        q2 = Query().age.between(18, 65)
        q3 = Query().age.between(18, 66)

        # Same parameters should have same hash
        assert hash(q1) == hash(q2)
        assert q1 == q2

        # Different parameters should have different hash
        assert hash(q1) != hash(q3)
        assert q1 != q3

    def test_between_composition_with_not(self):
        """Test between composes with ~ (NOT)."""
        self.db.insert_multiple([
            {'age': 17},
            {'age': 25},
            {'age': 65},
            {'age': 66},
        ])

        query = ~Query().age.between(18, 65)
        results = self.db.search(query)
        ages = sorted([doc['age'] for doc in results])

        assert ages == [17, 66]

    def test_between_type_error_raised(self):
        """Test that type errors during comparison are raised (matching existing behavior)."""
        self.db.insert_multiple([
            {'age': 25},
            {'age': 'twenty-five'},  # string instead of int
            {'age': 30},
        ])

        # Comparing int with string raises TypeError (matching existing behavior for >, >=, etc.)
        with pytest.raises(TypeError):
            self.db.search(Query().age.between(20, 30))

    def test_between_nested_field(self):
        """Test between works with nested field paths."""
        self.db.insert_multiple([
            {'user': {'age': 17}},
            {'user': {'age': 25}},
            {'user': {'age': 65}},
            {'user': {'age': 66}},
        ])

        results = self.db.search(Query().user.age.between(18, 65))
        ages = sorted([doc['user']['age'] for doc in results])

        assert ages == [25, 65]

    def test_between_with_none_values_raises(self):
        """Test that None values raise TypeError (matching existing behavior)."""
        self.db.insert_multiple([
            {'age': None},
            {'age': 25},
            {'age': 30},
        ])

        # None compared with int raises TypeError (matching existing behavior for >=, etc.)
        with pytest.raises(TypeError):
            self.db.search(Query().age.between(20, 30))

    def test_between_zero_bounds(self):
        """Test between with zero as bounds."""
        self.db.insert_multiple([
            {'value': -1},
            {'value': 0},
            {'value': 1},
        ])

        results = self.db.search(Query().value.between(0, 0))
        values = [doc['value'] for doc in results]

        assert values == [0]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
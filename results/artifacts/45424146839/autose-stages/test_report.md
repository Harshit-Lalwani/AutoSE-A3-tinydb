# Test report (issue #5, stages, attempt 2)

**Result:** FAIL

| AC | Test | With change | On `main` |
|---|---|---|---|
| AC-1 | `test_ac1_sort_ascending` | passed | failed |
| AC-2 | `test_ac2_sort_descending` | passed | failed |
| AC-3 | `test_ac3_sort_nested_field_dot_notation` | failed | failed |
| AC-4 | `test_ac4_limit_returns_exact_number` | passed | failed |
| AC-5 | `test_ac5_limit_larger_than_matches_returns_all` | passed | failed |
| AC-6 | `test_ac6_offset_and_limit_paging` | passed | failed |
| AC-7 | `test_ac7_offset_beyond_matches_returns_empty` | passed | failed |
| AC-8 | `test_ac8_sort_before_limit_offset` | passed | failed |
| AC-9 | `test_ac9_sort_invalid_type_raises_typeerror` | passed | failed |
| AC-9 | `test_ac9_sort_invalid_tuple_length_raises_typeerror` | passed | failed |
| AC-9 | `test_ac9_sort_invalid_field_type_raises_typeerror` | passed | failed |
| AC-9 | `test_ac9_sort_invalid_direction_raises_typeerror` | passed | failed |
| AC-10 | `test_ac10_limit_negative_raises_valueerror` | passed | failed |
| AC-10 | `test_ac10_limit_non_integer_raises_typeerror` | passed | failed |
| AC-10 | `test_ac10_offset_negative_raises_valueerror` | passed | failed |
| AC-10 | `test_ac10_offset_non_integer_raises_typeerror` | passed | failed |
| AC-11 | `test_ac11_offset_beyond_matches_returns_empty` | passed | failed |
| AC-12 | `test_ac12_backward_compatibility_no_new_params` | passed | passed |
| AC-12 | `test_ac12_backward_compatibility_all_docs` | passed | passed |
| AC-12 | `test_ac12_default_parameters_explicit` | passed | failed |
| AC-13 | `test_ac13_caching_middleware_works_with_sort_limit_offset` | passed | failed |

Full suite: 263 tests, 5 failing.

Failing:
- `tests.test_autose_issue_5.TestSearchCombined::test_sort_limit_offset_combined`
- `tests.test_autose_issue_5.TestSearchEdgeCases::test_search_sort_by_nonexistent_field`
- `tests.test_autose_issue_5.TestSearchEdgeCases::test_search_sort_nested_nonexistent_field`
- `tests.test_autose_issue_5.TestSearchSort::test_ac3_sort_nested_field_dot_notation`
- `tests.test_autose_issue_5.TestSearchSort::test_sort_multiple_fields`

## Problems

- full suite failed: 5 failing test(s)

<details><summary>pytest output (full suite)</summary>

```
..F....F...........F......FF............................................ [ 27%]
........................................................................ [ 54%]
........................................................................ [ 82%]
...............................................                          [100%]
=================================== FAILURES ===================================
____________ TestSearchSort.test_ac3_sort_nested_field_dot_notation ____________

self = <tests.test_autose_issue_5.TestSearchSort object at 0x71bdf04e02b0>

    def test_ac3_sort_nested_field_dot_notation(self):
        """AC-3: GIVEN documents with nested field {'user': {'name': 'Bob', 'score': 10}}, {'user': {'name': 'Alice', 'score': 20}}
        WHEN db.search(Query().user.score > 5, sort=[('user.score', 1)])
        THEN returns Alice first, then Bob (dot-notation field path works)"""
        db = TinyDB(storage=MemoryStorage)
        db.insert_multiple([
            {'user': {'name': 'Bob', 'score': 10}},
            {'user': {'name': 'Alice', 'score': 20}},
        ])
    
        results = db.search(Query().user.score > 5, sort=[('user.score', 1)])
    
        assert len(results) == 2
>       assert results[0]['user']['name'] == 'Alice'
E       AssertionError: assert 'Bob' == 'Alice'
E         
E         - Alice
E         + Bob

tests/test_autose_issue_5.py:73: AssertionError
___________________ TestSearchSort.test_sort_multiple_fields ___________________

self = <tests.test_autose_issue_5.TestSearchSort object at 0x71bdf0595350>

    def test_sort_multiple_fields(self):
        """Test sorting by multiple fields (secondary sort)."""
        db = TinyDB(storage=MemoryStorage)
        db.insert_multiple([
            {'name': 'Bob', 'age': 30, 'score': 100},
            {'name': 'Alice', 'age': 25, 'score': 200},
            {'name': 'Carol', 'age': 30, 'score': 50},
            {'name': 'Dave', 'age': 25, 'score': 150},
        ])
    
        # Sort by age ascending, then score descending
        results = db.search(Query().age > 20, sort=[('age', 1), ('score', -1)])
    
        assert len(results) == 4
        # Alice (25, 200) first, then Dave (25, 150)
        assert results[0]['name'] == 'Alice'
        assert results[1]['name'] == 'Dave'
        # Carol (30, 50) then Bob (30, 100) - score descending
>       assert results[2]['name'] == 'Carol'
E       AssertionError: assert 'Bob' == 'Carol'
E         
E         - Carol
E         + Bob

tests/test_autose_issue_5.py:128: AssertionError
______________ TestSearchCombined.test_sort_limit_offset_combined ______________

self = <tests.test_autose_issue_5.TestSearchCombined object at 0x71bdf0501bd0>

    def test_sort_limit_offset_combined(self):
        """Test combined sort, limit, and offset with multiple fields."""
        db = TinyDB(storage=MemoryStorage)
        db.insert_multiple([
            {'name': 'A', 'age': 30, 'score': 100},
            {'name': 'B', 'age': 25, 'score': 200},
  
... [7398 chars truncated] ...
ne:
            if not isinstance(sort, list):
                raise TypeError("sort must be a list of (field, direction) tuples")
            for item in sort:
                if not isinstance(item, tuple) or len(item) != 2:
                    raise TypeError("sort must be a list of (field, direction) tuples")
                field, direction = item
                if not isinstance(field, str):
                    raise TypeError("sort field must be a string")
                if direction not in (1, -1):
                    raise TypeError("sort direction must be 1 (ascending) or -1 (descending)")
    
        # Validate limit parameter
        if limit is not None:
            if not isinstance(limit, int):
                raise TypeError("limit must be an integer")
            if limit < 0:
                raise ValueError("limit must be a non-negative integer")
    
        # Validate offset parameter
        if not isinstance(offset, int):
            raise TypeError("offset must be an integer")
        if offset < 0:
            raise ValueError("offset must be a non-negative integer")
    
        # Check if we can use the cache (only when no sort, limit, or offset)
        use_cache = sort is None and limit is None and offset == 0
    
        if use_cache:
            # First, we check the query cache to see if it has results for this
            # query
            cached_results = self._query_cache.get(cond)
            if cached_results is not None:
                return cached_results[:]
    
        # Perform the search by applying the query to all documents.
        # Then, only if the document matches the query, convert it
        # to the document class and document ID class.
        docs = [
            self.document_class(doc, self.document_id_class(doc_id))
            for doc_id, doc in self._read_table().items()
            if cond(doc)
        ]
    
        # Apply sorting if requested
        if sort is not None:
            # Sort using multiple keys (stable sort, so apply in reverse order)
            for field, direction in reversed(sort):
>               docs.sort(
                    key=lambda d: self._resolve_field_path(d, field),  # type: ignore[arg-type,return-value]
                    reverse=(direction == -1)
                )
E               TypeError: '<' not supported between instances of 'NoneType' and 'NoneType'

tinydb/table.py:339: TypeError
=========================== short test summary info ============================
FAILED tests/test_autose_issue_5.py::TestSearchSort::test_ac3_sort_nested_field_dot_notation
FAILED tests/test_autose_issue_5.py::TestSearchSort::test_sort_multiple_fields
FAILED tests/test_autose_issue_5.py::TestSearchCombined::test_sort_limit_offset_combined
FAILED tests/test_autose_issue_5.py::TestSearchEdgeCases::test_search_sort_by_nonexistent_field
FAILED tests/test_autose_issue_5.py::TestSearchEdgeCases::test_search_sort_nested_nonexistent_field
5 failed, 258 passed in 0.95s

```
</details>

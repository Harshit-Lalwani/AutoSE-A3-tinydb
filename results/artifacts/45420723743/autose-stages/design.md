Now I have a thorough understanding of the codebase. Let me create the design document.

## Summary

Add a `between(low, high)` method to the `Query` class in `tinydb/queries.py` that creates an inclusive range query (`low <= value <= high`). The method will compose with `&`, `|`, `~`, work with the query cache, treat missing fields as non-matching, accept any orderable type, and return empty results when `low > high`.

## Root cause or approach

The `Query` class in `tinydb/queries.py` provides methods like `__eq__`, `__lt__`, `__le__`, `__gt__`, `__ge__` that generate `QueryInstance` objects via `_generate_test`. The new `between` method will follow the same pattern:

1. Add a `between(self, low, high)` method to the `Query` class
2. Use `_generate_test` to create a `QueryInstance` with:
   - A test function that returns `low <= value <= high` (or always `False` if `low > high`)
   - A hash value tuple `('between', self._path, freeze(low), freeze(high))` for cache compatibility
3. The existing `_generate_test` already handles missing fields (returns `False`) and type errors (returns `False`)

## Files and functions to change

| File | Function/Class | Change |
|------|----------------|--------|
| `tinydb/queries.py` | `Query.between` | **New method** - Add `between(low, high)` method to `Query` class that returns a `QueryInstance` for inclusive range queries |

## Step-by-step plan

1. **Add `between` method to `Query` class** in `tinydb/queries.py`:
   - Accept `low` and `high` parameters
   - If `low > high`, return a `QueryInstance` that always returns `False` (but is still cacheable with a proper hash)
   - Otherwise, return a `QueryInstance` that tests `low <= value <= high`
   - Use `_generate_test` with hash tuple `('between', self._path, freeze(low), freeze(high))`

2. **Write tests** in `tests/test_queries.py` covering all acceptance criteria (AC-1 through AC-12)

3. **Run tests** to verify implementation and 100% coverage

## Architecture constraints

| Constraint | Applies | How the plan respects it |
|------------|---------|--------------------------|
| C1 | No | No storage changes |
| C2 | **Yes** | Hash value includes operation, path, and frozen arguments: `('between', self._path, freeze(low), freeze(high))`. Uses `_generate_test` which handles missing fields and type errors. |
| C3 | No | No table update changes |
| C4 | No | No middleware changes |
| C5 | **Yes** | `queries.py` does not import `table.py` or `database.py`; the change stays within `queries.py` |

## Risks

- **Type comparison errors**: Comparing incompatible types (e.g., string vs number) raises `TypeError`. The existing `_generate_test` catches this and returns `False`, which is correct behavior.
- **Cache correctness**: The hash must include both `low` and `high` in the correct order. Using `freeze()` ensures arguments are hashable.
- **Edge case `low > high`**: Must return a query that matches nothing but is still cacheable (not `None` hash).

```json
{"files": [{"path": "tinydb/queries.py", "new": false, "symbols": [], "new_symbols": ["Query.between"]}]}
```
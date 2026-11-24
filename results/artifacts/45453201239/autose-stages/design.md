Now I have a thorough understanding of the codebase. Let me create the design document.

## Summary
Add a `between(low, high)` method to the `Query` class in `tinydb/queries.py` that creates an inclusive range query matching SQL BETWEEN semantics. The method will be composable with `&`, `|`, `~`, cache-compatible, and handle edge cases (missing fields, low > high).

## Root cause or approach
The `Query` class in `tinydb/queries.py` builds queries through `_generate_test()`, which:
1. Resolves the field path (handling missing fields by catching `KeyError`/`TypeError` and returning `False`)
2. Applies a test function to the resolved value
3. Creates a `QueryInstance` with a hash value for caching

The `between` method will follow the same pattern as existing comparison methods (`__le__`, `__ge__`, etc.), creating a test that checks `low <= value <= high` and a hash tuple `('between', path, freeze(low), freeze(high))`. When `low > high`, it returns a test that always returns `False` (matching SQL BETWEEN semantics).

## Files and functions to change

| file | function/class | change |
|------|----------------|--------|
| tinydb/queries.py | Query.between | Add new method `between(self, low, high)` that returns a `QueryInstance` for inclusive range queries |

## Step-by-step plan
1. Add the `between(low, high)` method to the `Query` class in `tinydb/queries.py` after the `__ge__` method (around line 327)
2. The method will:
   - Check if `low > high` and return a query that always evaluates to `False` (with a distinct hash)
   - Otherwise, create a test function `lambda value: low <= value <= high`
   - Create a hash value tuple `('between', self._path, freeze(low), freeze(high))`
   - Call `self._generate_test(test, hashval)` to create the `QueryInstance`
3. The existing `_generate_test` handles missing fields (returns `False`), caching (via hash), and composition (via `QueryInstance.__and__`, `__or__`, `__invert__`)

## Architecture constraints
- **C2 (Query hash stability)**: The hash value includes the operation name, field path, and both bounds made hashable via `freeze()`. This ensures identical queries share cache entries.
- **C5 (Downward dependencies)**: `queries.py` does not import `table.py` or `database.py`; the change stays within `queries.py`.
- **Cache compatibility**: The `QueryInstance` returned has a stable hash, making it cacheable by `Table._query_cache` (LRUCache). The cache key is the query object itself, which uses the hash value for equality.

## Risks
- **Type comparison errors**: If `low`/`high` are incomparable with the field value (e.g., string vs int), Python raises `TypeError`. The `_generate_test` runner catches `TypeError` and returns `False`, which is the desired behavior (no match).
- **Cache key distinct from expanded form**: Per assumption A-2, `between(low, high)` has a different cache key than `(field >= low) & (field <= high)`. This is acceptable and expected.
- **Performance**: The new method adds minimal overhead—single comparison in the test function, same path resolution as other methods. Existing query performance is unaffected.

```json
{"files": [{"path": "tinydb/queries.py", "new": false, "symbols": ["Query.between"]}]}
```
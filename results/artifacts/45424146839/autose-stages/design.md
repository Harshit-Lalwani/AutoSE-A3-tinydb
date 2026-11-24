## Summary
Add optional `sort`, `limit`, and `offset` keyword parameters to `Table.search()` for server-side ordering and paging of query results. The parameters are backward-compatible (default values preserve existing behavior).

## Root cause or approach
The current `search()` method in `tinydb/table.py` returns all matching documents in insertion order. The previous implementation attempt failed because:
1. The `_resolve_field_path` helper method was never implemented
2. Sorting with missing fields caused `TypeError` when comparing `None` values
3. Multiple field sorting logic had issues with the stable sort approach

The correct approach:
1. Add three optional keyword parameters to `Table.search()`: `sort`, `limit`, `offset`
2. Implement `_resolve_field_path` helper that handles dot-notation and returns `None` for missing paths (not raising KeyError)
3. When sorting, use a key function that returns a tuple with a sentinel for missing values to avoid `TypeError` during comparison
4. Apply sorting first (stable sort in reverse order for multiple keys), then offset, then limit
5. Bypass query cache when any of sort/limit/offset are used (since cached results don't reflect these parameters)
6. Validate parameters: `sort` must be list of `(field, direction)` tuples; `limit`/`offset` must be non-negative integers

## Files and functions to change

| file | function/class | change |
|------|----------------|--------|
| `tinydb/table.py` | `Table.search` | Add `sort`, `limit`, `offset` parameters; implement sorting, paging logic; bypass cache when these params used |
| `tinydb/table.py` | `Table._resolve_field_path` (new) | Helper method to extract nested field values using dot-notation (e.g., 'user.score'), returns `None` if path doesn't exist |

## Step-by-step plan

1. **Add `_resolve_field_path` helper method to `Table` class**
   - Takes a document (dict) and a field path string (e.g., 'user.score')
   - Splits by '.' and traverses the nested dict
   - Returns the value if found, `None` if any key in path is missing (no KeyError)

2. **Modify `Table.search` signature**
   - Add `sort: Optional[list[tuple[str, int]]] = None`
   - Add `limit: Optional[int] = None`
   - Add `offset: int = 0`

3. **Add parameter validation at start of `search`**
   - If `sort` is not None: validate it's a list of tuples, each tuple is (str, int) where int is 1 or -1
   - If `limit` is not None: validate it's an int >= 0
   - If `offset` is not None: validate it's an int >= 0
   - Raise `TypeError` for invalid `sort`, `ValueError` for negative `limit`/`offset`

4. **Modify cache logic**
   - Only use cache if `sort` is None AND `limit` is None AND `offset` == 0
   - When cache is bypassed, don't store results in cache

5. **Implement sorting with proper None handling**
   - If `sort` is provided, sort the matching documents using the field paths
   - For each sort key, extract value using `_resolve_field_path`
   - Use a key function that wraps values in a tuple `(value is not None, value)` so `None` sorts first in ascending order
   - Multiple sort keys: apply in reverse order (stable sort)
   - Direction: `reverse=(direction == -1)` for descending

6. **Implement offset and limit**
   - After sorting, apply `offset` (slice from offset)
   - Then apply `limit` (slice to limit)

7. **Return results**

## Architecture constraints

| Constraint | Applies? | How respected |
|------------|----------|---------------|
| C1: Storages subclass `Storage` | No | No storage changes needed |
| C2: Query hash describes everything affecting result | Yes | Sort/limit/offset are NOT part of query hash; they bypass cache entirely, so cache correctness is maintained |
| C3: Table changes through `_update_table` | No | Search is read-only |
| C4: Middlewares stay transparent | Yes | No middleware changes; search reads through storage normally |
| C5: Dependencies point downward | Yes | Changes only in `table.py`; no new imports from `database.py` or `queries.py` |

## Risks

1. **Cache bypass performance**: When sort/limit/offset are used, every search does a full table scan. This is acceptable because the feature is explicitly for server-side paging where the client requests specific pages. Users who don't use these params get full cache benefit.

2. **Missing field handling**: Documents missing the sort field will have `None` values, which sort first in ascending order. This is consistent with Python's default behavior and query behavior (queries treat missing fields as non-matching).

3. **Backward compatibility**: Default parameters ensure existing code works identically. The cache behavior is unchanged when new params aren't used.

4. **Type hints**: Need to ensure type hints are compatible with Python versions supported by TinyDB.

```json
{"files": [{"path": "tinydb/table.py", "new": false, "symbols": ["Table.search", "Table._resolve_field_path"]}]}
```
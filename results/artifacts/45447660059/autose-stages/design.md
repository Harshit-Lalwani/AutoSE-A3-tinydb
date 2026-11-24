Now I have a thorough understanding of the codebase. Let me create the design document.

## Summary

Add optional `sort_by`, `limit`, and `offset` parameters to `Table.search()` and `Table.all()` for server-side ordering and paging of query results. The implementation will:
1. Add parameters to both methods with proper type hints and validation
2. Apply sorting (using Python's stable sort with missing fields as `None`) before paging
3. Reuse the existing query cache for `search()` by applying sort/paging on cached results copies
4. Keep `all()` simple by getting all documents directly then applying sort/paging
5. Maintain full backward compatibility when parameters are not provided

## Root cause or approach

The feature requires extending two public methods (`Table.search` and `Table.all`) with three new optional parameters. The key design decisions:

- **Sorting**: Accept `sort_by` as a list of field names (strings), with `-` prefix for descending order. Missing fields evaluate to `None` (sorts first in Python). Use Python's built-in stable `list.sort()`.
- **Paging**: Apply `limit` (max results, `None` = unlimited) and `offset` (skip N results, default 0) after sorting.
- **Validation**: Strict type checking per acceptance criteria (TypeError for wrong types, ValueError for negative values).
- **Cache interaction**: For `search()`, fetch from cache (or compute), then apply sort/paging on the returned copy. This preserves cache efficiency while allowing different sort/paging per call. For `all()`, no cache is used (current behavior), just get all documents and apply sort/paging.
- **Backward compatibility**: When no new parameters are provided, behavior is identical to current implementation (storage order, no paging).

## Files and functions to change

| file | function/class | change |
|------|----------------|--------|
| `tinydb/table.py` | `Table.all` | Add `sort_by`, `limit`, `offset` parameters with validation; apply sorting/paging to results |
| `tinydb/table.py` | `Table.search` | Add `sort_by`, `limit`, `offset` parameters with validation; apply sorting/paging after cache lookup |
| `tinydb/table.py` | `Table._apply_sort_and_paging` (new) | Private helper method to apply sorting and paging to a list of documents |

## Step-by-step plan

1. **Add private helper `_apply_sort_and_paging`** in `Table` class:
   - Accept `docs: list[Document]`, `sort_by: Optional[list[str]]`, `limit: Optional[int]`, `offset: int`
   - Validate `sort_by` is a list (not str), each element is str
   - Validate `limit` is int or None, non-negative
   - Validate `offset` is int, non-negative
   - Build sort key function: for each field in `sort_by`, extract value (or `None` if missing), handle `-` prefix for descending
   - Apply stable sort using `list.sort(key=..., reverse=...)` for each field in reverse order (to achieve multi-field sort)
   - Apply paging: `docs[offset:offset+limit]` if limit set, else `docs[offset:]`
   - Return processed list

2. **Modify `Table.all`**:
   - Add parameters: `sort_by: Optional[list[str]] = None`, `limit: Optional[int] = None`, `offset: int = 0`
   - Get all documents via `list(iter(self))` (current behavior)
   - Call `_apply_sort_and_paging` and return result

3. **Modify `Table.search`**:
   - Add same parameters with same defaults
   - Keep existing cache logic: get cached results or compute and cache
   - **Important**: Work on a copy (`cached_results[:]` or `docs[:]`) before passing to `_apply_sort_and_paging` to avoid mutating cache
   - Call `_apply_sort_and_paging` on the copy and return result

4. **Add tests** (not part of this design but implied by AC-18): Cover all acceptance criteria including validation errors, sorting variations, paging edge cases, and combination of sort+paging.

## Architecture constraints

| Constraint | How plan respects it |
|------------|---------------------|
| **C1** (Storage interface) | No storage changes; sorting/paging happens in-memory after reading |
| **C2** (Query hash completeness) | No query changes; new parameters are not part of query condition, so cache key unchanged |
| **C3** (Table updates via `_update_table`) | Read-only operations; no writes involved |
| **C4** (Middleware transparency) | Middlewares unaffected; they only wrap storage read/write |
| **C5** (Downward dependencies) | No new imports; `table.py` already imports `QueryLike` from `queries.py`; helper uses only stdlib |

## Risks

1. **Cache behavior change**: Previously, `search()` returned cached results directly (as a copy). Now it applies sort/paging on the copy. This is safe because we operate on a copy, but callers who relied on cache returning storage-order results with no paging will get the same behavior when not passing new parameters.

2. **Performance on large tables**: Sorting large result sets in Python could be slow. However, this is "server-side" in the sense of in-process, and TinyDB is designed for small datasets. The alternative (database-level sorting) would require storage changes violating C1.

3. **Multi-field sort implementation**: Must apply sort keys in reverse order (last key first) to achieve correct multi-field sorting with Python's stable sort. This is a common pitfall.

4. **Type hint compatibility**: Must maintain compatibility with Python 3.10+ (per `pyproject.toml`). Use `Optional[list[str]]` etc. which works on 3.10+.

5. **Document mutation warning**: The docstring warns that returned documents are shared with cache. Our helper returns the same Document objects (just reordered/sliced), so this warning still applies.

```json
{"files": [{"path": "tinydb/table.py", "new": false, "symbols": ["Table.all", "Table.search", "Table._apply_sort_and_paging"]}]}
```
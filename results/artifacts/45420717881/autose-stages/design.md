## Summary

The issue is that `Table._update_table()` only clears the query cache on successful completion. When an exception occurs during the `updater` function or during `storage.write()`, the cache remains stale, violating AC-4. The fix wraps the mutation and write in a `try/finally` block so `clear_cache()` runs on **any** exception, while preserving the existing rollback behavior (which already works because the storage is only mutated after the updater succeeds).

## Root cause or approach

In `Table._update_table()` (lines ~780–860), the query cache is cleared **after** `self._storage.write(tables)`:

```python
updater(table)                    # Exception here → cache NOT cleared
tables[self.name] = {...}
self._storage.write(tables)       # Exception here → cache NOT cleared
self.clear_cache()                # Only reached on success
```

For `MemoryStorage`, `read()` returns the live `self.memory` dict, but the code builds a **new** `table` dict from it. The updater mutates this new dict; the assignment `tables[self.name] = {...}` (which mutates `self.memory`) and `write()` only happen if the updater succeeds. If the updater raises, the assignment never runs → in-memory data is automatically rolled back. If `write()` raises, the assignment already ran but the file (for `JSONStorage`) or memory (for `MemoryStorage`) is left in a consistent state because `write` is the persistence step.

The fix: wrap the updater, ID conversion, and `write()` in a `try` block and put `clear_cache()` in the `finally` block. This ensures cache invalidation on **any** exception while keeping the existing rollback semantics.

## Files and functions to change

| file | function/class | change |
|------|----------------|--------|
| `tinydb/table.py` | `Table._update_table` | Restructure to use `try/finally` so `self.clear_cache()` executes even when `updater` or `write` raises. |

## Step-by-step plan

1. **Locate `_update_table`** in `tinydb/table.py` (starts around line 780).
2. **Restructure the method**:
   - Keep the `read()` and table-preparation logic (lines 780–810) outside the `try` block.
   - Wrap the `updater(table)` call, the ID conversion (`tables[self.name] = {...}`), and `self._storage.write(tables)` in a `try` block.
   - Move `self.clear_cache()` into a `finally` block.
3. **Verify** the change doesn't break existing tests (run `pytest tests/`).
4. **Confirm** the fix satisfies all acceptance criteria:
   - AC-1/2/3: Rollback works because storage write never happens on exception.
   - AC-4: Cache invalidated because `clear_cache()` runs in `finally`.
   - AC-5: `JSONStorage` behavior unchanged (write not called on exception, cache now also cleared).

## Architecture constraints

| Constraint | Applies? | How the plan respects it |
|------------|----------|--------------------------|
| C1: Storages implement `read`/`write` | Yes | No storage changes; fix is in `Table._update_table` which uses the storage interface correctly. |
| C2: Query hash completeness | No | Unrelated to cache invalidation timing. |
| C3: Table changes via `_update_table` | **Yes** | The fix is **inside** `_update_table`, the single write path. |
| C4: Middleware transparency | No | Middlewares wrap storage; `Table` calls `storage.read/write` unchanged. |
| C5: Downward dependencies only | Yes | `table.py` already imports `Storage` from `storages.py`; no new imports. |

## Risks

- **Double cache clear on success**: The original `clear_cache()` call after `write` is removed; `finally` runs exactly once. No double-clear.
- **Cache cleared on storage write failure**: If `write()` raises (e.g., disk full), cache is cleared but on-disk data is unchanged. Next read repopulates cache from disk → correct behavior.
- **Performance**: `finally` block adds negligible overhead; `clear_cache()` is O(1) for `LRUCache.clear()`.
- **Mypy errors**: The previous attempt failed mypy because it likely modified the wrong method or introduced type issues. This plan only touches `_update_table` with a straightforward `try/finally` restructure that preserves all types.

```json
{"files": [{"path": "tinydb/table.py", "new": false, "symbols": ["Table._update_table"]}]}
```
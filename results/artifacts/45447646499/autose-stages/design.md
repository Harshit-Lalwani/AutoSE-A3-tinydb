## Summary

The issue is that `Table._update_table` modifies documents in-place before writing to storage. For `MemoryStorage`, `storage.read()` returns the internal `self.memory` dict directly, so in-place mutations during the updater (e.g., `delete('tmp')` raising `KeyError` halfway through) leave the storage partially modified. `JSONStorage` accidentally works because it reads from a file into new dicts each time. The query cache is cleared after `storage.write()`, so a failed write doesn't clear the cache—but for `MemoryStorage` the data has already changed, making the cache stale.

## Root cause or approach

**Root cause**: In `Table._update_table`, the `table` dict passed to the updater contains the *same document dict objects* that live in `tables` (which came from `storage.read()`). For `MemoryStorage`, `tables` *is* `self.memory`. When the updater mutates documents in-place (e.g., `del doc['tmp']`), it mutates the storage's memory directly. If an exception occurs later, the write still happens (or the mutated data remains in memory), and the cache is not cleared, leaving the cache inconsistent with the now-modified storage.

**Approach**: Make `_update_table` truly atomic by:
1. Deep-copying the table data (documents) before calling the updater
2. Only writing to storage and clearing the cache if the updater succeeds
3. On exception: don't write, don't clear cache, let the exception propagate

This ensures all storages (including `MemoryStorage`) behave atomically and the query cache stays consistent with the stored data.

## Files and functions to change

| file | function/class | change |
|------|----------------|--------|
| `tinydb/table.py` | `Table._update_table` | Deep-copy the table before mutation; only write to storage and clear cache on success; wrap updater in try/except to roll back on failure |

## Step-by-step plan

1. **Import `copy`** at the top of `table.py` (add `import copy`).
2. **Modify `Table._update_table`**:
   - After reading `tables` from storage and extracting/converting `raw_table` to `table`, create a deep copy: `table = copy.deepcopy(table)`.
   - Wrap the `updater(table)` call in a `try` block.
   - On success: convert IDs back to strings, write to storage, clear cache.
   - On exception: do not write, do not clear cache, re-raise the exception.
3. **Verify no other callers of `_update_table` need changes**—all table write operations (`insert`, `insert_multiple`, `update`, `update_multiple`, `upsert`, `remove`, `truncate`) go through `_update_table`, so they all get atomicity automatically.
4. **Ensure `_next_id` handling remains correct**—`_next_id` is updated inside the updater (e.g., in `insert_multiple`), and since the updater runs on the deep-copied table, `_next_id` mutations are also rolled back on failure (which is correct: a failed insert shouldn't consume IDs).

## Architecture constraints

- **C1 (Storages subclass `Storage`)**: Unchanged. The fix is entirely in `Table._update_table`; storages still implement `read()`/`write()` on the whole database dict.
- **C2 (Query hash values)**: Unchanged. Cache invalidation still happens in `Table.clear_cache()` after successful write.
- **C3 (Table changes go only through `Table._update_table`)**: **Strengthened**. The fix makes `_update_table` the single atomic transaction point, which is exactly what C3 intends.
- **C4 (Middlewares stay transparent)**: Unchanged. Middlewares wrap storages; `Table._update_table` calls `storage.read()`/`write()` as before.
- **C5 (Dependencies point downward)**: Unchanged. `table.py` still only imports from `queries`, `storages`, `utils`; no new upward dependencies.

## Risks

- **Performance**: `copy.deepcopy` on every write adds overhead. For large tables this could be noticeable. Mitigation: the copy is only of the *current table's* documents, not the entire database; typical TinyDB tables are small. If needed later, a copy-on-write optimization could be added.
- **`_next_id` rollback**: A failed `insert_multiple` will roll back `_next_id` to its pre-call value. This is correct (no IDs consumed on failure) but differs from the current half-modified behavior. Existing tests may need updating if they rely on the buggy behavior.
- **Custom `document_class`**: `deepcopy` must handle custom document classes. `Document` is a `dict` subclass, so `deepcopy` works. If users provide a non-copyable `document_class`, they'd hit an error—but that's a pre-existing constraint (documents must be JSON-serializable for `JSONStorage` anyway).
- **Middlewares with write caching** (`CachingMiddleware`): The middleware's `write` is only called on success, so its internal write cache is unaffected. No change needed.

```json
{"files": [{"path": "tinydb/table.py", "new": false, "symbols": ["Table._update_table"]}]}
```
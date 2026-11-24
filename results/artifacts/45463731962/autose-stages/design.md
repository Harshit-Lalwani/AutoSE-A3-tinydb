## Summary
Make MemoryStorage write operations (update, remove, insert_multiple) atomic like JSONStorage (all-or-nothing on exception) and ensure the search cache is invalidated after any write attempt (success or failure) so searches always reflect stored data.

## Root cause or approach
**Root cause 1 (non-atomic MemoryStorage):** `MemoryStorage.read()` returns the internal `self.memory` dict directly. `Table._update_table()` modifies this dict in-place (`tables[self.name] = ...`) before calling `write()`. If an exception occurs during the updater, the in-memory data is already partially mutated, and `write()` is never called to "commit" – but the damage is done because `tables` *is* `self.memory`.

**Root cause 2 (stale cache on failed writes):** `Table._update_table()` calls `clear_cache()` *after* `self._storage.write()`. If the updater or write raises, `clear_cache()` is skipped, leaving the query cache stale. Subsequent searches return cached results that don't match the actual stored data.

**Approach:**
1. **MemoryStorage atomicity:** Make `read()` return a deep copy so the table layer works on a private snapshot. `write()` replaces `self.memory` with the new snapshot (copy-on-write). This matches JSONStorage's semantics where the file is untouched until the atomic rename.
2. **Cache invalidation:** Move `clear_cache()` into a `finally` block in `_update_table()` so it runs regardless of whether the updater or write succeeds. This ensures the cache is always invalidated after a write attempt, forcing a fresh read on the next search.

## Files and functions to change

| file | function/class | change |
|------|----------------|--------|
| tinydb/storages.py | MemoryStorage.read | Return `copy.deepcopy(self.memory)` instead of the live dict; add `import copy` at module top |
| tinydb/table.py | Table._update_table | Wrap updater + write in `try/finally`; call `self.clear_cache()` in `finally` block |

## Step-by-step plan
1. **Modify `MemoryStorage.read()`** (tinydb/storages.py):
   - Add `import copy` at module top.
   - Change `read()` to return `copy.deepcopy(self.memory)` (handles `None` gracefully).
   - This ensures the table layer mutates a private copy; `self.memory` stays unchanged until `write()`.

2. **Modify `Table._update_table()`** (tinydb/table.py):
   - Restructure the method: read data, build `table`, run `updater(table)`, prepare `tables[self.name]`, write, all inside a `try` block.
   - Add a `finally` block that calls `self.clear_cache()`.
   - This guarantees cache invalidation on both success and failure paths.

3. **Verify no other write paths bypass `_update_table`**:
   - `insert`, `insert_multiple`, `update`, `remove`, `truncate` all delegate to `_update_table` – covered.

4. **Run existing tests** to ensure JSONStorage behavior (AC-7) is preserved and no regressions.

## Architecture constraints
- **C1 (Storage interface):** Unchanged – `read()`/`write()` signatures stay the same; only `MemoryStorage` implementation changes.
- **C2 (Table layer):** `_update_table` remains the single write funnel; cache invalidation moves there (A-3).
- **C3 (Query cache):** `clear_cache()` is already the invalidation primitive; calling it in `finally` respects the cache contract.
- **C4 (No external deps):** `copy.deepcopy` is stdlib – no new dependencies.
- **C5 (Atomicity):** Copy-on-write (A-2) gives all-or-nothing semantics for `update`, `remove`, `insert_multiple` (A-4) on MemoryStorage, matching JSONStorage.

## Risks
- **Performance:** `deepcopy` on every read adds overhead for large databases. Acceptable for MemoryStorage (typically small/in-memory use cases). Could be optimized later with copy-on-write dict if needed.
- **Nested mutable objects in documents:** `deepcopy` handles them correctly; documents are plain dicts per TinyDB contract.
- **Concurrency:** Not in scope – TinyDB is single-threaded.

```json
{"files": [{"path": "tinydb/storages.py", "new": false, "symbols": ["MemoryStorage.read"]}, {"path": "tinydb/table.py", "new": false, "symbols": ["Table._update_table"]}]}
```
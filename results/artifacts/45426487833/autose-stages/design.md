## Summary
Make `MemoryStorage` writes atomic by having `read()` return a deep copy of the in-memory data. This ensures mutations during `Table._update_table()` affect only the copy; on exception the original `self.memory` is untouched, and the query cache (cleared only after successful `write()`) stays consistent with committed data—matching `JSONStorage` behavior.

## Root cause or approach
`MemoryStorage.read()` returns the live `self.memory` dict. `Table._update_table()` reads this dict, shallow-copies the table layer but shares the document objects, mutates them in the updater, then calls `write()`. If the updater raises (e.g., `delete('tmp')` on a document lacking `tmp`), the documents inside `self.memory` are already mutated, but `write()` is never reached so the query cache isn't cleared. Subsequent reads see the partial mutation while the cache still holds pre-failure results.

`JSONStorage` avoids this because `read()` deserializes fresh objects from disk; mutations hit only the in-memory copy, and a failed updater never calls `write()`, leaving the file (and next `read()`) unchanged.

Fix: `MemoryStorage.read()` returns `copy.deepcopy(self.memory)` (or `None`). The updater mutates the copy; `write()` atomically replaces `self.memory` with that copy. On exception the original data survives, `clear_cache()` isn't called, and the cache remains valid.

## Files and functions to change

| file | function/class | change |
|------|----------------|--------|
| tinydb/storages.py | MemoryStorage.read | Return a deep copy of `self.memory` (or `None`) instead of the live object. |
| tinydb/storages.py | MemoryStorage.__init__ | Add `import copy` at module top; no logic change needed. |

## Step-by-step plan
1. Add `import copy` to the imports in `tinydb/storages.py`.
2. Modify `MemoryStorage.read()` to return `copy.deepcopy(self.memory)` when `self.memory` is not `None`, otherwise `None`.
3. Verify `MemoryStorage.write()` simply assigns `self.memory = data` (already correct—the `data` passed is the mutated deep copy from `_update_table`).
4. Run the existing test suite to confirm AC-5 (no regressions).
5. The acceptance criteria AC-1 through AC-4 are satisfied by the atomic read-copy-write cycle: failed updaters leave `self.memory` and the query cache untouched; successful updaters replace `self.memory` and trigger `clear_cache()`.

## Architecture constraints
- **C1**: `MemoryStorage` still implements `read()`/`write(data)` on the whole database dict; `read()` returns `None` for empty store.
- **C3**: Table changes remain exclusively in `Table._update_table()`; no direct `storage.write()` calls added.
- **C5**: No new dependencies; `copy` is in the standard library. No upward imports introduced.

## Risks
- **Performance**: Deep-copying on every `read()` adds overhead for large in-memory databases. Acceptable for `MemoryStorage`'s typical use case (small datasets, testing).
- **CachingMiddleware interaction**: Middleware caches the deep copy returned by `read()`; its periodic `flush()` still calls `write()` correctly. No behavioral change.
- **Mutation of cached `Document` objects**: Unchanged—callers are already warned not to mutate search results.

```json
{"files": [{"path": "tinydb/storages.py", "new": false, "symbols": ["MemoryStorage.read"]}]}
```
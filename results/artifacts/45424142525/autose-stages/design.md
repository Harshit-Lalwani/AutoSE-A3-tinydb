## Summary
Add an `append` operation to `tinydb/operations.py` and modify `tinydb/table.py` to catch exceptions per document during updates (skip-fail behavior), so that `TypeError` raised for non-list fields doesn't propagate out of `update()`.

## Root cause or approach
The previous design only added the `append` operation to `operations.py` but assumed `Table.update()` already had skip-fail exception handling (Assumption A-2). However, the actual code in `table.py` shows no try/except around `perform_update()` calls — exceptions propagate out of `update()`, causing AC-6 to fail.

The fix requires two changes:
1. **`tinydb/operations.py`**: Add the `append(field, value)` factory function following the existing pattern (returns a `transform(doc)` callable that mutates the document in place).
2. **`tinydb/table.py`**: Wrap each `perform_update(table, doc_id)` call in a try/except block inside the `updater` functions (for `doc_ids`, `cond`, and unconditional paths) to catch exceptions, skip the failing document, and continue with the next one. This implements the skip-fail behavior required by AC-6.

## Files and functions to change

| file | function/class | change |
|------|----------------|--------|
| tinydb/operations.py | append (new) | Add factory function `append(field: str, value: Any) -> Callable[[MutableMapping], None]` returning a transform that appends to list, creates `[value]` if missing, raises `TypeError` if field exists but is not a list |
| tinydb/table.py | Table.update | In all three `updater` functions (doc_ids, cond, unconditional), wrap `perform_update(table, doc_id)` in `try/except Exception` to catch and ignore per-document failures, continuing the loop |

## Step-by-step plan
1. Open `tinydb/operations.py`, add `append` function after `decrement`:
   ```python
   def append(field: str, value: Any) -> Callable[[MutableMapping], None]:
       def transform(doc: MutableMapping):
           if field not in doc:
               doc[field] = [value]
           elif isinstance(doc[field], list):
               doc[field].append(value)
           else:
               raise TypeError(f"Field '{field}' is not a list")
       return transform
   ```
2. Open `tinydb/table.py`, locate the three `updater` functions inside `update()` (lines ~468, ~489, ~517).
3. In each `updater`, change:
   ```python
   for doc_id in ...:
       ...
       perform_update(table, doc_id)
   ```
   to:
   ```python
   for doc_id in ...:
       ...
       try:
           perform_update(table, doc_id)
       except Exception:
           # Skip-fail: ignore errors on individual documents, continue with next
           pass
   ```
4. Ensure the `updated_ids` list only includes successfully updated documents (move `updated_ids.append(doc_id)` inside the try block, after successful `perform_update`).

## Architecture constraints
- **C5 (Dependencies point downward only)**: `operations.py` only imports from stdlib (`collections.abc`, `typing`). The change adds no new imports. `table.py` already imports `Callable` from `collections.abc`; the change uses only stdlib exceptions. Both respect C5.
- **C3 (Table changes go only through `Table._update_table()`)**: The change is inside `update()` which calls `_update_table()` — no violation.
- **C1, C2, C4**: Not applicable — changes are confined to `operations.py` (leaf) and `table.py` (core table logic).
- **AC-7**: Satisfied — no imports outside stdlib and tinydb itself.

## Risks
- **Exception breadth**: Catching `Exception` (not just `TypeError`) is intentional per AC-6 ("no exception propagates out of update()"). This matches the skip-fail assumption.
- **updated_ids accuracy**: Moving `updated_ids.append(doc_id)` inside the try block ensures only successfully updated documents are reported, which is correct behavior.
- **Performance**: Minimal overhead — one try/except per document update, only on the update path.
- **Backward compatibility**: Existing operations (`add`, `set`, etc.) don't raise on valid documents; this change only affects behavior when an operation *does* raise (previously it would abort the entire update, now it skips one document).

```json
{"files": [{"path": "tinydb/operations.py", "new": false, "symbols": ["append"]}, {"path": "tinydb/table.py", "new": false, "symbols": ["Table.update"]}]}
```
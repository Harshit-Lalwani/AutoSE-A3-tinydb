Now I have a thorough understanding of the codebase. Let me create the design document.

## Summary

Add an `append` operation to `tinydb/operations.py` that appends a value to a list field in matching documents. The operation creates the field as a single-element list if missing, and raises `TypeError` if the field exists but is not a list. The implementation follows the existing pattern of operation factories returning a `transform(doc)` callable.

## Root cause or approach

The existing operations (`add`, `subtract`, `increment`, etc.) are simple factory functions that return a `transform(doc: MutableMapping) -> None` callable. The `append` operation needs to:
1. Check if the field exists in the document
2. If missing: create it as `[value]`
3. If present and is a list: append `value` to it
4. If present but not a list: raise `TypeError`

The fail-fast semantics (AC-7) are already the default behavior of `Table.update()` - when an exception is raised during the updater loop, the exception propagates out of `_update_table()` after the storage write has already occurred for documents processed so far. This matches the acceptance criteria.

## Files and functions to change

| file | function/class | change |
|------|----------------|--------|
| `tinydb/operations.py` | `append` (new function) | Add new `append(field: str, value: Any) -> Callable[[MutableMapping], None]` factory function |

## Step-by-step plan

1. **Add `append` function to `tinydb/operations.py`**:
   - Import `Any` from typing (already imported)
   - Create `append(field: str, value: Any)` function that returns a `transform(doc)` closure
   - In `transform`:
     - If `field not in doc`: set `doc[field] = [value]`
     - Elif `isinstance(doc[field], list)`: `doc[field].append(value)`
     - Else: raise `TypeError(f"Field '{field}' is not a list")`
   - Add docstring following existing style

2. **Export `append` from `tinydb/operations.py`** (add to module's public API)

3. **Write tests** (not part of this design, but will be needed):
   - Test AC-1: import works
   - Test AC-2: returns callable usable with `db.update`
   - Test AC-3: creates field as single-element list when missing
   - Test AC-4: appends to existing list
   - Test AC-5: raises TypeError for non-list field
   - Test AC-6: works with multiple documents
   - Test AC-7: fail-fast semantics (first error aborts, earlier docs modified)
   - Test AC-8: no new dependencies

## Architecture constraints

| Constraint | Applies? | How the plan respects it |
|------------|----------|--------------------------|
| C1: New storages subclass `Storage` | No | Not modifying storages |
| C2: Query hash values | No | Not modifying queries |
| C3: Table changes through `_update_table()` | Yes | Operation works through existing `Table.update()` which uses `_update_table()` |
| C4: Middlewares transparent | Yes | Operation is a simple callable, middlewares don't need to know about it |
| C5: Dependencies point downward | Yes | `operations.py` doesn't import `table.py` or `database.py`; new function follows same pattern |

## Risks

1. **Fail-fast behavior with partial writes**: The current `Table.update()` implementation writes all processed documents to storage before an exception propagates. This means if `append` raises `TypeError` on the 2nd of 3 matching documents, the 1st document's change is persisted. This matches AC-7 but users should be aware.

2. **No nested field support**: Per A-3, only simple field names are supported (e.g., `'tags'`, not `'tags.0'` or `'nested.field'`). This is consistent with existing operations.

3. **TypeError message**: The exact error message format should be clear but doesn't need to match any specific format since it's not specified in AC.

```json
{"files": [{"path": "tinydb/operations.py", "new": false, "symbols": ["append"]}]}
```
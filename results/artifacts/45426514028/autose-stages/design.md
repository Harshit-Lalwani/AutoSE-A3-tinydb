The design document is complete. Here's the final answer:

## Summary
Add an `append` operation to `tinydb.operations` that appends a value to a list field. The operation creates the field as a single-element list if missing, and raises `TypeError` if the field exists but is not a list.

## Root cause or approach
The `operations.py` module provides factory functions that return callable transformers (`transform(doc)`) for use with `Table.update()`. Existing operations (`add`, `subtract`, `set`, etc.) follow a simple pattern: they are functions taking `(field, value)` that return a closure mutating the document in place.

The new `append` operation needs to:
1. Check if the field exists in the document
2. If missing: create it as a single-element list `[value]`
3. If present: verify it's a list, then append `value`
4. If present but not a list: raise `TypeError`

This follows the same protocol as existing operations (AC-7): a factory function returning a `Callable[[MutableMapping], None]`.

## Files and functions to change

| File | Function/Class | Change |
|------|----------------|--------|
| `tinydb/operations.py` | `append` (new function) | Add new factory function `append(field, value)` returning a transform that appends `value` to `doc[field]` (creating as list if missing, raising TypeError if not a list) |
| `tinydb/operations.py` | `__all__` | Add `'append'` to the exported symbols |

## Step-by-step plan

1. **Add the `append` function to `tinydb/operations.py`**:
   - Define `append(field: str, value: Any) -> Callable[[MutableMapping], None]`
   - The returned `transform(doc)` will:
     - If `field not in doc`: set `doc[field] = [value]`
     - Elif `isinstance(doc[field], list)`: `doc[field].append(value)`
     - Else: raise `TypeError(f"Field '{field}' is not a list")`
   - Add `'append'` to `__all__`

2. **Write tests in `tests/test_operations.py`** (not part of this design, but implied):
   - Test appending to existing list
   - Test creating new list on missing field
   - Test TypeError on non-list field
   - Test fail-fast behavior on mixed documents (first succeeds, second fails)

## Architecture constraints

| Constraint | Applies? | How the plan respects it |
|------------|----------|--------------------------|
| C1: New storages subclass `Storage` | No | Operations don't involve storage |
| C2: Query hash values | No | Operations don't affect queries |
| C3: Table changes through `_update_table` | Yes | `append` is used via `Table.update()` which already uses `_update_table` |
| C4: Middlewares transparent | No | Operations don't involve middlewares |
| C5: Dependencies point downward | Yes | `operations.py` imports only from stdlib (`collections.abc`, `typing`); no imports from `table.py` or `database.py` |

## Risks

1. **Fail-fast behavior (AC-5, A-2)**: If `db.update(append(...), query)` matches multiple documents and one fails with `TypeError`, the exception propagates immediately. Documents already updated remain modified. This matches the existing behavior of other operations (e.g., `add` on incompatible types).

2. **TypeError message**: The exact message isn't specified in AC-4; we'll use a clear message like `f"Field '{field}' is not a list"`.

3. **Concurrency**: Not applicable; TinyDB is single-threaded.

4. **Mutation during iteration**: The transform mutates the document in place, which is the expected pattern (same as `add`, `set`, etc.).

```json
{"files": [{"path": "tinydb/operations.py", "new": false, "symbols": ["append"]}]}
```
Now I have a complete understanding. Let me write the design document.

## Summary
Add an `append` operation class to `tinydb/operations.py` that appends a value to a list field, creates the field as a single-element list if absent, and raises `TypeError` if the field exists but is not a list.

## Root cause or approach
The `tinydb/operations.py` module currently provides functions (`delete`, `add`, `subtract`, `set`, `increment`, `decrement`) that return a `transform` callable. The acceptance criteria specify that `append` should be a **class** with `__init__(field, value)` and `__call__(document)` following the same pattern. The `__call__` method will:
1. Check if the field exists in the document
2. If not, create it as `[value]`
3. If it exists and is a list, append `value` to it
4. If it exists but is not a list, raise `TypeError(f"Field '{field}' is not a list")`
5. Return the modified document (matching AC-6)

The existing `Table.update()` mechanism calls the operation with the document and ignores the return value, so returning the document is compatible.

## Files and functions to change

| file | function/class | change |
|------|----------------|--------|
| tinydb/operations.py | append (new class) | Add new `append` class with `__init__(self, field, value)` and `__call__(self, document)` |

## Step-by-step plan
1. Open `tinydb/operations.py`
2. Add the `append` class after the existing operations (e.g., after `decrement`)
3. Implement `__init__` to store `field` and `value`
4. Implement `__call__` with the logic described above
5. Verify the implementation works by running the existing tests and manual tests matching AC-1 through AC-5

## Architecture constraints
- **C5 (Dependencies point downward)**: `operations.py` must not import `table.py` or `database.py`. The new class only uses built-in types, so this constraint is satisfied.
- **C3 (Table changes through `_update_table`)**: The operation is called from `Table.update()` which uses `_update_table`, so this is respected.
- The implementation follows the existing pattern of operations being callables that mutate documents in place (the return value is not used by the update mechanism, but we return the document per AC-6).

## Risks
- **Low risk**: The change is isolated to `operations.py` and follows existing patterns.
- **Compatibility**: The operation must be a class (per AC-1), not a function like the others. This is a slight deviation but is explicitly required by the acceptance criteria.
- **Error message**: Must match the format in Assumption A-3: `TypeError(f"Field '{field}' is not a list")`.

```json
{"files": [{"path": "tinydb/operations.py", "new": false, "symbols": ["append"]}]}
```
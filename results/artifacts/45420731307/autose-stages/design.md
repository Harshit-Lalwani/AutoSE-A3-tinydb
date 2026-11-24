## Summary
Add an `append` operation to `tinydb.operations` that appends a value to a list field, creating the field if missing, raising `TypeError` if the field exists but is not a list, and supporting dot-notation paths for nested fields.

## Root cause or approach
The `tinydb/operations.py` module provides factory functions (`delete`, `add`, `subtract`, `set`, `increment`, `decrement`) that return a `transform(doc)` callable mutating the document in place. The new `append` operation follows this exact pattern. It must:
1. Parse dot-notation paths (e.g., `'meta.tags'`) to navigate nested dicts
2. Create intermediate dicts as needed
3. Create the target field as a new list `[value]` if missing
4. Raise `TypeError` if the target exists and is not a list
5. Perform a functional update (create new list) per Assumption A-1: `current[field] = current[field] + [value]`

The implementation mirrors how `Query._generate_test` resolves paths, but as a mutating transform function compatible with `Table.update()`.

## Files and functions to change

| file | function/class | change |
|------|----------------|--------|
| tinydb/operations.py | append (new) | Add `append(field: str, value: Any) -> Callable[[MutableMapping], None]` factory function |

## Step-by-step plan
1. Open `tinydb/operations.py`
2. Add `from typing import Any` to imports (if not present; `Any` is already used in `set`)
3. Implement `append(field: str, value: Any)` function that:
   - Splits `field` on `'.'` to get path parts
   - Walks the document, creating missing intermediate dicts
   - At the final key: if missing, set to `[value]`; if present and not a list, raise `TypeError`; if a list, replace with `old_list + [value]` (functional update)
   - Returns the `transform` callable
4. Export `append` in `__all__` (if module uses `__all__`; it doesn't currently, so just define the function)
5. Verify the change works by running existing tests and mentally checking against AC-1 through AC-9

## Architecture constraints
- **C5 (Dependencies point downward)**: `operations.py` imports only stdlib and `typing`; it does not import `table.py`, `database.py`, or `queries.py`. The change respects this.
- **C3 (Table changes through `_update_table`)**: The operation is a pure transform callable; `Table.update` handles atomicity and cache invalidation. No change needed.
- **C1, C2, C4**: Not directly affected (no storage, query, or middleware changes).

## Risks
- **Dot-notation collision**: If a field name literally contains `.` (e.g., `{'a.b': 1}`), the path split will misinterpret it. This matches Query's behavior (Query also uses `.` for nesting), so it's consistent.
- **TypeError on non-dict intermediate**: If an intermediate path component exists but is not a dict (e.g., `{'meta': 'not-a-dict'}`), the transform will raise `TypeError` when trying to assign `current[part] = {}`. This is acceptable—mirrors Query's behavior of returning `False` on `TypeError` during path resolution.
- **Concurrency**: AC-8 requires atomic replacement. `Table._update_table` reads the whole table, applies all transforms, then writes back, so no intermediate state is visible. The operation itself is a pure function, so this holds.

```json
{"files": [{"path": "tinydb/operations.py", "new": false, "symbols": ["append"]}]}
```

## Why this stage stopped

- tinydb/operations.py: symbol 'append' not found (mark it under 'new_symbols' if it is new)
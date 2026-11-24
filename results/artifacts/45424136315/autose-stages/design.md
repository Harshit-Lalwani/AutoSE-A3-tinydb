## Summary
Make `Table.update()` and `Table.remove()` accept string document IDs in `doc_ids` (e.g., `['1', '2']`) by converting them to `int` (the default `document_id_class`), matching the conversion behavior that `Table.get()` already performs for valid numeric strings. Non-existent IDs are silently skipped. Invalid strings (e.g., `'abc'`) raise `ValueError` from `int()` conversion. Return values remain lists of `int` IDs.

## Root cause or approach
The `get()` method handles string IDs by converting them to strings and looking up in the raw storage table (which has string keys). However, `update()` and `remove()` operate on the converted table inside `_update_table`, where keys are already transformed to `document_id_class` (`int`). When `doc_ids` contains strings like `'1'`, the membership check `doc_id in table` fails because `table` has integer keys. The fix is to convert each `doc_id` in `requested_ids` to `self.document_id_class` before the membership check. Invalid strings will naturally raise `ValueError` from `int()` conversion.

## Files and functions to change

| file | function/class | change |
|------|----------------|--------|
| tinydb/table.py | Table.update | In the `doc_ids` branch, convert each `doc_id` in `requested_ids` to `self.document_id_class` before checking membership in `table`; catch `ValueError` from invalid strings and re-raise |
| tinydb/table.py | Table.remove | Same conversion and error handling as `update` |

## Step-by-step plan
1. In `Table.update()`, modify the `doc_ids` branch: before the `updater` closure, convert `requested_ids` to a list of `self.document_id_class` values, catching `ValueError` and re-raising with a clear message. Use the converted list for membership checks and updates.
2. In `Table.remove()`, apply the identical conversion logic in its `doc_ids` branch.
3. Ensure the returned `updated_ids`/`removed_ids` lists contain `int` values (the converted form).
4. Run the test suite to verify AC-1 through AC-8.

## Architecture constraints
- **C3 (Table changes go only through `Table._update_table()`)**: The change stays inside the `updater` closures passed to `_update_table`; no direct storage writes.
- **C5 (Dependencies point downward)**: `table.py` already imports `queries.py` and `utils.py`; no new imports needed.
- **C1, C2, C4**: Not affected (no storage, query, or middleware changes).

## Risks
- **Behavioral mismatch with `get()`**: `get(doc_id='abc')` currently returns `None` (no error), while this change makes `update/remove` raise `ValueError` for `'abc'`. AC-5 explicitly requires the `ValueError`, so this is intentional per spec.
- **Mixed int/str lists**: The conversion handles mixed lists (AC-6) because each element is converted individually.
- **Custom `document_id_class`**: Using `self.document_id_class` respects subclasses that override the ID type.

```json
{"files": [{"path": "tinydb/table.py", "new": false, "symbols": ["Table.update", "Table.remove"]}]}
```

## Why this stage stopped

Stage `design`: token budget exhausted: used 2,480,004 of 2,500,000, next call could need up to 25,087.

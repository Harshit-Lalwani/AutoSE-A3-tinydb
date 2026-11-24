## Summary
The `Table.update()` and `Table.remove()` methods don't accept numeric string document IDs (e.g., `'1'`, `'2'`), while `Table.get()` and `Table.contains()` do. The fix is to convert `doc_ids` to integers at the start of both methods using `self.document_id_class()`, matching the existing behavior of `get()`/`contains()`.

## Root cause or approach
In `_update_table()`, the storage keys (strings) are converted to `document_id_class` (integers) before the updater function runs. However, `update(doc_ids=...)` and `remove(doc_ids=...)` pass the raw `doc_ids` to the updater, which checks `doc_id in table` where `table` now has integer keys. String IDs like `'1'` never match integer key `1`.

`Table.get(doc_ids=...)` works because it converts IDs to strings for lookup against the raw storage keys (line 377: `doc_ids_set = set(str(doc_id) for doc_id in doc_ids)`). The fix is to do the opposite in `update`/`remove`: convert input IDs to `document_id_class` (integers) upfront, before the updater runs.

Non-numeric strings (e.g., `'abc'`, `''`) will raise `ValueError` from `int()`, matching assumption A-1 and the behavior of `get()`/`contains()` when passed invalid types.

## Files and functions to change

| file | function/class | change |
|------|----------------|--------|
| tinydb/table.py | Table.update | Convert `doc_ids` to `document_id_class` at method start when `doc_ids is not None` |
| tinydb/table.py | Table.remove | Convert `doc_ids` to `document_id_class` at method start when `doc_ids is not None` |

## Step-by-step plan
1. In `Table.update()`, after validating `doc_ids is not None`, convert the iterable to a list of `self.document_id_class(doc_id)` for each `doc_id`. This replaces `requested_ids = list(doc_ids)`.
2. In `Table.remove()`, same conversion: replace `requested_ids = list(doc_ids)` with converted list.
3. The rest of the logic (filtering existing IDs, updating/removing, returning integer IDs) remains unchanged.
4. The conversion will naturally raise `ValueError` for non-numeric strings, satisfying A-1.

## Architecture constraints
- **C3**: Table changes go only through `Table._update_table()`. The plan respects this—we only preprocess input before calling `_update_table()`.
- **C5**: Dependencies point downward only. We only modify `table.py`, which already imports from `queries`, `storages`, `utils`. No new imports needed.

## Risks
- **Low risk**: Change is minimal, localized to two methods, and mirrors existing conversion pattern in `get()`.
- **Type hints**: The `doc_ids` parameter is annotated as `Optional[Iterable[int]]`; accepting strings widens the accepted type at runtime but the return type `list[int]` is preserved.
- **Backward compatibility**: Integer IDs continue to work identically (AC-5). Only string IDs are newly supported.

```json
{"files": [{"path": "tinydb/table.py", "new": false, "symbols": ["Table.update", "Table.remove"]}]}
```
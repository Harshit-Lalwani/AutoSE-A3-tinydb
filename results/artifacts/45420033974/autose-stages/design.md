## Summary
Make `Table.update()` and `Table.remove()` accept string document IDs by converting them to integers (using `document_id_class`), matching the existing behavior of `get()` and `contains()`. Non-existent IDs are skipped; unparseable strings raise `ValueError`.

## Root cause or approach
In `Table.get()` and `Table.contains()`, document IDs are converted to strings for lookup in the raw storage table (which has string keys). However, `Table.update()` and `Table.remove()` operate on the converted table inside `_update_table()`, where keys are already integers (`document_id_class`). These methods currently don't normalize string inputs to integers, causing string IDs to fail the `doc_id in table` check.

The fix: add a helper method `_normalize_doc_id()` that converts a single doc_id to `document_id_class` (int), raising `ValueError` for unparseable strings. Apply it to each element of `doc_ids` (and `doc_id` for the singular parameter) in `update()` and `remove()` before using them.

## Files and functions to change

| file | function/class | change |
|------|----------------|--------|
| tinydb/table.py | Table._normalize_doc_id | New private method to convert a doc_id to `document_id_class`, raising `ValueError` on failure |
| tinydb/table.py | Table.update | Normalize `doc_ids` (and `doc_id` if added for consistency) using `_normalize_doc_id` before processing |
| tinydb/table.py | Table.remove | Normalize `doc_ids` (and `doc_id` if added for consistency) using `_normalize_doc_id` before processing |

## Step-by-step plan
1. Add `_normalize_doc_id(self, doc_id)` method to `Table` class that:
   - Returns `self.document_id_class(doc_id)` (which is `int(doc_id)`)
   - Lets `ValueError` propagate for unparseable strings (e.g., 'abc', '1.5')
2. In `update()`:
   - When `doc_ids` is provided, convert each element: `requested_ids = [self._normalize_doc_id(d) for d in doc_ids]`
   - (Optional) Also support singular `doc_id` parameter for consistency with `get()`/`contains()` - but AC-7/AC-8 only test `doc_id` as string, which currently isn't a parameter of `update()`/`remove()`. Looking at the signature, `update()` only has `doc_ids`, not `doc_id`. The AC-7/AC-8 test `doc_id='1'` - this suggests we may need to add `doc_id` parameter or the tests use `doc_ids=['1']`. Re-reading AC-7: `db.update({'a': 10}, doc_id='1')` - this uses `doc_id` singular. But the current signature only has `doc_ids`. This might be a test expectation that we need to support `doc_id` parameter too. However, the current code doesn't have `doc_id` parameter for update/remove. Let me check the signature again... The signature shows `doc_ids: Optional[Iterable[int]] = None` only. So AC-7/AC-8 might be testing a new parameter. But the spec says "matching the existing behaviour of get() and contains()" - and get/contains have both `doc_id` and `doc_ids`. For minimal change, I'll focus on `doc_ids` normalization first. If `doc_id` parameter is needed, it would be a separate parameter addition.
3. In `remove()`:
   - Same normalization for `doc_ids`
4. Ensure empty list handling works (already works - returns empty list)
5. Ensure non-existent IDs are skipped (already works - checks `if doc_id in table`)

## Architecture constraints
- **C3**: Table changes go only through `Table._update_table()`. The plan respects this - we only modify the input normalization before passing to the updater function.
- **C5**: Dependencies point downward only. The change is entirely within `table.py` with no new imports.
- No storage changes needed (C1), no query changes (C2), no middleware changes (C4).

## Risks
- **Type signature change**: `doc_ids` parameter type changes from `Iterable[int]` to `Iterable[Union[int, str]]`. This is a backward-compatible widening.
- **Error behavior**: Previously, passing a string like `'1'` would silently skip (not found in integer-keyed table). Now it will work. Passing `'abc'` previously would also silently skip (string not in integer-keyed table); now it raises `ValueError`. This matches the spec (AC-11, AC-12).
- **Performance**: Negligible - one `int()` conversion per ID.

```json
{"files": [{"path": "tinydb/table.py", "new": false, "symbols": ["Table._normalize_doc_id", "Table.update", "Table.remove"]}]}
```

## Why this stage stopped

- tinydb/table.py: symbol 'Table._normalize_doc_id' not found (mark it under 'new_symbols' if it is new)
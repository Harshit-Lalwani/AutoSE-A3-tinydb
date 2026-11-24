## Summary
Make `TinyDB.update()` and `TinyDB.remove()` accept string document IDs (both single `doc_id` and `doc_ids` list) by converting valid integer strings to `int`, matching the existing behaviour of `get()` and `contains()`. Non-existent and unparsable IDs are skipped silently; return value remains `list[int]`.

## Root cause or approach
The `get()` and `contains()` methods already handle string IDs by converting them with `str(doc_id)` when looking up in the internal table (which stores keys as strings in storage). However, `update()` and `remove()` methods in `table.py` only accept `int` for `doc_ids` and compare directly against the table dict keys (which are `int` after `_update_table` converts them from strings), so string IDs fail to match.

The fix is to add a helper that normalizes incoming IDs: attempt `int(id)` for each, keep only those that parse successfully, and silently drop the rest. Apply this normalization at the entry of `update()` and `remove()` for both `doc_id` and `doc_ids` parameters. The internal logic (which works with `int` IDs) remains unchanged.

## Files and functions to change

| file | function/class | change |
|------|----------------|--------|
| tinydb/table.py | `_normalize_doc_ids` (new helper) | Add a private static method that takes a single ID or iterable of IDs (int or str), attempts `int()` conversion, returns list of valid int IDs (skipping unparsable/non-int silently) |
| tinydb/table.py | `update` | Change signature to accept `doc_id: Optional[Union[int, str]] = None` and `doc_ids: Optional[Iterable[Union[int, str]]] = None`; normalize IDs at start of each branch |
| tinydb/table.py | `remove` | Change signature to accept `doc_id: Optional[Union[int, str]] = None` and `doc_ids: Optional[Iterable[Union[int, str]]] = None`; normalize IDs at start of each branch |

## Step-by-step plan
1. Add `_normalize_doc_ids` static method to `Table` class that accepts `Union[int, str, Iterable[Union[int, str]]]` and returns `list[int]` of successfully parsed IDs.
2. Modify `update()` signature to accept `doc_id: Optional[Union[int, str]] = None` and `doc_ids: Optional[Iterable[Union[int, str]]] = None`.
3. In `update()`, if `doc_id` is provided, normalize it and treat as `doc_ids=[normalized_id]`; if `doc_ids` provided, normalize the whole iterable. Then proceed with existing logic using the normalized `list[int]`.
4. Modify `remove()` signature similarly and apply same normalization logic.
5. Update docstrings to document that string IDs are accepted and converted.

## Architecture constraints
- **C3 (Table changes go only through `Table._update_table()`)**: The plan respects this—normalization happens before calling `_update_table`, and the internal table dict still uses `int` keys.
- **C5 (Dependencies point downward only)**: The change is confined to `table.py`; no new imports from `database.py` or other upward dependencies.
- **C1, C2, C4**: Not affected—no storage, query, or middleware changes.

## Risks
- **Type hint compatibility**: Changing parameter types from `int` to `Union[int, str]` is backward-compatible (existing `int` calls still work). Must ensure `Iterable[Union[int, str]]` doesn't break callers passing `list[int]`.
- **Silent skipping**: Unparsable strings (`'abc'`, `''`, `'1.5'`) are skipped silently per acceptance criteria. This matches `get()`/`contains()` behaviour for non-existent IDs but could hide typos. Accepted per A-1.
- **Single `doc_id` parameter**: Adding `doc_id` to `update()`/`remove()` matches `contains()` API (A-2). Must ensure it doesn't conflict with existing `cond` parameter (mutually exclusive with `doc_ids`).
- **Atomicity**: Existing code filters `requested_ids` against `table` keys inside the updater for atomicity. Normalization happens before, so only valid int IDs reach the atomic check—correct.
- **Mypy errors**: The previous attempt had issues with function naming conflicts and incorrect `get` calls. The new plan avoids naming helpers `get` and ensures `contains` continues to call the existing `get` method correctly.

```json
{"files": [{"path": "tinydb/table.py", "new": false, "symbols": ["Table._normalize_doc_ids", "Table.update", "Table.remove"]}]}
```
Now I have a clear understanding of the codebase. Let me write the design.

## Summary
Make `Table.update()` and `Table.remove()` accept document IDs as strings (parsable by `int()`) like `get()`/`contains()` do, converting them to integers internally. Invalid strings raise `ValueError`; non-existent IDs are skipped; return type remains `List[int]`.

## Root cause or approach
The `get()` and `contains()` methods already accept string IDs because they convert inputs to strings for table lookup (storage keys are strings). However, `update()` and `remove()` with `doc_ids` parameter expect integers and directly check `doc_id in table` where `table` has integer keys (converted by `_update_table`). Since table keys are integers, integer IDs work but string IDs don't match.

The fix: add a private helper method `_normalize_doc_ids()` that converts an iterable of `int | str` to a list of `int`, using `int()` for string conversion (raising `ValueError` on invalid strings). Apply this at the start of `update()` and `remove()` when `doc_ids` is provided. Update type hints to accept `Iterable[Union[int, str]]`.

## Files and functions to change

| file | function/class | change |
|------|----------------|--------|
| tinydb/table.py | `Table._normalize_doc_ids` (new) | Add private helper method to convert `Iterable[Union[int, str]]` to `list[int]` using `int()` |
| tinydb/table.py | `Table.update` | Call `_normalize_doc_ids(doc_ids)` at start of `doc_ids` branch; update type hint to `Optional[Iterable[Union[int, str]]]`; update docstring |
| tinydb/table.py | `Table.remove` | Call `_normalize_doc_ids(doc_ids)` at start of `doc_ids` branch; update type hint to `Optional[Iterable[Union[int, str]]]`; update docstring |

## Step-by-step plan
1. Add `_normalize_doc_ids(self, doc_ids: Iterable[Union[int, str]]) -> list[int]` method that iterates input, calls `int(x)` on each element (which accepts `int` and valid numeric strings, raises `ValueError` otherwise), returns list of ints.
2. In `update()`: change `doc_ids` type hint from `Optional[Iterable[int]]` to `Optional[Iterable[Union[int, str]]]`; at the start of the `if doc_ids is not None:` block, replace `requested_ids = list(doc_ids)` with `requested_ids = self._normalize_doc_ids(doc_ids)`.
3. In `remove()`: same changes as `update()`.
4. Update docstrings for `update()` and `remove()` to document that `doc_ids` accepts strings parsable by `int()`.

## Architecture constraints
- **C1 (No runtime deps)**: Uses only stdlib `int()`, no new dependencies.
- **C2 (Storage agnostic)**: Change is in Table layer only; storage sees same integer keys.
- **C3 (Thread-safety)**: No new shared state; conversion happens before `_update_table` lock.
- **C4 (Atomic writes)**: Conversion happens before the atomic updater; no change to write semantics.
- **C5 (Extensibility)**: `document_id_class` remains `int`; helper uses `int()` directly (not the class) per A-1 assumption.

## Risks
- **Type hint change**: `Iterable[int]` → `Iterable[Union[int, str]]` is backward-compatible (accepts more).
- **Performance**: Negligible - single pass conversion before existing logic.
- **Error messages**: `ValueError` from `int()` is clear (e.g., "invalid literal for int() with base 10: 'abc'").

```json
{"files": [{"path": "tinydb/table.py", "new": false, "symbols": ["Table._normalize_doc_ids", "Table.update", "Table.remove"]}]}
```
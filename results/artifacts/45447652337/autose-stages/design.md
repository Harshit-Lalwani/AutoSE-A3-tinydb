Now I have a complete understanding of the codebase. Let me create the design document.

## Summary

The issue is an API inconsistency: `Table.get()` and `Table.contains()` accept both integer and string document IDs (coercing strings to integers internally), but `Table.update()` and `Table.remove()` only accept integer IDs via the `doc_ids` parameter. The fix adds a `doc_id` parameter (for single ID) to both methods and adds string-to-integer coercion for both `doc_id` and `doc_ids` parameters, matching `get()`'s behavior.

## Root cause or approach

**Root cause**: In `Table.update()` and `Table.remove()`, the `doc_ids` parameter is used directly without coercion. The internal table representation (after `_update_table` conversion) uses integer keys, but the methods don't convert string inputs to integers. Meanwhile, `get()` explicitly converts `doc_id` to string for storage lookup (`str(doc_id)`), which works because storage keys are strings.

**Approach**: 
1. Add `doc_id: Optional[Union[int, str]] = None` parameter to both `update()` and `remove()`
2. Add a helper method `_coerce_doc_id()` to convert string IDs to integers, raising `ValueError` for non-coercible strings
3. Apply coercion to both `doc_id` and each element of `doc_ids` before use
4. Ensure returned IDs are integers (they already are since internal table uses int keys)

## Files and functions to change

| file | function/class | change |
|------|----------------|--------|
| tinydb/table.py | Table._coerce_doc_id (new) | New private helper method to coerce single ID (int or str) to int, raising ValueError on failure |
| tinydb/table.py | Table.update | Add `doc_id` parameter; update `doc_ids` type to `Optional[Iterable[Union[int, str]]]`; add coercion for both parameters |
| tinydb/table.py | Table.remove | Add `doc_id` parameter; update `doc_ids` type to `Optional[Iterable[Union[int, str]]]`; add coercion for both parameters |

## Step-by-step plan

1. **Add `_coerce_doc_id` helper method** in `Table` class (after `_read_table` method, around line 230):
   - Accept `Union[int, str]`
   - If int, return as-is (wrapped in `self.document_id_class`)
   - If str, try `int(value)`, raise `ValueError` on failure
   - Return `self.document_id_class(coerced_value)` for consistency

2. **Modify `Table.update()`**:
   - Add `doc_id: Optional[Union[int, str]] = None` parameter before `doc_ids`
   - Update type hint for `doc_ids` to `Optional[Iterable[Union[int, str]]]`
   - If `doc_id` is provided, coerce it and treat as single-element list for the existing logic
   - If `doc_ids` is provided, coerce each element using `_coerce_doc_id`
   - Maintain existing behavior for query-based and unconditional updates

3. **Modify `Table.remove()`**:
   - Add `doc_id: Optional[Union[int, str]] = None` parameter before `doc_ids`
   - Update type hint for `doc_ids` to `Optional[Iterable[Union[int, str]]]`
   - If `doc_id` is provided, coerce it and treat as single-element list for the existing logic
   - If `doc_ids` is provided, coerce each element using `_coerce_doc_id`
   - Maintain existing behavior for query-based removal

4. **Update docstrings** for both methods to document the new `doc_id` parameter and string coercion behavior

## Architecture constraints

| Constraint | Applies? | How plan respects it |
|------------|----------|---------------------|
| C1: Storages subclass `Storage` | No | No storage changes |
| C2: Query hash values | No | No query changes |
| C3: Table changes via `_update_table` | Yes | Changes only modify parameter handling before calling `_update_table`; the updater functions remain unchanged |
| C4: Middlewares transparent | No | No middleware changes |
| C5: Dependencies point downward | Yes | Only modifies `table.py`; no new imports from `database.py` or external deps |

## Risks

1. **Type hint changes**: The `doc_ids` parameter type changes from `Iterable[int]` to `Iterable[Union[int, str]]`. This is a widening of the type, so it's backward compatible for callers passing ints, but type checkers may need updates.

2. **Behavioral change for invalid strings**: Previously, passing a string like `'abc'` to `doc_ids` would likely cause a `TypeError` or `KeyError` later. Now it raises `ValueError` immediately (matching `int('abc')` behavior). This is intentional per AC-6.

3. **Atomicity**: The existing logic collects "actually updated/removed" IDs inside the updater function for atomicity. The coercion happens before the updater, so invalid IDs fail fast before any modification - correct per AC-6.

4. **Table subclassing**: If users subclass `Table` and override `update`/`remove`, they may need to update their signatures. This is a normal maintenance consideration.

```json
{"files": [{"path": "tinydb/table.py", "new": false, "symbols": ["Table._coerce_doc_id", "Table.update", "Table.remove"]}]}
```
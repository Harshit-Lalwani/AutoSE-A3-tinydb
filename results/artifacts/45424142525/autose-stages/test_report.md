# Test report (issue #4, stages, attempt 2)

**Result:** FAIL

| AC | Test | With change | On `main` |
|---|---|---|---|
| AC-1 | `test_ac1_append_is_importable_and_callable` | passed | not run |
| AC-2 | `test_ac2_append_to_existing_list` | passed | not run |
| AC-3 | `test_ac3_append_creates_field_when_missing` | passed | not run |
| AC-4 | `test_ac4_append_raises_typeerror_on_non_list` | passed | not run |
| AC-5 | `test_ac5_append_works_on_table` | passed | not run |
| AC-6 | `test_ac6_append_skip_fail_on_mixed_documents` | failed | not run |
| AC-7 | `test_ac7_no_external_imports` | passed | not run |
| AC-8 | `test_ac8_test_suite_passes_on_supported_python_versions` | passed | not run |

Full suite: 239 tests, 1 failing.

Failing:
- `tests.test_autose_issue_4::test_ac6_append_skip_fail_on_mixed_documents`

## Problems

- full suite failed: 1 failing test(s)

<details><summary>pytest output (full suite)</summary>

```
.....F.................................................................. [ 30%]
........................................................................ [ 60%]
........................................................................ [ 90%]
.......................                                                  [100%]
=================================== FAILURES ===================================
_________________ test_ac6_append_skip_fail_on_mixed_documents _________________

    def test_ac6_append_skip_fail_on_mixed_documents():
        """
        AC-6: GIVEN a database with documents [{'tags': ['a']}, {'tags': 'not-a-list'}, {'tags': ['c']}]
        WHEN db.update(append('tags', 'x'), Query().tags.exists())
        THEN the first and third documents are updated to ['a', 'x'] and ['c', 'x'];
             the second document is unchanged; no exception propagates out of update()
        """
        db = TinyDB(storage=MemoryStorage)
        db.insert_multiple([
            {'tags': ['a']},
            {'tags': 'not-a-list'},
            {'tags': ['c']}
        ])
    
        # This should not raise an exception (skip-fail behavior)
>       db.update(append('tags', 'x'), Query().tags.exists())

tests/test_autose_issue_4.py:121: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
tinydb/table.py:508: in update
    self._update_table(updater)
tinydb/table.py:840: in _update_table
    updater(table)
tinydb/table.py:505: in updater
    perform_update(table, doc_id)
tinydb/table.py:452: in perform_update
    fields(table[doc_id])
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

doc = {'tags': 'not-a-list'}

    def transform(doc: MutableMapping):
        if field not in doc:
            doc[field] = [value]
        elif isinstance(doc[field], list):
            doc[field].append(value)
        else:
>           raise TypeError(f"Field '{field}' is not a list")
E           TypeError: Field 'tags' is not a list

tinydb/operations.py:91: TypeError
=========================== short test summary info ============================
FAILED tests/test_autose_issue_4.py::test_ac6_append_skip_fail_on_mixed_documents
1 failed, 238 passed in 0.51s

```
</details>

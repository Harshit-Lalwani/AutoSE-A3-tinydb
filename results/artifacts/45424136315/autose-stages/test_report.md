# Test report (issue #2, stages, attempt 1)

**Result:** FAIL

| AC | Test | With change | On `main` |
|---|---|---|---|
| AC-1 | `test_ac1_update_with_string_doc_ids` | passed | failed |
| AC-2 | `test_ac2_update_with_string_doc_ids_skipping_nonexistent` | passed | failed |
| AC-3 | `test_ac3_remove_with_string_doc_ids` | passed | failed |
| AC-4 | `test_ac4_remove_with_string_doc_ids_skipping_nonexistent` | passed | failed |
| AC-5 | `test_ac5_update_with_invalid_string_raises_valueerror` | passed | failed |
| AC-5 | `test_ac5_remove_with_invalid_string_raises_valueerror` | passed | failed |
| AC-6 | `test_ac6_update_with_mixed_int_str_doc_ids` | passed | failed |
| AC-7 | `test_ac7_get_with_string_doc_id` | failed | failed |
| AC-7 | `test_ac7_get_with_string_doc_ids_list` | passed | passed |
| AC-7 | `test_ac7_contains_with_string_doc_id` | passed | passed |
| AC-7 | `test_ac7_insert_unchanged` | passed | passed |
| AC-7 | `test_ac7_upsert_unchanged` | passed | passed |
| AC-7 | `test_ac7_update_with_int_doc_ids_still_works` | passed | passed |
| AC-7 | `test_ac7_remove_with_int_doc_ids_still_works` | passed | passed |
| AC-7 | `test_ac7_update_with_query_still_works` | passed | passed |
| AC-7 | `test_ac7_remove_with_query_still_works` | passed | passed |
| AC-7 | `test_ac7_update_all_still_works` | passed | passed |
| AC-7 | `test_ac7_get_invalid_string_raises_valueerror` | failed | failed |
| AC-7 | `test_ac7_get_invalid_string_in_list_raises_valueerror` | failed | failed |
| AC-7 | `test_ac7_contains_invalid_string_raises_valueerror` | failed | failed |
| AC-8 | (none) | missing | |

Full suite: 258 tests, 8 failing.

Failing:
- `tests.test_autose_issue_2.TestEdgeCases::test_remove_with_duplicate_string_doc_ids`
- `tests.test_autose_issue_2.TestEdgeCases::test_remove_with_negative_string_doc_id`
- `tests.test_autose_issue_2.TestEdgeCases::test_update_with_duplicate_string_doc_ids`
- `tests.test_autose_issue_2.TestEdgeCases::test_update_with_negative_string_doc_id`
- `tests.test_autose_issue_2.TestNoRegression::test_ac7_contains_invalid_string_raises_valueerror`
- `tests.test_autose_issue_2.TestNoRegression::test_ac7_get_invalid_string_in_list_raises_valueerror`
- `tests.test_autose_issue_2.TestNoRegression::test_ac7_get_invalid_string_raises_valueerror`
- `tests.test_autose_issue_2.TestNoRegression::test_ac7_get_with_string_doc_id`

## Problems

- TEST-SIDE AC-8: no test named test_ac8_*
- full suite failed: 8 failing test(s)

<details><summary>pytest output (full suite)</summary>

```
.......F.........FFF..FF....FF.......................................... [ 27%]
........................................................................ [ 55%]
........................................................................ [ 83%]
..........................................                               [100%]
=================================== FAILURES ===================================
_______________ TestNoRegression.test_ac7_get_with_string_doc_id _______________

self = <tests.test_autose_issue_2.TestNoRegression object at 0x73ac1cd85450>
db = <TinyDB tables=['_default'], tables_count=1, default_table_documents_count=3, all_tables_documents_count=['_default=3']>

    def test_ac7_get_with_string_doc_id(self, db):
        """AC-7: table.get(doc_id='1') behaves exactly as before."""
        # get with string doc_id should work (existing behavior)
        doc = db.get(doc_id='1')
        assert doc == {'a': 1}
>       assert doc.doc_id == 1
E       AssertionError: assert '1' == 1
E        +  where '1' = {'a': 1}.doc_id

tests/test_autose_issue_2.py:128: AssertionError
________ TestNoRegression.test_ac7_get_invalid_string_raises_valueerror ________

self = <tests.test_autose_issue_2.TestNoRegression object at 0x73ac1cdac9b0>
db = <TinyDB tables=['_default'], tables_count=1, default_table_documents_count=3, all_tables_documents_count=['_default=3']>

    def test_ac7_get_invalid_string_raises_valueerror(self, db):
        """AC-7: table.get(doc_id='abc') raises ValueError (existing behavior)."""
>       with pytest.raises(ValueError):
             ^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE ValueError

tests/test_autose_issue_2.py:195: Failed
____ TestNoRegression.test_ac7_get_invalid_string_in_list_raises_valueerror ____

self = <tests.test_autose_issue_2.TestNoRegression object at 0x73ac1cdde7b0>
db = <TinyDB tables=['_default'], tables_count=1, default_table_documents_count=3, all_tables_documents_count=['_default=3']>

    def test_ac7_get_invalid_string_in_list_raises_valueerror(self, db):
        """AC-7: table.get(doc_ids=['abc']) raises ValueError (existing behavior)."""
>       with pytest.raises(ValueError):
             ^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE ValueError

tests/test_autose_issue_2.py:200: Failed
_____ TestNoRegression.test_ac7_contains_invalid_string_raises_valueerror ______

self = <tests.test_autose_issue_2.TestNoRegression object at 0x73ac1cddeb30>
db = <TinyDB tables=['_default'], tables_count=1, default_table_documents_count=3, all_tables_documents_count=['_default=3']>

    def test_ac7_contains_invalid_string_raises_valueerror(self, db):
        """AC-7: table.contains(doc_id='abc') raises ValueError (existing behavior)."""
>       with pytest.raises(ValueError):
             ^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE ValueError

tests/test_autose_issue_2.py:205: Failed
____________ TestEdgeCases.test_update_with_negative_string_doc_id _____________

self = <test
... [1015 chars truncated] ...
E ValueError

tests/test_autose_issue_2.py:229: Failed
___________ TestEdgeCases.test_update_with_duplicate_string_doc_ids ____________

self = <tests.test_autose_issue_2.TestEdgeCases object at 0x73ac1cd92c50>
db = <TinyDB tables=['_default'], tables_count=1, default_table_documents_count=3, all_tables_documents_count=['_default=3']>

    def test_update_with_duplicate_string_doc_ids(self, db):
        """Update with duplicate string doc_ids updates each document once."""
        result = db.update({'a': 10}, doc_ids=['1', '1', '2'])
>       assert result == [1, 2]
E       assert [1, 1, 2] == [1, 2]
E         
E         At index 1 diff: 1 != 2
E         Left contains one more item: 2
E         Use -v to get more diff

tests/test_autose_issue_2.py:257: AssertionError
___________ TestEdgeCases.test_remove_with_duplicate_string_doc_ids ____________

self = <tests.test_autose_issue_2.TestEdgeCases object at 0x73ac1cdad5e0>
db = <TinyDB tables=['_default'], tables_count=1, default_table_documents_count=3, all_tables_documents_count=['_default=3']>

    def test_remove_with_duplicate_string_doc_ids(self, db):
        """Remove with duplicate string doc_ids removes each document once."""
>       result = db.remove(doc_ids=['1', '1', '2'])
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_autose_issue_2.py:263: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
tinydb/table.py:680: in remove
    self._update_table(updater)
tinydb/table.py:858: in _update_table
    updater(table)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

table = {2: {'a': 2}, 3: {'a': 3}}

    def updater(table: dict):
        # Filter to IDs that exist *before* performing any removals,
        # so the operation is atomic: either every existing target is
        # removed, or none is.
        removed_ids.extend(
            doc_id for doc_id in requested_ids if doc_id in table
        )
        for doc_id in removed_ids:
>           del table[doc_id]
                ^^^^^^^^^^^^^
E           KeyError: 1

tinydb/table.py:677: KeyError
=========================== short test summary info ============================
FAILED tests/test_autose_issue_2.py::TestNoRegression::test_ac7_get_with_string_doc_id
FAILED tests/test_autose_issue_2.py::TestNoRegression::test_ac7_get_invalid_string_raises_valueerror
FAILED tests/test_autose_issue_2.py::TestNoRegression::test_ac7_get_invalid_string_in_list_raises_valueerror
FAILED tests/test_autose_issue_2.py::TestNoRegression::test_ac7_contains_invalid_string_raises_valueerror
FAILED tests/test_autose_issue_2.py::TestEdgeCases::test_update_with_negative_string_doc_id
FAILED tests/test_autose_issue_2.py::TestEdgeCases::test_remove_with_negative_string_doc_id
FAILED tests/test_autose_issue_2.py::TestEdgeCases::test_update_with_duplicate_string_doc_ids
FAILED tests/test_autose_issue_2.py::TestEdgeCases::test_remove_with_duplicate_string_doc_ids
8 failed, 250 passed in 0.57s

```
</details>

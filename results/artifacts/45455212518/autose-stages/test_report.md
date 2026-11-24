# Test report (issue #1, stages, attempt 2)

**Result:** FAIL

| AC | Test | With change | On `main` |
|---|---|---|---|
| AC-1 | `test_ac1_update_atomic_on_memory_storage` | passed | failed |
| AC-2 | `test_ac2_update_atomic_on_json_storage` | failed | failed |
| AC-3 | `test_ac3_insert_multiple_atomic_on_exception` | passed | passed |
| AC-4 | `test_ac4_cache_invalidated_on_failed_update` | passed | passed |
| AC-5 | `test_ac5_cache_invalidated_on_successful_remove` | passed | passed |
| AC-6 | `test_ac6_update_raises_keyerror_with_message` | passed | passed |
| AC-7 | `test_ac7_imports_and_basic_usage` | failed | failed |

Full suite: 235 tests, 2 failing.

Failing:
- `tests.test_autose_issue_1.TestAtomicUpdate::test_ac2_update_atomic_on_json_storage`
- `tests.test_autose_issue_1.TestPublicAPI::test_ac7_imports_and_basic_usage`

## Problems

- TEST-SIDE mypy errors (CI type-checks tests too):
tests/test_autose_issue_1.py:87: error: Invalid "type: ignore" comment  [syntax]
tests/test_autose_issue_1.py:88: error: List item 1 has incompatible type "InvalidDoc"; expected "Mapping[Any, Any]"  [list-item]
tests/test_autose_issue_1.py:149: error: Module "tinydb.operations" has no attribute "multiply"  [attr-defined]
tests/test_autose_issue_1.py:149: error: Module "tinydb.operations" has no attribute "divide"  [attr-defined]
tests/test_autose_issue_1.py:186: error: Value of type "Document | None" is not indexable  [index]
Found 5 errors in 1 file (checked 11 source files)

- full suite failed: 2 failing test(s)

<details><summary>pytest output (full suite)</summary>

```
.F....F................................................................. [ 30%]
........................................................................ [ 61%]
........................................................................ [ 91%]
...................                                                      [100%]
=================================== FAILURES ===================================
___________ TestAtomicUpdate.test_ac2_update_atomic_on_json_storage ____________

self = <tests.test_autose_issue_1.TestAtomicUpdate object at 0x7f6ed173ce10>

    def test_ac2_update_atomic_on_json_storage(self) -> None:
        """AC-2: update with delete raises KeyError, file unchanged on JSONStorage."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
    
        try:
            db = TinyDB(storage=JSONStorage, path=temp_path)
            db.insert({'name': 'a', 'tmp': 1})
            db.insert({'name': 'b'})
    
            with pytest.raises(KeyError) as exc_info:
                db.update(delete('tmp'))
    
            # Exception message should be "'tmp'"
            assert str(exc_info.value) == "'tmp'"
    
            # File content should be unchanged
            with open(temp_path, 'r') as f:
                import json
                file_data = json.load(f)
>           assert file_data == {'_default': [{'name': 'a', 'tmp': 1}, {'name': 'b'}]}
E           AssertionError: assert {'_default': ...'name': 'b'}}} == {'_default': ...'name': 'b'}]}
E             
E             Differing items:
E             {'_default': {'1': {'name': 'a', 'tmp': 1}, '2': {'name': 'b'}}} != {'_default': [{'name': 'a', 'tmp': 1}, {'name': 'b'}]}
E             Use -v to get more diff

tests/test_autose_issue_1.py:53: AssertionError
________________ TestPublicAPI.test_ac7_imports_and_basic_usage ________________

self = <tests.test_autose_issue_1.TestPublicAPI object at 0x7f6ed173d1d0>

    def test_ac7_imports_and_basic_usage(self) -> None:
        """AC-7: All public classes and methods are present and work."""
        from tinydb import TinyDB, Query, where
        from tinydb.storages import MemoryStorage, JSONStorage
        from tinydb.middlewares import CachingMiddleware
>       from tinydb.operations import set, delete, increment, decrement, add, subtract, multiply, divide
E       ImportError: cannot import name 'multiply' from 'tinydb.operations' (/srv/autose/ws/tinydb/operations.py)

tests/test_autose_issue_1.py:149: ImportError
=========================== short test summary info ============================
FAILED tests/test_autose_issue_1.py::TestAtomicUpdate::test_ac2_update_atomic_on_json_storage
FAILED tests/test_autose_issue_1.py::TestPublicAPI::test_ac7_imports_and_basic_usage
2 failed, 233 passed in 0.84s

```
</details>

# Test report (issue #1, stages, attempt 1)

**Result:** PASS

| AC | Test | With change | On `main` |
|---|---|---|---|
| AC-1 | `test_ac1_update_delete_raises_keyerror_unchanged` | passed | failed |
| AC-2 | `test_ac2_remove_with_failing_updater_unchanged` | passed | failed |
| AC-3 | `test_ac3_query_cache_consistent_after_failed_update` | passed | passed |
| AC-4 | `test_ac4_successful_update_reflects_change` | passed | passed |
| AC-5 | `test_ac5_import_succeeds_and_existing_tests_pass` | passed | failed |

Full suite: 233 tests, 0 failing.

<details><summary>pytest output (full suite)</summary>

```
........................................................................ [ 30%]
........................................................................ [ 61%]
........................................................................ [ 92%]
.................                                                        [100%]
233 passed in 0.78s

```
</details>

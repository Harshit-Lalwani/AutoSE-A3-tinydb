# Test report (issue #4, stages, attempt 1)

**Result:** PASS

| AC | Test | With change | On `main` |
|---|---|---|---|
| AC-1 | `test_ac1_append_importable` | passed | not run |
| AC-2 | `test_ac2_append_to_existing_list[memory]` | passed | not run |
| AC-2 | `test_ac2_append_to_existing_list[json]` | passed | not run |
| AC-3 | `test_ac3_append_creates_new_list[memory]` | passed | not run |
| AC-3 | `test_ac3_append_creates_new_list[json]` | passed | not run |
| AC-4 | `test_ac4_append_raises_typeerror_on_non_list[memory]` | passed | not run |
| AC-4 | `test_ac4_append_raises_typeerror_on_non_list[json]` | passed | not run |
| AC-5 | `test_ac5_append_fail_fast_on_mixed_documents[memory]` | passed | not run |
| AC-5 | `test_ac5_append_fail_fast_on_mixed_documents[json]` | passed | not run |
| AC-6 | `test_ac6_append_applies_to_all_matching_documents[memory]` | passed | not run |
| AC-6 | `test_ac6_append_applies_to_all_matching_documents[json]` | passed | not run |
| AC-7 | `test_ac7_append_follows_same_protocol_as_add[memory]` | passed | not run |
| AC-7 | `test_ac7_append_follows_same_protocol_as_add[json]` | passed | not run |

Full suite: 243 tests, 0 failing.

<details><summary>pytest output (full suite)</summary>

```
........................................................................ [ 29%]
........................................................................ [ 59%]
........................................................................ [ 88%]
...........................                                              [100%]
243 passed in 0.55s

```
</details>

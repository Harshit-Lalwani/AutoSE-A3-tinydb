# Test report (issue #3, stages, attempt 1)

**Result:** PASS

| AC | Test | With change | On `main` |
|---|---|---|---|
| AC-1 | `test_ac1_basic_between_query` | passed | failed |
| AC-2 | `test_ac2_between_returns_callable` | passed | failed |
| AC-3 | `test_ac3_inclusive_bounds` | passed | failed |
| AC-4 | `test_ac4_exact_match_bounds` | passed | failed |
| AC-5 | `test_ac5_missing_field_excluded` | passed | failed |
| AC-6 | `test_ac6_composition_with_and` | passed | failed |
| AC-7 | `test_ac7_composition_with_or` | passed | failed |
| AC-8 | `test_ac8_cache_compatibility` | passed | failed |
| AC-9 | `test_ac9_low_greater_than_high_returns_empty` | passed | failed |
| AC-10 | `test_ac10_only_between_method_added` | passed | passed |
| AC-11 | `test_ac11_performance_not_degraded` | passed | failed |

Full suite: 247 tests, 0 failing.

<details><summary>pytest output (full suite)</summary>

```
........................................................................ [ 29%]
........................................................................ [ 58%]
........................................................................ [ 87%]
...............................                                          [100%]
247 passed in 0.77s

```
</details>

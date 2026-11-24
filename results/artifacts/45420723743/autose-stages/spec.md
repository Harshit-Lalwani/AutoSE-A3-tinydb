# Artefact 1: Requirements Specification

## Purpose and scope
Add a `between(low, high)` method to TinyDB's `Query` class that returns a query matching documents where the field value is inclusively between `low` and `high`. The method must compose with existing query operators (`&`, `|`, `~`), work with the query cache, and behave like the equivalent `(field >= low) & (field <= high)` expression for all orderable types and edge cases.

**In scope:** `Query().field.between(low, high)` method, its integration with query composition and caching, tests.

**Out of scope:** Changes to storage, middlewares, table API, or any other TinyDB component; exclusive-range variant; SQL `BETWEEN` syntax parsing.

## Input statements
| ID | Verbatim quote |
|----|----------------|
| ST-1 | "Range queries come up all the time for me (ages, prices, timestamps)." |
| ST-2 | "Right now I write `db.search((Query().age >= 18) & (Query().age <= 65))`" |
| ST-3 | "which is fine but noisy, and easy to get wrong when the field path is long." |
| ST-4 | "It would be nice to have `db.search(Query().age.between(18, 65))`" |
| ST-5 | "with both ends included, like SQL's BETWEEN." |
| ST-6 | "Documents that don't have the field should just not match, the same as with `<` / `>=` today." |
| ST-7 | "And it should of course work with the query cache and with `&`, `|`, `~` like the other query methods." |

## Glossary
| ID | Term | Possible meanings | Status |
|----|------|-------------------|--------|
| T-1 | between | Inclusive range [low, high] (SQL semantics) | Defined (ST-5) |
| T-2 | query cache | TinyDB's internal caching of query results for performance | Defined (README) |
| T-3 | orderable type | Any Python type supporting `<`, `<=`, `>`, `>=` (numbers, strings, datetimes, etc.) | Defined (inferred from existing operators) |

## Actors
| ID | Actor | Description | Tag | Source |
|----|-------|-------------|-----|--------|
| ACT-1 | Application developer | Writes queries using TinyDB's Python API | [S] | ST-1, ST-2 |
| ACT-2 | TinyDB maintainer | Reviews and merges the feature | [I] | Project context |

## Functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| FR-1 | The system shall provide a `between(low, high)` method on query fields that matches documents where the field value `v` satisfies `low <= v <= high`. | [S] | ST-4, ST-5 | Must | Proposed | AC-1, AC-2, AC-3, AC-4, AC-5, AC-6 | — |
| FR-2 | The system shall treat missing fields as non-matching, consistent with existing comparison operators. | [S] | ST-6 | Must | Proposed | AC-7 | — |
| FR-3 | The system shall support composition with `&`, `|`, `~` operators. | [S] | ST-7 | Must | Proposed | AC-8, AC-9, AC-10 | — |
| FR-4 | The system shall work with TinyDB's query cache. | [S] | ST-7 | Must | Proposed | AC-11 | — |

## Non-functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| NFR-1 | The `between` method shall accept any orderable type (numbers, strings, datetimes, etc.), matching the behaviour of existing comparison operators. | [I] | ST-1, ST-2, README examples | Must | Proposed | AC-1, AC-2 | — |
| NFR-2 | The implementation shall achieve 100% test coverage for the new method. | [S] | README "100% test coverage" | Must | Proposed | AC-12 | — |
| NFR-3 | When `low > high`, the query shall match no documents (empty result), consistent with the logical AND of `(field >= low) & (field <= high)` and SQL BETWEEN semantics. | [I] | ST-5, logical consistency | Must | Proposed | AC-3 | — |

## Constraints, dependencies, risks
| ID | Item | Tag | Source | Status |
|----|------|-----|--------|--------|
| CON-1 | Python 3.8+ compatibility | [S] | README | Confirmed |
| CON-2 | No external dependencies | [S] | README | Confirmed |
| DEP-1 | Existing `Query` class and query operator infrastructure | [I] | Codebase structure | Proposed |
| RISK-1 | If `between` is not hashable/serializable like other query objects, query cache will break | [I] | ST-7 | Proposed |

## Traceability
| Requirement ID | Supported by | Verified by |
|----------------|--------------|-------------|
| FR-1 | ST-4, ST-5 | AC-1–AC-6 |
| FR-2 | ST-6 | AC-7 |
| FR-3 | ST-7 | AC-8–AC-10 |
| FR-4 | ST-7 | AC-11 |
| NFR-1 | ST-1, ST-2, README | AC-1, AC-2 |
| NFR-2 | README | AC-12 |
| NFR-3 | ST-5, logical consistency | AC-3 |

---

# Artefact 2: Assumptions and Open-Questions Register

## Confirmed facts
ST-1 through ST-7 (all input statements).

## Inferences
| ID | Inference | Follows from | Risk if wrong |
|----|-----------|--------------|---------------|
| I-1 | `between` should accept any orderable type because existing operators (`>=`, `<=`) do | ST-1, ST-2, README examples | If maintainer wants numeric-only, tests and type hints need narrowing |
| I-2 | `low > high` should yield empty result (no match) because `(field >= low) & (field <= high)` naturally does | ST-5, logical consistency | If maintainer prefers swap or error, AC-3 changes |
| I-3 | Query cache compatibility requires the query object to be hashable and comparable like existing query objects | ST-7, TinyDB architecture | Cache breaks silently if not implemented correctly |

## Assumptions
| ID | Assumption | Why needed | Linked Q | Risk if wrong |
|----|------------|------------|----------|---------------|
| A-1 | `between` accepts any orderable type (numbers, strings, datetimes, etc.) | NFR-1 scope, type hints, test matrix | — | Maintainer may restrict to numeric; would require narrowing tests and docs |
| A-2 | When `low > high`, the query matches no documents (empty result) | NFR-3, AC-3 definition | — | Maintainer may prefer swap bounds or raise ValueError; would change AC-3 and user expectations |
| A-3 | The method name is `between` (not `in_range`, `range`, etc.) | ST-4 | — | Low risk; name is explicit in issue |
| A-4 | Both bounds are inclusive (`low <= v <= high`) | ST-5 "both ends included" | — | Confirmed by ST-5 |

## Open questions
| ID | Question | Why it matters | Blocks | Priority | Ask whom | Default used |
|----|----------|----------------|--------|----------|----------|--------------|
| Q-1 | Should `between` accept any orderable type or only numeric types? | Determines FR-1 scope, type hints, test matrix | FR-1, NFR-1 | Important (not blocking) | Maintainer | Any orderable type (A-1) |
| Q-2 | When `low > high`, should it return empty, swap bounds, or raise ValueError? | Determines correctness of AC-3 and user expectations | NFR-3 | Important (not blocking) | Maintainer | Empty result (A-2) |

**Note:** Both questions are *important* but not *blocking* because conservative defaults (A-1, A-2) exist that a maintainer would very likely accept (consistent with existing operators and SQL semantics). The pipeline should proceed with these defaults.

## Conflicts
None found. The contradiction sweep found no contradictions between restrictions and capabilities.

## External evidence log
External evidence: not consulted (no tool available).

## Unresolved items
None. All gaps covered by assumptions with documented defaults.

---

# Artefact 3: Validation Summary

## Validation checks
| Check | Result | Findings |
|-------|--------|----------|
| Completeness | Pass | All Step 3 checklist items covered: actors (ACT-1), goals (ST-1), scope (in/out lists), functional (FR-1–4), data (FR-2), interfaces (FR-3, FR-4), non-functional (NFR-1–3), constraints (CON-1,2), operations (cache), acceptance (ACs). |
| Consistency | Pass | No contradictory requirements. Glossary defines terms. FR-1–4, NFR-1–3 align. |
| Traceability | Pass | Every requirement has source tag, source column, at least one AC, traceability table complete. IDs unique. |
| Feasibility | Pass | No requirement contradicts constraints. RISK-1 documented for cache compatibility. |
| Testability | Pass | All ACs are measurable Given/When/Then with observable Python API calls. No vague words. |
| Invention check | Pass | No `Confirmed` item without exact quote. No invented numbers, laws, technologies. `EV-n` absent (no tool). |

## Readiness counts
| Status | Count |
|--------|-------|
| Confirmed (implementation-ready) | 0 |
| Proposed (awaiting confirmation) | 7 (FR-1–4, NFR-1–3) |
| Needs clarification | 0 |
| Unresolved | 0 |

## Boundary statement
Requirements from the input: 7 (ST-1–7). Supported by external evidence (still need stakeholder confirmation): 0. Need stakeholder confirmation: 2 (Q-1, Q-2 — important but not blocking; conservative defaults applied).

## Blocking questions (would unlock most requirements)
None. The two important questions have conservative defaults (A-1, A-2) that allow the pipeline to proceed.

## Run notes
- Stakeholders consulted: No (non-interactive run).
- Tools used: None available.
- Human intervention needed: No.

---

```json
{
  "summary": "Add Query().field.between(low, high) method for inclusive range queries that composes with &, |, ~, works with query cache, treats missing fields as non-matching, and accepts any orderable type with empty result when low > high.",
  "issue_type": "feature",
  "acceptance_criteria": [
    {
      "id": "AC-1",
      "requirement": "FR-1",
      "given": "a TinyDB instance with documents {'age': 18}, {'age': 25}, {'age': 65}, {'age': 70}",
      "when": "db.search(Query().age.between(18, 65))",
      "then": "returns [{'age': 18}, {'age': 25}, {'age': 65}]"
    },
    {
      "id": "AC-2",
      "requirement": "FR-1",
      "given": "a TinyDB instance with documents {'name': 'Alice'}, {'name': 'Bob'}, {'name': 'Charlie'}",
      "when": "db.search(Query().name.between('Alice', 'Bob'))",
      "then": "returns [{'name': 'Alice'}, {'name': 'Bob'}] (string ordering)"
    },
    {
      "id": "AC-3",
      "requirement": "NFR-3",
      "given": "a TinyDB instance with documents {'age': 25}",
      "when": "db.search(Query().age.between(65, 18))",
      "then": "returns [] (empty list, no match when low > high)"
    },
    {
      "id": "AC-4",
      "requirement": "FR-1",
      "given": "a TinyDB instance with documents {'ts': datetime(2024,1,1)}, {'ts': datetime(2024,6,1)}, {'ts': datetime(2024,12,31)}",
      "when": "db.search(Query().ts.between(datetime(2024,1,1), datetime(2024,6,30)))",
      "then": "returns [{'ts': datetime(2024,1,1)}, {'ts': datetime(2024,6,1)}] (datetime ordering)"
    },
    {
      "id": "AC-5",
      "requirement": "FR-1",
      "given": "a TinyDB instance with documents {'price': 9.99}, {'price': 19.99}, {'price': 29.99}",
      "when": "db.search(Query().price.between(10.0, 20.0))",
      "then": "returns [{'price': 19.99}] (float ordering)"
    },
    {
      "id": "AC-6",
      "requirement": "FR-1",
      "given": "a TinyDB instance with documents {'age': 25}",
      "when": "db.search(Query().age.between(25, 25))",
      "then": "returns [{'age': 25}] (single-value range works)"
    },
    {
      "id": "AC-7",
      "requirement": "FR-2",
      "given": "a TinyDB instance with documents {'age': 25}, {'name': 'Bob'} (missing age)",
      "when": "db.search(Query().age.between(18, 65))",
      "then": "returns [{'age': 25}] (document without 'age' field does not match)"
    },
    {
      "id": "AC-8",
      "requirement": "FR-3",
      "given": "a TinyDB instance with documents {'age': 25, 'active': True}, {'age': 30, 'active': False}, {'age': 35, 'active': True}",
      "when": "db.search((Query().age.between(20, 40)) & (Query().active == True))",
      "then": "returns [{'age': 25, 'active': True}, {'age': 35, 'active': True}] (AND composition)"
    },
    {
      "id": "AC-9",
      "requirement": "FR-3",
      "given": "a TinyDB instance with documents {'age': 15}, {'age': 25}, {'age': 65}",
      "when": "db.search((Query().age.between(18, 30)) | (Query().age.between(60, 70)))",
      "then": "returns [{'age': 25}, {'age': 65}] (OR composition)"
    },
    {
      "id": "AC-10",
      "requirement": "FR-3",
      "given": "a TinyDB instance with documents {'age': 25}, {'age': 30}, {'age': 35}",
      "when": "db.search(~(Query().age.between(28, 32)))",
      "then": "returns [{'age': 25}, {'age': 35}] (NOT composition)"
    },
    {
      "id": "AC-11",
      "requirement": "FR-4",
      "given": "a TinyDB instance with CachingMiddleware enabled and documents {'age': 25}, {'age': 30}",
      "when": "db.search(Query().age.between(20, 30)) called twice",
      "then": "second call returns cached result (same list object or equal content) without re-scanning storage"
    },
    {
      "id": "AC-12",
      "requirement": "NFR-2",
      "given": "the test suite for the new between method",
      "when": "running pytest with coverage",
      "then": "coverage for the between method and its query class is 100%"
    }
  ],
  "assumptions": [
    {
      "id": "A-1",
      "assumption": "between accepts any orderable type (numbers, strings, datetimes, etc.)",
      "default_used": "Any orderable type, matching existing comparison operators"
    },
    {
      "id": "A-2",
      "assumption": "When low > high, the query matches no documents (empty result)",
      "default_used": "Empty result, consistent with (field >= low) & (field <= high) and SQL BETWEEN"
    },
    {
      "id": "A-3",
      "assumption": "The method name is 'between'",
      "default_used": "between (from ST-4)"
    },
    {
      "id": "A-4",
      "assumption": "Both bounds are inclusive (low <= v <= high)",
      "default_used": "Inclusive (from ST-5 'both ends included')"
    }
  ],
  "blocking_questions": []
}
```
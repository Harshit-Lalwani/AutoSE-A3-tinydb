# Artefact 1: Requirements Specification

## Purpose and scope
Add a `between(low, high)` method to TinyDB's query objects that performs an inclusive range check on a document field, matching SQL's `BETWEEN` semantics. The method must integrate with the existing query composition operators (`&`, `|`, `~`) and the query cache.

**In scope:**
- `Query().field.between(low, high)` returning a query object
- Inclusive bounds (low ≤ value ≤ high)
- Documents missing the field do not match
- Works with any type supporting `<=` comparison (consistent with existing operators)
- Composes with `&`, `|`, `~`
- Works with query cache

**Out of scope:**
- Exclusive bounds variants
- Keyword-argument signatures
- Changes to storage, middleware, or table APIs
- Implementation details (which file, which class)

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
| T-1 | between | Inclusive range check (low ≤ x ≤ high) per SQL BETWEEN | Defined (ST-5) |
| T-2 | query cache | TinyDB's internal caching of query results for performance | Defined (README) |
| T-3 | field path | Nested field access like `Query().user.address.zip` | Defined (README examples) |

## Actors
| ID | Actor | Description | Tag | Source |
|----|-------|-------------|-----|--------|
| ACT-1 | Application developer | Writes queries using TinyDB's Python API | [S] | ST-1, ST-2, ST-4 |

## Functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| FR-1 | The system shall provide a `between(low, high)` method on query field objects that returns a query matching documents where the field value satisfies `low <= value <= high`. | [S] | ST-4, ST-5 | Must | Proposed | AC-1, AC-2, AC-3 | — |
| FR-2 | The system shall not match documents that lack the queried field when using `between`. | [S] | ST-6 | Must | Proposed | AC-4 | — |
| FR-3 | The system shall allow `between` queries to be combined with `&`, `|`, `~` operators. | [S] | ST-7 | Must | Proposed | AC-5, AC-6 | — |
| FR-4 | The system shall support `between` queries in the query cache. | [S] | ST-7 | Must | Proposed | AC-7 | — |

## Non-functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Quality (ISO 25010) |
|----|-------------|-----|--------|----------|--------|---------------------|---------------------|
| NFR-1 | The `between` method shall accept any `low` and `high` values that support `<=` comparison with the field value, consistent with existing comparison operators. | [I] | ST-1, ST-2, ST-7 | Should | Proposed | AC-8 | Compatibility |
| NFR-2 | When `low > high`, the query shall match no documents (empty result), consistent with SQL `BETWEEN` semantics and the equivalent composed query `(field >= low) & (field <= high)`. | [I] | ST-5, ST-2 | Should | Proposed | AC-9 | Correctness |

## Constraints, dependencies, risks
| ID | Item | Tag | Source | Status |
|----|------|-----|--------|--------|
| CON-1 | Python 3.8+ compatibility | [S] | README | Confirmed |
| CON-2 | No external dependencies | [S] | README | Confirmed |
| DEP-1 | Existing `Query` class and comparison operator implementation | [I] | ST-7, README | Proposed |
| RISK-1 | If `between` implementation diverges from composed `>=`/`<=` behaviour, existing tests may need updates | [I] | ST-2, ST-7 | Proposed |

## Traceability
| Requirement ID | Supported by | Verified by |
|----------------|--------------|-------------|
| FR-1 | ST-4, ST-5 | AC-1, AC-2, AC-3 |
| FR-2 | ST-6 | AC-4 |
| FR-3 | ST-7 | AC-5, AC-6 |
| FR-4 | ST-7 | AC-7 |
| NFR-1 | ST-1, ST-2, ST-7 | AC-8 |
| NFR-2 | ST-5, ST-2 | AC-9 |

---

# Artefact 2: Assumptions and Open-Questions Register

## Confirmed facts
ST-1, ST-2, ST-3, ST-4, ST-5, ST-6, ST-7

## Inferences
| ID | Inference | Follows from | Risk if wrong |
|----|-----------|--------------|---------------|
| I-1 | The desired API is exactly `Query().field.between(low, high)` with positional arguments and inclusive bounds | ST-4, ST-5 | Low — issue shows this exact syntax |
| I-2 | Type support should mirror existing comparison operators (any type with `<=`) | ST-2, ST-7 | Low — maintains consistency |
| I-3 | `low > high` should yield an empty result set (like SQL BETWEEN and like the equivalent composed query) | ST-5, ST-2 | Low — follows stated analogy |

## Assumptions
| ID | Assumption | Why needed | Linked Q | Risk if wrong |
|----|------------|------------|----------|---------------|
| A-1 | Method signature is `between(low, high)` with positional args, inclusive bounds, name `between` | Issue shows this exact API; no alternative suggested | — | Low — explicit in issue |
| A-2 | Works with any type supporting `<=` (numbers, strings, dates, etc.) | Existing operators work this way; issue mentions "ages, prices, timestamps" but not exclusivity | — | Medium — if maintainer wants numeric-only, tests/docs change |
| A-3 | `between(low, high)` with `low > high` returns a query matching nothing (empty list) | Matches SQL BETWEEN and the behaviour of `(field >= low) & (field <= high)` when low > high | — | Low — conservative, safe default |

## Open questions
| ID | Question | Why it matters | Blocks | Priority | Ask whom | Default used |
|----|----------|----------------|--------|----------|----------|--------------|
| — | (none — all resolved by assumptions above) | | | | | |

## Conflicts
| ID | Side A (quote) | Side B (quote) | Affected IDs | Who decides |
|----|----------------|----------------|--------------|-------------|
| — | (none found) | | | |

## External evidence log
External evidence: not consulted (no tool available)

## Unresolved items
None — all gaps covered by assumptions with conservative defaults.

---

# Artefact 3: Validation Summary

## Validation checks
| Check | Result | Findings |
|-------|--------|----------|
| Completeness | Pass | All ST items traced; checklist items covered (actors, goals, scope, functional, data, interfaces, NFR, constraints, operations, acceptance) |
| Consistency | Pass | No contradictions; glossary defines terms; FR/NFR align |
| Traceability | Pass | Every requirement has source and ACs; traceability table complete |
| Feasibility | Pass | No requirement conflicts with constraints; RISK-1 noted |
| Testability | Pass | All ACs measurable via public API; no vague words |
| Invention check | Pass | No `Confirmed` item without quote; no invented numbers/laws; assumptions labelled |

## Readiness counts
| Status | Count |
|--------|-------|
| Confirmed (implementation-ready) | 0 |
| Proposed | 6 (FR-1..4, NFR-1..2) |
| Needs clarification | 0 |
| Unresolved | 0 |

## Boundary statement
Requirements from the input: 7 statements → 4 functional + 2 non-functional requirements. Supported by external evidence: 0. Need stakeholder confirmation: 6 (all `Proposed` pending maintainer review of assumptions A-1..A-3).

## Blocking questions (would unlock most requirements)
None — all assumptions use conservative defaults a maintainer would likely accept.

## Run notes
- Stakeholders consulted: no (non-interactive pipeline)
- Tools used: none available
- Human intervention needed: no

---

```json
{
  "summary": "Add Query().field.between(low, high) method for inclusive range queries, matching SQL BETWEEN semantics, composable with & | ~ and compatible with query cache.",
  "issue_type": "feature",
  "acceptance_criteria": [
    {
      "id": "AC-1",
      "requirement": "FR-1",
      "given": "a TinyDB instance with documents [{'age': 18}, {'age': 25}, {'age': 65}, {'age': 70}]",
      "when": "db.search(Query().age.between(18, 65))",
      "then": "returns [{'age': 18}, {'age': 25}, {'age': 65}]"
    },
    {
      "id": "AC-2",
      "requirement": "FR-1",
      "given": "a TinyDB instance with documents [{'price': 10.5}, {'price': 100.0}, {'price': 1000.0}]",
      "when": "db.search(Query().price.between(10.5, 100.0))",
      "then": "returns [{'price': 10.5}, {'price': 100.0}]"
    },
    {
      "id": "AC-3",
      "requirement": "FR-1",
      "given": "a TinyDB instance with documents [{'ts': '2024-01-01'}, {'ts': '2024-06-15'}, {'ts': '2024-12-31'}]",
      "when": "db.search(Query().ts.between('2024-01-01', '2024-06-15'))",
      "then": "returns [{'ts': '2024-01-01'}, {'ts': '2024-06-15'}]"
    },
    {
      "id": "AC-4",
      "requirement": "FR-2",
      "given": "a TinyDB instance with documents [{'age': 25}, {'name': 'Bob'}, {'age': 30, 'name': 'Alice'}]",
      "when": "db.search(Query().age.between(20, 40))",
      "then": "returns [{'age': 25}, {'age': 30, 'name': 'Alice'}] (document without 'age' excluded)"
    },
    {
      "id": "AC-5",
      "requirement": "FR-3",
      "given": "a TinyDB instance with documents [{'age': 25, 'active': True}, {'age': 30, 'active': False}, {'age': 35, 'active': True}]",
      "when": "db.search((Query().age.between(20, 40)) & (Query().active == True))",
      "then": "returns [{'age': 25, 'active': True}, {'age': 35, 'active': True}]"
    },
    {
      "id": "AC-6",
      "requirement": "FR-3",
      "given": "a TinyDB instance with documents [{'age': 15}, {'age': 25}, {'age': 65}]",
      "when": "db.search(~(Query().age.between(18, 65)))",
      "then": "returns [{'age': 15}]"
    },
    {
      "id": "AC-7",
      "requirement": "FR-4",
      "given": "a TinyDB instance with CachingMiddleware enabled and documents [{'age': 25}, {'age': 30}]",
      "when": "db.search(Query().age.between(20, 40)) called twice",
      "then": "second call returns cached result [{'age': 25}, {'age': 30}] without re-executing query"
    },
    {
      "id": "AC-8",
      "requirement": "NFR-1",
      "given": "a TinyDB instance with documents [{'val': 'apple'}, {'val': 'banana'}, {'val': 'cherry'}]",
      "when": "db.search(Query().val.between('banana', 'cherry'))",
      "then": "returns [{'val': 'banana'}, {'val': 'cherry'}] (string comparison works)"
    },
    {
      "id": "AC-9",
      "requirement": "NFR-2",
      "given": "a TinyDB instance with documents [{'age': 25}, {'age': 30}]",
      "when": "db.search(Query().age.between(65, 18))",
      "then": "returns [] (empty list, no error raised)"
    }
  ],
  "assumptions": [
    {
      "id": "A-1",
      "assumption": "Method signature is between(low, high) with positional arguments, inclusive bounds, name 'between'",
      "default_used": "Exactly as shown in issue: Query().age.between(18, 65)"
    },
    {
      "id": "A-2",
      "assumption": "Works with any type supporting <= comparison (numbers, strings, dates, etc.)",
      "default_used": "Mirror existing comparison operator behaviour"
    },
    {
      "id": "A-3",
      "assumption": "between(low, high) with low > high returns a query matching nothing (empty result)",
      "default_used": "Consistent with SQL BETWEEN and composed (field >= low) & (field <= high) behaviour"
    }
  ],
  "blocking_questions": []
}
```
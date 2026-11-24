# Artefact 1: Requirements Specification

## Purpose and scope
This specification covers the addition of a `between(low, high)` method to TinyDB's `Query` class, enabling inclusive range queries on document fields. The feature must integrate with the existing query language (composition with `&`, `|`, `~`), work with the query cache, and follow the existing behaviour for missing fields (no match).

**In scope:**
- `Query().field.between(low, high)` returning a query object
- Inclusive bounds (both `low` and `high` included)
- Composition with `&`, `|`, `~`
- Query cache compatibility
- Missing-field behaviour consistent with existing comparisons

**Out of scope:**
- Exclusive bounds variants
- New storage or middleware changes
- Changes to the `Query` constructor or other query methods
- Implementation details (which file, which class, how the cache works internally)

## Input statements

| ID | Verbatim quote |
|----|----------------|
| ST-1 | "Range queries come up all the time for me (ages, prices, timestamps)." |
| ST-2 | "Right now I write `db.search((Query().age >= 18) & (Query().age <= 65))` which is fine but noisy, and easy to get wrong when the field path is long." |
| ST-3 | "It would be nice to have `db.search(Query().age.between(18, 65))` with both ends included, like SQL's BETWEEN." |
| ST-4 | "Documents that don't have the field should just not match, the same as with `<` / `>=` today." |
| ST-5 | "And it should of course work with the query cache and with `&`, `|`, `~` like the other query methods." |

## Glossary

| ID | Term | Possible meanings | Status |
|----|------|-------------------|--------|
| T-1 | between(low, high) | Inclusive range query method on Query field accessor | Defined |
| T-2 | query cache | TinyDB's internal caching of query results for performance | Defined (from README) |
| T-3 | field path | Nested field access like `Query().user.age` | Defined (from README examples) |

## Actors

| ID | Actor | Description | Tag | Source |
|----|-------|-------------|-----|--------|
| ACT-1 | Application developer | Writes queries using TinyDB's Python API | [S] | ST-1, ST-2 |
| ACT-2 | TinyDB maintainer | Reviews and merges the feature | [I] | Project context |

## Functional requirements

| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| FR-1 | The system shall provide a `between(low, high)` method on field accessors of `Query` objects. | [S] | ST-3 | Must | Proposed | AC-1, AC-2 | — |
| FR-2 | `between(low, high)` shall match documents where the field value is greater than or equal to `low` and less than or equal to `high` (inclusive bounds). | [S] | ST-3 | Must | Proposed | AC-3, AC-4 | — |
| FR-3 | Documents that do not have the queried field shall not match, consistent with existing comparison operators. | [S] | ST-4 | Must | Proposed | AC-5 | — |
| FR-4 | The query object returned by `between` shall compose with `&`, `|`, `~` like other query methods. | [S] | ST-5 | Must | Proposed | AC-6, AC-7 | — |
| FR-5 | Queries using `between` shall work with TinyDB's query cache (be cacheable and return correct cached results). | [S] | ST-5 | Must | Proposed | AC-8 | — |
| FR-6 | When `low > high`, `between(low, high)` shall match no documents (SQL BETWEEN semantics). | [A] | A-1 | Must | Proposed | AC-9 | — |

## Non-functional requirements

| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| NFR-1 | The feature shall not change the public API of `Query` other than adding `between`. | [I] | ST-3, ST-5 | Must | Proposed | AC-10 | — |
| NFR-2 | The feature shall not degrade performance of existing queries. | [I] | Project context | Should | Proposed | AC-11 | — |

## Constraints, dependencies, risks

| ID | Item | Tag | Source | Status |
|----|------|-----|--------|--------|
| CON-1 | Python 3.8+ compatibility | [S] | README | Confirmed |
| CON-2 | No external dependencies | [S] | README | Confirmed |
| DEP-1 | Existing `Query` class and query cache implementation | [I] | Codebase | Proposed |
| RISK-1 | Cache key deduplication with expanded form `(field >= low) & (field <= high)` not guaranteed | [A] | A-2 | Proposed |

## Traceability

| Requirement ID | Supported by | Verified by |
|----------------|--------------|-------------|
| FR-1 | ST-3 | AC-1, AC-2 |
| FR-2 | ST-3 | AC-3, AC-4 |
| FR-3 | ST-4 | AC-5 |
| FR-4 | ST-5 | AC-6, AC-7 |
| FR-5 | ST-5 | AC-8 |
| FR-6 | A-1 | AC-9 |
| NFR-1 | ST-3, ST-5 | AC-10 |
| NFR-2 | Project context | AC-11 |

---

# Artefact 2: Assumptions and Open-Questions Register

## Confirmed facts
ST-1, ST-2, ST-3, ST-4, ST-5

## Inferences

| ID | Inference | Follows from | Risk if wrong |
|----|-----------|--------------|---------------|
| I-1 | The feature is a pure addition to the `Query` class, not a modification of existing methods | ST-3, ST-5 | Low — if existing methods change, scope expands |
| I-2 | "Work with the query cache" means the query is cacheable and returns correct results, not necessarily identical cache keys to the expanded form | ST-5 | Medium — if deduplication is expected, performance may differ |

## Assumptions

| ID | Assumption | Why needed | Linked Q | Default used | Risk if wrong |
|----|------------|------------|----------|--------------|---------------|
| A-1 | `between(low, high)` with `low > high` matches no documents (SQL BETWEEN semantics) | Issue references SQL's BETWEEN; ST-3 says "like SQL's BETWEEN" | — | Match nothing | Low — SQL behaviour is the explicit reference |
| A-2 | Cache key for `between(low, high)` may differ from the expanded form `(field >= low) & (field <= high)`; both are cacheable independently | ST-5 says "work with the query cache", not "deduplicate with expanded form" | — | Distinct keys acceptable | Medium — users switching from expanded form may not get cache hits |

## Open questions
*None — all uncertainties resolved with conservative defaults above.*

## Conflicts
*None identified.*

## External evidence log
External evidence: not consulted (no tool available)

## Unresolved items
*None.*

---

# Artefact 3: Validation Summary

## Validation checks

| Check | Result | Findings |
|-------|--------|----------|
| Completeness | Pass | All ST items traced; checklist items covered (actors, goals, scope, functional, data, interfaces, NFR, constraints, operations, acceptance) |
| Consistency | Pass | No contradictory requirements; glossary terms used consistently |
| Traceability | Pass | Every requirement has source and acceptance criteria; traceability table complete |
| Feasibility | Pass | No requirement contradicts constraints; pure Python addition |
| Testability | Pass | All ACs are measurable via public API calls; no vague terms |
| Invention check | Pass | No `Confirmed` items without quotes; no invented numbers/laws/technologies; assumptions labelled `[A]` |

## Readiness counts
- Confirmed (implementation-ready): 0 (all are `[S]` but need maintainer confirmation to be `Confirmed`)
- Proposed: 8 (FR-1–FR-6, NFR-1, NFR-2)
- Needs clarification: 0
- Unresolved: 0

## Boundary statement
Requirements from the input: 5 (ST-1–ST-5). Supported by external evidence (still need stakeholder confirmation): 0. Need stakeholder confirmation: 8 (all proposed requirements).

## Blocking questions (in order)
*None — all resolved with conservative defaults.*

## Run notes
- Stakeholders consulted: No (non-interactive pipeline run)
- Tools used: None available
- Human intervention needed: No

---

```json
{
  "summary": "Add Query().field.between(low, high) method for inclusive range queries, composable with &, |, ~, cache-compatible, matching SQL BETWEEN semantics (no match when low > high, missing fields don't match).",
  "issue_type": "feature",
  "acceptance_criteria": [
    {
      "id": "AC-1",
      "requirement": "FR-1",
      "given": "a TinyDB instance with documents containing an 'age' field",
      "when": "calling db.search(Query().age.between(18, 65))",
      "then": "returns a list of documents where 18 <= age <= 65"
    },
    {
      "id": "AC-2",
      "requirement": "FR-1",
      "given": "a Query object",
      "when": "accessing Query().age.between",
      "then": "returns a callable that accepts two arguments (low, high) and returns a query object"
    },
    {
      "id": "AC-3",
      "requirement": "FR-2",
      "given": "documents with ages 17, 18, 30, 65, 66",
      "when": "searching with Query().age.between(18, 65)",
      "then": "returns only documents with ages 18, 30, 65"
    },
    {
      "id": "AC-4",
      "requirement": "FR-2",
      "given": "documents with price 9.99, 10.00, 10.01",
      "when": "searching with Query().price.between(10.00, 10.00)",
      "then": "returns only documents with price exactly 10.00"
    },
    {
      "id": "AC-5",
      "requirement": "FR-3",
      "given": "documents [{'age': 25}, {'name': 'Bob'}, {'age': 30}]",
      "when": "searching with Query().age.between(20, 30)",
      "then": "returns only [{'age': 25}, {'age': 30}] (document without 'age' excluded)"
    },
    {
      "id": "AC-6",
      "requirement": "FR-4",
      "given": "a Query object",
      "when": "combining Query().age.between(18, 65) & Query().name == 'John'",
      "then": "returns a valid query object that matches documents satisfying both conditions"
    },
    {
      "id": "AC-7",
      "requirement": "FR-4",
      "given": "a Query object",
      "when": "combining Query().age.between(18, 65) | Query().status == 'admin'",
      "then": "returns a valid query object that matches documents satisfying either condition"
    },
    {
      "id": "AC-8",
      "requirement": "FR-5",
      "given": "a TinyDB instance with caching enabled (CachingMiddleware)",
      "when": "executing db.search(Query().age.between(18, 65)) twice",
      "then": "the second call returns the same result and uses the cache (verified by cache hit or execution time)"
    },
    {
      "id": "AC-9",
      "requirement": "FR-6",
      "given": "documents with ages 20, 30, 40",
      "when": "searching with Query().age.between(30, 20) (low > high)",
      "then": "returns an empty list"
    },
    {
      "id": "AC-10",
      "requirement": "NFR-1",
      "given": "the TinyDB public API before the change",
      "when": "importing tinydb and inspecting Query class",
      "then": "only the 'between' method is added; no existing methods are removed or changed"
    },
    {
      "id": "AC-11",
      "requirement": "NFR-2",
      "given": "a benchmark of existing query operations",
      "when": "running the same benchmark after adding between",
      "then": "performance of existing queries (==, >=, <=, &, |, ~) is not measurably degraded"
    }
  ],
  "assumptions": [
    {
      "id": "A-1",
      "assumption": "between(low, high) with low > high matches no documents (SQL BETWEEN semantics)",
      "default_used": "match nothing"
    },
    {
      "id": "A-2",
      "assumption": "Cache key for between(low, high) may differ from expanded form (field >= low) & (field <= high); both are independently cacheable",
      "default_used": "distinct keys acceptable"
    }
  ],
  "blocking_questions": []
}
```
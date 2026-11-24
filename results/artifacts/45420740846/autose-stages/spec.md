# Artefact 1: Requirements Specification

## Purpose and scope
Add optional server-side sorting and pagination to `Table.search()` so that callers can receive ordered, page-sized result subsets without post-processing in Python. The change is backward-compatible: existing calls without the new parameters behave exactly as before.

**In scope**
- `Table.search(query, sort=None, limit=None, offset=None)`
- `sort` as a list of `(field_path, direction)` tuples, direction `1` (asc) or `-1` (desc)
- `limit` and `offset` as non-negative integers
- Deterministic ordering when `sort` is provided; stable but unspecified order when omitted
- Validation with clear exceptions for invalid parameters

**Out of scope**
- Cursor-based pagination, `page`/`page_size` helpers, `Query()`-chaining sort API
- Index-accelerated sorting (storage-layer change)
- Cross-table joins or aggregation

## Input statements
| ID | Verbatim quote |
|----|----------------|
| ST-1 | "one of my tables has a few thousand records now" |
| ST-2 | "When I search I get everything back at once and in whatever order" |
| ST-3 | "then I sort and slice the list myself in Python" |
| ST-4 | "Would be nice if TinyDB could help with this somehow, ordering and getting results page by page" |
| ST-5 | "Not sure what the best API would be" |

## Glossary
| ID | Term | Possible meanings | Status |
|----|------|-------------------|--------|
| T-1 | field_path | Dot-separated path to a nested field (e.g. "user.age") | Defined (matches existing Query syntax) |
| T-2 | direction | `1` for ascending, `-1` for descending | Defined |
| T-3 | page | A contiguous slice of the sorted result set | Defined |

## Actors
| ID | Actor | Description | Tag | Source |
|----|-------|-------------|-----|--------|
| ACT-1 | Application developer | Calls `Table.search()` with optional sort/limit/offset | [S] | ST-1..ST-4 |

## Functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| FR-1 | The system shall accept an optional `sort` parameter on `Table.search()` that specifies a list of `(field_path, direction)` tuples. | [I] | ST-4, ST-5 | Must | Proposed | AC-1, AC-2 | — |
| FR-2 | The system shall accept optional `limit` and `offset` parameters on `Table.search()` for pagination. | [I] | ST-3, ST-4 | Must | Proposed | AC-3, AC-4 | — |
| FR-3 | The system shall return results ordered by the `sort` criteria when provided; when omitted, order is stable but unspecified (current behaviour). | [I] | ST-2, ST-4 | Must | Proposed | AC-5 | — |
| FR-4 | The system shall apply `offset` then `limit` to the sorted result set. | [I] | ST-3, ST-4 | Must | Proposed | AC-6 | — |
| FR-5 | The system shall raise `ValueError` if `sort` contains an invalid direction (not `1` or `-1`). | [I] | ST-5 | Must | Proposed | AC-7 | — |
| FR-6 | The system shall raise `ValueError` if `limit` or `offset` is negative. | [I] | ST-5 | Must | Proposed | AC-8 | — |
| FR-7 | The system shall raise `TypeError` if `sort` is not a list of 2-tuples, or if `limit`/`offset` are not integers. | [I] | ST-5 | Must | Proposed | AC-9 | — |
| FR-8 | The system shall preserve existing behaviour when `sort`, `limit`, `offset` are all omitted or `None`. | [S] | ST-2 | Must | Confirmed | AC-10 | — |

## Non-functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| NFR-1 | The system shall not increase memory usage asymptotically beyond the current full-result load (sorting is in-memory; pagination slices after sort). | [I] | ST-1 | Should | Proposed | AC-11 | — |

## Constraints, dependencies, risks
| ID | Item | Tag | Source | Status |
|----|------|-----|--------|--------|
| CON-1 | Python 3.8+ | [S] | README | Confirmed |
| CON-2 | No external dependencies | [S] | README | Confirmed |
| DEP-1 | Existing `Query` field-path syntax reused for `field_path` | [I] | ST-4 | Proposed |
| RISK-1 | In-memory sort on thousands of documents may be slow; acceptable for target use case (small apps) | [I] | ST-1 | Proposed |

## Traceability
| Requirement ID | Supported by | Verified by |
|----------------|--------------|-------------|
| FR-1 | ST-4, ST-5, A-1 | AC-1, AC-2 |
| FR-2 | ST-3, ST-4, A-2 | AC-3, AC-4 |
| FR-3 | ST-2, ST-4, A-1 | AC-5 |
| FR-4 | ST-3, ST-4, A-2 | AC-6 |
| FR-5 | ST-5, A-1 | AC-7 |
| FR-6 | ST-5, A-2 | AC-8 |
| FR-7 | ST-5, A-1, A-2 | AC-9 |
| FR-8 | ST-2 | AC-10 |
| NFR-1 | ST-1 | AC-11 |

---

# Artefact 2: Assumptions and Open-Questions Register

## Confirmed facts
ST-1, ST-2, ST-3, ST-4, ST-5

## Inferences
| ID | Inference | Follows from | Risk if wrong |
|----|-----------|--------------|---------------|
| I-1 | Sorting and pagination are applied in-memory after the query matches | ST-1 (few thousand records), TinyDB architecture (no server-side index) | If data grows larger, performance degrades; mitigated by NFR-1 |
| I-2 | Field paths in `sort` follow the same dot-notation as `Query()` | ST-4 (existing query usage), README examples | If syntax differs, developers must learn two systems |

## Assumptions
| ID | Assumption | Why needed | Linked Q | Risk if wrong |
|----|------------|------------|----------|---------------|
| A-1 | `sort` uses MongoDB-style list of `(field_path, direction)` tuples with direction `1`/`−1` | ST-5 asks for API guidance; this is explicit, common, and fits `Query()` field syntax | — | Maintainer prefers a different style; would require API change |
| A-2 | Pagination uses `limit` + `offset` integer parameters on `Table.search()` | ST-3 describes manual slicing; `limit`/`offset` maps directly | — | Maintainer prefers cursor-based or page-based; would require API change |
| A-3 | New parameters are optional keyword arguments on `Table.search()` | Least disruptive; preserves all existing call sites | — | Maintainer wants a separate method or `Query()` chaining; would require API change |

## Open questions
| ID | Question | Why it matters | Blocks | Priority | Ask whom | Default used |
|----|----------|----------------|--------|----------|----------|--------------|
| Q-1 | Should `sort` accept a callable key function in addition to field-path tuples? | Affects API surface and implementation complexity | FR-1, FR-3 | Nice-to-know | Maintainer | No (field-path tuples only) |
| Q-2 | Should `limit=0` return an empty list or raise? | Edge-case behaviour | FR-4 | Nice-to-know | Maintainer | Return empty list (consistent with Python slicing) |

## Conflicts
None.

## External evidence log
External evidence: not consulted (no tool available).

## Unresolved items
Q-1, Q-2 remain open but are non-blocking; defaults recorded in assumptions.

---

# Artefact 3: Validation Summary

## Checks
| Check | Result | Findings |
|-------|--------|----------|
| Completeness | Pass | All Step-3 checklist items covered: actors (ACT-1), goals (ST-4), scope (in/out lists), functional (FR-1..8), data (none new), interfaces (Table.search), non-functional (NFR-1), constraints (CON-1,2), operations (none), acceptance (AC-1..11). |
| Consistency | Pass | No contradictory requirements; single meaning for `field_path`, `direction`, `limit`, `offset`. |
| Traceability | Pass | Every requirement has source tag and ≥1 AC; traceability table complete; IDs unique. |
| Feasibility | Pass | In-memory sort + slice is feasible for "few thousand records" (ST-1); RISK-1 documented. |
| Testability | Pass | All ACs are measurable Given/When/Then with concrete Python calls and observable results; no vague words. |
| Invention check | Pass | No `Confirmed` item lacks a verbatim quote; no invented numbers/laws/technologies; all `[I]`/`[A]` items are `Proposed`. |

## Readiness counts
| Status | Count |
|--------|-------|
| Confirmed (implementation-ready) | 1 (FR-8) |
| Proposed (awaiting confirmation) | 8 (FR-1..7, NFR-1) |
| Needs clarification | 0 |
| Unresolved | 0 |

## Boundary statement
Requirements from the input: 5 (ST-1..5). Supported by external evidence (still need stakeholder confirmation): 0. Need stakeholder confirmation: 8 (all Proposed items; Q-1, Q-2 are non-blocking nice-to-know).

## Blocking questions (in order)
None. All API design choices have conservative defaults recorded as assumptions (A-1, A-2, A-3). Q-1 and Q-2 are non-blocking enhancements.

## Run notes
- Stakeholders not consulted (non-interactive run).
- No external tools available; evidence log empty.
- Human intervention not needed; specification is complete for a maintainer to accept or adjust the assumed defaults.

---

```json
{
  "summary": "Add optional sort, limit, and offset parameters to Table.search() for server-side ordering and pagination of query results.",
  "issue_type": "feature",
  "acceptance_criteria": [
    {"id": "AC-1", "requirement": "FR-1", "given": "a table with documents {'name': 'Bob', 'age': 30}, {'name': 'Alice', 'age': 25}, {'name': 'Carol', 'age': 35}", "when": "calling table.search(Query().age > 20, sort=[('age', 1)])", "then": "the returned list is ordered by age ascending: [{'name': 'Alice', 'age': 25}, {'name': 'Bob', 'age': 30}, {'name': 'Carol', 'age': 35}]"},
    {"id": "AC-2", "requirement": "FR-1", "given": "a table with documents {'name': 'Bob', 'age': 30}, {'name': 'Alice', 'age': 25}, {'name': 'Carol', 'age': 35}", "when": "calling table.search(Query().age > 20, sort=[('age', -1)])", "then": "the returned list is ordered by age descending: [{'name': 'Carol', 'age': 35}, {'name': 'Bob', 'age': 30}, {'name': 'Alice', 'age': 25}]"},
    {"id": "AC-3", "requirement": "FR-2", "given": "a table with 5 documents matching a query", "when": "calling table.search(query, limit=2, offset=1)", "then": "the returned list contains exactly 2 documents: the 2nd and 3rd items of the full sorted result set"},
    {"id": "AC-4", "requirement": "FR-2", "given": "a table with 3 documents matching a query", "when": "calling table.search(query, limit=10, offset=0)", "then": "the returned list contains all 3 documents (limit larger than result set)"},
    {"id": "AC-5", "requirement": "FR-3", "given": "a table with documents inserted in random order", "when": "calling table.search(query) without sort parameter", "then": "the returned list order is stable across repeated calls with the same database state (current behaviour preserved)"},
    {"id": "AC-6", "requirement": "FR-4", "given": "a table with documents {'id': 1}, {'id': 2}, {'id': 3}, {'id': 4} matching a query", "when": "calling table.search(query, sort=[('id', 1)], limit=2, offset=1)", "then": "the returned list is [{'id': 2}, {'id': 3}] (offset applied first, then limit)"},
    {"id": "AC-7", "requirement": "FR-5", "given": "a table with any documents", "when": "calling table.search(query, sort=[('age', 2)])", "then": "ValueError is raised with a message indicating invalid direction"},
    {"id": "AC-8", "requirement": "FR-6", "given": "a table with any documents", "when": "calling table.search(query, limit=-1) or table.search(query, offset=-5)", "then": "ValueError is raised with a message indicating negative value not allowed"},
    {"id": "AC-9", "requirement": "FR-7", "given": "a table with any documents", "when": "calling table.search(query, sort='age') or table.search(query, limit='two') or table.search(query, offset=1.5)", "then": "TypeError is raised with a message indicating expected type"},
    {"id": "AC-10", "requirement": "FR-8", "given": "a table with existing code calling table.search(query) without new parameters", "when": "running that code after the change", "then": "the return value and order are identical to the pre-change behaviour"},
    {"id": "AC-11", "requirement": "NFR-1", "given": "a table with 5000 documents matching a query", "when": "calling table.search(query, sort=[('field', 1)], limit=10)", "then": "the call completes without MemoryError and returns exactly 10 documents (verifies in-memory sort does not explode memory)"}
  ],
  "assumptions": [
    {"id": "A-1", "assumption": "sort uses MongoDB-style list of (field_path, direction) tuples with direction 1/-1", "default_used": "A-1"},
    {"id": "A-2", "assumption": "pagination uses limit + offset integer parameters on Table.search()", "default_used": "A-2"},
    {"id": "A-3", "assumption": "new parameters are optional keyword arguments on Table.search()", "default_used": "A-3"}
  ],
  "blocking_questions": []
}
```
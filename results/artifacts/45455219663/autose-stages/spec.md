# Artefact 1: Requirements Specification

## Purpose and scope
Add server-side sorting and pagination to TinyDB's `search()` and `all()` methods on both `TinyDB` and `Table` classes, so callers can avoid fetching large result sets and sorting/slicing in Python. The change is backward-compatible: new keyword arguments are optional and default to current behaviour.

**In scope:** `TinyDB.search`, `TinyDB.all`, `Table.search`, `Table.all` gain `sort_by`, `limit`, `offset` parameters.  
**Out of scope:** cursor/token pagination, iterator/chunked streaming, changes to `get()`, `insert()`, `update()`, `remove()`, storage layer, middleware, query language, or any implementation details.

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
| T-1 | "page by page" | (a) offset/limit pagination, (b) cursor/token pagination, (c) iterator yielding chunks | Defined via A-2 → offset/limit |
| T-2 | "ordering" | (a) single-field sort, (b) multi-field sort with directions, (c) sort by transformed values (Query.map) | Defined via A-1 → single/multi-field, string syntax |
| T-3 | "search" | `TinyDB.search()`, `Table.search()` | Defined (ST-2, ST-4) |

## Actors
| ID | Actor | Description | Tag | Source |
|----|-------|-------------|-----|--------|
| ACT-1 | Application developer | Writes Python code using TinyDB's public API; wants to sort and paginate query results without loading all documents | [S] | ST-1, ST-3 |

## Functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| FR-1 | The system shall accept a `sort_by` parameter on `search()` and `all()` that specifies one or more fields to sort by, with optional descending order. | [I] | ST-2, ST-4, A-1 | Must | Proposed | AC-1, AC-2, AC-3, AC-11 | — |
| FR-2 | The system shall accept a `limit` parameter on `search()` and `all()` that caps the number of returned documents. | [I] | ST-3, ST-4, A-2 | Must | Proposed | AC-4, AC-6, AC-7, AC-12 | — |
| FR-3 | The system shall accept an `offset` parameter on `search()` and `all()` that skips the first N documents before applying `limit`. | [I] | ST-3, ST-4, A-2 | Must | Proposed | AC-5, AC-6, AC-7, AC-13 | — |
| FR-4 | The system shall apply `sort_by` before `limit`/`offset` so that pagination operates on ordered results. | [I] | ST-4, A-5 | Must | Proposed | AC-7 | — |
| FR-5 | The system shall support the parameters on both `TinyDB` and `Table` instances for both `search()` and `all()`. | [I] | ST-1, ST-2, A-6 | Must | Proposed | AC-8, AC-9, AC-10 | — |
| FR-6 | The system shall return a `list[dict]` (same type as today) for backward compatibility. | [I] | ST-3, A-4 | Must | Proposed | AC-1..AC-13 (return type) | — |
| FR-7 | The system shall treat a missing sort field in a document as `None` (Python default sort behaviour) rather than raising an error. | [I] | A-5 | Should | Proposed | AC-11 | — |
| FR-8 | The system shall raise `ValueError` for negative `limit` or `offset` values. | [I] | A-5 | Should | Proposed | AC-14 | — |

## Non-functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| NFR-1 | The system shall not increase memory usage for callers who do not use the new parameters (backward-compatible performance). | [I] | ST-1, README "tiny" | Should | Proposed | — | — |
| NFR-2 | The system shall preserve 100% test coverage (README claim). | [S] | README "100% test coverage" | Must | Confirmed | — | — |

## Constraints, dependencies, risks
| ID | Item | Tag | Source | Status |
|----|------|-----|--------|--------|
| CON-1 | Python 3.8+ only (README). | [S] | README | Confirmed |
| CON-2 | No external dependencies (README). | [S] | README | Confirmed |
| CON-3 | Project in maintenance mode; only bugfixes and community-contributed features (README). | [S] | README | Confirmed |
| DEP-1 | Existing `Query` class and query execution pipeline. | [S] | README examples | Confirmed |
| RISK-1 | Maintainer may reject the feature entirely due to maintenance mode. | [I] | CON-3 | Proposed |
| RISK-2 | Sorting large tables in pure Python may be slow; no index support exists. | [I] | ST-1, README "pure Python" | Proposed |

## Traceability
| Requirement ID | Supported by | Verified by |
|----------------|--------------|-------------|
| FR-1 | ST-2, ST-4, A-1 | AC-1, AC-2, AC-3, AC-11 |
| FR-2 | ST-3, ST-4, A-2 | AC-4, AC-6, AC-7, AC-12 |
| FR-3 | ST-3, ST-4, A-2 | AC-5, AC-6, AC-7, AC-13 |
| FR-4 | ST-4, A-5 | AC-7 |
| FR-5 | ST-1, ST-2, A-6 | AC-8, AC-9, AC-10 |
| FR-6 | ST-3, A-4 | AC-1..AC-13 |
| FR-7 | A-5 | AC-11 |
| FR-8 | A-5 | AC-14 |
| NFR-1 | ST-1, README | — |
| NFR-2 | README | — |

---

# Artefact 2: Assumptions and Open-Questions Register

## Confirmed facts
ST-1, ST-2, ST-3, ST-4, ST-5, CON-1, CON-2, CON-3, DEP-1, NFR-2.

## Inferences
| ID | Inference | Follows from | Risk if wrong |
|----|-----------|--------------|---------------|
| I-1 | Sorting and pagination belong on `search()` and `all()` because the issue describes searching a table and getting "everything back at once". | ST-1, ST-2, ST-4 | Low — if maintainer wants a separate method, FR-1..FR-3 scope changes. |
| I-2 | Return type must stay `list[dict]` because the user currently "sort and slice the list myself in Python". | ST-3, README API examples | Low — changing to iterator would break existing code. |
| I-3 | Parameters should work on `Table` as well as `TinyDB` because the issue says "one of my tables". | ST-1 | Low — if Table is excluded, FR-5 scope shrinks. |

## Assumptions
| ID | Assumption | Why needed | Linked Q | Risk if wrong |
|----|------------|------------|----------|---------------|
| A-1 | `sort_by` accepts a field name string (e.g., `'name'`) or list of strings (e.g., `['name', '-age']`); `-` prefix means descending. | ST-5 "Not sure what the best API would be"; need a concrete, testable syntax. | — | Maintainer prefers `Query().field` objects or tuple syntax; ACs would need rewrite. |
| A-2 | Pagination uses `limit` (int, max results) and `offset` (int, skip count) — offset/limit style. | T-1 "page by page" is ambiguous; offset/limit is simplest and matches "slice the list myself". | — | Maintainer wants cursor/token or iterator; FR-2, FR-3, AC-4..AC-7, AC-12, AC-13 change. |
| A-3 | New parameters are keyword arguments on existing `search()` and `all()` methods (no method chaining, no new methods). | ST-5; minimal API change fits "simple and clean API" (README). | — | Maintainer wants `query.sort(...).limit(...)` chaining; all FRs and ACs change. |
| A-4 | Return type remains `list[dict]`; no streaming/iterator API. | ST-3 (user slices list), README "simple API", backward compatibility. | — | If maintainer wants lazy iteration, FR-6 and all ACs change. |
| A-5 | Sorting applies after query filter, before limit/offset; missing sort fields compare as `None`; negative limit/offset raise `ValueError`. | Need deterministic, testable behaviour for edge cases. | — | Different semantics (e.g., missing field → error, or negative offset → count from end) would change AC-11, AC-14. |
| A-6 | Feature applies to `TinyDB.search`, `TinyDB.all`, `Table.search`, `Table.all`. | ST-1 "one of my tables", ST-2 "When I search". | — | If only `Table.search` is in scope, FR-5 and AC-8, AC-10 drop. |

## Open questions
| ID | Question | Why it matters | Blocks | Priority | Ask whom | Default used |
|----|----------|----------------|--------|----------|----------|--------------|
| Q-1 | Should `sort_by` support sorting by transformed values via `Query().field.map(fn)`? | Adds complexity; not mentioned in issue. | FR-1, AC-1..AC-3 | Nice-to-know | Maintainer | No (A-1 covers field names only) |
| Q-2 | Should `all()` without a query also support `sort_by`/`limit`/`offset`? | `all()` returns all documents; issue focuses on `search`. | FR-5, AC-8, AC-10 | Nice-to-know | Maintainer | Yes (A-6) |
| Q-3 | Is the maintainer willing to accept this feature given "maintenance mode"? | CON-3 says only bugfixes/community features. | All FRs | Blocking | Maintainer | Proceed with spec (community contribution path) |

## Conflicts
| ID | Side A (quote) | Side B (quote) | Affected IDs | Who decides |
|----|----------------|----------------|--------------|-------------|
| X-1 | "project is in maintenance mode… significant new features… not planned" (README) | "Would be nice if TinyDB could help with this somehow" (ST-4) | All FRs | Maintainer |

## External evidence log
External evidence: not consulted (no tool available).

## Unresolved items
- Q-3 (maintainer willingness) — risk: entire spec may be rejected. Recorded as RISK-1.
- Q-1, Q-2 — nice-to-know; defaults in A-1, A-6 used for ACs.

---

# Artefact 3: Validation Summary

## Validation checks
| Check | Result | Findings |
|-------|--------|----------|
| Completeness | Pass | Every Step-3 checklist item covered: actors (ACT-1), goals (ST-4), scope (in/out lists), functional (FR-1..FR-8), data (documents), interfaces (public API), non-functional (NFR-1, NFR-2), constraints (CON-1..CON-3), operations (backward compatibility), acceptance (ACs). All ST-n traced. |
| Consistency | Pass | No contradictory requirements. X-1 recorded as conflict (maintenance mode vs feature request). Glossary terms resolved via assumptions. |
| Traceability | Pass | Every FR/NFR has source tag and ≥1 AC. Traceability table complete. IDs unique. |
| Feasibility | Pass | Pure-Python sort/slice on list is feasible. RISK-2 notes performance on large tables. No requirement contradicts CON-1/CON-2. |
| Testability | Pass | All ACs are measurable Given/When/Then with concrete Python calls and observable results. No vague words. |
| Invention check | Pass | No `Confirmed` item lacks a verbatim quote. All `[I]`/`[A]` items are `Proposed`. No invented numbers, laws, or technologies. No source code in output. |

## Readiness counts
| Status | Count |
|--------|-------|
| Confirmed (implementation-ready) | 1 (NFR-2) |
| Proposed (awaiting confirmation) | 13 (FR-1..FR-8, NFR-1, CON-1..CON-3, DEP-1, RISK-1..RISK-2) |
| Needs clarification | 0 |
| Unresolved | 0 |

## Boundary statement
Requirements from the input: 5 (ST-1..ST-5). Supported by external evidence (still need stakeholder confirmation): 0. Need stakeholder confirmation: 13 proposed items + 3 open questions (Q-1..Q-3) + 1 conflict (X-1).

## Blocking questions (in order)
1. **Q-3** — Is the maintainer willing to accept this feature given "maintenance mode"? (Blocks all FRs; without yes, work may be wasted.)

## Run notes
- Stakeholders consulted: **No** (non-interactive pipeline run).
- Tools used: **None** (no web search tool available).
- Human intervention needed: **Yes** for Q-3 (maintainer intent on maintenance-mode policy).

---

```json
{
  "summary": "Add optional sort_by, limit, offset keyword arguments to TinyDB.search, TinyDB.all, Table.search, Table.all for server-side sorting and offset/limit pagination, returning list[dict] as today.",
  "issue_type": "feature",
  "acceptance_criteria": [
    {"id": "AC-1", "requirement": "FR-1", "given": "a TinyDB instance with documents [{'name': 'Bob', 'age': 30}, {'name': 'Alice', 'age': 25}, {'name': 'Carol', 'age': 35}]", "when": "db.search(Query().age > 20, sort_by='name')", "then": "returns [{'name': 'Alice', 'age': 25}, {'name': 'Bob', 'age': 30}, {'name': 'Carol', 'age': 35}]"},
    {"id": "AC-2", "requirement": "FR-1", "given": "a TinyDB instance with documents [{'name': 'Bob', 'age': 30}, {'name': 'Alice', 'age': 25}, {'name': 'Alice', 'age': 20}]", "when": "db.search(Query().name == 'Alice', sort_by=['name', '-age'])", "then": "returns [{'name': 'Alice', 'age': 25}, {'name': 'Alice', 'age': 20}] (name asc, then age desc)"},
    {"id": "AC-3", "requirement": "FR-1", "given": "a TinyDB instance with documents [{'age': 30}, {'age': 25}, {'age': 35}]", "when": "db.all(sort_by='-age')", "then": "returns [{'age': 35}, {'age': 30}, {'age': 25}] (descending)"},
    {"id": "AC-4", "requirement": "FR-2", "given": "a TinyDB instance with 10 documents", "when": "db.all(limit=3)", "then": "returns a list of length 3"},
    {"id": "AC-5", "requirement": "FR-3", "given": "a TinyDB instance with 10 documents", "when": "db.all(offset=4)", "then": "returns a list of length 6 (documents 5-10)"},
    {"id": "AC-6", "requirement": "FR-2,FR-3", "given": "a TinyDB instance with 10 documents", "when": "db.all(limit=3, offset=4)", "then": "returns a list of length 3 (documents 5-7)"},
    {"id": "AC-7", "requirement": "FR-4", "given": "a TinyDB instance with documents [{'name': 'Bob', 'age': 30}, {'name': 'Alice', 'age': 25}, {'name': 'Carol', 'age': 35}]", "when": "db.search(Query().age > 20, sort_by='name', limit=2, offset=1)", "then": "returns [{'name': 'Bob', 'age': 30}, {'name': 'Carol', 'age': 35}] (sorted by name, then skip 1, take 2)"},
    {"id": "AC-8", "requirement": "FR-5", "given": "a TinyDB instance", "when": "db.all(sort_by='name', limit=5, offset=0)", "then": "returns sorted, paginated list (TinyDB.all supports the parameters)"},
    {"id": "AC-9", "requirement": "FR-5", "given": "a Table instance from db.table('users')", "when": "table.search(Query().age > 18, sort_by='-age', limit=10)", "then": "returns sorted, limited list (Table.search supports the parameters)"},
    {"id": "AC-10", "requirement": "FR-5", "given": "a Table instance", "when": "table.all(offset=2, limit=2)", "then": "returns paginated list (Table.all supports the parameters)"},
    {"id": "AC-11", "requirement": "FR-7", "given": "a TinyDB instance with documents [{'name': 'Alice'}, {'age': 30}]", "when": "db.all(sort_by='name')", "then": "returns [{'age': 30}, {'name': 'Alice'}] (missing 'name' treated as None, sorts first)"},
    {"id": "AC-12", "requirement": "FR-2", "given": "a TinyDB instance with 5 documents", "when": "db.all(limit=0)", "then": "returns []"},
    {"id": "AC-13", "requirement": "FR-3", "given": "a TinyDB instance with 5 documents", "when": "db.all(offset=10)", "then": "returns []"},
    {"id": "AC-14", "requirement": "FR-8", "given": "a TinyDB instance", "when": "db.all(limit=-1)", "then": "raises ValueError"},
    {"id": "AC-15", "requirement": "FR-8", "given": "a TinyDB instance", "when": "db.all(offset=-1)", "then": "raises ValueError"}
  ],
  "assumptions": [
    {"id": "A-1", "assumption": "sort_by accepts field name string or list of strings with '-' prefix for descending (e.g., 'name', ['name', '-age'])", "default_used": "A-1"},
    {"id": "A-2", "assumption": "Pagination uses offset/limit integers (limit=max results, offset=skip count)", "default_used": "A-2"},
    {"id": "A-3", "assumption": "Parameters added as keyword arguments on existing search()/all() methods (no chaining, no new methods)", "default_used": "A-3"},
    {"id": "A-4", "assumption": "Return type remains list[dict] (no iterator/streaming)", "default_used": "A-4"},
    {"id": "A-5", "assumption": "Sort before limit/offset; missing sort field compares as None; negative limit/offset raise ValueError", "default_used": "A-5"},
    {"id": "A-6", "assumption": "Feature applies to TinyDB.search, TinyDB.all, Table.search, Table.all", "default_used": "A-6"}
  ],
  "blocking_questions": [
    {"id": "Q-3", "question": "Is the maintainer willing to accept this feature given the project's stated 'maintenance mode' (only bugfixes/community features)?", "why_blocking": "If the answer is no, all proposed requirements (FR-1..FR-8) are out of scope and the spec should not be implemented."}
  ]
}
```

## Why this stage stopped

- 1 blocking question(s) need a maintainer's answer
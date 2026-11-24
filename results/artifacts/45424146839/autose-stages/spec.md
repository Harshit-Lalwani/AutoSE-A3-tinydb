# Artefact 1: Requirements Specification

## Purpose and scope
Add optional sorting and paging capabilities to TinyDB's `search()` method so users can order results and retrieve subsets without post-processing in Python. The change is backward-compatible and limited to the public `Table.search()` / `TinyDB.search()` API.

**In scope:** `search(query, sort=..., limit=..., offset=...)` parameters; documentation updates; tests.  
**Out of scope:** cursor/iterator API, server-side indexes, query planner changes, any storage-layer modification, implementation code.

## Input statements
| ID | Verbatim quote |
|----|----------------|
| ST-1 | "When I search I get everything back at once and in whatever order, and then I sort and slice the list myself in Python." |
| ST-2 | "Would be nice if TinyDB could help with this somehow, ordering and getting results page by page." |
| ST-3 | "Not sure what the best API would be." |

## Glossary
| ID | Term | Possible meanings | Status |
|----|------|-------------------|--------|
| T-1 | sort | List of (field, direction) tuples; direction 1=asc, -1=desc | Defined (A-1) |
| T-2 | limit | Maximum number of documents to return | Defined (A-1) |
| T-3 | offset | Number of documents to skip before returning | Defined (A-1) |

## Actors
| ID | Actor | Description | Tag | Source |
|----|-------|-------------|-----|--------|
| ACT-1 | Application developer | Writes Python code using TinyDB; wants to sort and page search results | [S] | ST-1, ST-2 |

## Functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| FR-1 | The system shall accept an optional `sort` parameter in `search()` that specifies a list of (field_path, direction) tuples where direction is 1 (ascending) or -1 (descending). | [A] | ST-2, ST-3 | Must | Proposed | AC-1, AC-2, AC-3 | — |
| FR-2 | The system shall accept an optional `limit` parameter in `search()` that restricts the number of returned documents to at most the given non-negative integer. | [A] | ST-2, ST-3 | Must | Proposed | AC-4, AC-5 | — |
| FR-3 | The system shall accept an optional `offset` parameter in `search()` that skips the first N matching documents before applying `limit`. | [A] | ST-2, ST-3 | Must | Proposed | AC-6, AC-7 | — |
| FR-4 | The system shall apply sorting before limit/offset when both are provided. | [I] | FR-1, FR-2, FR-3 | Must | Proposed | AC-8 | — |
| FR-5 | The system shall raise `TypeError` if `sort` is not a list of 2-tuples, or if direction is not 1 or -1. | [I] | FR-1 | Should | Proposed | AC-9 | — |
| FR-6 | The system shall raise `ValueError` if `limit` or `offset` is negative. | [I] | FR-2, FR-3 | Should | Proposed | AC-10 | — |
| FR-7 | The system shall return an empty list when `offset` exceeds the number of matching documents. | [I] | FR-3 | Must | Proposed | AC-11 | — |

## Non-functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| NFR-1 | The system shall not change the behaviour of existing `search(query)` calls without the new parameters. | [S] | ST-1 (implied) | Must | Confirmed | AC-12 | — |
| NFR-2 | The system shall work with all existing storage backends and middlewares without modification. | [I] | README "powerfully extensible" | Must | Proposed | AC-13 | — |

## Constraints, dependencies, risks
| ID | Item | Tag | Source | Status |
|----|------|-----|--------|--------|
| CON-1 | Python 3.8+ compatibility must be maintained | [S] | README | Confirmed |
| CON-2 | Zero external dependencies must be maintained | [S] | README | Confirmed |
| DEP-1 | Existing `Query` and `where` classes unchanged | [I] | FR-1..FR-3 | Proposed |
| RISK-1 | Large offset values on large tables may be slow (full scan) | [I] | FR-3 | Proposed |

## Traceability
| Requirement ID | Supported by | Verified by |
|----------------|--------------|-------------|
| FR-1 | ST-2, ST-3, A-1 | AC-1, AC-2, AC-3 |
| FR-2 | ST-2, ST-3, A-1 | AC-4, AC-5 |
| FR-3 | ST-2, ST-3, A-1 | AC-6, AC-7 |
| FR-4 | FR-1, FR-2, FR-3 | AC-8 |
| FR-5 | FR-1 | AC-9 |
| FR-6 | FR-2, FR-3 | AC-10 |
| FR-7 | FR-3 | AC-11 |
| NFR-1 | ST-1 | AC-12 |
| NFR-2 | README | AC-13 |

---

# Artefact 2: Assumptions and Open-Questions Register

## Confirmed facts
ST-1, ST-2, ST-3, CON-1, CON-2

## Inferences
| ID | Inference | Follows from | Risk if wrong |
|----|-----------|--------------|---------------|
| I-1 | Sorting and paging are applied in-memory after the query matches (no index support) | TinyDB has no query planner or indexes; README says "tiny" and "no external dependencies" | Performance on large tables may disappoint users expecting DB-style optimization |
| I-2 | `sort` field paths use the same dot-notation as `Query` (e.g. `user.name`) | Consistency with existing query language | If different syntax is needed, API feels inconsistent |

## Assumptions
| ID | Assumption | Why needed | Linked Q | Risk if wrong |
|----|------------|------------|----------|---------------|
| A-1 | API uses `search(query, sort=[('field', 1)], limit=10, offset=0)` — optional keyword arguments on the existing `search()` method | ST-3 says "not sure what the best API would be"; this is the minimal, backward-compatible extension following Python conventions (Django, SQLAlchemy, PyMongo) | — | Maintainer prefers a different API (e.g. Query method chaining); would require rewrite |

## Open questions
| ID | Question | Why it matters | Blocks | Priority | Ask whom | Default used |
|----|----------|----------------|--------|----------|----------|--------------|
| Q-1 | Should `sort` accept a callable for custom ordering? | Adds flexibility but complicates API | FR-1 | Nice-to-know | Maintainer | No (not in MVP) |
| Q-2 | Should `limit=0` mean "no limit" or "return empty list"? | Edge case | FR-2 | Nice-to-know | Maintainer | `limit=0` → empty list (consistent with Python slicing) |

## Conflicts
None.

## External evidence log
External evidence: not consulted (no tool available).

## Unresolved items
None.

---

# Artefact 3: Validation Summary

## Checks
| Check | Result | Findings |
|-------|--------|----------|
| Completeness | Pass | All Step-3 checklist items covered: actors (ACT-1), goals (ST-2), scope (in/out lists), functional (FR-1..7), non-functional (NFR-1..2), data (N/A), interfaces (search()), constraints (CON-1..2), operations (N/A), acceptance (AC-1..13). |
| Consistency | Pass | No contradictory requirements; glossary defines all terms; FR-4 orders sort before limit/offset. |
| Traceability | Pass | Every requirement has source tag and ≥1 AC; traceability table complete; IDs unique. |
| Feasibility | Pass | In-memory sort/slice on list of dicts is trivial in Python; no storage changes needed. RISK-1 documented. |
| Testability | Pass | All ACs are measurable Given/When/Then with concrete Python calls; no vague words. |
| Invention check | Pass | No `Confirmed` item lacks exact quote; A-1 is explicitly `[A]` with status `Proposed`; no invented numbers/laws. |

## Readiness counts
| Status | Count |
|--------|-------|
| Confirmed (implementation-ready) | 2 (NFR-1, CON-1, CON-2) |
| Proposed | 9 (FR-1..7, NFR-2, DEP-1, RISK-1) |
| Needs clarification | 0 |
| Unresolved | 0 |

## Boundary statement
Requirements from the input: 3 (ST-1..3). Supported by external evidence (still need stakeholder confirmation): 0. Need stakeholder confirmation: 1 (A-1 — API shape).

## Blocking questions (would unlock most requirements)
None. A-1 is an assumption with a conservative default; if the maintainer rejects it, the pipeline will stop at the design stage, not here.

## Run notes
Stakeholders not consulted (non-interactive run). No tools available. Human intervention not needed.

---

```json
{
  "summary": "Add optional sort, limit, and offset parameters to TinyDB's search() method for server-side ordering and paging of query results.",
  "issue_type": "feature",
  "acceptance_criteria": [
    {"id": "AC-1", "requirement": "FR-1", "given": "a table with documents {'name': 'Bob', 'age': 30}, {'name': 'Alice', 'age': 25}, {'name': 'Carol', 'age': 35}", "when": "db.search(Query().age > 20, sort=[('age', 1)])", "then": "returns documents ordered by age ascending: Alice (25), Bob (30), Carol (35)"},
    {"id": "AC-2", "requirement": "FR-1", "given": "same table", "when": "db.search(Query().age > 20, sort=[('age', -1)])", "then": "returns documents ordered by age descending: Carol (35), Bob (30), Alice (25)"},
    {"id": "AC-3", "requirement": "FR-1", "given": "documents with nested field {'user': {'name': 'Bob', 'score': 10}}, {'user': {'name': 'Alice', 'score': 20}}", "when": "db.search(Query().user.score > 5, sort=[('user.score', 1)])", "then": "returns Alice first, then Bob (dot-notation field path works)"},
    {"id": "AC-4", "requirement": "FR-2", "given": "table with 5 matching documents", "when": "db.search(Query().active == True, limit=3)", "then": "returns exactly 3 documents"},
    {"id": "AC-5", "requirement": "FR-2", "given": "table with 2 matching documents", "when": "db.search(Query().active == True, limit=10)", "then": "returns both documents (no error)"},
    {"id": "AC-6", "requirement": "FR-3", "given": "table with documents [A, B, C, D, E] matching query", "when": "db.search(query, offset=2, limit=2)", "then": "returns [C, D] (skips first 2, takes next 2)"},
    {"id": "AC-7", "requirement": "FR-3", "given": "table with 3 matching documents", "when": "db.search(query, offset=10)", "then": "returns empty list"},
    {"id": "AC-8", "requirement": "FR-4", "given": "documents [{'x': 3}, {'x': 1}, {'x': 2}]", "when": "db.search(Query().x > 0, sort=[('x', 1)], limit=2, offset=1)", "then": "returns [{'x': 2}, {'x': 3}] (sort applied before limit/offset)"},
    {"id": "AC-9", "requirement": "FR-5", "given": "any table", "when": "db.search(query, sort='invalid')", "then": "raises TypeError"},
    {"id": "AC-10", "requirement": "FR-6", "given": "any table", "when": "db.search(query, limit=-1) or db.search(query, offset=-1)", "then": "raises ValueError"},
    {"id": "AC-11", "requirement": "FR-7", "given": "table with 2 matching documents", "when": "db.search(query, offset=5)", "then": "returns empty list"},
    {"id": "AC-12", "requirement": "NFR-1", "given": "existing code calling db.search(Query().name == 'John')", "when": "the same call is executed after the change", "then": "returns identical results in identical order (insertion order) with no new parameters required"},
    {"id": "AC-13", "requirement": "NFR-2", "given": "a TinyDB instance using CachingMiddleware(JSONStorage)", "when": "search() is called with sort, limit, offset", "then": "works without middleware changes and returns correct paged/sorted results"}
  ],
  "assumptions": [
    {"id": "A-1", "assumption": "API uses search(query, sort=[('field', 1)], limit=10, offset=0) — optional keyword arguments on existing search() method", "default_used": "minimal backward-compatible extension following Python conventions (Django, SQLAlchemy, PyMongo)"}
  ],
  "blocking_questions": []
}
```
# Artefact 1: Requirements Specification

## Purpose and scope
Add optional server-side sorting and paging to TinyDB's `Table.search()` and `Table.all()` methods so that callers can receive ordered, windowed results without post-processing in Python. The change is purely additive: existing calls without the new parameters behave exactly as before.

**In scope**
- New optional parameters on `Table.search()` and `Table.all()`
- Sorting by one or more document fields, ascending or descending
- Paging via `limit` and `offset`
- Input validation with clear exceptions
- Preservation of 100% test coverage

**Out of scope**
- Cursor/keyset pagination, streaming results, or index-backed ordering
- Changes to `Query` syntax beyond what is needed for the new parameters
- Any modification to storage or middleware layers
- Implementation (this is a specification only)

## Input statements
| ID | Verbatim quote |
|----|----------------|
| ST-1 | "When I search I get everything back at once and in whatever order, and then I sort and slice the list myself in Python." |
| ST-2 | "Would be nice if TinyDB could help with this somehow, ordering and getting results page by page." |
| ST-3 | "Not sure what the best API would be." |

## Glossary
| ID | Term | Possible meanings | Status |
|----|------|-------------------|--------|
| T-1 | "ordering" / "sorting" | Arrange result documents by one or more field values, ascending or descending | Defined (FR-1) |
| T-2 | "paging" / "page by page" | Return a contiguous slice of the ordered result set | Defined (FR-2) |
| T-3 | "whatever order" | Current implementation returns documents in storage order (insertion order for JSONStorage) | Defined (inferred from ST-1) |

## Actors
| ID | Actor | Description | Tag | Source |
|----|-------|-------------|-----|--------|
| ACT-1 | Application developer | Writes Python code that calls `Table.search()` / `Table.all()` | [S] | ST-1, ST-2 |
| ACT-2 | TinyDB maintainer | Reviews and merges the pull request | [I] | Project context |

## Functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| FR-1 | The system shall accept an optional `sort_by` parameter on `Table.search()` and `Table.all()` that specifies one or more fields to sort by, with optional descending direction per field. | [I] | ST-1, ST-2, ST-3 | Must | Proposed | AC-1, AC-2, AC-3, AC-4, AC-5 | — |
| FR-2 | The system shall accept optional `limit` and `offset` parameters on `Table.search()` and `Table.all()` to return a slice of the (optionally sorted) result set. | [I] | ST-1, ST-2 | Must | Proposed | AC-6, AC-7, AC-8, AC-9, AC-10 | — |
| FR-3 | The system shall raise `TypeError` when `sort_by`, `limit`, or `offset` values are of invalid type. | [I] | ST-3 | Must | Proposed | AC-11, AC-12, AC-13 | — |
| FR-4 | The system shall raise `ValueError` when `limit` or `offset` are negative. | [I] | ST-3 | Must | Proposed | AC-14, AC-15 | — |
| FR-5 | The system shall apply sorting before paging when both are provided. | [I] | ST-1, ST-2 | Must | Proposed | AC-16 | — |
| FR-6 | The system shall not modify the behaviour of calls that omit the new parameters. | [S] | ST-1 | Must | Confirmed | AC-17 | — |

## Non-functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Quality (ISO 25010) |
|----|-------------|-----|--------|----------|--------|---------------------|---------------------|
| NFR-1 | The system shall maintain 100% test coverage after the change. | [S] | README "100% test coverage" | Must | Confirmed | AC-18 | Maintainability |
| NFR-2 | The system shall not introduce external dependencies. | [S] | README "no external dependencies" | Must | Confirmed | AC-19 | Compatibility |
| NFR-3 | The system shall support Python 3.8+ and PyPy3. | [S] | README "Supported Python Versions" | Must | Confirmed | AC-20 | Portability |

## Constraints, dependencies, risks
| ID | Item | Tag | Source | Status |
|----|------|-----|--------|--------|
| CON-1 | Project is in maintenance mode; only bugfixes and community-contributed features are accepted. | [S] | README "Project Status" | Confirmed |
| DEP-1 | Existing `Table.search()` and `Table.all()` signatures and return types. | [S] | README Example Code | Confirmed |
| RISK-1 | If the chosen `sort_by` syntax diverges from future maintainer preference, a breaking change may be needed later. | [I] | ST-3, CON-1 | Proposed (Impact: Medium, Mitigation: Document as provisional in docstring) |

## Traceability
| Requirement ID | Supported by | Verified by |
|----------------|--------------|-------------|
| FR-1 | ST-1, ST-2, ST-3, A-1 | AC-1–AC-5 |
| FR-2 | ST-1, ST-2, A-2 | AC-6–AC-10 |
| FR-3 | ST-3 | AC-11–AC-13 |
| FR-4 | ST-3 | AC-14–AC-15 |
| FR-5 | ST-1, ST-2 | AC-16 |
| FR-6 | ST-1 | AC-17 |
| NFR-1 | README | AC-18 |
| NFR-2 | README | AC-19 |
| NFR-3 | README | AC-20 |

---

# Artefact 2: Assumptions and Open-Questions Register

## Confirmed facts
ST-1, ST-2, ST-3, CON-1, DEP-1, NFR-1, NFR-2, NFR-3 (all `[S]`)

## Inferences
| ID | Inference | Follows from | Risk if wrong |
|----|-----------|--------------|---------------|
| I-1 | Sorting and paging are applied in-memory on the full result list (no storage-level optimisation). | ST-1 ("get everything back at once"), TinyDB architecture (no query planner) | Low — matches current performance profile |
| I-2 | `sort_by` accepts a list of field specifiers; a leading `-` means descending (e.g., `['name', '-age']`). | ST-3 ("Not sure what the best API would be"), common Python convention (Django, DRF) | Medium — maintainer may prefer a different syntax; mitigated by A-1 |
| I-3 | `limit` and `offset` are independent non-negative integers; `offset` defaults to 0, `limit` defaults to None (no limit). | ST-2 ("page by page"), universal paging convention | Low — standard behaviour |

## Assumptions
| ID | Assumption | Why needed | Linked Q | Default used | Risk if wrong |
|----|------------|------------|----------|--------------|---------------|
| A-1 | `sort_by` parameter format: list of strings, `-` prefix for descending (e.g., `sort_by=['name', '-created_at']`). | ST-3 leaves API open; a concrete signature is required to write testable ACs. | — | List of strings with `-` prefix for desc | Maintainer prefers `Query().field.asc()/desc()` objects or tuple format; would require signature change. |
| A-2 | Paging parameters: `limit` (int or None) and `offset` (int, default 0). Mutual exclusion with page/page_size not required. | ST-3 leaves API open; limit/offset is the most universal and conservative choice. | — | `limit` and `offset` only | Maintainer wants page/page_size instead or in addition; would require parameter change. |
| A-3 | Sorting is stable and uses Python's default comparison (works for str, int, float, None; mixed types raise TypeError). | Needed to define observable behaviour for ACs. | — | Python's `list.sort()` semantics | Documents with incomparable field values (e.g., str vs int) raise during search; may surprise users. |
| A-4 | Missing fields in a document are treated as `None` for sorting purposes (consistent with `Query().field == value` not matching missing fields). | Needed to define observable behaviour for ACs. | — | Missing → `None` | Maintainer prefers missing fields to sort last/first or raise; would change sort order. |

## Open questions
| ID | Question | Why it matters | Blocks | Priority | Ask whom | Default used |
|----|----------|----------------|--------|----------|----------|--------------|
| Q-1 | Should `sort_by` also accept a single string (e.g., `sort_by='name'`) in addition to a list? | Ergonomics for single-field sort. | FR-1 | Nice-to-know | Maintainer | No (list only) — keeps type validation simple |
| Q-2 | Should the `Query` class gain `.asc()` / `.desc()` helpers for a more fluent API (e.g., `sort_by=[User.name.asc(), User.age.desc()]`)? | API consistency with existing `Query` patterns. | FR-1 | Nice-to-know | Maintainer | No — string list is sufficient for MVP |

## Conflicts
None found. The contradiction sweep compared:
- Restriction: "Project is in maintenance mode; significant new features not planned" (CON-1)
- Capability: "Add sorting and paging" (FR-1, FR-2)
→ No contradiction: community-contributed features are explicitly welcome (README).

## External evidence log
External evidence: not consulted (no tool available). All gaps resolved via assumptions A-1–A-4.

## Unresolved items
None. All gaps have conservative defaults recorded as assumptions.

---

# Artefact 3: Validation Summary

## Validation checks
| Check | Result | Findings |
|-------|--------|----------|
| Completeness | Pass | Every Step-3 checklist item covered: actors (ACT-1), goals (FR-1, FR-2), scope (in/out lists), functional (FR-1–6), data (sort/paging on documents), interfaces (Table.search/all), non-functional (NFR-1–3), constraints (CON-1), operations (no change), acceptance (ACs). All ST-n traced. |
| Consistency | Pass | No contradictory requirements. Single meaning for "sorting", "paging" (glossary). FR-5 explicitly orders sort before paging. |
| Traceability | Pass | Every requirement has source tag, at least one AC, traceability row. IDs unique. |
| Feasibility | Pass | In-memory sort/slice on list of dicts is trivial in Python. No storage changes. Risks documented (RISK-1). |
| Testability | Pass | All ACs are Given/When/Then with concrete Python calls and observable results. No vague words. |
| Invention check | Pass | Confirmed items (FR-6, NFR-1–3, CON-1, DEP-1) have exact quotes. Proposed items tagged [I] with rationale. Assumptions A-1–A-4 explicit. No invented numbers, laws, or users. |

## Readiness counts
| Status | Count |
|--------|-------|
| Confirmed (implementation-ready) | 4 (FR-6, NFR-1, NFR-2, NFR-3) |
| Proposed (awaiting confirmation) | 9 (FR-1–5, NFR-1–3 are confirmed; FR-1–5 proposed, RISK-1 proposed) |
| Needs clarification | 0 |
| Unresolved | 0 |

## Boundary statement
Requirements from the input: 3 (ST-1, ST-2, ST-3). Supported by external evidence (still need stakeholder confirmation): 0. Need stakeholder confirmation: 6 proposed requirements + 4 assumptions.

## Blocking questions (would unlock most requirements)
None. All proposed requirements have conservative defaults in A-1–A-4 and testable acceptance criteria. Q-1 and Q-2 are "Nice-to-know" only.

## Run notes
- Stakeholders consulted: No (non-interactive pipeline run).
- Tools used: None available.
- Human intervention needed: No.

---

```json
{
  "summary": "Add optional sort_by, limit, and offset parameters to Table.search() and Table.all() for server-side ordering and paging of query results.",
  "issue_type": "feature",
  "acceptance_criteria": [
    {"id": "AC-1", "requirement": "FR-1", "given": "a table with documents [{'name': 'Bob', 'age': 30}, {'name': 'Alice', 'age': 25}, {'name': 'Alice', 'age': 35}]", "when": "calling table.search(Query().name.exists(), sort_by=['name', 'age'])", "then": "the returned list equals [{'name': 'Alice', 'age': 25}, {'name': 'Alice', 'age': 35}, {'name': 'Bob', 'age': 30}]"},
    {"id": "AC-2", "requirement": "FR-1", "given": "a table with documents [{'name': 'Bob', 'age': 30}, {'name': 'Alice', 'age': 25}]", "when": "calling table.search(Query().name.exists(), sort_by=['-name'])", "then": "the returned list equals [{'name': 'Bob', 'age': 30}, {'name': 'Alice', 'age': 25}]"},
    {"id": "AC-3", "requirement": "FR-1", "given": "a table with documents [{'name': 'Bob'}, {'name': 'Alice', 'age': 25}]", "when": "calling table.search(Query().name.exists(), sort_by=['age'])", "then": "the returned list equals [{'name': 'Bob'}, {'name': 'Alice', 'age': 25}] (missing field treated as None, sorts first)"},
    {"id": "AC-4", "requirement": "FR-1", "given": "a table with documents [{'name': 'Bob', 'age': 30}, {'name': 'Alice', 'age': 25}]", "when": "calling table.all(sort_by=['name'])", "then": "the returned list equals [{'name': 'Alice', 'age': 25}, {'name': 'Bob', 'age': 30}]"},
    {"id": "AC-5", "requirement": "FR-1", "given": "a table with documents [{'name': 'Bob', 'age': 30}, {'name': 'Alice', 'age': 25}]", "when": "calling table.search(Query().name.exists(), sort_by='name')", "then": "TypeError is raised (sort_by must be a list)"},
    {"id": "AC-6", "requirement": "FR-2", "given": "a table with 5 documents", "when": "calling table.all(limit=2, offset=1)", "then": "the returned list contains exactly 2 documents (the 2nd and 3rd in storage order)"},
    {"id": "AC-7", "requirement": "FR-2", "given": "a table with 3 documents", "when": "calling table.all(limit=10)", "then": "the returned list contains all 3 documents (limit larger than result set)"},
    {"id": "AC-8", "requirement": "FR-2", "given": "a table with 3 documents", "when": "calling table.all(offset=5)", "then": "the returned list is empty (offset beyond result set)"},
    {"id": "AC-9", "requirement": "FR-2", "given": "a table with documents [{'name': 'Bob', 'age': 30}, {'name': 'Alice', 'age': 25}, {'name': 'Carol', 'age': 35}]", "when": "calling table.search(Query().name.exists(), sort_by=['age'], limit=2, offset=1)", "then": "the returned list equals [{'name': 'Bob', 'age': 30}, {'name': 'Carol', 'age': 35}] (sort applied before paging)"},
    {"id": "AC-10", "requirement": "FR-2", "given": "a table with 3 documents", "when": "calling table.all(limit=None, offset=0)", "then": "the returned list contains all 3 documents (explicit defaults behave like no paging)"},
    {"id": "AC-11", "requirement": "FR-3", "given": "a table with documents", "when": "calling table.search(Query().name.exists(), sort_by='name')", "then": "TypeError is raised with message indicating sort_by must be a list"},
    {"id": "AC-12", "requirement": "FR-3", "given": "a table with documents", "when": "calling table.all(limit='two')", "then": "TypeError is raised with message indicating limit must be an integer or None"},
    {"id": "AC-13", "requirement": "FR-3", "given": "a table with documents", "when": "calling table.all(offset=1.5)", "then": "TypeError is raised with message indicating offset must be an integer"},
    {"id": "AC-14", "requirement": "FR-4", "given": "a table with documents", "when": "calling table.all(limit=-1)", "then": "ValueError is raised with message indicating limit must be non-negative"},
    {"id": "AC-15", "requirement": "FR-4", "given": "a table with documents", "when": "calling table.all(offset=-1)", "then": "ValueError is raised with message indicating offset must be non-negative"},
    {"id": "AC-16", "requirement": "FR-5", "given": "a table with documents [{'name': 'Bob', 'age': 30}, {'name': 'Alice', 'age': 25}, {'name': 'Carol', 'age': 35}]", "when": "calling table.search(Query().name.exists(), sort_by=['-age'], limit=2)", "then": "the returned list equals [{'name': 'Carol', 'age': 35}, {'name': 'Bob', 'age': 30}] (sorted descending by age, then limited)"},
    {"id": "AC-17", "requirement": "FR-6", "given": "a table with documents [{'name': 'Bob'}, {'name': 'Alice'}]", "when": "calling table.search(Query().name.exists()) and table.all()", "then": "both return [{'name': 'Bob'}, {'name': 'Alice'}] in storage order (unchanged behaviour)"},
    {"id": "AC-18", "requirement": "NFR-1", "given": "the modified codebase", "when": "running the test suite with coverage", "then": "coverage remains 100%"},
    {"id": "AC-19", "requirement": "NFR-2", "given": "the modified codebase", "when": "inspecting setup.py / pyproject.toml and import statements", "then": "no new external dependencies are declared or imported"},
    {"id": "AC-20", "requirement": "NFR-3", "given": "the modified codebase", "when": "running the test suite on Python 3.8, 3.9, 3.10, 3.11, 3.12, 3.13 and PyPy3", "then": "all tests pass"}
  ],
  "assumptions": [
    {"id": "A-1", "assumption": "sort_by parameter format: list of strings, '-' prefix for descending (e.g., sort_by=['name', '-created_at'])", "default_used": "List of strings with '-' prefix for desc"},
    {"id": "A-2", "assumption": "Paging parameters: limit (int or None) and offset (int, default 0). No page/page_size parameters.", "default_used": "limit and offset only"},
    {"id": "A-3", "assumption": "Sorting uses Python's default comparison; missing fields treated as None; mixed comparable types raise TypeError during sort.", "default_used": "Python list.sort() semantics with missing -> None"},
    {"id": "A-4", "assumption": "Stable sort; documents with equal sort keys retain their relative order from the unsorted result.", "default_used": "Python's stable sort guarantee"}
  ],
  "blocking_questions": []
}
```
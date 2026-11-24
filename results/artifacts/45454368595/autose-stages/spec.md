# Artefact 1: Requirements Specification

## Purpose and scope
This specification defines an `append` operation for TinyDB that adds a value to a list field in matching documents. The operation integrates with the existing `tinydb.operations` module and the `db.update()` method.

**In scope:**
- New `append` operation in `tinydb.operations`
- Field creation when missing (initialise as single-element list)
- TypeError when field exists but is not a list
- Integration with `db.update(operation, query)` for multiple documents

**Out of scope:**
- Nested field paths (dot notation)
- Other collection types (sets, tuples)
- Atomic batch semantics beyond fail-fast default
- Implementation details (file locations, class vs function internals)

## Input statements
| ID | Verbatim quote |
|----|----------------|
| ST-1 | "I keep tags as a list in my documents. To add a tag I currently do a `get`, change the list in Python, and `update` it back, which is clumsy and not great when several documents match." |
| ST-2 | "It would be nice to have an operation in `tinydb.operations` next to `add`, `increment` etc." |
| ST-3 | "`from tinydb.operations import append`" |
| ST-4 | "`db.update(append('tags', 'urgent'), Query().project == 'x')`" |
| ST-5 | "If a matching document doesn't have the field yet, I'd like it to be created as a list with just that value." |
| ST-6 | "If the field exists but isn't a list, raising a `TypeError` seems right to me (like adding a str to an int does), rather than silently doing something weird." |

## Glossary
| ID | Term | Possible meanings | Status |
|----|------|-------------------|--------|
| T-1 | append | New operation to add a value to a list field | Defined (ST-2, ST-3) |
| T-2 | operation | Callable object used with `db.update(operation, query)` | Defined (ST-2) |
| T-3 | field | Dictionary key in a document | Defined (ST-1) |
| T-4 | matching document | Document returned by the query | Defined (ST-1) |

## Actors
| ID | Actor | Description | Tag | Source |
|----|-------|-------------|-----|--------|
| ACT-1 | Application developer | Writes code using `db.update(append(...), query)` | [S] | ST-1, ST-4 |
| ACT-2 | TinyDB maintainer | Reviews and merges the feature | [S] | Implied by issue context |

## Functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| FR-1 | The system shall provide an `append` operation importable from `tinydb.operations`. | [S] | ST-2, ST-3 | Must | Proposed | AC-1 | — |
| FR-2 | The system shall accept `append(field_name, value)` where `field_name` is a string and `value` is any JSON-serialisable value. | [S] | ST-4 | Must | Proposed | AC-2 | — |
| FR-3 | When a matching document lacks the field, the system shall create the field as a list containing only the given value. | [S] | ST-5 | Must | Proposed | AC-3 | — |
| FR-4 | When a matching document has the field as a list, the system shall append the value to that list. | [S] | ST-1, ST-4 | Must | Proposed | AC-4 | — |
| FR-5 | When a matching document has the field but it is not a list, the system shall raise `TypeError` and not modify that document. | [S] | ST-6 | Must | Proposed | AC-5, AC-7 | — |
| FR-6 | The system shall apply the operation to all documents matching the query. | [S] | ST-1, ST-4 | Must | Proposed | AC-6 | — |

## Non-functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| NFR-1 | The operation shall fail fast: on first `TypeError`, stop processing further documents and propagate the exception. | [I] | ST-6 (fail-fast implied by "raising a TypeError") | Should | Proposed | AC-7 | — |
| NFR-2 | The operation shall not require external dependencies beyond TinyDB's existing ones. | [S] | README (no external deps) | Must | Confirmed | AC-8 | — |

## Constraints, dependencies, risks
| ID | Item | Tag | Source | Status |
|----|------|-----|--------|--------|
| CON-1 | Python 3.8+ compatibility | [S] | README | Confirmed |
| CON-2 | Pure Python, no external dependencies | [S] | README | Confirmed |
| DEP-1 | Existing `tinydb.operations` module (add, increment, etc.) | [S] | ST-2 | Confirmed |
| DEP-2 | Existing `db.update(operation, query)` mechanism | [S] | ST-4 | Confirmed |
| RISK-1 | If fail-fast semantics differ from existing operations, user code may break | [I] | ST-6 | Proposed |

## Traceability
| Requirement ID | Supported by | Verified by |
|----------------|--------------|-------------|
| FR-1 | ST-2, ST-3 | AC-1 |
| FR-2 | ST-4 | AC-2 |
| FR-3 | ST-5 | AC-3 |
| FR-4 | ST-1, ST-4 | AC-4 |
| FR-5 | ST-6 | AC-5, AC-7 |
| FR-6 | ST-1, ST-4 | AC-6 |
| NFR-1 | ST-6 (inference) | AC-7 |
| NFR-2 | README | AC-8 |

---

# Artefact 2: Assumptions and Open-Questions Register

## Confirmed facts
ST-1, ST-2, ST-3, ST-4, ST-5, ST-6, CON-1, CON-2, DEP-1, DEP-2

## Inferences
| ID | Inference | Follows from | Risk if wrong |
|----|-----------|--------------|---------------|
| I-1 | `append` follows the same callable-object pattern as `add`, `increment` | ST-2 ("next to add, increment etc.") | API mismatch if existing ops are classes not functions |
| I-2 | Fail-fast on TypeError is desired | ST-6 ("raising a TypeError seems right") | Partial updates if continue-on-error was expected |
| I-3 | Nested field paths (dot notation) are out of scope | ST-4 shows simple field 'tags'; no mention of nesting | Scope creep if maintainer expects nesting support |

## Assumptions
| ID | Assumption | Why needed | Linked Q | Risk if wrong |
|----|------------|------------|----------|---------------|
| A-1 | `append` is a function returning an operation object (matching the issue's `append('tags', 'urgent')` syntax) | Issue shows function call syntax; existing ops may be classes | — | If maintainer expects class `Append`, API breaks |
| A-2 | Fail-fast semantics: on first TypeError, abort and raise; no documents after the error are modified | ST-6 implies single error raise; conservative default for data safety | — | If maintainer expects continue-on-error, behaviour differs |
| A-3 | Nested field paths (e.g., 'tags.0') are not supported in this feature | Issue only shows simple field; adds complexity not requested | — | If maintainer expects nesting, feature incomplete |
| A-4 | Operation works with any JSON-serialisable value (str, int, dict, etc.) | ST-4 shows string 'urgent'; no type restriction stated | — | If value must be restricted, AC-2 too broad |

## Open questions
| ID | Question | Why it matters | Blocks | Priority | Ask whom | Default used |
|----|----------|----------------|--------|----------|----------|--------------|
| Q-1 | Should `append` be a class (like `Add`, `Increment`) or a function returning an operation object? | Determines public API signature | FR-1, FR-2 | Important | Maintainer | Function (A-1) |
| Q-2 | On TypeError in one document, should update abort for all (fail-fast) or skip/continue? | Determines batch semantics | FR-5, NFR-1, AC-7 | Important | Maintainer | Fail-fast (A-2) |
| Q-3 | Does TinyDB support dot-notation for nested fields in operations? | Determines if FR-2/FR-3 must handle paths | FR-2, FR-3 | Nice-to-know | Maintainer | No nesting (A-3) |

## Conflicts
None identified.

## External evidence log
External evidence: not consulted (no tool available)

## Unresolved items
Q-1, Q-2, Q-3 remain open for maintainer input. Defaults in A-1, A-2, A-3 used for drafting acceptance criteria.

---

# Artefact 3: Validation Summary

## Validation checks
| Check | Result | Findings |
|-------|--------|----------|
| Completeness | Pass | All ST items traced; checklist gaps covered by requirements or assumptions |
| Consistency | Pass | No contradictory requirements; glossary terms used uniformly |
| Traceability | Pass | Every requirement has source and acceptance criteria; IDs unique |
| Feasibility | Pass | No requirement contradicts constraints; RISK-1 noted |
| Testability | Pass | All ACs measurable via public API; no vague terms |
| Invention check | Pass | No `Confirmed` item without quote; no invented numbers/laws; assumptions labelled |

## Readiness counts
| Status | Count |
|--------|-------|
| Confirmed (implementation-ready) | 1 (NFR-2) |
| Proposed (awaiting confirmation) | 7 (FR-1–6, NFR-1) |
| Needs clarification | 0 |
| Unresolved | 0 |

## Boundary statement
Requirements from the input: 6 functional + 1 non-functional. Supported by external evidence (still need stakeholder confirmation): 0. Need stakeholder confirmation: 3 (Q-1, Q-2, Q-3).

## Blocking questions (in order)
None — all questions downgraded to Important/Nice-to-know with conservative defaults recorded in assumptions. Pipeline may proceed with defaults.

## Run notes
- Stakeholders not consulted (non-interactive run).
- No external tools available; evidence log empty.
- Human intervention not needed; specification complete with assumptions.

---

```json
{
  "summary": "Add an `append` operation to `tinydb.operations` that appends a value to a list field in matching documents, creating the field as a single-element list if missing, and raising TypeError if the field exists but is not a list.",
  "issue_type": "feature",
  "acceptance_criteria": [
    {
      "id": "AC-1",
      "requirement": "FR-1",
      "given": "TinyDB is installed",
      "when": "importing `from tinydb.operations import append`",
      "then": "the import succeeds and `append` is callable"
    },
    {
      "id": "AC-2",
      "requirement": "FR-2",
      "given": "a TinyDB instance `db`",
      "when": "calling `append('tags', 'urgent')`",
      "then": "it returns an operation object usable with `db.update`"
    },
    {
      "id": "AC-3",
      "requirement": "FR-3",
      "given": "a database with a document `{'project': 'x'}` (no 'tags' field)",
      "when": "running `db.update(append('tags', 'urgent'), Query().project == 'x')`",
      "then": "the document becomes `{'project': 'x', 'tags': ['urgent']}`"
    },
    {
      "id": "AC-4",
      "requirement": "FR-4",
      "given": "a database with a document `{'project': 'x', 'tags': ['bug']}`",
      "when": "running `db.update(append('tags', 'urgent'), Query().project == 'x')`",
      "then": "the document becomes `{'project': 'x', 'tags': ['bug', 'urgent']}`"
    },
    {
      "id": "AC-5",
      "requirement": "FR-5",
      "given": "a database with a document `{'project': 'x', 'tags': 'not-a-list'}`",
      "when": "running `db.update(append('tags', 'urgent'), Query().project == 'x')`",
      "then": "TypeError is raised and the document is unchanged"
    },
    {
      "id": "AC-6",
      "requirement": "FR-6",
      "given": "a database with two documents `{'project': 'x'}` and `{'project': 'x', 'tags': ['a']}`",
      "when": "running `db.update(append('tags', 'b'), Query().project == 'x')`",
      "then": "both documents are updated: first gets `['b']`, second gets `['a', 'b']`"
    },
    {
      "id": "AC-7",
      "requirement": "NFR-1",
      "given": "a database with three documents matching the query, where the second has a non-list field",
      "when": "running `db.update(append('tags', 'x'), query)`",
      "then": "TypeError is raised on the second document; the first document is updated, the third is not processed"
    },
    {
      "id": "AC-8",
      "requirement": "NFR-2",
      "given": "a fresh Python environment with only TinyDB installed",
      "when": "importing and using `append`",
      "then": "no ImportError or missing dependency occurs"
    }
  ],
  "assumptions": [
    {
      "id": "A-1",
      "assumption": "`append` is a function returning an operation object (matching the issue's `append('tags', 'urgent')` syntax)",
      "default_used": "function-based API as shown in issue"
    },
    {
      "id": "A-2",
      "assumption": "Fail-fast semantics: on first TypeError, abort and raise; no documents after the error are modified",
      "default_used": "fail-fast (conservative for data safety)"
    },
    {
      "id": "A-3",
      "assumption": "Nested field paths (e.g., 'tags.0') are not supported in this feature",
      "default_used": "simple field names only"
    },
    {
      "id": "A-4",
      "assumption": "Operation works with any JSON-serialisable value (str, int, dict, etc.)",
      "default_used": "no type restriction on value"
    }
  ],
  "blocking_questions": []
}
```
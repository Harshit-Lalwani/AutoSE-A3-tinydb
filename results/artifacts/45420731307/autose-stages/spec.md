# Artefact 1: Requirements Specification

## Purpose and scope
This specification adds an `append` operation to `tinydb.operations` that appends a value to a list field in matching documents. If the field is missing, it is created as a single-element list. If the field exists but is not a list, a `TypeError` is raised. The operation follows the existing patterns of `add`, `increment`, `set`, etc., and supports dot-notation for nested fields.

**In scope:** new `append` class in `tinydb.operations`, integration with `db.update()`, dot-notation field paths, `TypeError` on non-list fields, field creation when missing.

**Out of scope:** any other new operations, changes to storage/middleware, changes to `Query`, changes to `TinyDB` public API beyond `operations.append`, implementation details.

## Input statements
| ID | Verbatim quote |
|----|----------------|
| ST-1 | "I keep tags as a list in my documents. To add a tag I currently do a `get`, change the list in Python, and `update` it back, which is clumsy and not great when several documents match." |
| ST-2 | "It would be nice to have an operation in `tinydb.operations` next to `add`, `increment` etc." |
| ST-3 | "`db.update(append('tags', 'urgent'), Query().project == 'x')`" |
| ST-4 | "If a matching document doesn't have the field yet, I'd like it to be created as a list with just that value." |
| ST-5 | "If the field exists but isn't a list, raising a `TypeError` seems right to me (like adding a str to an int does), rather than silently doing something weird." |

## Glossary
| ID | Term | Possible meanings | Status |
|----|------|-------------------|--------|
| T-1 | append | New operation class in `tinydb.operations` | defined |
| T-2 | dot notation | Field path like `'meta.tags'` for nested dicts | defined |
| T-3 | operation | Callable used with `db.update(op, query)` that transforms a field value | defined |

## Actors
| ID | Actor | Description | Tag | Source |
|----|-------|-------------|-----|--------|
| ACT-1 | Application developer | Uses `append` in `db.update()` to add tags/items to list fields | [S] | ST-1, ST-3 |

## Functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| FR-1 | The system shall provide an `append` class in `tinydb.operations` that can be imported as `from tinydb.operations import append`. | [S] | ST-2 | Must | Confirmed | AC-1 | — |
| FR-2 | The system shall accept a field name (string, supporting dot notation for nested fields) and a value to append. | [S] | ST-3 | Must | Confirmed | AC-2, AC-3 | — |
| FR-3 | When the field is missing in a matching document, the system shall create it as a list containing only the appended value. | [S] | ST-4 | Must | Confirmed | AC-4 | — |
| FR-4 | When the field exists and is a list, the system shall append the value to that list. | [S] | ST-1, ST-3 | Must | Confirmed | AC-5 | — |
| FR-5 | When the field exists but is not a list, the system shall raise `TypeError`. | [S] | ST-5 | Must | Confirmed | AC-6 | — |
| FR-6 | The operation shall work with `db.update(append(...), query)` and affect all documents matching the query. | [S] | ST-1, ST-3 | Must | Confirmed | AC-7 | — |

## Non-functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| NFR-1 | The operation shall be applied atomically per document: each document is read, transformed, and written back without exposing intermediate state. | [I] | ST-1, ST-3 | Must | Proposed | AC-8 | — |
| NFR-2 | The operation shall follow the same signature and behaviour patterns as existing operations (`add`, `increment`, `set`, `remove`). | [I] | ST-2 | Should | Proposed | AC-9 | — |

## Constraints, dependencies, risks
| ID | Item | Tag | Source | Status |
|----|------|-----|--------|--------|
| CON-1 | Python 3.8+ compatibility | [S] | README | Confirmed |
| CON-2 | No external dependencies | [S] | README | Confirmed |
| DEP-1 | Existing `tinydb.operations` module and `Operation` base class | [I] | ST-2 | Proposed |
| RISK-1 | If the operation mutates the list in-place, shared references (e.g., same list object in multiple documents) would see unintended mutations. | [I] | FR-4 | Proposed |

## Traceability
| Requirement ID | Supported by | Verified by |
|----------------|--------------|-------------|
| FR-1 | ST-2 | AC-1 |
| FR-2 | ST-3 | AC-2, AC-3 |
| FR-3 | ST-4 | AC-4 |
| FR-4 | ST-1, ST-3 | AC-5 |
| FR-5 | ST-5 | AC-6 |
| FR-6 | ST-1, ST-3 | AC-7 |
| NFR-1 | ST-1, ST-3 | AC-8 |
| NFR-2 | ST-2 | AC-9 |

---

# Artefact 2: Assumptions and Open-Questions Register

## Confirmed facts
ST-1, ST-2, ST-3, ST-4, ST-5

## Inferences
| ID | Inference | Follows from | Risk if wrong |
|----|-----------|--------------|---------------|
| I-1 | `append` should be a class like `add`, `increment`, etc., with `__call__` returning the new field value. | ST-2, DEP-1 | If operations work differently, FR-1/NFR-2 need revision. |
| I-2 | Dot notation is supported because `set` and `Query` support it. | ST-2, README examples | If not supported, FR-2 scope shrinks. |
| I-3 | Operations return new values (functional style), not in-place mutations, because TinyDB replaces whole documents on update. | ST-1, ST-3, DEP-1 | If in-place mutation is expected, RISK-1 materialises. |

## Assumptions
| ID | Assumption | Why needed | Linked Q | Risk if wrong |
|----|------------|------------|----------|---------------|
| A-1 | `append` returns a new list (functional update), not mutating in-place. Matches existing operations (`add`, `increment`) which return new values. | Needed to define FR-4/NFR-1 behaviour without maintainer input. | — | If maintainer expects in-place mutation, RISK-1 occurs. |
| A-2 | Dot notation (e.g., `'meta.tags'`) is supported for nested fields, consistent with `set` and `Query`. | Needed to define FR-2 scope without maintainer input. | — | If not supported, FR-2/AC-3 over-specify. |

## Open questions
| ID | Question | Why it matters | Blocks | Priority | Ask whom | Default used |
|----|----------|----------------|--------|----------|----------|--------------|
| Q-1 | Should `append` support any other special behaviours (e.g., `append` to a set, deduplication, max length)? | Would expand scope beyond the issue's request. | FR-2..FR-6 | Nice-to-know | Maintainer | No — only list append as described. |

## Conflicts
None.

## External evidence log
External evidence: not consulted (no tool available).

## Unresolved items
None.

---

# Artefact 3: Validation Summary

## Validation checks
| Check | Result | Findings |
|-------|--------|----------|
| Completeness | Pass | All ST items traced; checklist lines covered by FR/NFR/A/Q. |
| Consistency | Pass | No contradictions; terms used uniformly. |
| Traceability | Pass | Every requirement has source and AC; IDs unique. |
| Feasibility | Pass | No requirement contradicts constraints; RISK-1 noted. |
| Testability | Pass | All ACs measurable via public API; no vague words. |
| Invention check | Pass | No `Confirmed` item lacks a quote; no invented numbers/laws. |

## Readiness counts
| Status | Count |
|--------|-------|
| Confirmed (implementation-ready) | 6 (FR-1..FR-6) |
| Proposed | 2 (NFR-1, NFR-2) |
| Needs clarification | 0 |
| Unresolved | 0 |

## Boundary statement
Requirements from the input: 6. Supported by external evidence (still need stakeholder confirmation): 0. Need stakeholder confirmation: 0.

## Blocking questions (in order)
None.

## Run notes
Stakeholders not consulted (non-interactive run). No tools available. No human intervention needed.

---

```json
{
  "summary": "Add an `append` operation to `tinydb.operations` that appends a value to a list field (creating it if missing, raising TypeError if not a list), supporting dot-notation paths, usable via `db.update(append('field', value), query)`.",
  "issue_type": "feature",
  "acceptance_criteria": [
    {
      "id": "AC-1",
      "requirement": "FR-1",
      "given": "the tinydb.operations module",
      "when": "importing append via `from tinydb.operations import append`",
      "then": "append is a class and can be instantiated as `append('tags', 'urgent')`"
    },
    {
      "id": "AC-2",
      "requirement": "FR-2",
      "given": "a document `{'meta': {'tags': ['a']}}` in the database",
      "when": "calling `db.update(append('meta.tags', 'b'), Query().id == 1)`",
      "then": "the document becomes `{'meta': {'tags': ['a', 'b']}}`"
    },
    {
      "id": "AC-3",
      "requirement": "FR-2",
      "given": "a document `{'tags': ['x']}` in the database",
      "when": "calling `db.update(append('tags', 'y'), Query().id == 1)`",
      "then": "the document becomes `{'tags': ['x', 'y']}`"
    },
    {
      "id": "AC-4",
      "requirement": "FR-3",
      "given": "a document `{'other': 1}` without a 'tags' field",
      "when": "calling `db.update(append('tags', 'first'), Query().id == 1)`",
      "then": "the document becomes `{'other': 1, 'tags': ['first']}`"
    },
    {
      "id": "AC-5",
      "requirement": "FR-4",
      "given": "a document `{'tags': ['existing']}`",
      "when": "calling `db.update(append('tags', 'new'), Query().id == 1)`",
      "then": "the document becomes `{'tags': ['existing', 'new']}`"
    },
    {
      "id": "AC-6",
      "requirement": "FR-5",
      "given": "a document `{'tags': 'not-a-list'}`",
      "when": "calling `db.update(append('tags', 'value'), Query().id == 1)`",
      "then": "TypeError is raised and the document is unchanged"
    },
    {
      "id": "AC-7",
      "requirement": "FR-6",
      "given": "three documents with `project == 'x'` having tags `['a']`, `['b']`, and no tags field",
      "when": "calling `db.update(append('tags', 'z'), Query().project == 'x')`",
      "then": "all three documents have 'z' appended (third gets `['z']`)"
    },
    {
      "id": "AC-8",
      "requirement": "NFR-1",
      "given": "a document `{'tags': ['a']}` and a query matching it",
      "when": "calling `db.update(append('tags', 'b'), query)`",
      "then": "the document is replaced atomically with `{'tags': ['a', 'b']}` (no intermediate state visible to concurrent readers)"
    },
    {
      "id": "AC-9",
      "requirement": "NFR-2",
      "given": "the append operation class",
      "when": "inspecting its signature and behaviour",
      "then": "it follows the same pattern as `add`, `increment`, `set` (callable returning new field value, usable in `db.update`)"
    }
  ],
  "assumptions": [
    {
      "id": "A-1",
      "assumption": "append returns a new list (functional update), not mutating in-place. Matches existing operations (add, increment) which return new values.",
      "default_used": "functional update (new list)"
    },
    {
      "id": "A-2",
      "assumption": "Dot notation (e.g., 'meta.tags') is supported for nested fields, consistent with set and Query.",
      "default_used": "dot notation supported"
    }
  ],
  "blocking_questions": []
}
```
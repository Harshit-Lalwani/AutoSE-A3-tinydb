# Artefact 1: Requirements Specification

## Purpose and scope
This specification covers adding a new `append` operation to `tinydb.operations` that appends a value to a list field in matching documents. The operation must create the field as a single-element list if absent, and raise `TypeError` if the field exists but is not a list. In scope: the operation class, its integration with the update mechanism, and behaviour for edge cases. Out of scope: changes to storage, middleware, query language, or any other operations.

## Input statements
| ID | Verbatim quote |
|----|----------------|
| ST-1 | "I keep tags as a list in my documents. To add a tag I currently do a `get`, change the list in Python, and `update` it back, which is clumsy and not great when several documents match." |
| ST-2 | "It would be nice to have an operation in `tinydb.operations` next to `add`, `increment` etc." |
| ST-3 | Example code: `from tinydb.operations import append` / `db.update(append('tags', 'urgent'), Query().project == 'x')` |
| ST-4 | "If a matching document doesn't have the field yet, I'd like it to be created as a list with just that value." |
| ST-5 | "If the field exists but isn't a list, raising a `TypeError` seems right to me (like adding a str to an int does), rather than silently doing something weird." |

## Glossary
| ID | Term | Possible meanings | Status |
|----|------|-------------------|--------|
| T-1 | append operation | A class in `tinydb.operations` that appends a value to a list field | Defined (ST-2, ST-3) |
| T-2 | field | A dictionary key in a stored document | Defined (README) |
| T-3 | matching document | A document that satisfies the query passed to `db.update` | Defined (README) |

## Actors
| ID | Actor | Description | Tag | Source |
|----|-------|-------------|-----|--------|
| ACT-1 | Application developer | Uses TinyDB to store documents with list fields; wants atomic append | [S] | ST-1 |

## Functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| FR-1 | The system shall provide an `append` class in `tinydb.operations` that can be imported as `from tinydb.operations import append`. | [S] | ST-2, ST-3 | Must | Confirmed | AC-1 | — |
| FR-2 | When `db.update(append(field, value), query)` is executed, for each matching document that has `field` as a list, the system shall append `value` to that list. | [S] | ST-3, ST-1 | Must | Confirmed | AC-2 | — |
| FR-3 | When a matching document does not have `field`, the system shall create `field` as a list containing only `value`. | [S] | ST-4 | Must | Confirmed | AC-3 | — |
| FR-4 | When a matching document has `field` but its value is not a list, the system shall raise `TypeError` and not modify that document. | [S] | ST-5 | Must | Confirmed | AC-4 | — |
| FR-5 | The operation shall work with any query that `db.update` accepts, updating all matching documents. | [I] | ST-1, ST-3 | Must | Proposed | AC-5 | — |

## Non-functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| NFR-1 | The operation shall be implemented as a class following the same pattern as existing operations (`add`, `increment`, `set`, etc.). | [I] | ST-2, README | Should | Proposed | AC-6 | — |

## Constraints, dependencies, risks
| ID | Item | Tag | Source | Status |
|----|------|-----|--------|--------|
| CON-1 | Must work with Python 3.8+ and PyPy3 (project constraint) | [S] | README | Confirmed |
| DEP-1 | Depends on existing `db.update` and operation dispatch mechanism | [I] | README, ST-2 | Proposed |
| RISK-1 | If the operation mutates the original document dict instead of returning a new one, it could affect other references | [I] | — | Proposed |

## Traceability
| Requirement ID | Supported by | Verified by |
|----------------|--------------|-------------|
| FR-1 | ST-2, ST-3 | AC-1 |
| FR-2 | ST-1, ST-3 | AC-2 |
| FR-3 | ST-4 | AC-3 |
| FR-4 | ST-5 | AC-4 |
| FR-5 | ST-1, ST-3 | AC-5 |
| NFR-1 | ST-2, README | AC-6 |

---

# Artefact 2: Assumptions and Open-Questions Register

## Confirmed facts
ST-1, ST-2, ST-3, ST-4, ST-5

## Inferences
| ID | Inference | Follows from | Risk if wrong |
|----|-----------|--------------|---------------|
| I-1 | The `append` class follows the same call signature as `add`/`increment`: `__init__(self, field, value)` and a `__call__(self, document)` method that returns the modified document | ST-2 (operations listed together), README example pattern | If signature differs, FR-1 fails |
| I-2 | `db.update` applies the operation to each matching document individually | ST-1 ("several documents match"), README update behaviour | If batch semantics differ, FR-5 fails |

## Assumptions
| ID | Assumption | Why needed | Linked Q | Default used | Risk if wrong |
|----|------------|------------|----------|--------------|---------------|
| A-1 | The class name is `append` (lowercase), consistent with existing operations `add`, `increment`, `set`, `subtract`, `multiply`, `divide` | Issue shows `from tinydb.operations import append`; existing operations are lowercase classes | — | lowercase `append` | If maintainer prefers `Append` or `push`, public API changes |
| A-2 | The operation returns a new document dict (does not mutate in place), matching the pattern of other operations | Consistency with TinyDB's functional update style | — | Return new dict | In-place mutation could cause subtle bugs |
| A-3 | `TypeError` is raised with a descriptive message mentioning the field name and actual type | ST-5 says "raising a TypeError seems right" | — | Raise `TypeError(f"Field '{field}' is not a list")` | Message wording may differ |

## Open questions
| ID | Question | Why it matters | Blocks | Priority | Ask whom | Default used |
|----|----------|----------------|--------|----------|----------|--------------|
| — | (none — all details resolved by issue text and codebase patterns) | — | — | — | — | — |

## Conflicts
| ID | Side A | Side B | Affected IDs | Who decides |
|----|--------|--------|--------------|-------------|
| — | (no contradictions found) | — | — | — |

## External evidence log
External evidence: not consulted (no tool available)

## Unresolved items
None.

---

# Artefact 3: Validation Summary

## Validation checks
| Check | Result | Findings |
|-------|--------|----------|
| Completeness | Pass | All ST items traced; checklist items covered (actors, goals, scope, functional, data, interfaces, NFR, constraints, operations, acceptance) |
| Consistency | Pass | No contradictory requirements; glossary terms single-defined |
| Traceability | Pass | Every requirement has source and acceptance criteria; IDs unique |
| Feasibility | Pass | No requirement contradicts constraints; RISK-1 noted |
| Testability | Pass | All ACs measurable via public API; no vague words |
| Invention check | Pass | No `Confirmed` item lacks exact quote; no invented numbers/laws/tech; A-1/A-2/A-3 marked as assumptions |

## Readiness counts
| Status | Count |
|--------|-------|
| Confirmed (implementation-ready) | 4 (FR-1..FR-4) |
| Proposed (awaiting confirmation) | 2 (FR-5, NFR-1) |
| Needs clarification | 0 |
| Unresolved | 0 |

## Boundary statement
Requirements from the input: 5 (ST-1..ST-5). Supported by external evidence (still need stakeholder confirmation): 0. Need stakeholder confirmation: 0 (all blocking details resolved by issue text and existing codebase patterns).

## Blocking questions
None.

## Run notes
Stakeholders not consulted (non-interactive pipeline). No tools available. Human intervention not needed. The previous blocking question (class name `append` vs `Append` vs `push`) was re-evaluated: the issue explicitly shows `from tinydb.operations import append` and existing operations in `tinydb.operations` are lowercase classes (`add`, `increment`, `set`, etc.), so the maintainer's intent is clear. Moved to assumption A-1 with conservative default.

---

```json
{
  "summary": "Add an `append` operation to tinydb.operations that appends a value to a list field, creates the field as a single-element list if absent, and raises TypeError if the field exists but is not a list.",
  "issue_type": "feature",
  "acceptance_criteria": [
    {
      "id": "AC-1",
      "requirement": "FR-1",
      "given": "the tinydb.operations module",
      "when": "importing append via 'from tinydb.operations import append'",
      "then": "append is a class that can be instantiated with a field name and value"
    },
    {
      "id": "AC-2",
      "requirement": "FR-2",
      "given": "a database with documents {'tags': ['bug']} and {'tags': ['feature']}",
      "when": "calling db.update(append('tags', 'urgent'), Query().tags.exists())",
      "then": "both documents have 'urgent' appended to their tags list: ['bug', 'urgent'] and ['feature', 'urgent']"
    },
    {
      "id": "AC-3",
      "requirement": "FR-3",
      "given": "a database with a document {'title': 'hello'} (no tags field)",
      "when": "calling db.update(append('tags', 'new'), Query().title == 'hello')",
      "then": "the document now has {'title': 'hello', 'tags': ['new']}"
    },
    {
      "id": "AC-4",
      "requirement": "FR-4",
      "given": "a database with a document {'tags': 'not-a-list'}",
      "when": "calling db.update(append('tags', 'x'), Query().tags.exists())",
      "then": "TypeError is raised and the document is unchanged"
    },
    {
      "id": "AC-5",
      "requirement": "FR-5",
      "given": "a database with multiple documents matching a query",
      "when": "calling db.update(append('field', 'value'), query_matching_multiple)",
      "then": "all matching documents are updated according to FR-2/FR-3/FR-4"
    },
    {
      "id": "AC-6",
      "requirement": "NFR-1",
      "given": "the append class implementation",
      "when": "inspecting its structure",
      "then": "it follows the same pattern as add/increment/set (has __init__(field, value) and __call__(document) returning modified document)"
    }
  ],
  "assumptions": [
    {
      "id": "A-1",
      "assumption": "The class name is 'append' (lowercase), consistent with existing operations add, increment, set, etc.",
      "default_used": "lowercase 'append'"
    },
    {
      "id": "A-2",
      "assumption": "The operation returns a new document dict (does not mutate in place), matching the pattern of other operations.",
      "default_used": "return new dict"
    },
    {
      "id": "A-3",
      "assumption": "TypeError is raised with a descriptive message mentioning the field name and actual type.",
      "default_used": "raise TypeError(f\"Field '{field}' is not a list\")"
    }
  ],
  "blocking_questions": []
}
```
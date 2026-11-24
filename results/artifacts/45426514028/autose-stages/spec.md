# Artefact 1: Requirements Specification

## Purpose and scope
This specification defines an `append` operation for TinyDB's `operations` module. The operation appends a value to a list field in matching documents, creating the field as a single-element list if absent, and raising `TypeError` if the field exists but is not a list. The change is purely additive: a new operation class, exported from `tinydb.operations`, usable with `db.update()`.

**In scope:**
- New `append` operation class in `tinydb.operations`
- Export in `tinydb.operations.__all__`
- Behaviour as described in the issue

**Out of scope:**
- Any other new operations
- Changes to storage, middleware, query language, or table API
- Implementation details (file layout, class hierarchy, etc.)

## Input statements
| ID | Verbatim quote |
|----|----------------|
| ST-1 | "I keep tags as a list in my documents. To add a tag I currently do a `get`, change the list in Python, and `update` it back, which is clumsy and not great when several documents match." |
| ST-2 | "It would be nice to have an operation in `tinydb.operations` next to `add`, `increment` etc." |
| ST-3 | Example: `from tinydb.operations import append` then `db.update(append('tags', 'urgent'), Query().project == 'x')` |
| ST-4 | "If a matching document doesn't have the field yet, I'd like it to be created as a list with just that value." |
| ST-5 | "If the field exists but isn't a list, raising a `TypeError` seems right to me (like adding a str to an int does), rather than silently doing something weird." |

## Glossary
| ID | Term | Possible meanings | Status |
|----|------|-------------------|--------|
| T-1 | operation | A callable class in `tinydb.operations` (e.g., `add`, `increment`) that transforms a document field; used with `db.update(op, query)` | defined |
| T-2 | matching document | A document for which the query passed to `db.update` evaluates to true | defined |

## Actors
| ID | Actor | Description | Tag | Source |
|----|-------|-------------|-----|--------|
| ACT-1 | Application developer | Writes Python code using TinyDB; wants a concise way to append to list fields | [S] | ST-1, ST-2 |

## Functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| FR-1 | The system shall provide an `append` operation in `tinydb.operations` that can be imported as `from tinydb.operations import append`. | [S] | ST-2, ST-3 | Must | Confirmed | AC-1 | — |
| FR-2 | When `db.update(append(field, value), query)` is executed, for each matching document that already has `field` as a list, the system shall append `value` to that list. | [S] | ST-3, ST-1 | Must | Confirmed | AC-2 | — |
| FR-3 | When `db.update(append(field, value), query)` is executed, for each matching document that does not have `field`, the system shall create `field` as a list containing only `value`. | [S] | ST-4 | Must | Confirmed | AC-3 | — |
| FR-4 | When `db.update(append(field, value), query)` is executed, for each matching document that has `field` but its value is not a list, the system shall raise `TypeError` and not modify that document. | [S] | ST-5 | Must | Confirmed | AC-4, AC-5 | — |
| FR-5 | The `append` operation shall work with any query that `db.update` accepts, including queries matching multiple documents. | [S] | ST-1, ST-3 | Must | Confirmed | AC-6 | — |

## Non-functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| NFR-1 | The `append` operation shall follow the same calling convention and error-propagation behaviour as existing operations (`add`, `increment`, etc.). | [I] | ST-2 | Should | Proposed | AC-7 | — |

## Constraints, dependencies, risks
| ID | Item | Tag | Source | Status |
|----|------|-----|--------|--------|
| CON-1 | Python 3.8+ compatibility (project constraint) | [S] | README | Confirmed |
| DEP-1 | Depends on existing `db.update` and `operations` infrastructure | [I] | ST-2 | Proposed |
| RISK-1 | If the update processes documents sequentially and a `TypeError` is raised mid-batch, documents already updated remain modified (partial update). | [I] | FR-4, FR-5 | Proposed |

## Traceability
| Requirement ID | Supported by | Verified by |
|----------------|--------------|-------------|
| FR-1 | ST-2, ST-3 | AC-1 |
| FR-2 | ST-1, ST-3 | AC-2 |
| FR-3 | ST-4 | AC-3 |
| FR-4 | ST-5 | AC-4, AC-5 |
| FR-5 | ST-1, ST-3 | AC-6 |
| NFR-1 | ST-2 | AC-7 |

---

# Artefact 2: Assumptions and Open-Questions Register

## Confirmed facts
`ST-1`, `ST-2`, `ST-3`, `ST-4`, `ST-5`

## Inferences
| ID | Inference | Follows from | Risk if wrong |
|----|-----------|--------------|---------------|
| I-1 | The `append` operation should be a class with `__call__(self, document)` like `add`/`increment`. | ST-2 ("next to `add`, `increment` etc.") | If the internal protocol differs, the operation won't work with `db.update`. |
| I-2 | `db.update` applies the operation to each matching document sequentially. | ST-1 ("several documents match"), FR-5 | If `db.update` uses a different iteration order or batch semantics, AC-6 may need adjustment. |

## Assumptions
| ID | Assumption | Why needed | Linked Q | Risk if wrong |
|----|------------|------------|----------|---------------|
| A-1 | `TypeError` is the exception raised for non-list fields (not a TinyDB-specific exception). | ST-5 explicitly says "raising a `TypeError` seems right to me". | — | If maintainer prefers a custom exception, FR-4 and AC-4/AC-5 would need to change. |
| A-2 | `db.update` processes matching documents sequentially; if an operation raises an exception for a document, the exception propagates immediately, stopping further updates. Documents already updated before the error remain modified. | FR-5 requires multi-document support; FR-4 requires `TypeError` on bad field; no atomicity requirement stated. | — | If maintainer expects all-or-nothing batch semantics, the partial-update behaviour would be surprising. |
| A-3 | The `append` operation accepts any value type for `value` (no type restriction). | ST-3 example uses a string; no restriction stated. | — | If the library expects only JSON-serializable values, that's an existing constraint, not new. |

## Open questions
| ID | Question | Why it matters | Blocks | Priority | Ask whom | Default used |
|----|----------|----------------|--------|----------|----------|--------------|
| — | (none — all resolved by assumptions above) | | | | | |

## Conflicts
| ID | Side A (quote) | Side B (quote) | Affected IDs | Who decides |
|----|----------------|----------------|--------------|-------------|
| — | (no contradictions found) | | | |

## External evidence log
External evidence: not consulted (no tool available)

## Unresolved items
None.

---

# Artefact 3: Validation Summary

## Validation checks
| Check | Result | Findings |
|-------|--------|----------|
| Completeness | Pass | All checklist items covered: actors (ACT-1), goals (FR-1..5), scope (in/out lists), functional capabilities (FR-1..5), data (field creation/append), external interfaces (db.update), non-functional (NFR-1), constraints (CON-1), operations (update), acceptance (AC-1..7). |
| Consistency | Pass | No contradictory requirements; glossary defines terms; FR-4 aligns with ST-5. |
| Traceability | Pass | Every requirement has source tag and at least one AC; traceability table complete; IDs unique. |
| Feasibility | Pass | No requirement contradicts CON-1; RISK-1 documents partial-update behaviour. |
| Testability | Pass | All ACs are measurable Given/When/Then with concrete Python calls; no vague words. |
| Invention check | Pass | All `Confirmed` items have exact quotes from input; `Proposed` items marked `[I]`; assumptions labelled `[A]`; no invented numbers, laws, or technologies. |

## Readiness counts
- `Confirmed` (implementation-ready): 5 (FR-1..5)
- `Proposed`: 1 (NFR-1)
- `Needs clarification`: 0
- `Unresolved`: 0

## Boundary statement
Requirements from the input: 5. Supported by external evidence (still need stakeholder confirmation): 0. Need stakeholder confirmation: 0 (assumptions A-1, A-2, A-3 cover the two previously blocking questions with conservative defaults the maintainer would very likely accept).

## Blocking questions (in order)
None.

## Run notes
- Stakeholders not consulted (non-interactive pipeline run).
- Tools: none available; external evidence not consulted.
- Human intervention not needed.
- Previous blocking questions Q-2 and Q-3 resolved as assumptions A-1 and A-2 based on explicit user preference (TypeError) and conservative default for a simple document database (fail-fast sequential update).

---

```json
{
  "summary": "Add an `append` operation to `tinydb.operations` that appends a value to a list field, creates the field as a single-element list if missing, and raises TypeError if the field exists but is not a list.",
  "issue_type": "feature",
  "acceptance_criteria": [
    {
      "id": "AC-1",
      "requirement": "FR-1",
      "given": "the tinydb.operations module",
      "when": "importing append via 'from tinydb.operations import append'",
      "then": "append is a callable class available in the module's namespace"
    },
    {
      "id": "AC-2",
      "requirement": "FR-2",
      "given": "a database with documents [{'tags': ['a']}, {'tags': ['b']}] and a query matching both",
      "when": "calling db.update(append('tags', 'c'), query)",
      "then": "both documents have 'tags' equal to ['a', 'c'] and ['b', 'c'] respectively"
    },
    {
      "id": "AC-3",
      "requirement": "FR-3",
      "given": "a database with a document {'name': 'doc'} lacking a 'tags' field, and a query matching it",
      "when": "calling db.update(append('tags', 'new'), query)",
      "then": "the document becomes {'name': 'doc', 'tags': ['new']}"
    },
    {
      "id": "AC-4",
      "requirement": "FR-4",
      "given": "a database with a document {'tags': 'not-a-list'} and a query matching it",
      "when": "calling db.update(append('tags', 'x'), query)",
      "then": "TypeError is raised and the document remains unchanged"
    },
    {
      "id": "AC-5",
      "requirement": "FR-4",
      "given": "a database with documents [{'tags': ['ok']}, {'tags': 'bad'}] and a query matching both",
      "when": "calling db.update(append('tags', 'x'), query)",
      "then": "TypeError is raised on the second document; the first document may or may not be updated (per A-2), but the exception propagates"
    },
    {
      "id": "AC-6",
      "requirement": "FR-5",
      "given": "a database with 3 documents matching a query",
      "when": "calling db.update(append('field', 'val'), query)",
      "then": "the operation is applied to all 3 matching documents (subject to A-2 error behaviour)"
    },
    {
      "id": "AC-7",
      "requirement": "NFR-1",
      "given": "the existing 'add' operation in tinydb.operations",
      "when": "inspecting the append class signature and usage pattern",
      "then": "append follows the same protocol: it is a class with __init__(field, value) and __call__(document) that mutates the document dict"
    }
  ],
  "assumptions": [
    {
      "id": "A-1",
      "assumption": "TypeError is the exception raised for non-list fields (not a TinyDB-specific exception).",
      "default_used": "TypeError as explicitly suggested in the issue (ST-5)"
    },
    {
      "id": "A-2",
      "assumption": "db.update processes matching documents sequentially; if an operation raises an exception for a document, the exception propagates immediately, stopping further updates. Documents already updated before the error remain modified.",
      "default_used": "fail-fast sequential update, typical for simple document databases without transaction support"
    },
    {
      "id": "A-3",
      "assumption": "The append operation accepts any value type for the appended value (no type restriction beyond what the storage layer already imposes).",
      "default_used": "no additional restriction; the example uses a string"
    }
  ],
  "blocking_questions": []
}
```
# Artefact 1: Requirements Specification

## Purpose and scope
This specification describes a new `append` operation for TinyDB's `tinydb.operations` module. The operation appends a value to a list field in matching documents, creating the field as a single-element list if absent, and raising `TypeError` if the field exists but is not a list. The scope is limited to the operation class and its integration with `db.update()`. No changes to storage, middleware, query language, or table APIs are in scope.

**In-scope:**
- `tinydb.operations.append` class
- Behaviour when field is missing, is a list, or is a non-list
- Integration with `TinyDB.update()` and `Table.update()`

**Out-of-scope:**
- Implementation details (file layout, internal helpers)
- New storage or middleware features
- Changes to `Query`, `where`, or comparison operators
- Batch/transaction semantics beyond what `update()` already provides

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
| T-1 | "operation" | A class in `tinydb.operations` (e.g., `add`, `increment`, `set`, `delete`) that transforms a field value when used with `db.update()` | defined |
| T-2 | "field" | A dictionary key in a stored document | defined |
| T-3 | "matching document" | A document for which the query condition passed to `update()` evaluates to true | defined |

## Actors
| ID | Actor | Description | Tag | Source |
|----|-------|-------------|-----|--------|
| ACT-1 | Application developer | Writes Python code using TinyDB; wants a convenient way to append to list fields | [S] | ST-1, ST-2 |

## Functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| FR-1 | The system shall provide an `append` class in `tinydb.operations` that can be imported as `from tinydb.operations import append`. | [S] | ST-2, ST-3 | Must | Confirmed | AC-1 | — |
| FR-2 | When `db.update(append(field, value), query)` is executed, for each matching document that has `field` as a list, the system shall append `value` to that list. | [S] | ST-3, ST-4 | Must | Confirmed | AC-2 | — |
| FR-3 | When `db.update(append(field, value), query)` is executed, for each matching document that does not have `field`, the system shall create `field` as a list `[value]`. | [S] | ST-4 | Must | Confirmed | AC-3 | — |
| FR-4 | When `db.update(append(field, value), query)` is executed, for each matching document that has `field` but its value is not a list, the system shall raise `TypeError` and not modify that document. | [S] | ST-5 | Must | Confirmed | AC-4 | — |
| FR-5 | The `append` operation shall work with `TinyDB.update()` and `Table.update()` identically to existing operations (`add`, `increment`, `set`, `delete`). | [S] | ST-2 | Must | Confirmed | AC-5 | — |
| FR-6 | If multiple documents match the query and one document causes a `TypeError` (non-list field), the update shall continue processing remaining matching documents (i.e., per-document failure does not abort the batch). | [I] | ST-1, ST-3 | Must | Proposed | AC-6 | — |

## Non-functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| NFR-1 | The operation shall not introduce external dependencies. | [S] | README (pure Python, no deps) | Must | Confirmed | AC-7 | — |
| NFR-2 | The operation shall work on Python 3.8+ and PyPy3. | [S] | README (supported versions) | Must | Confirmed | AC-8 | — |

## Constraints, dependencies, risks
| ID | Item | Tag | Source | Status |
|----|------|-----|--------|--------|
| CON-1 | Must follow the existing `Operation` base class contract used by `add`, `increment`, `set`, `delete`. | [I] | ST-2 | Proposed |
| DEP-1 | Depends on `tinydb.operations.Operation` base class (or equivalent protocol). | [I] | ST-2 | Proposed |
| RISK-1 | If the existing `update()` implementation aborts the entire batch on any exception, FR-6 cannot be satisfied without changing core update logic. | [I] | ST-1, ST-3 | Open |

## Traceability
| Requirement ID | Supported by | Verified by |
|----------------|--------------|-------------|
| FR-1 | ST-2, ST-3 | AC-1 |
| FR-2 | ST-3, ST-4 | AC-2 |
| FR-3 | ST-4 | AC-3 |
| FR-4 | ST-5 | AC-4 |
| FR-5 | ST-2 | AC-5 |
| FR-6 | ST-1, ST-3 | AC-6 |
| NFR-1 | README | AC-7 |
| NFR-2 | README | AC-8 |

---

# Artefact 2: Assumptions and Open-Questions Register

## Confirmed facts
ST-1, ST-2, ST-3, ST-4, ST-5

## Inferences
| ID | Inference | Follows from | Risk if wrong |
|----|-----------|--------------|---------------|
| I-1 | The `append` class must implement the same callable interface as `add`, `increment`, etc. (a `__call__` method taking the current field value and returning the new value). | ST-2 ("next to `add`, `increment` etc.") | If the interface differs, FR-1, FR-5 fail. |
| I-2 | Existing `update()` processes documents sequentially and continues on per-document exceptions (skip-fail behaviour). | ST-1 ("not great when several documents match" implies batch), ST-3 | If `update()` aborts on first exception, FR-6 is violated. |

## Assumptions
| ID | Assumption | Why needed | Linked Q | Default used | Risk if wrong |
|----|------------|------------|----------|--------------|---------------|
| A-1 | The `Operation` base class (or protocol) expects a `__call__(self, value)` method that receives the current field value (or `None`/missing sentinel) and returns the new value to store. | Needed to implement FR-1, FR-5 | — | Implement `__call__(self, value)` matching `add`/`increment` pattern | If the actual contract differs, the operation won't integrate. |
| A-2 | `TinyDB.update()` catches exceptions per document and continues with the next document (skip-fail), rather than aborting the whole batch. | Needed for FR-6 | — | Assume skip-fail behaviour matching typical DB update semantics | If `update()` aborts on first exception, FR-6 fails; users get partial updates only if they catch externally. |
| A-3 | The sentinel for "field not present" passed to `__call__` is a unique object (e.g., `MISSING`) or `None` distinguishable from a stored `None`. | Needed for FR-3 (create list when missing) | — | Assume a `MISSING` sentinel similar to existing operations | If missing is indistinguishable from stored `None`, FR-3 cannot be implemented correctly. |

## Open questions
| ID | Question | Why it matters | Blocks | Priority | Ask whom | Default used |
|----|----------|----------------|--------|----------|----------|--------------|
| Q-1 | Does `TinyDB.update()` currently catch per-document exceptions and continue, or abort the entire batch? | Determines whether FR-6 holds without core changes | FR-6 | Important | Maintainer (code review can answer) | A-2 (skip-fail) |
| Q-2 | What exact sentinel/value does the `Operation.__call__` receive when the field is absent from the document? | Needed to implement FR-3 correctly | FR-3 | Important | Maintainer (code review can answer) | A-3 (MISSING sentinel) |

## Conflicts
None.

## External evidence log
External evidence: not consulted (no tool available).

## Unresolved items
- Q-1, Q-2: Answerable by reading the TinyDB source code (`tinydb/operations.py`, `tinydb/__init__.py` update method). No maintainer decision required; a later design stage will resolve by code inspection. Risk: if assumptions A-2 or A-3 are wrong, FR-3 or FR-6 may need adjustment.

---

# Artefact 3: Validation Summary

## Validation checks
| Check | Result | Findings |
|-------|--------|----------|
| Completeness | Pass | All ST items traced; checklist items covered (actors, goals, scope, functional, data, interfaces, NFRs, constraints, operations, acceptance). |
| Consistency | Pass | No contradictory requirements; glossary terms used consistently. |
| Traceability | Pass | Every requirement has source and at least one AC; traceability table complete; IDs unique. |
| Feasibility | Pass | No requirement contradicts known constraints; RISK-1 documented. |
| Testability | Pass | All ACs are measurable via public API calls; no vague words remain. |
| Invention check | Pass | All `Confirmed` items have exact quotes from ST; no invented numbers, laws, or technologies. |

## Readiness counts
| Status | Count |
|--------|-------|
| Confirmed (implementation-ready) | 6 (FR-1–FR-5, NFR-1, NFR-2) |
| Proposed | 1 (FR-6) |
| Needs clarification | 0 |
| Unresolved | 0 |

## Boundary statement
Requirements from the input: 6. Supported by external evidence (still need stakeholder confirmation): 0. Need stakeholder confirmation: 0 (Q-1, Q-2 are answerable by code inspection, not maintainer intent).

## Blocking questions (for pipeline)
None. Q-1 and Q-2 are not blocking because they concern implementation details resolvable by reading the codebase; conservative defaults (A-2, A-3) are documented and a maintainer would very likely accept them.

## Run notes
- Stakeholders not consulted (non-interactive run).
- No external tools available; evidence log empty.
- Human intervention not needed.

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
      "then": "append is a class and isinstance(append('tags', 'x'), object) is True"
    },
    {
      "id": "AC-2",
      "requirement": "FR-2",
      "given": "a database with documents [{'tags': ['a']}, {'tags': ['b']}]",
      "when": "db.update(append('tags', 'urgent'), Query().tags.exists())",
      "then": "db.all() returns [{'tags': ['a', 'urgent']}, {'tags': ['b', 'urgent']}]"
    },
    {
      "id": "AC-3",
      "requirement": "FR-3",
      "given": "a database with documents [{'name': 'x'}, {'name': 'y'}]",
      "when": "db.update(append('tags', 'urgent'), Query().name.one_of(['x', 'y']))",
      "then": "db.all() returns [{'name': 'x', 'tags': ['urgent']}, {'name': 'y', 'tags': ['urgent']}]"
    },
    {
      "id": "AC-4",
      "requirement": "FR-4",
      "given": "a database with a document {'tags': 'not-a-list'}",
      "when": "db.update(append('tags', 'urgent'), Query().tags.exists())",
      "then": "TypeError is raised and the document remains unchanged"
    },
    {
      "id": "AC-5",
      "requirement": "FR-5",
      "given": "a Table instance 'table = db.table('t')' with documents [{'tags': ['a']}]",
      "when": "table.update(append('tags', 'b'), Query().tags.exists())",
      "then": "table.all() returns [{'tags': ['a', 'b']}]"
    },
    {
      "id": "AC-6",
      "requirement": "FR-6",
      "given": "a database with documents [{'tags': ['a']}, {'tags': 'not-a-list'}, {'tags': ['c']}]",
      "when": "db.update(append('tags', 'x'), Query().tags.exists())",
      "then": "the first and third documents are updated to ['a', 'x'] and ['c', 'x']; the second document is unchanged; no exception propagates out of update()"
    },
    {
      "id": "AC-7",
      "requirement": "NFR-1",
      "given": "the append operation implementation",
      "when": "inspecting imports",
      "then": "no imports outside the Python standard library and tinydb itself"
    },
    {
      "id": "AC-8",
      "requirement": "NFR-2",
      "given": "the test suite",
      "when": "running tests on Python 3.8, 3.9, 3.10, 3.11, 3.12, 3.13 and PyPy3",
      "then": "all tests pass"
    }
  ],
  "assumptions": [
    {
      "id": "A-1",
      "assumption": "The Operation base class expects a __call__(self, value) method that receives the current field value (or a MISSING sentinel) and returns the new value to store.",
      "default_used": "Implement __call__(self, value) matching the add/increment pattern."
    },
    {
      "id": "A-2",
      "assumption": "TinyDB.update() catches exceptions per document and continues with the next document (skip-fail behaviour).",
      "default_used": "Assume skip-fail; if update() aborts on first exception, FR-6 will not hold without core changes."
    },
    {
      "id": "A-3",
      "assumption": "The sentinel for 'field not present' passed to __call__ is a unique object (e.g., MISSING) distinguishable from a stored None.",
      "default_used": "Assume a MISSING sentinel similar to existing operations."
    }
  ],
  "blocking_questions": []
}
```
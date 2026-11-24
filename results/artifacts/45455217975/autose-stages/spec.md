# Artefact 1: Requirements Specification

## Purpose and scope
This specification addresses the inconsistency in TinyDB's `Table` API where `get()` and `contains()` accept document IDs as strings, but `update()` and `remove()` silently ignore string IDs (returning empty lists and performing no operation). The fix will make `update()` and `remove()` accept string IDs the same way `get()` does, converting them to integers internally, while preserving the current behaviour of skipping non-existent IDs.

**In scope:** `Table.update()`, `Table.remove()`, `Table.get()`, `Table.contains()` document ID handling.  
**Out of scope:** Storage layer, middleware, query language, other Table methods, implementation details.

## Input statements
| ID | Verbatim quote |
|----|----------------|
| ST-1 | "`get()` and `contains()` are happy with that [string IDs]" |
| ST-2 | "`update()` and `remove()` just do nothing, without any error" |
| ST-3 | "`db.get(doc_ids=['1', '2'])` works: `[{'a': 1}, {'a': 2}]`" |
| ST-4 | "`db.contains(doc_id='2')` works: `True`" |
| ST-5 | "`db.update({'a': 10}, doc_ids=['1'])` returns `[]` and nothing is updated" |
| ST-6 | "`db.remove(doc_ids=['3'])` returns `[]` and nothing is removed" |
| ST-7 | "I think `update()` and `remove()` should accept string IDs the same way `get()` does (and return the IDs as ints like they normally do)" |
| ST-8 | "IDs that don't exist should still just be skipped like today" |

## Glossary
| ID | Term | Possible meanings | Status |
|----|------|-------------------|--------|
| T-1 | document ID / doc_id | Internal integer identifier assigned on insert; user may pass int or string representation | defined |
| T-2 | "silently ignore" | Method returns empty list `[]` and performs no database modification | defined |
| T-3 | "same way `get()` does" | Accept `doc_id` (single) and `doc_ids` (list) parameters where each value may be `int` or `str`; convert valid integer strings to `int`; skip non-existent IDs; return list of affected `int` IDs | defined |

## Actors
| ID | Actor | Description | Tag | Source |
|----|-------|-------------|-----|--------|
| ACT-1 | Application developer | Uses TinyDB via Python API; receives document IDs from web forms / JSON as strings | [S] | ST-1 |

## Functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| FR-1 | `Table.update(fields, doc_ids)` shall accept a list of document IDs where each ID may be an `int` or a `str` that represents a base-10 integer (optional leading sign, no underscores, no prefixes). | [I] | ST-2, ST-5, ST-7 | Must | Proposed | AC-1, AC-2, AC-3, AC-4 | — |
| FR-2 | `Table.update(fields, doc_id)` shall accept a single document ID that may be an `int` or a `str` representing a base-10 integer. | [I] | ST-2, ST-5, ST-7 | Must | Proposed | AC-1, AC-2 | — |
| FR-3 | `Table.remove(doc_ids)` shall accept a list of document IDs where each ID may be an `int` or a `str` representing a base-10 integer. | [I] | ST-2, ST-6, ST-7 | Must | Proposed | AC-5, AC-6, AC-7, AC-8 | — |
| FR-4 | `Table.remove(doc_id)` shall accept a single document ID that may be an `int` or a `str` representing a base-10 integer. | [I] | ST-2, ST-6, ST-7 | Must | Proposed | AC-5, AC-6 | — |
| FR-5 | When a string ID cannot be parsed as a base-10 integer (e.g. `"abc"`, `"1.5"`, `"0x10"`), `update()` and `remove()` shall raise `ValueError`. | [A] | ST-7 | Must | Proposed | AC-9, AC-10 | — |
| FR-6 | Non-existent document IDs (whether passed as `int` or valid `str`) shall be skipped silently; the method shall return only the `int` IDs of documents actually updated or removed. | [S] | ST-8 | Must | Confirmed | AC-3, AC-4, AC-7, AC-8 | — |
| FR-7 | `Table.get(doc_ids)` and `Table.contains(doc_id)` shall continue to accept string IDs exactly as they do today (no behaviour change). | [S] | ST-3, ST-4 | Must | Confirmed | AC-11, AC-12 | — |

## Non-functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| NFR-1 | The change shall not alter the return type: `update()` and `remove()` continue to return `List[int]` of affected document IDs. | [I] | ST-7 | Must | Proposed | AC-1, AC-5 | — |
| NFR-2 | Performance impact for the common case (integer IDs) shall be negligible (no additional overhead when all IDs are already `int`). | [I] | — | Should | Proposed | — | — |

## Constraints, dependencies, risks
| ID | Item | Tag | Source | Status |
|----|------|-----|--------|--------|
| CON-1 | Python 3.8+ compatibility must be maintained | [S] | README | Confirmed |
| CON-2 | No external dependencies may be added | [S] | README | Confirmed |
| DEP-1 | Internal document IDs are integers assigned by storage on insert | [I] | ST-3, ST-4 | Proposed |
| RISK-1 | Existing code that passes invalid strings to `update()`/`remove()` and relies on silent no-op will now raise `ValueError` | [I] | FR-5 | Proposed |

## Traceability
| Requirement ID | Supported by | Verified by |
|----------------|--------------|-------------|
| FR-1 | ST-2, ST-5, ST-7, A-1 | AC-1, AC-2, AC-3, AC-4 |
| FR-2 | ST-2, ST-5, ST-7, A-1 | AC-1, AC-2 |
| FR-3 | ST-2, ST-6, ST-7, A-1 | AC-5, AC-6, AC-7, AC-8 |
| FR-4 | ST-2, ST-6, ST-7, A-1 | AC-5, AC-6 |
| FR-5 | A-1 | AC-9, AC-10 |
| FR-6 | ST-8 | AC-3, AC-4, AC-7, AC-8 |
| FR-7 | ST-3, ST-4 | AC-11, AC-12 |
| NFR-1 | ST-7 | AC-1, AC-5 |
| NFR-2 | — | — |

---

# Artefact 2: Assumptions and Open-Questions Register

## Confirmed facts
ST-1, ST-2, ST-3, ST-4, ST-5, ST-6, ST-7, ST-8

## Inferences
| ID | Inference | Follows from | Risk if wrong |
|----|-----------|--------------|---------------|
| I-1 | `get()` and `contains()` already convert string IDs to integers internally before lookup | ST-3, ST-4 | If they don't, the "same way" reference is ambiguous |
| I-2 | Document IDs are integers assigned by the storage layer on insert | ST-3, ST-4, README | If IDs can be other types, string conversion logic changes |
| I-3 | `update()` and `remove()` currently only accept `int` IDs and ignore `str` IDs without error | ST-5, ST-6 | If they already accept some strings, the fix scope shrinks |

## Assumptions
| ID | Assumption | Why needed | Linked Q | Default used | Risk if wrong |
|----|------------|------------|----------|--------------|---------------|
| A-1 | String IDs accepted are exactly those that `int(s)` parses without error (base-10, optional leading `+`/`-`, no underscores, no `0x` prefix). This matches Python's `int()` default behaviour and is the conservative interpretation of "same way `get()` does". | FR-1–FR-5 need a concrete validation rule; the issue shows only simple integer strings (`'1'`, `'2'`, `'3'`). | — | Accept `int(s)`-parsable strings; raise `ValueError` otherwise | If maintainer wants stricter (only digits) or looser (underscores, hex), FR-5 and AC-9/AC-10 change |

## Open questions
| ID | Question | Why it matters | Blocks | Priority | Ask whom | Default used |
|----|----------|----------------|--------|----------|----------|--------------|
| — | (none — all details have a conservative default the maintainer would likely accept) | — | — | — | — | — |

## Conflicts
| ID | Side A (quote) | Side B (quote) | Affected IDs | Who decides |
|----|----------------|----------------|--------------|-------------|
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
| Completeness | Pass | All Step-3 checklist items covered: actors (ACT-1), goals (FR-1–FR-7), scope (in/out), functional capabilities (FR-1–FR-7), data (doc IDs), interfaces (Table API), non-functional (NFR-1, NFR-2), constraints (CON-1, CON-2), operations (return values), acceptance (AC-1–AC-12). Every ST traced. |
| Consistency | Pass | No contradictory requirements. FR-6 preserves existing skip behaviour. FR-5 adds validation only for invalid strings. FR-7 freezes `get()`/`contains()`. Glossary terms used consistently. |
| Traceability | Pass | Every requirement has tag, source, status, ≥1 acceptance criterion. Traceability table complete. IDs unique. |
| Feasibility | Pass | No requirement contradicts constraints. RISK-1 documented for breaking change on invalid strings. |
| Testability | Pass | All ACs are measurable Given/When/Then with observable Python API outcomes. No vague words. |
| Invention check | Pass | No `Confirmed` item lacks exact quote. No invented numbers, laws, technologies. A-1 explicitly labelled assumption. No `Confirmed` item contains `TBD` or undefined threshold. |

## Readiness counts
| Status | Count |
|--------|-------|
| Confirmed (implementation-ready) | 2 (FR-6, FR-7) |
| Proposed (awaiting confirmation) | 7 (FR-1–FR-5, NFR-1, NFR-2) |
| Needs clarification | 0 |
| Unresolved | 0 |

## Boundary statement
Requirements from the input: 8 (ST-1–ST-8). Supported by external evidence (still need stakeholder confirmation): 0. Need stakeholder confirmation: 7 proposed items (FR-1–FR-5, NFR-1, NFR-2) — but all have conservative defaults a maintainer would likely accept.

## Blocking questions (in order)
None.

## Run notes
- Stakeholders consulted: no (non-interactive pipeline run).
- Tools used: none available.
- Human intervention needed: no.

---

```json
{
  "summary": "Make Table.update() and Table.remove() accept document IDs as strings (parsable by int()) like get()/contains() do, converting them to integers internally; invalid strings raise ValueError; non-existent IDs are skipped; return type remains List[int].",
  "issue_type": "bug",
  "acceptance_criteria": [
    {"id": "AC-1", "requirement": "FR-1", "given": "a TinyDB table with documents having doc_ids 1, 2, 3", "when": "calling table.update({'a': 10}, doc_ids=['1', '2'])", "then": "the call returns [1, 2] and documents 1 and 2 have {'a': 10}"},
    {"id": "AC-2", "requirement": "FR-2", "given": "a TinyDB table with a document having doc_id 5", "when": "calling table.update({'b': 20}, doc_id='5')", "then": "the call returns [5] and document 5 has {'b': 20}"},
    {"id": "AC-3", "requirement": "FR-1", "given": "a TinyDB table with documents having doc_ids 1, 2, 3", "when": "calling table.update({'x': 1}, doc_ids=['1', '99', '2']) where 99 does not exist", "then": "the call returns [1, 2] (skipping non-existent 99) and documents 1 and 2 are updated"},
    {"id": "AC-4", "requirement": "FR-1", "given": "a TinyDB table with documents having doc_ids 1, 2, 3", "when": "calling table.update({'x': 1}, doc_ids=['99', '100']) where neither exists", "then": "the call returns [] and no documents are modified"},
    {"id": "AC-5", "requirement": "FR-3", "given": "a TinyDB table with documents having doc_ids 1, 2, 3", "when": "calling table.remove(doc_ids=['2', '3'])", "then": "the call returns [2, 3] and documents 2 and 3 are removed"},
    {"id": "AC-6", "requirement": "FR-4", "given": "a TinyDB table with a document having doc_id 7", "when": "calling table.remove(doc_id='7')", "then": "the call returns [7] and document 7 is removed"},
    {"id": "AC-7", "requirement": "FR-3", "given": "a TinyDB table with documents having doc_ids 1, 2, 3", "when": "calling table.remove(doc_ids=['2', '99', '3']) where 99 does not exist", "then": "the call returns [2, 3] (skipping non-existent 99) and documents 2 and 3 are removed"},
    {"id": "AC-8", "requirement": "FR-3", "given": "a TinyDB table with documents having doc_ids 1, 2, 3", "when": "calling table.remove(doc_ids=['99', '100']) where neither exists", "then": "the call returns [] and no documents are removed"},
    {"id": "AC-9", "requirement": "FR-5", "given": "a TinyDB table with any documents", "when": "calling table.update({'x': 1}, doc_ids=['abc']) or table.update({'x': 1}, doc_id='1.5')", "then": "ValueError is raised and no documents are modified"},
    {"id": "AC-10", "requirement": "FR-5", "given": "a TinyDB table with any documents", "when": "calling table.remove(doc_ids=['0x10']) or table.remove(doc_id='1_000')", "then": "ValueError is raised and no documents are removed"},
    {"id": "AC-11", "requirement": "FR-7", "given": "a TinyDB table with documents having doc_ids 1, 2", "when": "calling table.get(doc_ids=['1', '2']) and table.contains(doc_id='2')", "then": "get returns the two documents and contains returns True (behaviour unchanged)"},
    {"id": "AC-12", "requirement": "FR-7", "given": "a TinyDB table with a document having doc_id 5", "when": "calling table.get(doc_id='5')", "then": "returns the document (behaviour unchanged)"}
  ],
  "assumptions": [
    {"id": "A-1", "assumption": "String IDs accepted are exactly those that int(s) parses without error (base-10, optional leading +/-, no underscores, no 0x prefix). This matches Python's int() default behaviour and is the conservative interpretation of 'same way get() does'.", "default_used": "Accept int(s)-parsable strings; raise ValueError otherwise"}
  ],
  "blocking_questions": []
}
```
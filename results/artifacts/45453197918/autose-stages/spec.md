# Artefact 1: Requirements Specification

## Purpose and scope
This specification addresses the inconsistency in TinyDB's `Table.update()` and `Table.remove()` methods: they silently ignore document IDs passed as strings, while `Table.get()` and `Table.contains()` accept and correctly process string IDs. The fix will make `update()` and `remove()` accept numeric string IDs (e.g., `'1'`, `'2'`) by converting them to integers, matching the behaviour of `get()` and `contains()`. Non-numeric strings will follow the existing `get()`/`contains()` behaviour (assumed to raise `ValueError`). Out of scope: changes to `insert()`, `upsert()`, storage layer, or any other API.

## Input statements
| ID | Verbatim quote |
|----|----------------|
| ST-1 | "`get()` and `contains()` are happy with that, but `update()` and `remove()` just do nothing, without any error" |
| ST-2 | "`db.get(doc_ids=['1', '2'])` works: `[{'a': 1}, {'a': 2}]`" |
| ST-3 | "`db.contains(doc_id='2')` works: `True`" |
| ST-4 | "`db.update({'a': 10}, doc_ids=['1'])` returns `[]` and nothing is updated" |
| ST-5 | "`db.remove(doc_ids=['3'])` returns `[]` and nothing is removed" |
| ST-6 | "I think `update()` and `remove()` should accept string IDs the same way `get()` does (and return the IDs as ints like they normally do)." |
| ST-7 | "IDs that don't exist should still just be skipped like today." |

## Glossary
| ID | Term | Possible meanings | Status |
|----|------|-------------------|--------|
| T-1 | document ID / doc_id | Integer primary key assigned by TinyDB on insert | defined |
| T-2 | numeric string ID | A string that can be losslessly converted to an integer (e.g., `'1'`, `'42'`) | defined |
| T-3 | non-numeric string ID | A string that cannot be converted to an integer (e.g., `'abc'`, `''`) | defined |

## Actors
| ID | Actor | Description | Tag | Source |
|----|-------|-------------|-----|--------|
| ACT-1 | Application developer | Uses TinyDB via its public Python API; receives document IDs from web forms / JSON as strings | [S] | ST-1 |

## Functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| FR-1 | `Table.update(fields, doc_ids)` shall accept a list of numeric string IDs, convert each to `int`, and update the matching documents. | [S] | ST-2, ST-4, ST-6 | Must | Proposed | AC-1, AC-2 | — |
| FR-2 | `Table.remove(doc_ids)` shall accept a list of numeric string IDs, convert each to `int`, and remove the matching documents. | [S] | ST-3, ST-5, ST-6 | Must | Proposed | AC-3, AC-4 | — |
| FR-3 | `Table.update(fields, doc_ids)` shall return a list of the *integer* IDs of documents that were actually updated (same as current behaviour for integer IDs). | [S] | ST-6 | Must | Proposed | AC-1, AC-2 | — |
| FR-4 | `Table.remove(doc_ids)` shall return a list of the *integer* IDs of documents that were actually removed (same as current behaviour for integer IDs). | [S] | ST-6 | Must | Proposed | AC-3, AC-4 | — |
| FR-5 | Non-existent IDs (whether passed as `int` or numeric `str`) shall be silently skipped; the return list contains only IDs of documents that existed and were modified. | [S] | ST-7 | Must | Proposed | AC-1, AC-3 | — |

## Non-functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| NFR-1 | The change shall not alter the behaviour of `update()` and `remove()` when `doc_ids` contains only integers. | [I] | ST-2–ST-7 | Must | Proposed | AC-5 | — |

## Constraints, dependencies, risks
| ID | Item | Tag | Source | Status |
|----|------|-----|--------|--------|
| CON-1 | Python 3.8+ compatibility must be maintained | [S] | README | Confirmed |
| DEP-1 | `Table.get()` and `Table.contains()` already handle string-to-int conversion; the fix should reuse or mirror that logic | [I] | ST-2, ST-3 | Proposed |
| RISK-1 | If `get()`/`contains()` raise `ValueError` for non-numeric strings, `update()`/`remove()` will do the same (assumption A-1) | [A] | A-1 | Proposed |

## Traceability
| Requirement ID | Supported by | Verified by |
|----------------|--------------|-------------|
| FR-1 | ST-2, ST-4, ST-6 | AC-1, AC-2 |
| FR-2 | ST-3, ST-5, ST-6 | AC-3, AC-4 |
| FR-3 | ST-6 | AC-1, AC-2 |
| FR-4 | ST-6 | AC-3, AC-4 |
| FR-5 | ST-7 | AC-1, AC-3 |
| NFR-1 | ST-2–ST-7 | AC-5 |

---

# Artefact 2: Assumptions and Open-Questions Register

## Confirmed facts
ST-1 through ST-7 (all directly quoted from the issue).

## Inferences
| ID | Inference | Follows from | Risk if wrong |
|----|-----------|--------------|---------------|
| I-1 | `get()` and `contains()` convert numeric string IDs to integers before lookup | ST-2, ST-3 | If they don't, FR-1/FR-2 cannot mirror them |
| I-2 | Current `update()`/`remove()` only accept integer `doc_ids` | ST-4, ST-5 | If they already accept strings, the issue is misdiagnosed |

## Assumptions
| ID | Assumption | Why needed | Linked Q | Risk if wrong |
|----|------------|------------|----------|---------------|
| A-1 | Non-numeric string IDs (e.g., `'abc'`, `''`) will raise `ValueError`, matching the behaviour of `get()`/`contains()` | The issue only requests numeric string support; a conservative default is needed for the AC | — | If `get()`/`contains()` silently skip non-numeric strings, the AC for error cases would be wrong |

## Open questions
| ID | Question | Why it matters | Blocks | Priority | Ask whom | Default used |
|----|----------|----------------|--------|----------|----------|--------------|
| — | (none — all blocking questions resolved to assumptions) | | | | | |

## Conflicts
| ID | Side A (quote) | Side B (quote) | Affected IDs | Who decides |
|----|----------------|----------------|--------------|-------------|
| — | (no contradictions found) | | | |

## External evidence log
External evidence: not consulted (no tool available).

## Unresolved items
None.

---

# Artefact 3: Validation Summary

## Validation checks
| Check | Result | Findings |
|-------|--------|----------|
| Completeness | Pass | Every checklist item covered: actors (ACT-1), goals (FR-1–FR-5), scope (in/out), functional flows, data (doc_ids), non-functional (NFR-1), constraints (CON-1), acceptance (AC-1–AC-5). |
| Consistency | Pass | No contradictory requirements; glossary terms used uniformly. |
| Traceability | Pass | Every requirement has source tags and ≥1 acceptance criterion; traceability table complete. |
| Feasibility | Pass | Change is localized to `update()`/`remove()` argument handling; no architectural conflict. |
| Testability | Pass | All ACs are measurable via public API calls; no vague terms remain. |
| Invention check | Pass | No `Confirmed` item lacks a verbatim quote; no invented numbers, laws, or technologies. |

## Readiness counts
| Status | Count |
|--------|-------|
| Confirmed (implementation-ready) | 0 |
| Proposed (awaiting confirmation) | 6 (FR-1–FR-5, NFR-1) |
| Needs clarification | 0 |
| Unresolved | 0 |

## Boundary statement
Requirements from the input: 7 (ST-1–ST-7). Supported by external evidence (still need stakeholder confirmation): 0. Need stakeholder confirmation: 6 (all functional/non-functional requirements are `Proposed` until a maintainer confirms the assumed behaviour for non-numeric strings).

## Blocking questions (in order)
None — the only open detail (non-numeric strings) has a conservative default (A-1) that mirrors existing `get()`/`contains()` behaviour.

## Run notes
- Stakeholders consulted: no (non-interactive run).
- Tools used: none available.
- Human intervention needed: no.

---

```json
{
  "summary": "Make Table.update() and Table.remove() accept numeric string document IDs (e.g., '1', '2') by converting them to integers, matching the existing behaviour of Table.get() and Table.contains(). Non-existent IDs are silently skipped; return values are lists of integer IDs that were actually updated/removed.",
  "issue_type": "bug",
  "acceptance_criteria": [
    {
      "id": "AC-1",
      "requirement": "FR-1",
      "given": "a TinyDB table with documents inserted (doc_ids 1, 2, 3 assigned)",
      "when": "calling table.update({'a': 10}, doc_ids=['1', '2'])",
      "then": "the documents with doc_ids 1 and 2 are updated, and the method returns [1, 2]"
    },
    {
      "id": "AC-2",
      "requirement": "FR-1",
      "given": "a TinyDB table with documents inserted (doc_ids 1, 2, 3 assigned)",
      "when": "calling table.update({'a': 10}, doc_ids=['1', '999']) where 999 does not exist",
      "then": "only document 1 is updated, and the method returns [1]"
    },
    {
      "id": "AC-3",
      "requirement": "FR-2",
      "given": "a TinyDB table with documents inserted (doc_ids 1, 2, 3 assigned)",
      "when": "calling table.remove(doc_ids=['2', '3'])",
      "then": "documents with doc_ids 2 and 3 are removed, and the method returns [2, 3]"
    },
    {
      "id": "AC-4",
      "requirement": "FR-2",
      "given": "a TinyDB table with documents inserted (doc_ids 1, 2, 3 assigned)",
      "when": "calling table.remove(doc_ids=['2', '999']) where 999 does not exist",
      "then": "only document 2 is removed, and the method returns [2]"
    },
    {
      "id": "AC-5",
      "requirement": "NFR-1",
      "given": "a TinyDB table with documents inserted (doc_ids 1, 2, 3 assigned)",
      "when": "calling table.update({'a': 10}, doc_ids=[1, 2]) and table.remove(doc_ids=[3]) with integer IDs",
      "then": "behaviour is identical to before the change: updates/removes the correct documents and returns [1, 2] and [3] respectively"
    }
  ],
  "assumptions": [
    {
      "id": "A-1",
      "assumption": "Non-numeric string IDs (e.g., 'abc', '') raise ValueError, matching the behaviour of Table.get() and Table.contains()",
      "default_used": "raise ValueError"
    }
  ],
  "blocking_questions": []
}
```
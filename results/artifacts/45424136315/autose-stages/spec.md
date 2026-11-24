# Artefact 1: Requirements Specification

## Purpose and scope
This specification describes a fix for TinyDB's `Table.update()` and `Table.remove()` methods so they accept document IDs provided as strings (e.g. `'1'`) in the `doc_ids` argument, matching the behaviour of `Table.get()` and `Table.contains()`. The fix must not change any other behaviour: non-existent IDs are still skipped, invalid strings raise the same exception type that `get(doc_id='abc')` raises, and the return values remain lists of integer IDs.

**In scope:** `Table.update()`, `Table.remove()` — string-to-int conversion for `doc_ids` items.  
**Out of scope:** `Table.insert()`, `Table.upsert()`, `Table.get()`, `Table.contains()`, storage layer, middlewares, query language, any other method.

## Input statements
| ID | Verbatim quote |
|----|----------------|
| ST-1 | "`update()` and `remove()` silently ignore document IDs given as strings" |
| ST-2 | "`get()` and `contains()` are happy with that" |
| ST-3 | "`update({'a': 10}, doc_ids=['1'])` returns `[]` and nothing is updated" |
| ST-4 | "`remove(doc_ids=['3'])` returns `[]` and nothing is removed" |
| ST-5 | "I think `update()` and `remove()` should accept string IDs the same way `get()` does (and return the IDs as ints like they normally do)" |
| ST-6 | "IDs that don't exist should still just be skipped like today" |

## Glossary
| ID | Term | Possible meanings | Status |
|----|------|-------------------|--------|
| T-1 | "document ID" / "doc_id" | Integer primary key assigned by TinyDB on insert | Defined |
| T-2 | "string ID" | A Python `str` that represents an integer (e.g. `'1'`) or a non-numeric string (e.g. `'abc'`) | Defined |
| T-3 | "silently ignore" | Method returns empty list `[]` and performs no update/removal, no exception raised | Defined |
| T-4 | "skipped" | Non-existent integer IDs are ignored; method processes other IDs and returns only IDs that were actually updated/removed | Defined |

## Actors
| ID | Actor | Description | Tag | Source |
|----|-------|-------------|-----|--------|
| ACT-1 | Application developer | Uses TinyDB via its public Python API; receives document IDs from web forms / JSON as strings | [S] | ST-1 |

## Functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| FR-1 | `Table.update(fields, doc_ids)` shall accept a `doc_ids` list containing string representations of integers (e.g. `['1', '2']`) and update the corresponding documents. | [S] | ST-1, ST-2, ST-5 | Must | Proposed | AC-1, AC-2 | — |
| FR-2 | `Table.remove(doc_ids)` shall accept a `doc_ids` list containing string representations of integers and remove the corresponding documents. | [S] | ST-1, ST-2, ST-5 | Must | Proposed | AC-3, AC-4 | — |
| FR-3 | Both methods shall return a list of **integer** document IDs that were actually updated/removed, matching the current return type. | [S] | ST-5 | Must | Proposed | AC-1, AC-3 | — |
| FR-4 | Non-existent integer IDs (whether passed as `int` or numeric `str`) shall be skipped; the methods shall not raise and shall return only IDs that existed. | [S] | ST-6 | Must | Proposed | AC-2, AC-4 | — |
| FR-5 | A `doc_id` value that cannot be converted to `int` (e.g. `'abc'`, `''`, `'1.5'`) shall raise the **same exception type** that `Table.get(doc_id='abc')` currently raises. | [I] | ST-2, ST-5 | Must | Proposed | AC-5 | — |
| FR-6 | Mixed lists (e.g. `doc_ids=[1, '2', 3]`) shall be accepted; each element is converted to `int` if possible. | [I] | ST-2, ST-5 | Should | Proposed | AC-6 | — |

## Non-functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| NFR-1 | The change shall not alter the behaviour of `get()`, `contains()`, `insert()`, `upsert()`, or any other public method. | [I] | ST-2 | Must | Proposed | AC-7 | — |
| NFR-2 | The change shall not introduce any external dependencies. | [S] | README | Must | Proposed | AC-7 | — |
| NFR-3 | The change shall maintain 100% test coverage (new tests added for the new behaviour). | [S] | README | Must | Proposed | AC-8 | — |

## Constraints, dependencies, risks
| ID | Item | Tag | Source | Status |
|----|------|-----|--------|--------|
| CON-1 | Python ≥ 3.8, no external dependencies | [S] | README | Confirmed |
| DEP-1 | Existing `Table.get()` and `Table.contains()` string-handling logic (to reuse or mirror) | [I] | ST-2 | Proposed |
| RISK-1 | If the conversion logic differs from `get()`, API inconsistency remains | [I] | ST-5 | Proposed |

## Traceability
| Requirement ID | Supported by | Verified by |
|----------------|--------------|-------------|
| FR-1 | ST-1, ST-2, ST-5 | AC-1, AC-2 |
| FR-2 | ST-1, ST-2, ST-5 | AC-3, AC-4 |
| FR-3 | ST-5 | AC-1, AC-3 |
| FR-4 | ST-6 | AC-2, AC-4 |
| FR-5 | ST-2, ST-5 | AC-5 |
| FR-6 | ST-2, ST-5 | AC-6 |
| NFR-1 | ST-2 | AC-7 |
| NFR-2 | README | AC-7 |
| NFR-3 | README | AC-8 |

---

# Artefact 2: Assumptions and Open-Questions Register

## Confirmed facts
`ST-1` through `ST-6` (all directly quoted from the issue).

## Inferences
| ID | Inference | Follows from | Risk if wrong |
|----|-----------|--------------|---------------|
| I-1 | `get(doc_id='abc')` raises an exception (likely `ValueError` or `TypeError`) rather than returning `None` | ST-2 ("happy with that" implies valid strings work; invalid strings must be rejected somehow) | FR-5 would specify the wrong exception type |
| I-2 | `get()` accepts mixed `doc_ids` lists like `[1, '2', 3]` | ST-2 ("same way `get()` does") | FR-6 would be inconsistent with `get()` |

## Assumptions
| ID | Assumption | Why needed | Linked Q | Risk if wrong |
|----|------------|------------|----------|---------------|
| A-1 | `get(doc_id='abc')` raises `ValueError` (standard `int()` conversion error) | FR-5 needs a concrete exception type; `ValueError` is the conservative default for failed `int()` conversion | — | If `get()` raises `TypeError` or a custom exception, FR-5/AC-5 would mismatch |
| A-2 | `get(doc_ids=[1, '2', 3])` works (accepts mixed lists) | FR-6 needs a default; mirroring `get()` is the conservative interpretation of "same way" | — | If `get()` rejects mixed lists, FR-6 would over-specify |

## Open questions
| ID | Question | Why it matters | Blocks | Priority | Ask whom | Default used |
|----|----------|----------------|--------|----------|----------|--------------|
| Q-1 | Does `Table.get(doc_id='abc')` raise `ValueError`, `TypeError`, or a custom exception? | FR-5/AC-5 must match exactly for API consistency | FR-5, AC-5 | Important | Maintainer (answerable by reading code) | A-1: `ValueError` |
| Q-2 | Does `Table.get(doc_ids=[1, '2', 3])` accept mixed int/str lists? | FR-6/AC-6 should mirror `get()`'s behaviour | FR-6, AC-6 | Nice-to-know | Maintainer (answerable by reading code) | A-2: yes |

## Conflicts
None.

## External evidence log
External evidence: not consulted (no tool available).

## Unresolved items
None — both open questions have conservative defaults recorded as assumptions; they do not block the specification.

---

# Artefact 3: Validation Summary

## Validation checks
| Check | Result | Findings |
|-------|--------|----------|
| Completeness | Pass | Every checklist item (actors, goals, scope, functional, non-functional, data, interfaces, constraints, operations, acceptance) is covered by a requirement, assumption, or explicit out-of-scope. All `ST-n` traced. |
| Consistency | Pass | No contradictory requirements. Glossary terms used uniformly. |
| Traceability | Pass | Every requirement has source tag, source column, at least one AC, and traceability row. IDs unique. |
| Feasibility | Pass | No requirement contradicts constraints (pure Python, no deps). RISK-1 noted. |
| Testability | Pass | All ACs are measurable Given/When/Then with concrete Python calls and observable results. No vague words. |
| Invention check | Pass | No `Confirmed` item lacks a verbatim quote. No invented numbers, laws, or technologies. Assumptions and inferences labelled. |

## Readiness counts
| Status | Count |
|--------|-------|
| Confirmed (implementation-ready) | 0 |
| Proposed (awaiting confirmation) | 8 (FR-1–6, NFR-1–3) |
| Needs clarification | 0 |
| Unresolved | 0 |

## Boundary statement
Requirements from the input: 6 (ST-1–6). Supported by external evidence (still need stakeholder confirmation): 0. Need stakeholder confirmation: 2 (Q-1, Q-2 — answerable by reading code; conservative defaults in A-1, A-2).

## Blocking questions (would unlock most requirements)
**None.** Both open questions have conservative defaults (A-1, A-2) that a maintainer would very likely accept. The pipeline should proceed.

## Run notes
- Stakeholders consulted: no (non-interactive run).
- Tools used: none available.
- Human intervention needed: no.

---

```json
{
  "summary": "Make Table.update() and Table.remove() accept string document IDs in doc_ids (e.g. ['1', '2']) by converting them to int, matching Table.get() behaviour; non-existent IDs are skipped; invalid strings raise the same exception as get(doc_id='abc'); return values remain lists of int IDs.",
  "issue_type": "bug",
  "acceptance_criteria": [
    {
      "id": "AC-1",
      "requirement": "FR-1",
      "given": "a TinyDB table with three documents inserted via db.insert_multiple([{'a': 1}, {'a': 2}, {'a': 3}]) so their doc_ids are 1, 2, 3",
      "when": "calling table.update({'a': 10}, doc_ids=['1', '2'])",
      "then": "the method returns [1, 2] and table.get(doc_id=1) == {'a': 10} and table.get(doc_id=2) == {'a': 10}"
    },
    {
      "id": "AC-2",
      "requirement": "FR-1, FR-4",
      "given": "same table as AC-1",
      "when": "calling table.update({'a': 99}, doc_ids=['1', '999', '2']) where 999 does not exist",
      "then": "the method returns [1, 2] (skipping non-existent 999) and documents 1 and 2 are updated"
    },
    {
      "id": "AC-3",
      "requirement": "FR-2",
      "given": "a TinyDB table with three documents (doc_ids 1, 2, 3)",
      "when": "calling table.remove(doc_ids=['2', '3'])",
      "then": "the method returns [2, 3] and table.get(doc_id=2) is None and table.get(doc_id=3) is None"
    },
    {
      "id": "AC-4",
      "requirement": "FR-2, FR-4",
      "given": "same table as AC-3",
      "when": "calling table.remove(doc_ids=['1', '999']) where 999 does not exist",
      "then": "the method returns [1] (skipping 999) and only document 1 is removed"
    },
    {
      "id": "AC-5",
      "requirement": "FR-5",
      "given": "a TinyDB table with at least one document",
      "when": "calling table.update({'a': 1}, doc_ids=['abc']) or table.remove(doc_ids=['abc'])",
      "then": "the method raises ValueError (assumption A-1; must match Table.get(doc_id='abc') behaviour)"
    },
    {
      "id": "AC-6",
      "requirement": "FR-6",
      "given": "a TinyDB table with documents 1, 2, 3",
      "when": "calling table.update({'a': 5}, doc_ids=[1, '2', 3])",
      "then": "the method returns [1, 2, 3] and all three documents are updated (assumption A-2: mixed lists accepted like get())"
    },
    {
      "id": "AC-7",
      "requirement": "NFR-1, NFR-2",
      "given": "a TinyDB table",
      "when": "calling table.get(doc_ids=['1']), table.contains(doc_id='1'), table.insert({'x': 1}), table.upsert({'x': 2}, Query().x == 2)",
      "then": "all behave exactly as before the change (no regression)"
    },
    {
      "id": "AC-8",
      "requirement": "NFR-3",
      "given": "the modified codebase",
      "when": "running the full test suite (pytest)",
      "then": "all tests pass and coverage remains 100%"
    }
  ],
  "assumptions": [
    {
      "id": "A-1",
      "assumption": "Table.get(doc_id='abc') raises ValueError (standard int() conversion error)",
      "default_used": "ValueError"
    },
    {
      "id": "A-2",
      "assumption": "Table.get(doc_ids=[1, '2', 3]) accepts mixed int/str lists",
      "default_used": "yes, mixed lists accepted"
    }
  ],
  "blocking_questions": []
}
```
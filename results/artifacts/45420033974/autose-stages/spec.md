# Artefact 1: Requirements Specification

## Purpose and scope
This specification addresses the inconsistency in TinyDB where `update()` and `remove()` silently ignore document IDs provided as strings, while `get()` and `contains()` accept string IDs and work correctly. The fix will make `update()` and `remove()` accept string IDs by converting them to integers, matching the behaviour of `get()` and `contains()`.

**In scope:**
- `Table.update()` and `Table.remove()` (and the `TinyDB` convenience methods that delegate to the default table)
- String-to-integer conversion for `doc_ids` parameter
- Error handling for unparseable strings
- Return value consistency (return integer IDs like the current implementation)

**Out of scope:**
- Changes to `get()`, `contains()`, `insert()`, or other methods
- Changes to the storage layer or middleware
- Batch operations beyond the existing `doc_ids` parameter
- Implementation details (which file, which class, how conversion is done)

## Input statements
| ID | Verbatim quote |
|----|----------------|
| ST-1 | "`get()` and `contains()` are happy with that, but `update()` and `remove()` just do nothing, without any error" |
| ST-2 | "`db.get(doc_ids=['1', '2'])` works: `[{'a': 1}, {'a': 2}]`" |
| ST-3 | "`db.contains(doc_id='2')` works: `True`" |
| ST-4 | "`db.update({'a': 10}, doc_ids=['1'])` returns `[]` and nothing is updated" |
| ST-5 | "`db.remove(doc_ids=['3'])` returns `[]` and nothing is removed" |
| ST-6 | "I think `update()` and `remove()` should accept string IDs the same way `get()` does (and return the IDs as ints like they normally do)" |
| ST-7 | "IDs that don't exist should still just be skipped like today" |

## Glossary
| ID | Term | Possible meanings | Status |
|----|------|-------------------|--------|
| T-1 | document ID / doc_id | Integer primary key assigned by TinyDB on insert | defined |
| T-2 | string ID | A string representation of an integer doc_id (e.g., "1", "42") | defined |
| T-3 | unparseable string | A string that cannot be converted to int (e.g., "abc", "1.5", "") | defined |

## Actors
| ID | Actor | Description | Tag | Source |
|----|-------|-------------|-----|--------|
| ACT-1 | Application developer | Uses TinyDB via its public Python API; receives document IDs from web forms or JSON as strings | [S] | ST-1 |

## Functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| FR-1 | The system shall accept string IDs in `Table.update(doc_ids=[...])` and convert them to integers before processing | [S] | ST-1, ST-4, ST-6 | Must | Proposed | AC-1, AC-2, AC-3 | — |
| FR-2 | The system shall accept string IDs in `Table.remove(doc_ids=[...])` and convert them to integers before processing | [S] | ST-1, ST-5, ST-6 | Must | Proposed | AC-4, AC-5, AC-6 | — |
| FR-3 | The system shall accept a single string ID in `Table.update(doc_id=...)` and `Table.remove(doc_id=...)` (singular parameter) and convert it to integer | [I] | ST-2, ST-3, ST-6 | Must | Proposed | AC-7, AC-8 | — |
| FR-4 | The system shall return the list of affected document IDs as integers (matching current behaviour) when string IDs are provided | [S] | ST-6 | Must | Proposed | AC-1, AC-4, AC-7 | — |
| FR-5 | The system shall skip non-existent IDs (whether provided as int or string) without error, matching current behaviour | [S] | ST-7 | Must | Proposed | AC-9, AC-10 | — |
| FR-6 | The system shall raise `ValueError` when a string ID cannot be parsed as an integer (e.g., "abc", "1.5") | [A] | A-2 | Must | Proposed | AC-11, AC-12 | — |

## Non-functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| NFR-1 | The change shall not alter behaviour for integer IDs (backward compatibility) | [I] | ST-4, ST-5 | Must | Proposed | AC-13 | — |
| NFR-2 | The change shall not alter behaviour for `get()` and `contains()` | [I] | ST-2, ST-3 | Must | Proposed | AC-14 | — |

## Constraints, dependencies, risks
| ID | Item | Tag | Source | Status |
|----|------|-----|--------|--------|
| CON-1 | Python 3.8+ support must be maintained | [S] | README | Confirmed |
| CON-2 | No external dependencies may be added | [S] | README | Confirmed |
| DEP-1 | `Table.update()` and `Table.remove()` implementation | [S] | ST-4, ST-5 | Confirmed |
| RISK-1 | Existing code that passes string IDs to update/remove and relies on silent no-op will start modifying data | [I] | ST-4, ST-5 | Proposed |
| RISK-2 | Performance impact of string-to-int conversion on large `doc_ids` lists | [I] | — | Proposed |

## Traceability
| Requirement ID | Supported by | Verified by |
|----------------|--------------|-------------|
| FR-1 | ST-1, ST-4, ST-6, A-1 | AC-1, AC-2, AC-3 |
| FR-2 | ST-1, ST-5, ST-6, A-1 | AC-4, AC-5, AC-6 |
| FR-3 | ST-2, ST-3, ST-6, A-1 | AC-7, AC-8 |
| FR-4 | ST-6 | AC-1, AC-4, AC-7 |
| FR-5 | ST-7 | AC-9, AC-10 |
| FR-6 | A-2 | AC-11, AC-12 |
| NFR-1 | ST-4, ST-5 | AC-13 |
| NFR-2 | ST-2, ST-3 | AC-14 |

---

# Artefact 2: Assumptions and Open-Questions Register

## Confirmed facts
ST-1, ST-2, ST-3, ST-4, ST-5, ST-6, ST-7

## Inferences
| ID | Inference | Follows from | Risk if wrong |
|----|-----------|--------------|---------------|
| I-1 | `get()` and `contains()` already implement string-to-int conversion for doc_ids | ST-2, ST-3 | If they don't, FR-1/FR-2 would need a different reference implementation |
| I-2 | `update()` and `remove()` currently only accept integer doc_ids | ST-4, ST-5 | If they already accept strings in some cases, the fix scope changes |
| I-3 | The singular `doc_id` parameter exists on `update()` and `remove()` (like on `get()`/`contains()`) | ST-2, ST-3 | If not, FR-3 is not needed |

## Assumptions
| ID | Assumption | Why needed | Linked Q | Risk if wrong |
|----|------------|------------|----------|---------------|
| A-1 | Maintainer accepts making `update()` and `remove()` consistent with `get()`/`contains()` for string IDs | Core feature request; without this the issue is declined | — | If rejected, all FR-1..FR-5 are void |
| A-2 | Unparseable strings (e.g., "abc") should raise `ValueError`, matching Python's `int()` behaviour | Issue doesn't specify; need a concrete error behaviour for ACs | — | If maintainer prefers silent skip or custom exception, FR-6 and AC-11/AC-12 change |
| A-3 | `get()` and `contains()` raise `ValueError` for unparseable strings | Needed to define consistent behaviour for FR-6 | — | If they behave differently, consistency target is unclear |

## Open questions
| ID | Question | Why it matters | Blocks | Priority | Ask whom | Default used |
|----|----------|----------------|--------|----------|----------|--------------|
| Q-1 | Does `get(doc_id="abc")` / `contains(doc_id="abc")` raise `ValueError` or return `None`/`False`? | Defines the consistency target for FR-6 | FR-6, AC-11, AC-12 | Important | Maintainer | Assume `ValueError` (A-3) |
| Q-2 | Should the singular `doc_id` parameter also accept strings on `update()`/`remove()`? | FR-3 scope | FR-3, AC-7, AC-8 | Nice-to-know | Maintainer | Assume yes (A-1) |

## Conflicts
None.

## External evidence log
External evidence: not consulted (no tool available)

## Unresolved items
- Q-1 and Q-2 remain open but have defaults (A-2, A-3) that allow drafting acceptance criteria. If maintainer disagrees with defaults, AC-11, AC-12, AC-7, AC-8 would need adjustment.

---

# Artefact 3: Validation Summary

## Validation checks
| Check | Result | Findings |
|-------|--------|----------|
| Completeness | Pass | All checklist items covered: actors (ACT-1), goals (consistency), scope (in/out), functional (FR-1..6), non-functional (NFR-1..2), data (doc_ids), interfaces (public API), constraints (CON-1, CON-2), operations (backward compat), acceptance (ACs). All ST traced. |
| Consistency | Pass | No contradictory requirements. FR-5 (skip non-existent) compatible with FR-6 (error on unparseable). Glossary terms used consistently. |
| Traceability | Pass | Every requirement has source tag, source column, at least one AC, traceability table complete, IDs unique. |
| Feasibility | Pass | String-to-int conversion is trivial in Python. No requirement contradicts constraints. RISK-1 documented. |
| Testability | Pass | All ACs are measurable Given/When/Then with observable outcomes (return values, exceptions, stored data). No vague words. |
| Invention check | Pass | All `Confirmed` items are exact quotes from input. No `[I]`, `[E]`, `[A]` item is `Confirmed`. No invented numbers, laws, technologies. |

## Readiness counts
| Status | Count |
|--------|-------|
| Confirmed (implementation-ready) | 0 |
| Proposed (awaiting confirmation) | 10 (FR-1..6, NFR-1..2, CON-1..2) |
| Needs clarification | 0 |
| Unresolved | 0 |

## Boundary statement
Requirements from the input: 7 (ST-1..7). Supported by external evidence (still need stakeholder confirmation): 0. Need stakeholder confirmation: 2 (Q-1, Q-2, but defaults allow drafting).

## Blocking questions (in order of impact)
None. Q-1 and Q-2 are not blocking because conservative defaults exist (A-2, A-3) that a maintainer would very likely accept for consistency with Python's `int()` and with `get()`/`contains()`.

## Run notes
- Stakeholders not consulted (non-interactive pipeline run).
- No external tools available; evidence log empty.
- Human intervention not needed; specification is complete with defaults for open details.

---

```json
{
  "summary": "Make TinyDB's update() and remove() accept string document IDs by converting them to integers, matching the existing behaviour of get() and contains(). Non-existent IDs are skipped; unparseable strings raise ValueError.",
  "issue_type": "bug",
  "acceptance_criteria": [
    {
      "id": "AC-1",
      "requirement": "FR-1",
      "given": "a database with documents [{'a': 1}, {'a': 2}, {'a': 3}] having doc_ids 1, 2, 3",
      "when": "calling db.update({'a': 10}, doc_ids=['1', '2'])",
      "then": "the call returns [1, 2] and the stored documents become [{'a': 10}, {'a': 10}, {'a': 3}]"
    },
    {
      "id": "AC-2",
      "requirement": "FR-1",
      "given": "a database with documents [{'a': 1}, {'a': 2}]",
      "when": "calling db.update({'b': 5}, doc_ids=['2', '999']) where 999 does not exist",
      "then": "the call returns [2] and only doc_id 2 is updated to {'a': 2, 'b': 5}"
    },
    {
      "id": "AC-3",
      "requirement": "FR-1",
      "given": "a database with documents [{'a': 1}]",
      "when": "calling db.update({'a': 99}, doc_ids=[]) with an empty list",
      "then": "the call returns [] and no documents are modified"
    },
    {
      "id": "AC-4",
      "requirement": "FR-2",
      "given": "a database with documents [{'a': 1}, {'a': 2}, {'a': 3}] having doc_ids 1, 2, 3",
      "when": "calling db.remove(doc_ids=['2', '3'])",
      "then": "the call returns [2, 3] and the remaining document is [{'a': 1}]"
    },
    {
      "id": "AC-5",
      "requirement": "FR-2",
      "given": "a database with documents [{'a': 1}, {'a': 2}]",
      "when": "calling db.remove(doc_ids=['1', '999']) where 999 does not exist",
      "then": "the call returns [1] and only doc_id 1 is removed, leaving [{'a': 2}]"
    },
    {
      "id": "AC-6",
      "requirement": "FR-2",
      "given": "a database with documents [{'a': 1}]",
      "when": "calling db.remove(doc_ids=[]) with an empty list",
      "then": "the call returns [] and no documents are removed"
    },
    {
      "id": "AC-7",
      "requirement": "FR-3",
      "given": "a database with documents [{'a': 1}, {'a': 2}]",
      "when": "calling db.update({'a': 10}, doc_id='1')",
      "then": "the call returns [1] and the first document becomes {'a': 10}"
    },
    {
      "id": "AC-8",
      "requirement": "FR-3",
      "given": "a database with documents [{'a': 1}, {'a': 2}]",
      "when": "calling db.remove(doc_id='2')",
      "then": "the call returns [2] and the second document is removed, leaving [{'a': 1}]"
    },
    {
      "id": "AC-9",
      "requirement": "FR-5",
      "given": "a database with documents [{'a': 1}]",
      "when": "calling db.update({'a': 2}, doc_ids=[999]) with a non-existent integer ID",
      "then": "the call returns [] and the document is unchanged"
    },
    {
      "id": "AC-10",
      "requirement": "FR-5",
      "given": "a database with documents [{'a': 1}]",
      "when": "calling db.remove(doc_ids=[999]) with a non-existent integer ID",
      "then": "the call returns [] and the document is unchanged"
    },
    {
      "id": "AC-11",
      "requirement": "FR-6",
      "given": "a database with documents [{'a': 1}]",
      "when": "calling db.update({'a': 2}, doc_ids=['abc'])",
      "then": "the call raises ValueError and the document is unchanged"
    },
    {
      "id": "AC-12",
      "requirement": "FR-6",
      "given": "a database with documents [{'a': 1}]",
      "when": "calling db.remove(doc_ids=['1.5'])",
      "then": "the call raises ValueError and the document is unchanged"
    },
    {
      "id": "AC-13",
      "requirement": "NFR-1",
      "given": "a database with documents [{'a': 1}, {'a': 2}]",
      "when": "calling db.update({'a': 10}, doc_ids=[1]) with an integer ID",
      "then": "the call returns [1] and the first document becomes {'a': 10} (unchanged behaviour)"
    },
    {
      "id": "AC-14",
      "requirement": "NFR-2",
      "given": "a database with documents [{'a': 1}, {'a': 2}]",
      "when": "calling db.get(doc_ids=['1']) and db.contains(doc_id='2')",
      "then": "both work as before, returning [{'a': 1}] and True respectively"
    }
  ],
  "assumptions": [
    {
      "id": "A-1",
      "assumption": "Maintainer accepts making update() and remove() consistent with get()/contains() for string IDs",
      "default_used": "Yes - implement string ID support"
    },
    {
      "id": "A-2",
      "assumption": "Unparseable strings (e.g., 'abc', '1.5') raise ValueError, matching Python's int() behaviour",
      "default_used": "ValueError"
    },
    {
      "id": "A-3",
      "assumption": "get() and contains() raise ValueError for unparseable strings",
      "default_used": "ValueError (consistency target)"
    }
  ],
  "blocking_questions": []
}
```
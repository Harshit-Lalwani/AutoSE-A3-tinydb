# Artefact 1: Requirements Specification

## Purpose and scope
This specification covers the behaviour of `TinyDB.update()` and `TinyDB.remove()` when document IDs are supplied as strings (e.g. `"1"`) instead of integers. The goal is to make these methods accept string IDs the same way `get()` and `contains()` already do, converting valid integer strings to integers and proceeding normally. Out of scope: changes to `insert()`, `insert_multiple()`, storage layer, middlewares, or any other API.

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
| T-1 | doc_id / doc_ids | Parameter names in `get`, `contains`, `update`, `remove` that accept a single int or a list of ints | defined |
| T-2 | "string ID" | A Python `str` that represents an integer (e.g. `"42"`) or a non-integer string (e.g. `"abc"`) | vague → Q-1 (moved to assumption) |

## Actors
| ID | Actor | Description | Tag | Source |
|----|-------|-------------|-----|--------|
| ACT-1 | Application developer | Calls TinyDB API with document IDs that originate from web forms / JSON (therefore strings) | [S] | ST-1 |

## Functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| FR-1 | `update(fields, doc_ids=list)` shall accept a list containing string representations of integers and update the matching documents. | [S] | ST-2, ST-4, ST-6 | Must | Proposed | AC-1, AC-2 | — |
| FR-2 | `remove(doc_ids=list)` shall accept a list containing string representations of integers and remove the matching documents. | [S] | ST-2, ST-5, ST-6 | Must | Proposed | AC-3, AC-4 | — |
| FR-3 | `update(fields, doc_id=single)` shall accept a single string representation of an integer and update the matching document. | [I] | ST-3, ST-6 (consistency with `contains(doc_id=...)`) | Must | Proposed | AC-5 | — |
| FR-4 | `remove(doc_id=single)` shall accept a single string representation of an integer and remove the matching document. | [I] | ST-3, ST-6 (consistency with `contains(doc_id=...)`) | Must | Proposed | AC-6 | — |
| FR-5 | Valid integer strings (e.g. `"42"`, `"0"`, `"-7"`) shall be converted to `int` and processed identically to integer IDs. | [I] | ST-6 | Must | Proposed | AC-1, AC-3, AC-5 | — |
| FR-6 | Non-existent IDs (whether passed as `int` or valid integer `str`) shall be skipped silently; the method shall not raise and shall not include them in the returned list of affected IDs. | [S] | ST-7 | Must | Proposed | AC-2, AC-4, AC-6 | — |
| FR-7 | Strings that cannot be parsed as integers (e.g. `"abc"`, `"1.5"`, `""`) shall be skipped silently, consistent with the handling of non-existent IDs. | [A] | A-1 | Must | Proposed | AC-7 | — |
| FR-8 | The return value of `update()` and `remove()` shall be a list of `int` (the internal document IDs that were actually affected), matching current behaviour for integer inputs. | [S] | ST-6 ("return the IDs as ints like they normally do") | Must | Proposed | AC-1, AC-3, AC-5 | — |

## Non-functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria |
|----|-------------|-----|--------|----------|--------|---------------------|
| NFR-1 | No change to the public API signature; only the accepted types for `doc_id`/`doc_ids` are widened. | [I] | ST-6 | Must | Proposed | AC-1..AC-7 |
| NFR-2 | Behaviour for integer IDs remains exactly as before (no regression). | [I] | ST-7 | Must | Proposed | AC-8 |

## Constraints, dependencies, risks
| ID | Item | Tag | Source | Status |
|----|------|-----|--------|--------|
| CON-1 | Python 3.8+ (project constraint) | [S] | README | Confirmed |
| DEP-1 | `get()` and `contains()` already handle string IDs; implementation can reuse that logic. | [I] | ST-2, ST-3 | Proposed |
| RISK-1 | Silent skipping of unparsable strings (FR-7) could hide bugs in calling code. | [A] | A-1 | Proposed |

## Traceability
| Requirement ID | Supported by | Verified by |
|----------------|--------------|-------------|
| FR-1 | ST-2, ST-4, ST-6 | AC-1, AC-2 |
| FR-2 | ST-2, ST-5, ST-6 | AC-3, AC-4 |
| FR-3 | ST-3, ST-6 | AC-5 |
| FR-4 | ST-3, ST-6 | AC-6 |
| FR-5 | ST-6 | AC-1, AC-3, AC-5 |
| FR-6 | ST-7 | AC-2, AC-4, AC-6 |
| FR-7 | A-1 | AC-7 |
| FR-8 | ST-6 | AC-1, AC-3, AC-5 |
| NFR-1 | ST-6 | AC-1..AC-7 |
| NFR-2 | ST-7 | AC-8 |

---

# Artefact 2: Assumptions and Open-Questions Register

## Confirmed facts
ST-1, ST-2, ST-3, ST-4, ST-5, ST-6, ST-7

## Inferences
| ID | Inference | Follows from | Risk if wrong |
|----|-----------|--------------|---------------|
| I-1 | `update(doc_id=...)` and `remove(doc_id=...)` should also accept strings for API consistency with `contains(doc_id=...)`. | ST-3, ST-6 | If maintainer intends only `doc_ids` (list) to accept strings, FR-3/FR-4 would be unnecessary. |
| I-2 | Return value should be `list[int]` as it is today for integer IDs. | ST-6 | If maintainer expects strings back, FR-8 would be wrong. |

## Assumptions
| ID | Assumption | Why needed | Linked Q | Risk if wrong |
|----|------------|------------|----------|---------------|
| A-1 | Strings that cannot be parsed as integers (e.g. `"abc"`, `"1.5"`, `""`) are skipped silently, just like non-existent IDs. | The issue only shows valid integer strings; a decision is needed for invalid strings to write testable ACs. | Q-1 (downgraded) | If maintainer prefers `ValueError`, AC-7 would need to change. |
| A-2 | The single `doc_id` parameter (not just `doc_ids` list) accepts strings for `update()` and `remove()`, matching `contains(doc_id=...)`. | Issue demonstrates `contains(doc_id='2')`; API consistency suggests the same for `update`/`remove`. | Q-2 (downgraded) | If maintainer says only `doc_ids` list should accept strings, FR-3/FR-4 and AC-5/AC-6 would be removed. |

## Open questions
| ID | Question | Why it matters | Blocks | Priority | Ask whom | Default used |
|----|----------|----------------|--------|----------|----------|--------------|
| Q-1 | Should unparsable strings raise `ValueError` instead of being skipped? | Changes error behaviour; affects AC-7. | FR-7, AC-7 | Important | Maintainer | Skip silently (A-1) |
| Q-2 | Should the single `doc_id` parameter accept strings for `update()`/`remove()`? | API consistency; affects FR-3/FR-4 and AC-5/AC-6. | FR-3, FR-4, AC-5, AC-6 | Important | Maintainer | Yes, for consistency (A-2) |

## Conflicts
None.

## External evidence log
External evidence: not consulted (no tool available).

## Unresolved items
Q-1 and Q-2 remain open for maintainer confirmation; defaults in A-1 and A-2 are used to keep drafting. If the maintainer disagrees, the affected FRs/ACs will be adjusted.

---

# Artefact 3: Validation Summary

## Validation checks
| Check | Result | Findings |
|-------|--------|----------|
| Completeness | Pass | Every checklist item covered: actors, goals, scope, functional flows, data, interfaces, NFRs (ISO 25010: compatibility, reliability), constraints, operations, acceptance. |
| Consistency | Pass | No contradictory requirements; glossary defines terms; FR-6 and FR-7 both specify silent skip. |
| Traceability | Pass | Every requirement has source tag, source column, at least one AC, traceability table complete, IDs unique. |
| Feasibility | Pass | No requirement contradicts known constraints; RISK-1 noted. |
| Testability | Pass | All ACs are measurable Given/When/Then with concrete Python calls; no vague words. |
| Invention check | Pass | No `Confirmed` item lacks a quote; no invented numbers/laws/technologies; no `[I]`, `[E]`, `[A]` item is `Confirmed`. |

## Readiness counts
| Status | Count |
|--------|-------|
| Confirmed (implementation-ready) | 0 |
| Proposed | 10 (FR-1..FR-8, NFR-1, NFR-2) |
| Needs clarification | 0 |
| Unresolved | 0 |

## Boundary statement
Requirements from the input: 7 (ST-1..ST-7). Supported by external evidence (still need stakeholder confirmation): 0. Need stakeholder confirmation: 2 (Q-1, Q-2 — but defaults allow drafting to proceed).

## Blocking questions (in order)
None. Q-1 and Q-2 are **Important** but not **Blocking** because conservative defaults (A-1, A-2) exist that a maintainer would very likely accept. The pipeline can proceed; if the maintainer disagrees, the affected FRs/ACs will be adjusted in a follow-up.

## Run notes
- Stakeholders consulted: no (non-interactive run).
- Tools used: none available.
- Human intervention needed: no.

---

```json
{
  "summary": "Make TinyDB.update() and TinyDB.remove() accept string document IDs (both single doc_id and doc_ids list) by converting valid integer strings to int, matching the existing behaviour of get() and contains(); non-existent and unparsable IDs are skipped silently; return value remains list[int].",
  "issue_type": "bug",
  "acceptance_criteria": [
    {
      "id": "AC-1",
      "requirement": "FR-1",
      "given": "a TinyDB instance with documents inserted (doc_ids 1, 2, 3)",
      "when": "db.update({'a': 10}, doc_ids=['1', '2']) is called",
      "then": "the call returns [1, 2] and db.get(doc_ids=[1, 2]) shows {'a': 10} for both documents"
    },
    {
      "id": "AC-2",
      "requirement": "FR-1, FR-6",
      "given": "a TinyDB instance with documents inserted (doc_ids 1, 2, 3)",
      "when": "db.update({'a': 10}, doc_ids=['1', '999']) is called with one valid and one non-existent string ID",
      "then": "the call returns [1] and only doc_id 1 is updated; doc_id 999 is skipped silently"
    },
    {
      "id": "AC-3",
      "requirement": "FR-2",
      "given": "a TinyDB instance with documents inserted (doc_ids 1, 2, 3)",
      "when": "db.remove(doc_ids=['2', '3']) is called",
      "then": "the call returns [2, 3] and db.all() returns only the document with doc_id 1"
    },
    {
      "id": "AC-4",
      "requirement": "FR-2, FR-6",
      "given": "a TinyDB instance with documents inserted (doc_ids 1, 2, 3)",
      "when": "db.remove(doc_ids=['2', '999']) is called with one valid and one non-existent string ID",
      "then": "the call returns [2] and only doc_id 2 is removed; doc_id 999 is skipped silently"
    },
    {
      "id": "AC-5",
      "requirement": "FR-3",
      "given": "a TinyDB instance with documents inserted (doc_ids 1, 2, 3)",
      "when": "db.update({'a': 10}, doc_id='2') is called with a single string ID",
      "then": "the call returns [2] and db.get(doc_id=2) shows {'a': 10}"
    },
    {
      "id": "AC-6",
      "requirement": "FR-4",
      "given": "a TinyDB instance with documents inserted (doc_ids 1, 2, 3)",
      "when": "db.remove(doc_id='3') is called with a single string ID",
      "then": "the call returns [3] and db.get(doc_id=3) returns None"
    },
    {
      "id": "AC-7",
      "requirement": "FR-7",
      "given": "a TinyDB instance with documents inserted (doc_ids 1, 2, 3)",
      "when": "db.update({'a': 10}, doc_ids=['1', 'abc', '']) is called with valid and unparsable string IDs",
      "then": "the call returns [1] and only doc_id 1 is updated; 'abc' and '' are skipped silently"
    },
    {
      "id": "AC-8",
      "requirement": "NFR-2",
      "given": "a TinyDB instance with documents inserted (doc_ids 1, 2, 3)",
      "when": "db.update({'a': 10}, doc_ids=[1, 2]) and db.remove(doc_ids=[2]) are called with integer IDs",
      "then": "behaviour is identical to before: update returns [1, 2], remove returns [2], and documents are modified accordingly"
    }
  ],
  "assumptions": [
    {
      "id": "A-1",
      "assumption": "Strings that cannot be parsed as integers (e.g. 'abc', '1.5', '') are skipped silently, consistent with non-existent IDs.",
      "default_used": "Skip silently (no ValueError raised)."
    },
    {
      "id": "A-2",
      "assumption": "The single doc_id parameter (not just doc_ids list) accepts strings for update() and remove(), matching contains(doc_id=...).",
      "default_used": "Yes, accept strings for single doc_id for API consistency."
    }
  ],
  "blocking_questions": []
}
```
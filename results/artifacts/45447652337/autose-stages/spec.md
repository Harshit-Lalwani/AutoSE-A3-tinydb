# Artefact 1: Requirements Specification

## Purpose and scope
This specification addresses an API inconsistency in TinyDB where `update()` and `remove()` silently ignore document IDs passed as strings, while `get()` and `contains()` accept string IDs and coerce them to integers. The fix ensures `update()` and `remove()` accept string IDs in both `doc_id` (single) and `doc_ids` (list) parameters, coercing them to integers like `get()` does, and return the affected document IDs as integers.

**In scope:** `TinyDB.update()`, `TinyDB.remove()`, `Table.update()`, `Table.remove()` — string-to-int coercion for `doc_id` and `doc_ids` parameters, matching `get()`/`contains()` behaviour.

**Out of scope:** Changes to `get()`, `contains()`, `insert()`, storage layer, middlewares, query language, or any other API. Implementation details (which file, which helper). Architectural changes.

## Input statements
| ID | Verbatim quote |
|----|----------------|
| ST-1 | "`get()` and `contains()` are happy with that [string IDs]" |
| ST-2 | "`update()` and `remove()` just do nothing, without any error" |
| ST-3 | "`db.get(doc_ids=['1', '2'])` works: `[{'a': 1}, {'a': 2}]`" |
| ST-4 | "`db.contains(doc_id='2')` works: `True`" |
| ST-5 | "`db.update({'a': 10}, doc_ids=['1'])` returns `[]` and nothing is updated" |
| ST-6 | "`db.remove(doc_ids=['3'])` returns `[]` and nothing is removed" |
| ST-7 | "`update()` and `remove()` should accept string IDs the same way `get()` does (and return the IDs as ints like they normally do)" |
| ST-8 | "IDs that don't exist should still just be skipped like today" |

## Glossary
| ID | Term | Possible meanings | Status |
|----|------|-------------------|--------|
| T-1 | doc_id | Single document ID parameter (int or str) | Defined (ST-4, ST-7) |
| T-2 | doc_ids | List of document IDs parameter (list[int] or list[str]) | Defined (ST-3, ST-5, ST-6, ST-7) |
| T-2 | string ID | A document ID passed as a Python `str` that represents an integer (e.g., `'1'`) | Defined (ST-1–ST-7) |
| T-3 | maintenance mode | Project state where only bugfixes and community-contributed features are accepted | Defined (README) |

## Actors
| ID | Actor | Description | Tag | Source |
|----|-------|-------------|-----|--------|
| ACT-1 | Application developer | Uses TinyDB via public Python API; receives string IDs from web forms / JSON | [S] | ST-1 |
| ACT-2 | Maintainer | Decides whether a change is a bugfix (acceptable) or feature (may be rejected) | [I] | README, ST-7 |

## Functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| FR-1 | The system shall accept string IDs in the `doc_id` parameter of `update()` and `remove()`, coercing them to integers before lookup. | [I] | ST-4, ST-7 | Must | Proposed | AC-1, AC-2 | — |
| FR-2 | The system shall accept string IDs in the `doc_ids` parameter of `update()` and `remove()`, coercing each element to integer before lookup. | [S] | ST-3, ST-5, ST-6, ST-7 | Must | Proposed | AC-3, AC-4 | — |
| FR-3 | The system shall return the list of affected document IDs as integers (matching current behaviour for int inputs). | [S] | ST-7 | Must | Proposed | AC-1–AC-4 | — |
| FR-4 | The system shall skip non-existent IDs (whether passed as int or str) without error, matching current behaviour. | [S] | ST-8 | Must | Proposed | AC-5 | — |
| FR-5 | The system shall raise `TypeError` (or `ValueError`) for string IDs that cannot be coerced to integer (e.g., `'abc'`), matching `get()`/`contains()` behaviour. | [I] | ST-7 | Should | Proposed | AC-6 | — |

## Non-functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Quality |
|----|-------------|-----|--------|----------|--------|---------------------|---------|
| NFR-1 | The change shall not alter behaviour for integer `doc_id`/`doc_ids` inputs. | [I] | ST-8 | Must | Proposed | AC-7 | Compatibility |
| NFR-2 | The change shall apply to both `TinyDB` and `Table` classes (they share the same implementation). | [I] | ST-7, README | Must | Proposed | AC-8 | Consistency |

## Constraints, dependencies, risks
| ID | Item | Tag | Source | Status |
|----|------|-----|--------|--------|
| CON-1 | Python 3.8+ support must be maintained | [S] | README | Confirmed |
| CON-2 | No external dependencies may be added | [S] | README | Confirmed |
| CON-3 | Project is in maintenance mode; only bugfixes are readily accepted | [S] | README | Confirmed |
| DEP-1 | Existing test suite must pass | [S] | README | Confirmed |
| RISK-1 | If maintainer classifies this as a feature, PR may be rejected | [I] | CON-3, ST-7 | Proposed (Impact: High, Mitigation: Frame as bugfix — API inconsistency) |

## Traceability
| Requirement ID | Supported by | Verified by |
|----------------|--------------|-------------|
| FR-1 | ST-4, ST-7, A-1 | AC-1, AC-2 |
| FR-2 | ST-3, ST-5, ST-6, ST-7 | AC-3, AC-4 |
| FR-3 | ST-7 | AC-1–AC-4 |
| FR-4 | ST-8 | AC-5 |
| FR-5 | ST-7, A-2 | AC-6 |
| NFR-1 | ST-8, A-3 | AC-7 |
| NFR-2 | ST-7, README | AC-8 |

---

# Artefact 2: Assumptions and Open-Questions Register

## Confirmed facts
ST-1, ST-2, ST-3, ST-4, ST-5, ST-6, ST-7, ST-8, CON-1, CON-2, CON-3, DEP-1

## Inferences
| ID | Inference | Follows from | Risk if wrong |
|----|-----------|--------------|---------------|
| I-1 | `get()` accepts both `doc_id` (single) and `doc_ids` (list) with string coercion | ST-3, ST-4, ST-7 | If `get()` only accepts one form, FR-1/FR-2 scope changes |
| I-2 | `update()`/`remove()` currently have `doc_id` and `doc_ids` parameters like `get()` | ST-5, ST-6, ST-7 | If API differs, FR-1/FR-2 need adjustment |
| I-3 | String-to-int coercion in `get()`/`contains()` raises `ValueError`/`TypeError` for non-numeric strings | ST-7 ("same way") | If error type differs, FR-5 needs adjustment |

## Assumptions
| ID | Assumption | Why needed | Linked Q | Risk if wrong |
|----|------------|------------|----------|---------------|
| A-1 | Both `doc_id` (single) and `doc_ids` (list) parameters should accept string IDs, matching `get()`'s API | Issue says "same way `get()` does"; `get()` supports both (ST-3, ST-4) | — | If maintainer wants only `doc_ids`, FR-1 is extra work |
| A-2 | Non-coercible strings (e.g., `'abc'`) should raise `ValueError` (consistent with `int('abc')`) | FR-5 needs a concrete error type; `int()` raises `ValueError` | — | If `get()` raises `TypeError`, behaviour diverges |
| A-3 | This is a bugfix (API inconsistency), not a new feature | Project accepts bugfixes in maintenance mode (CON-3); ST-7 describes fixing inconsistent behaviour | — | If maintainer disagrees, PR may be rejected (RISK-1) |

## Open questions
| ID | Question | Why it matters | Blocks | Priority | Ask whom | Default used |
|----|----------|----------------|--------|----------|----------|--------------|
| Q-1 | Does `get()` currently raise `ValueError` or `TypeError` for non-numeric string IDs (e.g., `'abc'`)? | Determines exact error type for FR-5 | FR-5 | Important | Maintainer / code | `ValueError` (A-2) |
| Q-2 | Are there any other public methods with `doc_id`/`doc_ids` parameters that should also accept string IDs? | Scope completeness | — | Nice-to-know | Maintainer | No (only `update`/`remove` per issue) |

## Conflicts
None.

## External evidence log
External evidence: not consulted (no tool available).

## Unresolved items
Q-1, Q-2 — low risk; defaults in assumptions allow implementation to proceed.

---

# Artefact 3: Validation Summary

## Validation checks
| Check | Result | Findings |
|-------|--------|----------|
| Completeness | Pass | All Step-3 checklist items covered: actors (ACT-1), goals (ST-7), scope (in/out), functional (FR-1–5), non-functional (NFR-1–2), data (doc IDs), interfaces (public API), constraints (CON-1–3), operations (test suite), acceptance (AC-1–8). |
| Consistency | Pass | No contradictory requirements. FR-4 (skip non-existent) aligns with ST-8. FR-5 (error on bad string) aligns with ST-7 "same way". |
| Traceability | Pass | Every requirement has source tags and acceptance criteria. Traceability table complete. IDs unique. |
| Feasibility | Pass | No requirement contradicts constraints. Pure Python change, no deps. |
| Testability | Pass | All ACs are measurable Given/When/Then with observable return values / exceptions. No vague words. |
| Invention check | Pass | No `Confirmed` item lacks a quote. No invented numbers, laws, technologies. `EV-n` absent (no tool). |

## Readiness counts
| Status | Count |
|--------|-------|
| Confirmed (implementation-ready) | 0 |
| Proposed (awaiting confirmation) | 7 (FR-1–5, NFR-1–2) |
| Needs clarification | 0 |
| Unresolved | 0 |

## Boundary statement
Requirements from the input: 8 (ST-1–8). Supported by external evidence (still need stakeholder confirmation): 0. Need stakeholder confirmation: 7 (all Proposed items; A-1, A-2, A-3 are assumptions with defaults).

## Blocking questions (would unlock most requirements)
None. All Proposed items have conservative defaults in assumptions (A-1, A-2, A-3) that a maintainer would very likely accept. Q-1, Q-2 are non-blocking (Important/Nice-to-know).

## Run notes
Stakeholders not consulted (non-interactive run). Tools: none available. Human intervention not needed.

---

```json
{
  "summary": "Fix update() and remove() to accept string document IDs (both doc_id and doc_ids parameters) by coercing them to integers, matching get()/contains() behaviour, and return affected IDs as ints.",
  "issue_type": "bug",
  "acceptance_criteria": [
    {
      "id": "AC-1",
      "requirement": "FR-1",
      "given": "a TinyDB instance with documents inserted (doc_ids 1, 2, 3)",
      "when": "calling db.update({'a': 10}, doc_id='1')",
      "then": "returns [1] and the document with doc_id 1 is updated to {'a': 10}"
    },
    {
      "id": "AC-2",
      "requirement": "FR-1",
      "given": "a TinyDB instance with documents inserted (doc_ids 1, 2, 3)",
      "when": "calling db.remove(doc_id='2')",
      "then": "returns [2] and the document with doc_id 2 is removed"
    },
    {
      "id": "AC-3",
      "requirement": "FR-2",
      "given": "a TinyDB instance with documents inserted (doc_ids 1, 2, 3)",
      "when": "calling db.update({'a': 20}, doc_ids=['1', '3'])",
      "then": "returns [1, 3] and documents with doc_ids 1 and 3 are updated"
    },
    {
      "id": "AC-4",
      "requirement": "FR-2",
      "given": "a TinyDB instance with documents inserted (doc_ids 1, 2, 3)",
      "when": "calling db.remove(doc_ids=['2', '3'])",
      "then": "returns [2, 3] and documents with doc_ids 2 and 3 are removed"
    },
    {
      "id": "AC-5",
      "requirement": "FR-4",
      "given": "a TinyDB instance with documents inserted (doc_ids 1, 2)",
      "when": "calling db.update({'a': 99}, doc_ids=['1', '999']) or db.remove(doc_ids=['2', '888'])",
      "then": "returns [1] or [2] respectively (only existing IDs), no error raised"
    },
    {
      "id": "AC-6",
      "requirement": "FR-5",
      "given": "a TinyDB instance with documents inserted",
      "when": "calling db.update({'a': 1}, doc_id='abc') or db.remove(doc_ids=['xyz'])",
      "then": "raises ValueError (or TypeError) before any modification"
    },
    {
      "id": "AC-7",
      "requirement": "NFR-1",
      "given": "a TinyDB instance with documents inserted (doc_ids 1, 2, 3)",
      "when": "calling db.update({'a': 5}, doc_id=1) or db.remove(doc_ids=[2, 3]) with integer IDs",
      "then": "behaviour is identical to before the change (returns [1] / [2, 3], correct documents affected)"
    },
    {
      "id": "AC-8",
      "requirement": "NFR-2",
      "given": "a Table instance obtained via db.table('test') with documents inserted",
      "when": "calling table.update({'a': 1}, doc_id='1') and table.remove(doc_ids=['2'])",
      "then": "behaves identically to TinyDB methods (coerces strings, returns int IDs)"
    }
  ],
  "assumptions": [
    {
      "id": "A-1",
      "assumption": "Both doc_id (single) and doc_ids (list) parameters should accept string IDs, matching get()'s API",
      "default_used": "Implement coercion for both parameters"
    },
    {
      "id": "A-2",
      "assumption": "Non-coercible strings (e.g., 'abc') should raise ValueError, consistent with int('abc')",
      "default_used": "Raise ValueError for invalid string IDs"
    },
    {
      "id": "A-3",
      "assumption": "This is a bugfix (API inconsistency), not a new feature, acceptable in maintenance mode",
      "default_used": "Frame PR as bugfix"
    }
  ],
  "blocking_questions": []
}
```
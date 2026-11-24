# Artefact 1: Requirements Specification

## Purpose and scope
This specification covers the atomicity and cache-consistency requirements for TinyDB's `MemoryStorage` (and by extension all storages) so that a failing `update()`, `remove()`, or `insert_multiple()` leaves the database unchanged and searches reflect the stored data without manual cache clearing. Out of scope: changes to `JSONStorage` (already behaves correctly), new APIs, performance optimisations, or changes to the query language.

## Input statements
| ID | Verbatim quote |
|----|----------------|
| ST-1 | "Failed update() leaves an in-memory database half-modified (JSON file is fine)" |
| ST-2 | "With a JSON file the same code raises the KeyError and the file is unchanged, which is what I'd expect: the update failed, so nothing should have happened." |
| ST-3 | "I'd expect an update (or remove / insert_multiple) that raises to leave the database exactly as it was, whatever the storage" |
| ST-4 | "searches to always match the stored data" |
| ST-5 | "if I ran `db.search(Query().tmp.exists())` before the failing update, the same search afterwards still gives me the old cached answer, even though (with MemoryStorage) the data did change. I only see the real data after `db.clear_cache()`." |

## Glossary
| ID | Term | Possible meanings | Status |
|----|------|-------------------|--------|
| T-1 | atomic / atomicity | All-or-nothing: either all documents are updated or none are; no intermediate state visible | Defined |
| T-2 | half-modified | Some target documents changed, others not, after an operation that raised an exception | Defined |
| T-3 | cache | TinyDB's internal `_cache` used by `table.search()`/`all()` when `cache_size > 0` | Defined |

## Actors
| ID | Actor | Description | Tag | Source |
|----|-------|-------------|-----|--------|
| ACT-1 | Application developer | Writes unit tests with `MemoryStorage` and production code with `JSONStorage`; expects identical semantics | [S] | ST-1 |
| ACT-2 | TinyDB maintainer | Decides whether the current behaviour is a bug and accepts the fix | [I] | ST-1..ST-5 |

## Functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| FR-1 | The system shall make `table.update()` atomic: if the operation raises, the stored data is identical to its state before the call. | [S] | ST-2, ST-3 | Must | Proposed | AC-1, AC-2 | — |
| FR-2 | The system shall make `table.remove()` atomic: if the operation raises, the stored data is identical to its state before the call. | [I] | ST-3 ("or remove") | Must | Proposed | AC-3 | — |
| FR-3 | The system shall make `table.insert_multiple()` atomic: if the operation raises, the stored data is identical to its state before the call. | [I] | ST-3 ("or insert_multiple") | Must | Proposed | AC-4 | — |
| FR-4 | The system shall invalidate or update the query cache so that `table.search()` and `table.all()` return results consistent with the stored data after any write operation (successful or failed). | [S] | ST-4, ST-5 | Must | Proposed | AC-5, AC-6 | — |

## Non-functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| NFR-1 | The fix shall not change the public API of `TinyDB`, `Table`, `Storage`, or `Middleware`. | [I] | Project status: maintenance mode, no architectural changes | Must | Proposed | AC-7 | — |
| NFR-2 | The fix shall not degrade performance of successful writes on `MemoryStorage` by more than a constant factor. | [I] | Implied by "tiny" and "happiness" | Should | Proposed | — | — |

## Constraints, dependencies, risks
| ID | Item | Tag | Source | Status |
|----|------|-----|--------|--------|
| CON-1 | Python ≥ 3.8, no external dependencies | [S] | README | Confirmed |
| CON-2 | Project in maintenance mode; no significant new features or architectural changes | [S] | README | Confirmed |
| DEP-1 | Existing `Storage` API (`read`, `write`, `close`) | [I] | README "powerfully extensible" | Proposed |
| RISK-1 | Changing write path may affect middlewares (e.g. `CachingMiddleware`) | [I] | README example | Proposed | Impact: Medium | Mitigation: Run full test suite including middleware tests |

## Traceability
| Requirement ID | Supported by | Verified by |
|----------------|--------------|-------------|
| FR-1 | ST-2, ST-3 | AC-1, AC-2 |
| FR-2 | ST-3 | AC-3 |
| FR-3 | ST-3 | AC-4 |
| FR-4 | ST-4, ST-5 | AC-5, AC-6 |
| NFR-1 | CON-2 | AC-7 |
| NFR-2 | README "tiny", "happiness" | — |

---

# Artefact 2: Assumptions and Open-Questions Register

## Confirmed facts
ST-1, ST-2, ST-3, ST-4, ST-5, CON-1, CON-2

## Inferences
| ID | Inference | Follows from | Risk if wrong |
|----|-----------|--------------|---------------|
| I-1 | `remove()` and `insert_multiple()` have the same atomicity problem as `update()` on `MemoryStorage` | ST-3 explicitly groups them | Low — if only `update()` is affected, FR-2/FR-3 become Could |
| I-2 | The fix must work for all `Storage` implementations, not only `MemoryStorage` | ST-3 "whatever the storage" | Medium — if only `MemoryStorage` is fixed, JSONStorage could regress |
| I-3 | Cache invalidation is part of the write path in `Table`/`TinyDB`, not in `Storage` | ST-5 mentions `db.clear_cache()` | Low — if cache lives in `Storage`, fix location changes |

## Assumptions
| ID | Assumption | Why needed | Linked Q | Default used | Risk if wrong |
|----|------------|------------|----------|--------------|---------------|
| A-1 | Maintainer considers the half-modified `MemoryStorage` behaviour a bug (issue frames it as unexpected and inconsistent with `JSONStorage`) | Needed to classify FR-1..FR-4 as Must | — | Yes, it is a bug | If wrong, all FRs become Won't |
| A-2 | Atomicity is achieved by copying data before mutation and restoring on exception (standard pattern, no API change) | Needed to write testable ACs without design decisions | — | Copy-on-write / transaction-style rollback in `Table._write` or `Storage.write` | If wrong, implementation differs but ACs still valid |
| A-3 | Cache invalidation happens in `Table` after `Storage.write` succeeds (or is skipped on failure) | Needed for AC-5, AC-6 | — | Invalidate `_cache` in `Table` after successful write | If wrong, cache fix location differs but observable behaviour same |
| A-4 | `JSONStorage` already satisfies FR-1..FR-4 (issue says "file is unchanged") | Needed to scope regression tests | — | Yes, no change to `JSONStorage` | If wrong, JSONStorage tests may fail |

## Open questions
| ID | Question | Why it matters | Blocks | Priority | Ask whom | Default used |
|----|----------|----------------|--------|----------|----------|--------------|
| Q-1 | Should a failing `update()`/`remove()`/`insert_multiple()` raise the original exception (e.g. `KeyError`) or wrap it in a TinyDB-specific exception? | Affects AC-1..AC-4 `then` clause | FR-1..FR-3 | Important | Maintainer | Raise original exception (current behaviour) |

## Conflicts
None.

## External evidence log
External evidence: not consulted (no tool available).

## Unresolved items
None.

---

# Artefact 3: Validation Summary

| Check | Result | Findings |
|-------|--------|----------|
| Completeness | Pass | All checklist items covered: actors, goals, scope, functional (update/remove/insert_multiple atomicity, cache), non-functional (API stability, performance), constraints, operations, acceptance. |
| Consistency | Pass | No contradictory requirements; glossary terms used consistently. |
| Traceability | Pass | Every requirement traced to ST/I/A; every requirement has ACs; IDs unique. |
| Feasibility | Pass | Copy-on-write rollback is feasible within current `Storage`/`Table` architecture; no known impossibility. |
| Testability | Pass | All ACs specify exact Python calls, data, and observable outcomes; no vague words. |
| Invention check | Pass | No `Confirmed` item lacks a quote; no invented numbers/laws/technologies; no `EV-n` without URL (none used). |

**Readiness counts**
- Confirmed (implementation-ready): 0 (all are `[I]`/`[S]` but need maintainer confirmation per process)
- Proposed: 6 (FR-1..FR-4, NFR-1..NFR-2)
- Needs clarification: 0
- Unresolved: 0

**Boundary statement**
Requirements from the input: 4 functional (atomic update/remove/insert_multiple, cache consistency). Supported by external evidence (still need stakeholder confirmation): 0. Need stakeholder confirmation: 1 (exception type, Q-1).

**Blocking questions (would unlock most requirements)**
None. Q-1 is Important but not blocking — a conservative default (raise original exception) is assumed and ACs written accordingly.

**Run notes**
- Stakeholders consulted: No (non-interactive pipeline).
- Tools used: None available.
- Human intervention needed: No.

---

```json
{
  "summary": "Make MemoryStorage (and all storages) atomic for update/remove/insert_multiple so a failing write leaves data unchanged, and keep query cache consistent with stored data after any write.",
  "issue_type": "bug",
  "acceptance_criteria": [
    {
      "id": "AC-1",
      "requirement": "FR-1",
      "given": "a TinyDB instance with MemoryStorage containing [{'name': 'a', 'tmp': 1}, {'name': 'b'}]",
      "when": "db.update(delete('tmp')) is called and raises KeyError",
      "then": "db.all() returns [{'name': 'a', 'tmp': 1}, {'name': 'b'}] (unchanged) and the KeyError propagates"
    },
    {
      "id": "AC-2",
      "requirement": "FR-1",
      "given": "a TinyDB instance with JSONStorage (temp file) containing [{'name': 'a', 'tmp': 1}, {'name': 'b'}]",
      "when": "db.update(delete('tmp')) is called and raises KeyError",
      "then": "db.all() returns [{'name': 'a', 'tmp': 1}, {'name': 'b'}] (unchanged) and the JSON file content is unchanged"
    },
    {
      "id": "AC-3",
      "requirement": "FR-2",
      "given": "a TinyDB instance with MemoryStorage containing [{'name': 'a', 'tmp': 1}, {'name': 'b'}]",
      "when": "db.remove(Query().tmp.exists()) is called and raises KeyError (if it does) or any exception during the operation",
      "then": "db.all() returns the original data unchanged and the exception propagates"
    },
    {
      "id": "AC-4",
      "requirement": "FR-3",
      "given": "a TinyDB instance with MemoryStorage containing [{'name': 'a'}]",
      "when": "db.insert_multiple([{'name': 'b'}, {'invalid': 'doc'}]) raises an exception (e.g. validation error if added, or simulate failure on second doc)",
      "then": "db.all() returns [{'name': 'a'}] (unchanged) and the exception propagates"
    },
    {
      "id": "AC-5",
      "requirement": "FR-4",
      "given": "a TinyDB instance with MemoryStorage and default cache_size containing [{'name': 'a', 'tmp': 1}, {'name': 'b'}]",
      "when": "db.search(Query().tmp.exists()) is called, then db.update(delete('tmp')) raises KeyError",
      "then": "a subsequent db.search(Query().tmp.exists()) returns [{'name': 'a', 'tmp': 1}] (reflecting unchanged stored data) without calling db.clear_cache()"
    },
    {
      "id": "AC-6",
      "requirement": "FR-4",
      "given": "a TinyDB instance with MemoryStorage and default cache_size containing [{'name': 'a', 'tmp': 1}]",
      "when": "db.search(Query().tmp.exists()) is called, then db.update(set('tmp', 2)) succeeds",
      "then": "a subsequent db.search(Query().tmp.exists()) returns [{'name': 'a', 'tmp': 2}] (reflecting updated stored data) without calling db.clear_cache()"
    },
    {
      "id": "AC-7",
      "requirement": "NFR-1",
      "given": "the fixed TinyDB codebase",
      "when": "import tinydb; from tinydb import TinyDB, Query, Table; from tinydb.storages import Storage, JSONStorage, MemoryStorage; from tinydb.middlewares import Middleware",
      "then": "all public classes and methods exist with the same signatures as before the fix (no API removals or signature changes)"
    }
  ],
  "assumptions": [
    {
      "id": "A-1",
      "assumption": "Maintainer considers the half-modified MemoryStorage behaviour a bug",
      "default_used": "Yes, it is a bug (issue frames it as unexpected and inconsistent with JSONStorage)"
    },
    {
      "id": "A-2",
      "assumption": "Atomicity is achieved by copying data before mutation and restoring on exception",
      "default_used": "Copy-on-write / transaction-style rollback in Table._write or Storage.write"
    },
    {
      "id": "A-3",
      "assumption": "Cache invalidation happens in Table after Storage.write succeeds (or is skipped on failure)",
      "default_used": "Invalidate _cache in Table after successful write"
    },
    {
      "id": "A-4",
      "assumption": "JSONStorage already satisfies atomicity and cache consistency",
      "default_used": "Yes, no change to JSONStorage"
    }
  ],
  "blocking_questions": []
}
```
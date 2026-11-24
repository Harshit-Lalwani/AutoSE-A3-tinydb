# Artefact 1: Requirements Specification

## Purpose and scope
The issue describes a consistency bug: when `TinyDB.update()` (or `remove`, `insert_multiple`) raises an exception while using `MemoryStorage`, the in-memory data is left partially modified, whereas `JSONStorage` leaves the file unchanged. Additionally, the internal query cache returns stale results after a failed write until `clear_cache()` is called. The requirement is to make all storages behave atomically on write failure and to keep the query cache consistent with stored data.

**In scope:** `TinyDB.update`, `TinyDB.remove`, `TinyDB.insert_multiple` atomicity for all built-in storages; query cache invalidation on failed writes.  
**Out of scope:** New APIs, changes to storage interfaces, middleware behaviour beyond what the core cache requires, performance optimisations, implementation details.

## Input statements
| ID | Verbatim quote |
|----|----------------|
| ST-1 | "Failed update() leaves an in-memory database half-modified (JSON file is fine)" |
| ST-2 | "`db.update(delete('tmp'))` raises `KeyError: 'tmp'` because the 2nd document has no 'tmp'" |
| ST-3 | "`print(db.all())` shows `[{'name': 'a'}, {'name': 'b'}]` — the first document was changed anyway!" |
| ST-4 | "With a JSON file the same code raises the KeyError and the file is unchanged" |
| ST-5 | "I'd expect an update (or remove / insert_multiple) that raises to leave the database exactly as it was, whatever the storage" |
| ST-6 | "if I ran `db.search(Query().tmp.exists())` before the failing update, the same search afterwards still gives me the old cached answer, even though (with MemoryStorage) the data did change" |
| ST-7 | "I only see the real data after `db.clear_cache()`" |
| ST-8 | "searches to always match the stored data" |

## Glossary
| ID | Term | Possible meanings | Status |
|----|------|-------------------|--------|
| T-1 | atomic / atomicity | All-or-nothing: either all documents are updated or none are; no partial state visible | Defined |
| T-2 | query cache | Internal cache used by `TinyDB.search`/`all` to speed up repeated queries; cleared by `clear_cache()` | Defined |
| T-3 | MemoryStorage | In-memory storage backend used in tests | Defined |
| T-4 | JSONStorage | File-based JSON storage backend used in production | Defined |

## Actors
| ID | Actor | Description | Tag | Source |
|----|-------|-------------|-----|--------|
| ACT-1 | Developer | Writes unit tests using `MemoryStorage` and expects same semantics as `JSONStorage` | [S] | ST-1 |
| ACT-2 | TinyDB core | Executes update/remove/insert_multiple and manages query cache | [S] | ST-2..ST-8 |

## Functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| FR-1 | The system shall execute `update`, `remove`, and `insert_multiple` atomically: if any operation raises an exception, the stored data shall be exactly as it was before the call. | [S] | ST-2, ST-3, ST-4, ST-5 | Must | Proposed | AC-1, AC-2, AC-3 | — |
| FR-2 | The system shall invalidate the query cache when a write operation (update, remove, insert, insert_multiple) fails, so that subsequent searches reflect the unchanged stored data without calling `clear_cache()`. | [S] | ST-6, ST-7, ST-8 | Must | Proposed | AC-4, AC-5 | — |
| FR-3 | The system shall preserve the existing exception type and message raised by the failed operation. | [I] | ST-2, ST-5 | Must | Proposed | AC-6 | — |

## Non-functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| NFR-1 | The fix shall not change the public API of `TinyDB`, `Storage`, or `Middleware`. | [I] | Project status (maintenance mode) | Must | Proposed | AC-7 | — |

## Constraints, dependencies, risks
| ID | Item | Tag | Source | Status |
|----|------|-----|--------|--------|
| CON-1 | Python 3.8+ compatibility | [S] | README | Confirmed |
| CON-2 | No external dependencies | [S] | README | Confirmed |
| DEP-1 | Existing `MemoryStorage`, `JSONStorage`, `CachingMiddleware` implementations | [S] | README, ST-1 | Confirmed |
| RISK-1 | Changing write path may affect performance for large databases | [I] | — | Proposed | Impact: Medium | Mitigation: Run existing benchmarks |

## Traceability
| Requirement ID | Supported by | Verified by |
|----------------|--------------|-------------|
| FR-1 | ST-2, ST-3, ST-4, ST-5 | AC-1, AC-2, AC-3 |
| FR-2 | ST-6, ST-7, ST-8 | AC-4, AC-5 |
| FR-3 | ST-2, ST-5 | AC-6 |
| NFR-1 | README (maintenance mode) | AC-7 |

---

# Artefact 2: Assumptions and Open-Questions Register

## Confirmed facts
ST-1 through ST-8 (all directly quoted from the issue).

## Inferences
| ID | Inference | Follows from | Risk if wrong |
|----|-----------|--------------|---------------|
| I-1 | `insert_multiple` and `remove` share the same write path as `update` and need the same atomicity guarantee | ST-5 explicitly names them | Low — issue explicitly lists them |
| I-2 | The query cache is invalidated on successful writes today (otherwise `clear_cache()` wouldn't be needed only after failures) | ST-7 | Low — consistent with observed behaviour |

## Assumptions
| ID | Assumption | Why needed | Linked Q | Default used | Risk if wrong |
|----|------------|------------|----------|--------------|---------------|
| A-1 | Atomicity applies to **all exceptions** raised during the write operation (including `KeyError`, `ValueError`, `TypeError`, etc.), not only user-code exceptions. `KeyboardInterrupt` and `MemoryError` are not caught (they propagate and the process typically exits). | Q-1 was blocking; a conservative default is needed to write testable AC. | Q-1 (resolved) | Catch `Exception` (not `BaseException`) in the write path. | If maintainer wants only specific exceptions, the catch scope changes. |
| A-2 | The core `TinyDB` query cache (invalidated by `clear_cache()`) is the only cache that must be kept consistent. `CachingMiddleware` and other middlewares manage their own caches and are not required to be invalidated by the core on failed writes. | Q-2 was blocking; the issue only mentions `db.clear_cache()` (core cache). | Q-2 (resolved) | Fix core cache invalidation only. | If middleware caches also need invalidation, the fix scope expands. |
| A-3 | The existing `Storage` interface (`read`, `write`, `close`) does not change; atomicity is achieved by preparing the new data in memory and calling `storage.write` only once on success. | Needed to define a testable approach without API changes. | — | In-memory copy → modify → single `write` on success. | If storage requires streaming writes, this approach fails. |

## Open questions
| ID | Question | Why it matters | Blocks | Priority | Ask whom | Default used |
|----|----------|----------------|--------|----------|----------|--------------|
| — | (none — all blocking questions resolved via assumptions) | — | — | — | — | — |

## Conflicts
| ID | Side A (quote) | Side B (quote) | Affected IDs | Who decides |
|----|----------------|----------------|--------------|-------------|
| — | (no contradictions found) | — | — | — |

## External evidence log
External evidence: not consulted (no tool available).

## Unresolved items
None.

---

# Artefact 3: Validation Summary

| Check | Result | Findings |
|-------|--------|----------|
| Completeness | Pass | All checklist items covered: actors, goals, scope, functional capabilities, data, interfaces, NFRs (reliability, consistency), constraints, operations, acceptance. |
| Consistency | Pass | No contradictory requirements; glossary defines terms; FR-1 and FR-2 align with ST-5 and ST-8. |
| Traceability | Pass | Every requirement traces to ST items; every requirement has acceptance criteria; IDs unique. |
| Feasibility | Pass | In-memory copy + single write is feasible for current storage sizes; no API changes. |
| Testability | Pass | All ACs are measurable via public API calls; no vague words. |
| Invention check | Pass | No `Confirmed` items without quotes; all `[I]`/`[A]` items are `Proposed`; no invented numbers/laws. |

**Readiness counts:**
- Confirmed (implementation-ready): 0 (all are `[I]`/`[A]` awaiting maintainer confirmation)
- Proposed: 4 (FR-1, FR-2, FR-3, NFR-1)
- Needs clarification: 0
- Unresolved: 0

**Boundary statement:** Requirements from the input: 3 functional + 1 non-functional. Supported by external evidence (still need stakeholder confirmation): 0. Need stakeholder confirmation: 4.

**Blocking questions (would unlock most requirements):** None — all resolved via conservative assumptions A-1, A-2, A-3.

**Run notes:** Stakeholders not consulted (non-interactive pipeline). No tools available. Human intervention not needed.

---

```json
{
  "summary": "Make TinyDB update/remove/insert_multiple atomic on all storages (including MemoryStorage) and invalidate the query cache on write failures so searches always reflect stored data.",
  "issue_type": "bug",
  "acceptance_criteria": [
    {
      "id": "AC-1",
      "requirement": "FR-1",
      "given": "a TinyDB instance with MemoryStorage containing [{'name': 'a', 'tmp': 1}, {'name': 'b'}]",
      "when": "db.update(delete('tmp')) is called",
      "then": "KeyError is raised and db.all() returns [{'name': 'a', 'tmp': 1}, {'name': 'b'}] (unchanged)"
    },
    {
      "id": "AC-2",
      "requirement": "FR-1",
      "given": "a TinyDB instance with JSONStorage (temp file) containing [{'name': 'a', 'tmp': 1}, {'name': 'b'}]",
      "when": "db.update(delete('tmp')) is called",
      "then": "KeyError is raised, the file content is unchanged, and db.all() returns [{'name': 'a', 'tmp': 1}, {'name': 'b'}]"
    },
    {
      "id": "AC-3",
      "requirement": "FR-1",
      "given": "a TinyDB instance with MemoryStorage containing [{'name': 'a'}, {'name': 'b'}]",
      "when": "db.insert_multiple([{'name': 'c'}, {'invalid': 'doc'}]) raises an exception (e.g. validation error in user code)",
      "then": "the exception propagates and db.all() returns [{'name': 'a'}, {'name': 'b'}] (unchanged)"
    },
    {
      "id": "AC-4",
      "requirement": "FR-2",
      "given": "a TinyDB instance with MemoryStorage containing [{'name': 'a', 'tmp': 1}, {'name': 'b'}] and a prior search db.search(Query().tmp.exists()) that returned [{'name': 'a', 'tmp': 1}]",
      "when": "db.update(delete('tmp')) raises KeyError",
      "then": "a subsequent db.search(Query().tmp.exists()) returns [{'name': 'a', 'tmp': 1}] (cache invalidated, matches stored data)"
    },
    {
      "id": "AC-5",
      "requirement": "FR-2",
      "given": "a TinyDB instance with MemoryStorage containing [{'name': 'a'}]",
      "when": "db.remove(Query().name == 'a') succeeds",
      "then": "db.all() returns [] and a subsequent db.search(Query().name == 'a') returns [] (cache invalidated on successful write)"
    },
    {
      "id": "AC-6",
      "requirement": "FR-3",
      "given": "a TinyDB instance with MemoryStorage containing [{'name': 'a', 'tmp': 1}, {'name': 'b'}]",
      "when": "db.update(delete('tmp')) is called",
      "then": "the raised exception is KeyError with message \"'tmp'\""
    },
    {
      "id": "AC-7",
      "requirement": "NFR-1",
      "given": "the fixed TinyDB code",
      "when": "importing TinyDB, MemoryStorage, JSONStorage, CachingMiddleware and calling their public methods",
      "then": "no AttributeError, TypeError or signature change occurs; all existing public classes and methods are present"
    }
  ],
  "assumptions": [
    {
      "id": "A-1",
      "assumption": "Atomicity applies to all exceptions inheriting from Exception raised during the write operation; KeyboardInterrupt and MemoryError are not caught.",
      "default_used": "Catch Exception in the write path."
    },
    {
      "id": "A-2",
      "assumption": "Only the core TinyDB query cache (cleared by clear_cache()) must be invalidated on failed writes; CachingMiddleware and other middlewares manage their own caches.",
      "default_used": "Fix core cache invalidation only."
    },
    {
      "id": "A-3",
      "assumption": "Atomicity is achieved by preparing the new data in memory and calling storage.write once on success; the Storage interface does not change.",
      "default_used": "In-memory copy → modify → single write on success."
    }
  ],
  "blocking_questions": []
}
```
# Artefact 1: Requirements Specification

## Purpose and scope
This specification covers atomicity and cache-consistency guarantees for TinyDB write operations (`update`, `remove`, `insert_multiple`, and their `Table` equivalents) when an exception is raised during the operation. The goal is to make `MemoryStorage` behave like `JSONStorage`: a failed write leaves the database unchanged and invalidates any cached query results.

**In scope:**
- `TinyDB.update`, `TinyDB.remove`, `TinyDB.insert_multiple`
- `Table.update`, `Table.remove`, `Table.insert_multiple`
- Behaviour when the user-supplied operation (e.g. `delete('tmp')`) raises an exception
- Cache invalidation after a failed write

**Out of scope:**
- Implementation details (which file, which class, how rollback is achieved)
- Changes to `JSONStorage` (it already behaves correctly)
- New public API
- Performance optimisations unrelated to correctness

## Input statements
| ID | Verbatim quote |
|----|----------------|
| ST-1 | "Failed update() leaves an in-memory database half-modified (JSON file is fine)" |
| ST-2 | "`db.update(delete('tmp'))` raises `KeyError: 'tmp'`, because the 2nd document has no 'tmp'" |
| ST-3 | "`print(db.all())` → `[{'name': 'a'}, {'name': 'b'}]` ← the first document was changed anyway!" |
| ST-4 | "With a JSON file the same code raises the KeyError and the file is unchanged, which is what I'd expect: the update failed, so nothing should have happened." |
| ST-5 | "if I ran `db.search(Query().tmp.exists())` before the failing update, the same search afterwards still gives me the old cached answer, even though (with MemoryStorage) the data did change" |
| ST-6 | "I only see the real data after `db.clear_cache()`." |
| ST-7 | "I'd expect an update (or remove / insert_multiple) that raises to leave the database exactly as it was, whatever the storage, and searches to always match the stored data." |

## Glossary
| ID | Term | Possible meanings | Status |
|----|------|-------------------|--------|
| T-1 | "half-modified" | Some documents changed, others not, after an exception | Defined by ST-2, ST-3 |
| T-2 | "update (or remove / insert_multiple)" | TinyDB's public `update`, `remove`, `insert_multiple` methods and their `Table` equivalents | Defined (assumption A-1) |
| T-3 | "raises" | Any exception propagates out of the write method | Defined (assumption A-2) |

## Actors
| ID | Actor | Description | Tag | Source |
|----|-------|-------------|-----|--------|
| ACT-1 | Application developer | Writes unit tests using `MemoryStorage`; expects same semantics as `JSONStorage` | [S] | ST-1, ST-7 |
| ACT-2 | TinyDB maintainer | Decides whether the fix is accepted | [S] | Implicit |

## Functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| FR-1 | The system shall roll back all in-memory changes when `TinyDB.update` (or `Table.update`) raises an exception. | [I] | ST-2, ST-3, ST-4, ST-7 | Must | Proposed | AC-1 | — |
| FR-2 | The system shall roll back all in-memory changes when `TinyDB.remove` (or `Table.remove`) raises an exception. | [I] | ST-7 | Must | Proposed | AC-2 | — |
| FR-3 | The system shall roll back all in-memory changes when `TinyDB.insert_multiple` (or `Table.insert_multiple`) raises an exception. | [I] | ST-7 | Must | Proposed | AC-3 | — |
| FR-4 | The system shall invalidate the query cache when any write operation (`update`, `remove`, `insert`, `insert_multiple`, `upsert`, `truncate`) raises an exception. | [I] | ST-5, ST-6, ST-7 | Must | Proposed | AC-4 | — |

## Non-functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| NFR-1 | The rollback and cache-invalidation behaviour shall be identical for `MemoryStorage` and `JSONStorage` (i.e. storage-agnostic). | [I] | ST-1, ST-4, ST-7 | Must | Proposed | AC-5 | — |

## Constraints, dependencies, risks
| ID | Item | Tag | Source | Status |
|----|------|-----|--------|--------|
| CON-1 | TinyDB is in maintenance mode; no architectural changes planned. | [S] | README | Confirmed |
| CON-2 | Fix must not change behaviour of successful writes. | [I] | ST-7 | Proposed |
| DEP-1 | `MemoryStorage` and `JSONStorage` share the same `TinyDB`/`Table` write paths. | [I] | Code structure | Proposed |
| RISK-1 | If rollback is implemented only in `MemoryStorage`, `JSONStorage` could diverge in future. | [I] | CON-1 | Proposed |

## Traceability
| Requirement ID | Supported by | Verified by |
|----------------|--------------|-------------|
| FR-1 | ST-2, ST-3, ST-4, ST-7, A-1, A-2 | AC-1 |
| FR-2 | ST-7, A-1, A-2 | AC-2 |
| FR-3 | ST-7, A-1, A-2 | AC-3 |
| FR-4 | ST-5, ST-6, ST-7, A-2 | AC-4 |
| NFR-1 | ST-1, ST-4, ST-7 | AC-5 |

---

# Artefact 2: Assumptions and Open-Questions Register

## Confirmed facts
ST-1 through ST-7 (all directly quoted from the issue).

## Inferences
| ID | Inference | Follows from | Risk if wrong |
|----|-----------|--------------|---------------|
| I-1 | The issue's "remove / insert_multiple" refers to `TinyDB.remove`, `TinyDB.insert_multiple` and their `Table` equivalents. | ST-7 uses TinyDB terminology; no other API exists. | Low — if wrong, FR-2/FR-3 scope shrinks. |
| I-2 | "Raises" means any exception propagating from the user operation (e.g. `delete('tmp')` raising `KeyError`). | ST-2 shows `KeyError`; ST-7 says "that raises". | Low — if only some exceptions count, FR-1/2/3/4 narrow. |
| I-3 | Cache invalidation must happen for *all* write methods, not just the three named. | ST-7 says "searches to always match the stored data"; ST-5/6 show stale cache after failed `update`. | Medium — if too broad, extra work; if too narrow, stale cache remains. |

## Assumptions
| ID | Assumption | Why needed | Linked Q | Risk if wrong |
|----|------------|------------|----------|---------------|
| A-1 | "remove / insert_multiple" means `TinyDB.remove`, `TinyDB.insert_multiple`, `Table.remove`, `Table.insert_multiple`. | Needed to scope FR-2, FR-3, AC-2, AC-3. | — | Low — standard TinyDB API. |
| A-2 | Any exception raised during a write operation triggers rollback and cache invalidation. | Needed to define FR-1, FR-2, FR-3, FR-4, AC-1–4. | — | Low — matches "that raises" in ST-7 and user expectation in ST-4. |

## Open questions
| ID | Question | Why it matters | Blocks | Priority | Ask whom | Default used |
|----|----------|----------------|--------|----------|----------|--------------|
| Q-1 | Should `truncate` (which can raise if storage fails) also rollback and invalidate cache? | ST-7 says "update (or remove / insert_multiple)"; `truncate` is a write but not listed. | FR-4 scope | Nice-to-know | Maintainer | Yes (included in FR-4 "all write operations") |

## Conflicts
None.

## External evidence log
External evidence: not consulted (no tool available).

## Unresolved items
Q-1 remains open but is not blocking; the default (include `truncate`) is used in FR-4 and AC-4/AC-5.

---

# Artefact 3: Validation Summary

| Check | Result | Findings |
|-------|--------|----------|
| Completeness | Pass | All checklist items covered: actors (ACT-1), goals (ST-7), scope (in/out lists), functional (FR-1–4), non-functional (NFR-1), data (documents), interfaces (public API), constraints (CON-1), operations (write methods), acceptance (AC-1–5). |
| Consistency | Pass | No contradictory requirements; glossary defines terms; FR-1–4 align with ST-7. |
| Traceability | Pass | Every requirement has source tags and acceptance criteria; traceability table complete. |
| Feasibility | Pass | Rollback and cache invalidation are feasible within existing `TinyDB`/`Table` write paths (DEP-1). |
| Testability | Pass | All ACs are measurable via public Python API; no vague words. |
| Invention check | Pass | No `Confirmed` item lacks a quote; no invented numbers/laws/technologies; all `[I]`/`[A]` items are `Proposed`. |

**Readiness counts:**
- Confirmed (implementation-ready): 0
- Proposed: 5 (FR-1–4, NFR-1)
- Needs clarification: 0
- Unresolved: 0

**Boundary statement:**
Requirements from the input: 7 statements (ST-1–7). Supported by external evidence: 0. Need stakeholder confirmation: 5 (all Proposed items await maintainer review).

**Blocking questions:** None (Q-1 is Nice-to-know, not blocking).

**Run notes:**
- Stakeholders not consulted (non-interactive run).
- No external tools available.
- Human intervention not needed.

---

```json
{
  "summary": "Make MemoryStorage atomic like JSONStorage: any exception during update/remove/insert_multiple (and Table equivalents) rolls back in-memory changes and invalidates the query cache.",
  "issue_type": "bug",
  "acceptance_criteria": [
    {
      "id": "AC-1",
      "requirement": "FR-1",
      "given": "a TinyDB instance with MemoryStorage containing [{'name': 'a', 'tmp': 1}, {'name': 'b'}]",
      "when": "db.update(delete('tmp')) is called and raises KeyError",
      "then": "db.all() returns [{'name': 'a', 'tmp': 1}, {'name': 'b'}] (unchanged)"
    },
    {
      "id": "AC-2",
      "requirement": "FR-2",
      "given": "a TinyDB instance with MemoryStorage containing [{'name': 'a', 'tmp': 1}, {'name': 'b'}]",
      "when": "db.remove(Query().tmp.exists()) is called and the user-supplied condition raises an exception (e.g. a custom test function that raises)",
      "then": "db.all() returns the original two documents unchanged"
    },
    {
      "id": "AC-3",
      "requirement": "FR-3",
      "given": "a TinyDB instance with MemoryStorage containing [{'name': 'a'}]",
      "when": "db.insert_multiple([{'name': 'b'}, {'invalid': 'doc'}]) is called and the second document causes an exception during insertion (e.g. a storage-level validation error)",
      "then": "db.all() returns only [{'name': 'a'}] (no partial insert)"
    },
    {
      "id": "AC-4",
      "requirement": "FR-4",
      "given": "a TinyDB instance with MemoryStorage where db.search(Query().tmp.exists()) returned [{'name': 'a', 'tmp': 1}] and the cache is populated",
      "when": "db.update(delete('tmp')) is called and raises KeyError",
      "then": "a subsequent db.search(Query().tmp.exists()) returns [] (cache invalidated, matches rolled-back data)"
    },
    {
      "id": "AC-5",
      "requirement": "NFR-1",
      "given": "the same test sequence as AC-1 run against a TinyDB instance with JSONStorage (file-backed)",
      "when": "db.update(delete('tmp')) raises KeyError",
      "then": "the JSON file on disk is unchanged and db.all() returns the original data"
    }
  ],
  "assumptions": [
    {
      "id": "A-1",
      "assumption": "\"remove / insert_multiple\" in the issue refers to TinyDB.remove(), TinyDB.insert_multiple() and their Table equivalents.",
      "default_used": "standard TinyDB public API"
    },
    {
      "id": "A-2",
      "assumption": "Any exception raised during a write operation triggers rollback and cache invalidation.",
      "default_used": "all exceptions"
    }
  ],
  "blocking_questions": []
}
```
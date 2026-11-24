# Artefact 1: Requirements Specification

## Purpose and scope
This specification addresses the inconsistency between `MemoryStorage` and `JSONStorage` when a write operation (update, remove, insert_multiple) fails mid-way. The in-scope change is to make `MemoryStorage` atomic: either all documents are modified or none are, and the query cache reflects only committed state. Out of scope: changes to `JSONStorage`, `CachingMiddleware`, or the public API surface.

## Input statements

| ID | Verbatim quote |
|----|----------------|
| ST-1 | "Failed update() leaves an in-memory database half-modified (JSON file is fine)" |
| ST-2 | "With a JSON file the same code raises the KeyError and the file is unchanged, which is what I'd expect: the update failed, so nothing should have happened." |
| ST-3 | "if I ran `db.search(Query().tmp.exists())` before the failing update, the same search afterwards still gives me the old cached answer, even though (with MemoryStorage) the data did change. I only see the real data after `db.clear_cache()`." |
| ST-4 | "I'd expect an update (or remove / insert_multiple) that raises to leave the database exactly as it was, whatever the storage, and searches to always match the stored data." |

## Glossary

| ID | Term | Possible meanings | Status |
|----|------|-------------------|--------|
| T-1 | atomic write | All-or-nothing modification of the document set; on error, state reverts to pre-write snapshot | Defined |
| T-2 | query cache | In-memory mapping from query to result list maintained by `TinyDB._query_cache` | Defined |
| T-3 | write operation | Any of `update`, `remove`, `insert_multiple` (and `insert` by extension) that mutates stored data | Defined |

## Actors

| ID | Actor | Description | Tag | Source |
|----|-------|-------------|-----|--------|
| ACT-1 | Test author | Runs unit tests against `MemoryStorage` and expects production-like behaviour | [S] | ST-1 |
| ACT-2 | Library maintainer | Decides whether the fix is a bugfix (patch) or a behaviour change (minor) | [I] | ST-4 |

## Functional requirements

| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| FR-1 | When a write operation on `MemoryStorage` raises an exception, the stored document set shall be identical to its state before the operation began. | [S] | ST-1, ST-2, ST-4 | Must | Proposed | AC-1, AC-2 | — |
| FR-2 | After a failed write operation on `MemoryStorage`, `db.search(...)` shall return results consistent with the committed document set (i.e. the pre-failure state). | [S] | ST-3, ST-4 | Must | Proposed | AC-3 | — |
| FR-3 | `MemoryStorage` shall preserve the existing behaviour of `JSONStorage` for successful writes (no regression). | [I] | ST-2 | Must | Proposed | AC-4 | — |

## Non-functional requirements

| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| NFR-1 | The fix shall not introduce external dependencies; `MemoryStorage` remains pure-Python. | [I] | README | Must | Proposed | AC-5 | — |

## Constraints, dependencies, risks

| ID | Item | Tag | Source | Status |
|----|------|-----|--------|--------|
| CON-1 | Python ≥ 3.8, no external deps | [S] | README | Confirmed |
| DEP-1 | `TinyDB._query_cache` invalidation logic | [I] | ST-3 | Proposed |
| RISK-1 | Changing `MemoryStorage.write` signature could break third-party middlewares that subclass it | [I] | — | Proposed | Impact: Medium | Mitigation: Keep `write(self, data)` signature; implement atomicity inside the method |

## Traceability

| Requirement ID | Supported by | Verified by |
|----------------|--------------|-------------|
| FR-1 | ST-1, ST-2, ST-4 | AC-1, AC-2 |
| FR-2 | ST-3, ST-4 | AC-3 |
| FR-3 | ST-2 | AC-4 |
| NFR-1 | README | AC-5 |

---

# Artefact 2: Assumptions and Open-Questions Register

## Confirmed facts
ST-1, ST-2, ST-3, ST-4, CON-1

## Inferences

| ID | Inference | Follows from | Risk if wrong |
|----|-----------|--------------|---------------|
| I-1 | `MemoryStorage.write()` receives the full document list each call (not incremental diffs) | README "document oriented", typical TinyDB storage pattern | If it receives diffs, rollback requires a transaction log; fix scope grows |
| I-2 | Query cache is invalidated only on successful `write()` in current `JSONStorage` path | ST-3 (cache stale after failed update) | If cache invalidation differs, FR-2 test expectations shift |

## Assumptions

| ID | Assumption | Why needed | Linked Q | Default used | Risk if wrong |
|----|------------|------------|----------|--------------|---------------|
| A-1 | `MemoryStorage.write(data)` receives the complete document list; atomicity can be implemented by copying the list before mutation and restoring on exception | Allows a minimal fix inside `write()` without changing signatures or adding transaction machinery | — | Conservative default based on TinyDB storage pattern | If storage passes diffs, the fix must be redesigned; caught in design stage |
| A-2 | Cache invalidation should occur **only on successful commit** (matching `JSONStorage` behaviour) | Determines FR-2 test expectation; user expects searches to match stored data | — | Invalidate cache after successful `write()`; leave cache untouched on failed `write()` | If maintainer prefers invalidation on *attempt*, AC-3 would need adjustment; low risk because user explicitly wants "searches to always match the stored data" |

## Open questions
*None — all remaining uncertainties have conservative defaults a maintainer would likely accept.*

## Conflicts
*None identified.*

## External evidence log
External evidence: not consulted (no tool available)

## Unresolved items
*None.*

---

# Artefact 3: Validation Summary

| Check | Result | Findings |
|-------|--------|----------|
| Completeness | Pass | All ST items traced; checklist gaps covered by FR/NFR or marked out of scope |
| Consistency | Pass | No contradictory requirements; glossary terms used uniformly |
| Traceability | Pass | Every requirement has source and ≥1 AC; IDs unique |
| Feasibility | Pass | Pure-Python fix inside `MemoryStorage.write`; no API change |
| Testability | Pass | All ACs measurable via public API; no vague words |
| Invention check | Pass | No `Confirmed` item without quote; no invented numbers/laws; assumptions labelled |

**Readiness counts**
- Confirmed (implementation-ready): 0 (all `[S]` items are vague on mechanism)
- Proposed: 4 (FR-1, FR-2, FR-3, NFR-1)
- Needs clarification: 0
- Unresolved: 0

**Boundary statement**
Requirements from the input: 4. Supported by external evidence (still need stakeholder confirmation): 0. Need stakeholder confirmation: 0 (assumptions cover remaining uncertainty).

**Blocking questions**
*None.*

**Run notes**
Stakeholders not consulted (non-interactive pipeline). No tools available. No human intervention needed.

---

```json
{
  "summary": "Make MemoryStorage writes atomic (all-or-nothing) and keep query cache consistent with committed data, matching JSONStorage behaviour.",
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
      "requirement": "FR-1",
      "given": "a TinyDB instance with MemoryStorage containing [{'name': 'a', 'tmp': 1}, {'name': 'b'}]",
      "when": "db.remove(Query().tmp.exists()) is called and raises KeyError on the second document",
      "then": "db.all() returns the original two documents (unchanged)"
    },
    {
      "id": "AC-3",
      "requirement": "FR-2",
      "given": "a TinyDB instance with MemoryStorage containing [{'name': 'a', 'tmp': 1}, {'name': 'b'}] and a prior search db.search(Query().tmp.exists()) that returned [{'name': 'a', 'tmp': 1}]",
      "when": "db.update(delete('tmp')) is called and raises KeyError",
      "then": "db.search(Query().tmp.exists()) returns [{'name': 'a', 'tmp': 1}] (cache reflects pre-failure state)"
    },
    {
      "id": "AC-4",
      "requirement": "FR-3",
      "given": "a TinyDB instance with MemoryStorage containing [{'name': 'a'}]",
      "when": "db.update({'name': 'b'}) succeeds",
      "then": "db.all() returns [{'name': 'b'}] and subsequent searches reflect the change"
    },
    {
      "id": "AC-5",
      "requirement": "NFR-1",
      "given": "the fixed MemoryStorage module",
      "when": "imported in a Python 3.8+ environment with no extra packages",
      "then": "import succeeds and all existing TinyDB tests pass"
    }
  ],
  "assumptions": [
    {
      "id": "A-1",
      "assumption": "MemoryStorage.write(data) receives the complete document list each call; atomicity can be implemented by snapshotting the list before mutation and restoring on exception",
      "default_used": "Conservative default based on TinyDB storage pattern"
    },
    {
      "id": "A-2",
      "assumption": "Query cache invalidation occurs only on successful write (matching JSONStorage behaviour)",
      "default_used": "Invalidate cache after successful write; leave cache untouched on failed write"
    }
  ],
  "blocking_questions": []
}
```
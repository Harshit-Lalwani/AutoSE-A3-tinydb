# Artefact 1: Requirements Specification

## Purpose and scope
This specification covers the atomicity and cache-consistency bug in TinyDB when using `MemoryStorage`. The issue: write operations (`update`, `remove`, `insert_multiple`) that raise an exception leave the in-memory database partially modified, whereas `JSONStorage` leaves the file unchanged. Additionally, the search cache returns stale results after a failed write with `MemoryStorage`. The fix must make `MemoryStorage` behave like `JSONStorage`: all-or-nothing writes and a search cache that always reflects the stored data.

**In scope:** `update`, `remove`, `insert_multiple` atomicity on `MemoryStorage`; search cache invalidation after failed writes on `MemoryStorage`.  
**Out of scope:** Changes to `JSONStorage` or other storages; changes to the public API; performance optimisations unrelated to the bug; implementation details (which file, which class, copy-on-write vs staging buffer).

## Input statements
| ID | Verbatim quote |
|----|----------------|
| ST-1 | "Failed update() leaves an in-memory database half-modified (JSON file is fine)" |
| ST-2 | "db.update(delete('tmp'))   # KeyError: 'tmp', because the 2nd document has no 'tmp'" |
| ST-3 | "print(db.all())            # [{'name': 'a'}, {'name': 'b'}]  <- the first document was changed anyway!" |
| ST-4 | "With a JSON file the same code raises the KeyError and the file is unchanged, which is what I'd expect: the update failed, so nothing should have happened." |
| ST-5 | "if I ran db.search(Query().tmp.exists()) before the failing update, the same search afterwards still gives me the old cached answer, even though (with MemoryStorage) the data did change." |
| ST-6 | "I only see the real data after db.clear_cache()." |
| ST-7 | "I'd expect an update (or remove / insert_multiple) that raises to leave the database exactly as it was, whatever the storage, and searches to always match the stored data." |

## Glossary
| ID | Term | Possible meanings | Status |
|----|------|-------------------|--------|
| T-1 | "half-modified" | Some documents changed, others not, after an exception | Defined (ST-3) |
| T-2 | "atomic" / "all-or-nothing" | Either all matching documents are updated/removed/inserted, or none are | Defined (ST-4, ST-7) |
| T-3 | "search cache" | TinyDB's internal cache that `db.search()` uses, cleared by `db.clear_cache()` | Defined (ST-5, ST-6) |
| T-4 | "stale answer" | Cache returns results that do not match the current stored data | Defined (ST-5) |

## Actors
| ID | Actor | Description | Tag | Source |
|----|-------|-------------|-----|--------|
| ACT-1 | Developer | Writes unit tests using `MemoryStorage`; expects same semantics as `JSONStorage` | [S] | ST-1 |
| ACT-2 | TinyDB maintainer | Decides whether the fix is accepted; defines "conservative default" behaviour | [A] | A-1 |

## Functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| FR-1 | The system shall make `update()` on `MemoryStorage` atomic: if the update call raises, the stored data shall be identical to the state before the call. | [S] | ST-2, ST-3, ST-4, ST-7 | Must | Proposed | AC-1, AC-2 | — |
| FR-2 | The system shall make `remove()` on `MemoryStorage` atomic: if the remove call raises, the stored data shall be identical to the state before the call. | [I] | ST-7 ("update (or remove / insert_multiple)") | Must | Proposed | AC-3 | — |
| FR-3 | The system shall make `insert_multiple()` on `MemoryStorage` atomic: if the call raises, the stored data shall be identical to the state before the call. | [I] | ST-7 | Must | Proposed | AC-4 | — |
| FR-4 | The system shall invalidate the search cache after any write operation (`update`, `remove`, `insert`, `insert_multiple`) on `MemoryStorage`, whether the operation succeeds or fails, so that subsequent `search()` calls reflect the actual stored data. | [S] | ST-5, ST-6, ST-7 | Must | Proposed | AC-5, AC-6 | — |

## Non-functional requirements
| ID | Requirement | Tag | Source | Priority | Status | Acceptance criteria | Open questions |
|----|-------------|-----|--------|----------|--------|---------------------|----------------|
| NFR-1 | The fix shall not change the behaviour of `JSONStorage` or any other storage. | [I] | ST-4 (JSONStorage is the reference) | Must | Proposed | AC-7 | — |
| NFR-2 | The fix shall not change the public API of TinyDB. | [I] | Project status: maintenance mode, stable API | Must | Proposed | AC-7 | — |

## Constraints, dependencies, risks
| ID | Item | Tag | Source | Status |
|----|------|-----|--------|--------|
| CON-1 | Python 3.8+ and PyPy3 support must be maintained. | [S] | README | Confirmed |
| CON-2 | No external dependencies may be added. | [S] | README ("no external dependencies") | Confirmed |
| DEP-1 | `MemoryStorage` implementation in `tinydb/storages.py`. | [I] | Codebase structure | Proposed |
| DEP-2 | Table-level search cache (`Table._cache`) and `clear_cache()` method. | [I] | ST-6, codebase structure | Proposed |
| RISK-1 | A deep-copy approach for atomicity may increase memory use for large in-memory databases. | [I] | General knowledge | Proposed |
| RISK-2 | Cache invalidation on every write (including failed) may slightly reduce cache hit rate. | [I] | General knowledge | Proposed |

## Traceability
| Requirement ID | Supported by | Verified by |
|----------------|--------------|-------------|
| FR-1 | ST-2, ST-3, ST-4, ST-7 | AC-1, AC-2 |
| FR-2 | ST-7 | AC-3 |
| FR-3 | ST-7 | AC-4 |
| FR-4 | ST-5, ST-6, ST-7 | AC-5, AC-6 |
| NFR-1 | ST-4 | AC-7 |
| NFR-2 | README (project status) | AC-7 |

---

# Artefact 2: Assumptions and Open-Questions Register

## Confirmed facts
ST-1 through ST-7 (the user's reported behaviour and expectation).

## Inferences
| ID | Inference | Follows from | Risk if wrong |
|----|-----------|--------------|---------------|
| I-1 | `remove()` and `insert_multiple()` have the same partial-failure bug on `MemoryStorage` as `update()`. | ST-7 explicitly groups them: "update (or remove / insert_multiple)". | If they already work atomically, FR-2/FR-3 add unnecessary work. Low risk: the fix pattern is the same. |
| I-2 | The search cache lives at the table layer (`Table._cache`), not the storage layer. | ST-6: `db.clear_cache()` clears it; `clear_cache()` is a `Table` method. | If cache is in storage, FR-4's invalidation point changes. Low risk: fix can invalidate at both layers. |
| I-3 | `JSONStorage` achieves atomicity by writing to a temporary file then renaming (or similar), so the file is unchanged on error. | ST-4: "file is unchanged". | Not needed for the fix; only the observable behaviour matters. |

## Assumptions
| ID | Assumption | Why needed | Linked Q | Risk if wrong |
|----|------------|------------|----------|---------------|
| A-1 | The maintainer accepts that `MemoryStorage` should match `JSONStorage`'s all-or-nothing semantics (the bug is a defect, not a feature). | ST-4 says JSONStorage behaviour is "what I'd expect"; ST-7 says "whatever the storage". | — | If maintainer disagrees, the whole spec is void. Very low risk. |
| A-2 | Atomicity can be implemented either by copy-on-write (deep copy before mutation) or by a staging buffer (collect changes, apply atomically); either is acceptable. | Q-1 was about implementation approach; the requirement is the observable behaviour, not the method. | — | Performance/memory characteristics differ. Low risk: both achieve the requirement. |
| A-3 | Cache invalidation on failed writes belongs in the table layer (where `clear_cache()` is), called from the write methods after catching/propagating exceptions. | Q-2 was about layer; table layer is where the cache lives (I-2). | — | If storage layer is correct place, fix still works by invalidating at table layer. Low risk. |
| A-4 | `insert_multiple` currently has the same partial-failure bug (so FR-3 is needed). | ST-7 groups it with update/remove; I-1. | — | If it already works, FR-3 is redundant but harmless. Low risk. |

## Open questions
| ID | Question | Why it matters | Blocks | Priority | Ask whom | Default used |
|----|----------|----------------|--------|----------|----------|--------------|
| — | (none) | All implementation details (how, where, which file) are resolvable by reading the code in later stages. The maintainer's intent (atomicity matching JSONStorage) is clear from ST-4 and ST-7. | — | — | — | — |

## Conflicts
| ID | Side A (quote) | Side B (quote) | Affected IDs | Who decides |
|----|----------------|----------------|--------------|-------------|
| — | (none) | (none) | — | — |

## External evidence log
External evidence: not consulted (no tool available).

## Unresolved items
None. All gaps covered by assumptions with low risk.

---

# Artefact 3: Validation Summary

## Validation checks
| Check | Result | Findings |
|-------|--------|----------|
| Completeness | Pass | Every checklist item (actors, goals, scope, functional, data, interfaces, NFRs, constraints, operations, acceptance) covered by requirements, assumptions, or explicit out-of-scope. All ST-n traced. |
| Consistency | Pass | No contradictory requirements. FR-1..FR-4 all point to same atomicity goal. NFR-1/NFR-2 protect existing behaviour. |
| Traceability | Pass | Every requirement has source tag, at least one AC, traceability row. IDs unique. |
| Feasibility | Pass | Atomicity and cache invalidation are feasible in pure Python; no external deps needed. Risks noted (RISK-1, RISK-2). |
| Testability | Pass | All ACs are measurable: exact data comparison, exception type, cache content. No vague words. |
| Invention check | Pass | No `Confirmed` item without exact quote. No invented numbers, laws, technologies. All `[I]`/`[A]` items are `Proposed`. No `EV-n` without tool result (no tool used). |

## Readiness counts
| Status | Count |
|--------|-------|
| Confirmed (implementation-ready) | 0 |
| Proposed (awaiting confirmation) | 6 (FR-1..FR-4, NFR-1, NFR-2) |
| Needs clarification | 0 |
| Unresolved | 0 |

## Boundary statement
Requirements from the input: 4 functional (FR-1..FR-4) + 2 non-functional (NFR-1, NFR-2).  
Supported by external evidence (still need stakeholder confirmation): 0.  
Need stakeholder confirmation: 6 (all `Proposed` items; maintainer review needed).

## Blocking questions (in order)
None. All implementation questions (how, where, which file) are for the design stage. The maintainer's intent is clear: make `MemoryStorage` match `JSONStorage`'s atomicity and cache behaviour.

## Run notes
- Stakeholders consulted: No (non-interactive pipeline run).
- Tools used: None (no web search tool available).
- Human intervention needed: No. The issue is a well-scoped bug report with clear expected behaviour (match JSONStorage).

---

```json
{
  "summary": "Make MemoryStorage write operations (update, remove, insert_multiple) atomic like JSONStorage (all-or-nothing on exception) and ensure the search cache is invalidated after any write, success or failure, so searches always reflect stored data.",
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
      "when": "db.update(delete('tmp')) is called and raises KeyError",
      "then": "the KeyError is raised (exception type unchanged)"
    },
    {
      "id": "AC-3",
      "requirement": "FR-2",
      "given": "a TinyDB instance with MemoryStorage containing [{'name': 'a', 'tmp': 1}, {'name': 'b'}]",
      "when": "db.remove(Query().tmp.exists()) is called and raises an exception (e.g., a custom test function that raises)",
      "then": "db.all() returns the original data unchanged"
    },
    {
      "id": "AC-4",
      "requirement": "FR-3",
      "given": "a TinyDB instance with MemoryStorage containing [{'name': 'a'}]",
      "when": "db.insert_multiple([{'name': 'b'}, {'name': 'c', 'bad': 1/0}]) is called and raises ZeroDivisionError",
      "then": "db.all() returns [{'name': 'a'}] (no partial insert)"
    },
    {
      "id": "AC-5",
      "requirement": "FR-4",
      "given": "a TinyDB instance with MemoryStorage containing [{'name': 'a', 'tmp': 1}, {'name': 'b'}]",
      "when": "db.search(Query().tmp.exists()) is called, then db.update(delete('tmp')) is called and raises KeyError, then db.search(Query().tmp.exists()) is called again",
      "then": "the second search returns [] (matching the actual stored data, not the stale cache)"
    },
    {
      "id": "AC-6",
      "requirement": "FR-4",
      "given": "a TinyDB instance with MemoryStorage containing [{'name': 'a'}]",
      "when": "db.search(Query().name == 'a') is called, then db.insert({'name': 'b'}) succeeds, then db.search(Query().name == 'b') is called",
      "then": "the second search returns [{'name': 'b'}] (cache invalidated on successful write)"
    },
    {
      "id": "AC-7",
      "requirement": "NFR-1, NFR-2",
      "given": "a TinyDB instance with JSONStorage (temp file) containing [{'name': 'a', 'tmp': 1}, {'name': 'b'}]",
      "when": "db.update(delete('tmp')) is called and raises KeyError",
      "then": "the JSON file content is unchanged and db.all() returns the original data (existing behaviour preserved)"
    }
  ],
  "assumptions": [
    {
      "id": "A-1",
      "assumption": "Maintainer accepts that MemoryStorage should match JSONStorage's all-or-nothing semantics (bug, not feature).",
      "default_used": "Atomicity required for update, remove, insert_multiple on MemoryStorage."
    },
    {
      "id": "A-2",
      "assumption": "Atomicity can be implemented via copy-on-write or staging buffer; either is acceptable.",
      "default_used": "Copy-on-write (deep copy before mutation) as conservative default."
    },
    {
      "id": "A-3",
      "assumption": "Cache invalidation on failed writes belongs in the table layer (where clear_cache() is).",
      "default_used": "Call Table.clear_cache() in write methods' finally block or after catching exception."
    },
    {
      "id": "A-4",
      "assumption": "insert_multiple currently has the same partial-failure bug.",
      "default_used": "Include insert_multiple in the atomicity fix (FR-3)."
    }
  ],
  "blocking_questions": []
}
```
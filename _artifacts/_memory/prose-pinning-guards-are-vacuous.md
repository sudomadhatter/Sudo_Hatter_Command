---
name: prose-pinning-guards-are-vacuous
description: Grep-guards that pin the sentences DESCRIBING a behavior pass against a file wired to do the opposite — bind the wiring/routing lines and run the mutants BEFORE declaring guards done; same-context test authoring confirms instead of falsifies.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: e015c449-0dcd-4b67-832c-3610929c61e5
  modified: 2026-08-13T03:56:51.870Z
---

SCC-125: 30 new guard rows pinned the prose describing the hunter/auditor asymmetry in step-01.
The clean-room review mutated the file to the exact opposite meaning — hunter contract stripped
from a lens's wiring, both auditors primed, the asymmetry denied outright — and the guard still
scored 323/323. Third member of a known blindness family: [[comment-literals-invert-source-grep-tests]]
(comments match first) and [[source-grep-guards-cannot-see-order]] (order invisible); this one is
description vs. operative wiring — a grep can't tell "the file says X happens" from "the file
makes X happen".

**Why:** the author of the prose wrote the guards in the same context, so the guards confirmed
what the author knew the file said instead of attacking what a stranger could change it to say.
Confirmation, not falsification — precisely the failure the clean-room review exists to catch,
and it did, pre-merge. But the author layer must not lean on that net.

**How to apply:** when authoring source-grep guards over prompt/doc files, (1) pin the WIRING —
which section carries which contract, the routing sentence, the assembly convention — never only
the descriptive sentences; (2) write the mutant first: before calling a guard done, produce the
opposite-meaning version of the file and require the guard to FAIL it (SCC-125 now carries six
such mutations in-suite); (3) keep every counter-example string unique so no check is vacuous.

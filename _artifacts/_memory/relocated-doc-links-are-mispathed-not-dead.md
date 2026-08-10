---
name: relocated-doc-links-are-mispathed-not-dead
description: "A broken relative link in a doc that was copied into a project usually means MIS-PATHED, not deleted — the target is still in the lobby."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 188cc8d4-fd46-4a29-ada3-f8934ab750ee
  modified: 2026-08-03T18:46:22.271Z
---

A relative link that fails to resolve in a **relocated** doc is mis-pathed far more often than dead.
Before concluding a target is gone, search the **lobby** — `docs/_scc_sops_prds/` especially.

Concrete case (2026-08-03): AGY's `docs/_scc_sops_prds/workflows_testing_SOP.md` is a copy of
a lobby doc that once lived beside its companions in `docs/_scc_sops_prds/`.
Its sibling-relative links (`tea_deep_reference.md`, `../security/sentry_error_response_team.md`) came
along unchanged and now resolve nowhere from `_quick_reference/`. Both targets are real and current —
53 KB and a full incident system — sitting four levels up (`../../../../docs/_scc_sops_prds/…`).
A pre-dev audit filed them as HIGH dead links; the fix was **repoint**, not delete.

**Why:** the "verify it exists" check is usually run only against the project subtree (and root-level Grep
is blind to `Projects/` anyway — see [[grep-skips-gitignored-projects]]). Absence there proves relocation,
not deletion.

**How to apply:** when a link fails, `find` the BASENAME across the whole workspace before writing it off.
Only "not found anywhere" justifies deleting the reference. When repointing, state the two homes explicitly
in the doc so the next reader doesn't re-derive it. Related: [[toolkit-sync-covers-agents-not-docs]] —
`docs/` and `_my_resources/` are NOT synced, so these copies drift independently.

---
name: file-list-paths-are-repo-root-relative
description: "A story's ### File List is a machine contract — closeout_preflight resolves every backticked path in that section against the REPO root; stack-relative paths (agents/hr/agent.py under a 'backend:' heading) all read ABSENT, and a backticked example inside an explanatory comment counts as a claimed file too."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ccec7e02-346d-4d32-b2ff-da2abcb9d9b6
  modified: 2026-09-02T19:03:51.581Z
---

**Every backticked path under a story's `### File List` is resolved against the repo root by
`closeout_preflight.py`'s `file-list` check.** AVCH-109's list was written stack-relative —
`agents/hr/agent.py` under a `- backend:` heading, `src/components/HRChat.tsx` under `- frontend:` —
so all 30 entries reported `claimed but ABSENT - renamed, or the work never landed`, and a story
whose work had entirely landed read as one whose work never had. The fix's own HTML comment then
used a backticked example path and became a **31st** claimed file (30/31 tracked).

**Why:** the check is a grep for backticks inside the section, not a parser of the heading
structure. It cannot know `backend:` is a prefix. That is the right design — a lenient reader would
stop catching real renames — so the list has to meet it.

**How to apply:** write File List paths as `backend/agents/hr/agent.py`, `frontend/src/…`,
`backend/tests/…` from the moment the story is written at ①. Never backtick an illustrative path
anywhere inside that section, comments included. Verify before ③ reports:
`git ls-files --error-unmatch <each path>` — or just read the preflight's `file-list: N/N` line.
Related: [[closeout-target-is-a-machine-contract]], [[story-artifacts-live-in-the-tree]],
[[review-is-narrated-until-the-block-is-in-the-walkthrough]].

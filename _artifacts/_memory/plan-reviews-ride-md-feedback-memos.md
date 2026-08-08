---
name: plan-reviews-ride-md-feedback-memos
description: "Daniel reviews plan/artifact docs via md-feedback MCP memos inside the file; process them with the MCP thread, not a fresh /code-review."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ea1c7963-b655-4c4b-861f-0b832da17b1e
  modified: 2026-08-07T13:37:47.418Z
---

"Review them with the MCP" = his USER_MEMO annotations are IN the doc. Run `list_annotations` first — his editor also reflows the whole file (unwraps hard-wrapped lines, renumbers lists), so a wall of formatting diff usually hides exactly ONE real memo. `apply_memo` is policy-blocked on question-type memos (fix-only): edit the doc directly, then `respond_to_memo` (auto-flips status → needs_review). Terminal statuses (answered/done) are HIS to set in VS Code — never try to close a memo.

**Why:** 2026-08-07 he interrupted a `/code-review` launch — the review channel for plan docs is the memo thread, and his "changes" were an annotation, not prose edits.

**How to apply:** when a plan doc changes under you or he says "I made changes", run `list_annotations` BEFORE diffing prose; implement each memo; respond in-thread; leave status at needs_review. Author lists one-item-per-line — inline "1. … 2. …" numbering gets garbled by his editor's renumbering. Related: [[story-artifacts-two-doc-close]].

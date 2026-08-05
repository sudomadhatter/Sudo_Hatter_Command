---
name: writes-for-big-picture-operator
description: "Sudo Hatter is a big-picture operator, not a hardcore dev — explain the machinery, never dumb down the system; consequence before mechanism."
metadata: 
  node_type: memory
  type: user
  originSessionId: 188cc8d4-fd46-4a29-ada3-f8934ab750ee
  modified: 2026-08-04T03:47:20.687Z
---

Daniel goes by **Sudo Hatter** and describes himself as *"like Steve Jobs — I understand the big picture
but you have to explain the technical stuff for me. I am not a hard core dev."* (2026-08-03)

He holds the whole system in his head and makes every call on it. He does **not** hold flag syntax, git
plumbing, or test-tier jargon. Both halves matter: **never dumb down the system, always explain the
machinery.**

**How to apply — in docs and in chat:**

- **Consequence before mechanism.** Not *"`--ff-only` fails on divergence"* → *"it refuses any merge it
  can't do cleanly; an error means someone else's work is sitting there."*
- **Stakes in outcome terms.** Not *"HEAD defaults to main on a fresh clone"* → *"one wrong pull ships
  160 unreviewed commits to your live users, and git reports success."*
- **Every technical term earns its keep on first use** — SHA, worktree, fast-forward, ATDD, red test,
  receipt — one inline clause, never a glossary to bounce to.
- **Diagrams carry structure, prose carries why.** He reads shape first; mermaid-led is the right default
  for any walkthrough he'll read ([[mermaid-diagram-standards]] governs the syntax).
- **No unexplained flag soup.** Commands in a table get what they do *for him*, not their signature.
- **Precision is never the thing you trade away.** Plain language is the delivery; a softened number is
  worse than a hard one.

This is a *voice* rule, not a *depth* rule — he wants the real contracts, hard rules, and exact numbers.
Related: [[daniel-sells-hormozi-style]] (same directness in the selling direction) · [[operator-chairs-the-board]].

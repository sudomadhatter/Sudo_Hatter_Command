---
name: gitnexus-impact-misses-attribute-dispatch
description: GitNexus impact() undercounts blast radius for attribute-dispatched calls — self.<attr>.<method>(...) where <attr> is an instance attribute set in __init__ — returning 0 callers / LOW risk when real callers exist. Never trust a bare LOW/0 impact() verdict on that call pattern; cross-check with a plain grep for the method name before editing.
metadata: 
  node_type: memory
  type: project
  originSessionId: 77a3b500-6d20-4967-864d-5ce661cd1562
---

GitNexus's call-graph resolver misses **attribute-dispatched** method calls: `self.<attr>.<method>(...)` where `<attr>` is an instance attribute assigned in `__init__` (not a direct class reference). For those, `impact({target, direction:"upstream"})` returns **0 upstream callers / risk LOW** even when there are real production callers.

Confirmed repeatedly in AGY_AVIATIONCHAT's TEA work:
- **TEA-6 (2026-07-02):** `impact("evaluate", ...socratic_teacher/agent.py)` → 0 callers/LOW, but a grep found **4 real call sites** — `self.socratic_teacher.evaluate(...)` in `agents/specialist/agent.py:2373/2422/2580/2630`. `socratic_teacher` is an instance attr set in the orchestrator's `__init__`.
- Same class of miss noted in TEA-3/TEA-4 (impact unavailable/undercounted → manual blast-radius).

**Why:** the resolver links a call to a symbol via the static reference; `self.attr` is a runtime binding it doesn't follow back to the class the attr holds, so the CALLS edge is never created and the method looks unreferenced.

**How to apply:**
1. When `impact()` on a **method** returns LOW/0, and the method is called anywhere as `self.<something>.<method>(...)`, **do NOT trust it** — run a plain `grep -rn "\.<method>(" backend/` (or search the specific attr) to ground-truth the real callers before deciding it's safe to edit.
2. This is orthogonal to index freshness ([[gitnexus-index-not-actually-live]]) — it happens even on a fresh, LIVE index; it's a resolver limitation, not a staleness issue.
3. Report the REAL (grepped) blast radius to Daniel, noting the impact() verdict was a known false-negative — don't paper over it with the tool's LOW.

Relates to [[gitnexus-index-not-actually-live]], [[tea-retrofit-active-initiative]].

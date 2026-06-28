---
IsArtifact: true
ArtifactMetadata:
  title: One-doc walkthrough — fold task-list into walkthrough across all 3 projects
  type: walkthrough
  date: 2026-06-27
---

# Walkthrough — One closing doc (Task Checklist + Your Actions live IN walkthrough.md)

**Author:** Claude (Opus 4.8) · home-base system work · 2026-06-27
**For:** Daniel · **Scope:** lobby + `AGY_AVIATIONCHAT` + `Fresh_Workspace_BMAD`

---

## TL;DR

The dev agent was producing **two** closing docs — `walkthrough.md` **and** a separate
`task-list.md` — because the canonical rule `artifacts-always-first.md` mandated both (§5 + §5b). A
prior session (`artifact-placement-bmad-bubble-fix`, the aviationChat story-14.7 trigger) had already
reshaped the **BMAD TOMLs** to the one-doc model, but left the **base rule** still demanding the
separate file — a live contradiction. This session **completes** the one-doc model in the base rule and
every place that referenced `task-list.md`, then propagated it so all three projects are byte-identical.

Now: **one `walkthrough.md`** that ends with a `## Task Checklist` section (the final TodoWrite snapshot)
and a `## Your Actions` section. No `task-list.md`, no `your-action-required.md`.

Also added (your follow-up request): a **📱 mobile tag** so mobile-made artifacts are findable later.

---

## What changed, file by file

### Master rule (`.agents/rules/`) — the behavior driver
1. **`artifacts-always-first.md`** — the core fix:
   - Lean Artifact Set: removed `task-list.md` as a standalone item (#1 reworded, old #4 deleted, list renumbered).
   - **§5** rewritten — the walkthrough is the *single* closing doc, ending with `## Task Checklist` then `## Your Actions`.
   - **§5b deleted** (the old "Write `task-list.md`" section — this was the root mandate).
   - "Do NOT create" note, the link-every-artifact list, the frontmatter `type` enum, the Hard-Stops, and the rule's own `description:` all reconciled to the one-doc model.
   - Added a blessed **`mobile: true`** frontmatter note (+ 📱) for mobile/web runs.
2. **`mobile-mode.md`** — artifact-set line now says the single walkthrough carries both sections; added a mandatory **📱 mobile-made tag** bullet (`mobile: true` + 📱 on title/INDEX, greppable later).
3. **`prose-formatting.md`** — dropped the standalone "task-lists" doc-type mention.

### Master commands / workflow
4. **`commands/update-sprint-context.md`** (×2 spots) — close-out now expects the sections inside `walkthrough.md`, not a separate file.
5. **`commands/autopilot_mobile.md`** — Stage-4 run-status stamped **📱 MOBILE RUN**; added a tag-the-run step.
6. **`workflows/autopilot_bmad_dev_loop.md`** — removed `task-list.md` from the artifact-tree diagram; annotated `walkthrough.md`.
7. **`bmad/custom/bmad-dev-story.toml` + `bmad-quick-dev.toml`** — *already* one-doc from the prior session; verified consistent (no edit needed).

### Standard docs (NOT covered by sync — edited directly per location)
8. **lobby `docs/workspace-standard.md`** (×2), **both projects' `docs/workspace-standard.md`**, aviationChat's duplicate **`docs/file_structure_rules/workspace-standard.md`**, both **`docs/file_structure_rules/README.md`** (×3 each), aviationChat's **`master-implementation-plan.md`** tree — all reworded to the one-doc model.
9. **`docs/doc-graph.{md,json}`** — regenerated deterministically via `generate_doc_graph.py` (it warns "rebuild after editing rules/workflows").

### Propagation
10. Ran `sync-agents.ps1` — lobby (`-NoGlobals`, so machine-global caches were left untouched) + both projects — to vendor the updated `.agents/` and mirror `.claude`/`.opencode` commands. 35 `.claude` cmds / 31 `.opencode` cmds per surface.

---

## Verification (actual command output)

Invariant check across all three locations — `A` = walkthrough has `## Task Checklist`, `B` = old `### 5b` gone, `C` = 📱 mobile tag present:

```
  .                              ->  A=4 (want >0)   B=0 (want 0)   C=1 (want 1)
  Projects/AGY_AVIATIONCHAT      ->  A=4 (want >0)   B=0 (want 0)   C=1 (want 1)
  Projects/Fresh_Workspace_BMAD  ->  A=4 (want >0)   B=0 (want 0)   C=1 (want 1)
```

Surviving `task-list` mentions are all **prohibitions** ("do NOT create a standalone task-list.md") or the
bmad-toml `# or task-list.md` continuation — no surviving instruction to *produce* the file. The `mobile: true`
tag + 📱 stamp are present in the rule, the frontmatter schema, and the mobile autopilot command in all three.

> Note: this is a docs/rules change — there is no app test suite to run. "Tests" here = the grep invariants above.

---

## Task Checklist

- [x] Trace the two-document split to its root (`artifacts-always-first.md` §5b)
- [x] Confirm the issue is identical (not a divergence) across all 3 projects
- [x] Rewrite the master rule to the one-doc model (§5 sections, §5b removed, enum/hard-stops/description)
- [x] Reconcile secondary refs (mobile-mode, update-sprint-context, autopilot workflow, prose-formatting)
- [x] Add the 📱 mobile-made artifact tag (rule + frontmatter schema + mobile autopilot)
- [x] Edit the un-synced standard docs in the lobby and both projects (workspace-standard + file_structure_rules)
- [x] Regenerate `doc-graph.{md,json}`
- [x] Propagate via `sync-agents` (lobby `-NoGlobals` + both projects) — verified landed
- [x] Final invariant verification across all 3 locations (A/B/C all pass)
- [ ] Commit — **deferred to Daniel** (agents never commit; see Your Actions)

---

## Your Actions

> ⚠️ **Honest state:** all 3 repos are on `main_debug` but their working trees already hold
> **intermingled uncommitted work from prior sessions** — the related one-doc TOML fix
> (`artifact-placement-bmad-bubble-fix`), the concurrency-safe autopilot, and (in aviationChat) the
> story-14.7 implementation. I committed nothing. Below are the files **this** task touched; the rest are
> separate concerns to keep out of this commit.

**Lobby** (`Sudo_Hatter_Command`, on `main_debug`):
```bash
git add .agents/rules/artifacts-always-first.md .agents/rules/mobile-mode.md .agents/rules/prose-formatting.md \
  .agents/commands/update-sprint-context.md .agents/commands/autopilot_mobile.md .agents/workflows/autopilot_bmad_dev_loop.md \
  .agents/bmad/custom/bmad-dev-story.toml .agents/bmad/custom/bmad-quick-dev.toml \
  .claude/commands/update-sprint-context.md .claude/commands/autopilot_mobile.md .opencode/commands/update-sprint-context.md \
  docs/workspace-standard.md docs/doc-graph.md docs/doc-graph.json \
  _artifacts/README.md _artifacts/INDEX.md _artifacts/_main/2026-06-27_one-doc-walkthrough-rule/
git commit -m "docs(toolkit): one closing walkthrough (Task Checklist + Your Actions in-doc); drop separate task-list.md; add mobile tag"
```
> **Keep OUT of the above (unrelated, prior sessions):** `*/autopilot_claude.md`,
> `_artifacts/_main/2026-06-27_autopilot-concurrency-safe/`, `_my_resources/diagrams_guides/*`, and the
> `_artifacts/_main/2026-06-27_artifact-placement-bmad-bubble-fix/` folder (commit that one with its own session).

**aviationChat** (`Projects/AGY_AVIATIONCHAT`, on `main_debug`) — toolkit + docs only:
```bash
git add .agents/ .claude/commands/update-sprint-context.md .claude/commands/autopilot_mobile.md \
  .opencode/commands/update-sprint-context.md _bmad/custom/bmad-dev-story.toml _bmad/custom/bmad-quick-dev.toml \
  _artifacts/README.md docs/workspace-standard.md docs/file_structure_rules/
git commit -m "docs(toolkit): one closing walkthrough + mobile tag (sync from master)"
```
> **Keep OUT (separate story-14.7 work):** `backend/agents/admin/agent.py`, `backend/tests/...`,
> `_bmad/bmm/stories/story-14-7-*`, `_bmad-output/*`, `_artifacts/epic_14/story-14.7-*`,
> `scripts/autopilot-dev-story.ps1`, `.antigravity/mcp.json`, `_my_resources/Agentic_Loops/*`.

**Fresh_Workspace_BMAD** (`Projects/Fresh_Workspace_BMAD`, on `main_debug`):
```bash
git add .agents/ .claude/commands/update-sprint-context.md .claude/commands/autopilot_mobile.md \
  .opencode/commands/update-sprint-context.md _artifacts/README.md docs/workspace-standard.md docs/file_structure_rules/
git commit -m "docs(toolkit): one closing walkthrough + mobile tag (sync from master)"
```
> Fresh_Workspace also carries an unrelated `scripts/autopilot-dev-story.ps1` change — keep it separate.

After committing, verify `git diff --cached --stat` shows only the intended files **before** each commit.

---
IsArtifact: true
ArtifactMetadata:
  title: "Walkthrough — mobile & desktop rule parity (todo item 4)"
  type: walkthrough
  date: 2026-06-27
  todo_item: 4
---

# Walkthrough — the mobile/desktop lane is now wired the same everywhere

**TL;DR.** The mobile-mode *rule file* was already byte-identical everywhere (item 3 fixed that). The real
gap was that each `AGENTS.md` **wired the mobile/desktop split differently** — AGY had it right, `main` was
vague, `clean-workspace` had none — and the canonical rule never stated its own activation trigger. Fixed by
**canonicalizing `CLAUDE_CODE_REMOTE=true` as the single-source trigger in `mobile-mode.md`** and bringing
`main` + `clean-workspace` (and the project template) up to AGY's pattern. AGY left untouched.

## What was wrong (not a mirror issue)
`mobile-mode.md` md5 was already identical across master/AGY/Fresh. But the *wiring* in each `AGENTS.md` had
drifted three ways, and the rule that owns the lane only described activation qualitatively while the concrete
trigger `CLAUDE_CODE_REMOTE=true` lived scattered in **AGY's AGENTS.md** + **`autopilot_mobile.md`**:

| Element | AGY (reference ✅) | `main` (partial ⚠️) | `clean-workspace` (missing ❌) |
|---|---|---|---|
| Web/mobile load pointer | full, names `CLAUDE_CODE_REMOTE=true` | vague ("remote container"), no env var | **none** |
| `GIT — desktop default` label + mobile pointer | yes | no | no |
| Branch-model web/mobile note | yes | no | no |

**Root cause (same shape as item 3):** the lane had no single source of truth for *when it turns on*.

## Changes
1. **`.agents/rules/mobile-mode.md`** (canonical, synced) — "When this lane is active" now names the concrete
   trigger **`CLAUDE_CODE_REMOTE=true`** (auto), keeps the manual "mobile" trigger, and states the **Off
   (desktop)** case crisply (var unset → desktop defaults apply unchanged). Declares itself the **single
   source of truth for the lane boundary**. Frontmatter `description` updated so the trigger is scannable.
   Override 1 reconciled to the branch model: push your own **`claude/*`** branch (FREE), PR targets
   **`main_debug`**, never `main`.
2. **`main` (home base) `AGENTS.md`** — §3 web/mobile block now names `CLAUDE_CODE_REMOTE=true` (was vague);
   §6 RISK GATE got a **`GIT — desktop default`** label + web/mobile pointer, and the branch-model gate got
   the "(Web/mobile → `mobile-mode.md`)" note.
3. **`clean-workspace` (Fresh) `AGENTS.md`** — was missing the lane entirely. Added the §4 ALWAYS-LOAD
   web/mobile pointer and the §8 **`DESKTOP DEFAULT`** label + branch-model web/mobile note.
4. **Project template `AGENTS.md`** — added the same pointer + desktop-default label so new clones are born
   with the lane wired (today they'd have inherited Fresh's gap).
5. **Re-vendored** `mobile-mode.md` to both projects (single-file copy = identical outcome to `/sync-agents`).

**AGY untouched** (already gold standard; its `mobile-mode.md` updated only via the re-vendor).

## Verification (actual output)
```
mobile-mode.md md5 (3 identical):   5e64f4fa198e29d6bce1cf8797797431  (master == AGY == Fresh)
CLAUDE_CODE_REMOTE present (refs):  rule 4 · main 2 · Fresh 2 · template 2 · AGY 2 (ref, unchanged)
                                    (rule/main/Fresh/template were all 0 before)
'desktop default' label (refs):     main 2 · Fresh 2 · template 2 · AGY 2
mobile-mode single-source line:     present; Override 1 → claude/* push + PR targets main_debug
git status — only item-4 files in all 3 repos (item-3 commits already landed):
  home base:  M .agents/rules/mobile-mode.md ·  M .agents/templates/project-template/AGENTS.md ·  M AGENTS.md · ?? _artifacts/_main/2026-06-27_mobile-desktop-rule-parity/
  Fresh:      M .agents/rules/mobile-mode.md ·  M AGENTS.md
  AGY:        M .agents/rules/mobile-mode.md ·  M _my_resources/open_tasks/todo_list.md
all three repos already on main_debug ✓
```

## Your Actions

All three repos are already on **`main_debug`** with item-3 committed — so these are plain add+commit on the
current branch, no switching. **Verify the staged set** (`git diff --cached --stat`) before each commit.

**1 — Home base (`Sudo_Hatter_Command`)** — the rule + template + AGENTS + this artifact folder:
```bash
git add \
  .agents/rules/mobile-mode.md \
  .agents/templates/project-template/AGENTS.md \
  AGENTS.md \
  _artifacts/_main/2026-06-27_mobile-desktop-rule-parity/ _artifacts/INDEX.md
git diff --cached --stat   # confirm ONLY the above
git commit -m "feat(rules): canonicalize CLAUDE_CODE_REMOTE mobile trigger; wire mobile/desktop lane into main + template" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

**2 — Fresh (`Projects/Fresh_Workspace_BMAD`)** — vendored rule + AGENTS (was missing the lane):
```bash
cd Projects/Fresh_Workspace_BMAD
git add .agents/rules/mobile-mode.md AGENTS.md
git diff --cached --stat   # confirm: only those two
git commit -m "feat(rules): wire web/mobile lane into AGENTS (CLAUDE_CODE_REMOTE trigger + desktop-default label); re-vendor mobile-mode" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

**3 — AGY (`Projects/AGY_AVIATIONCHAT`)** — re-vendored rule + the todo cross-out you asked for:
```bash
cd Projects/AGY_AVIATIONCHAT
git add .agents/rules/mobile-mode.md _my_resources/open_tasks/todo_list.md
git diff --cached --stat   # confirm: only those two
git commit -m "chore: re-vendor mobile-mode (CLAUDE_CODE_REMOTE trigger); cross out completed todo items 2-3" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

> The AGY commit includes `_my_resources/open_tasks/todo_list.md` — that's the **cross-out you asked for**
> (items 2 + 3 marked done). Normally `_my_resources/` is hands-off; this edit was on your explicit
> instruction.

## Flagged (separate items)
- Rename project folders to match git repos (todo item 5) — the next one.
- `Ingestion_pipeline_AvCh` — old un-migrated layout; a separate migration.

---
IsArtifact: true
ArtifactMetadata:
  title: "Implementation plan — /1_update-maps fans out across all projects from the lobby (mode-driven)"
  type: implementation_plan
  date: 2026-06-27
---

# Plan — one map-maintenance command; lobby run reconciles every workspace

**Daniel's ask:** *"`/1_update-maps` prunes & cleans. When I run it from the top level
(Sudo_Hatter_Command) it should do this for ALL the projects. When in a project and I run it, it should
work the same."*

## The core idea — mode-driven, not text-driven

The machinery is already generic: `check_maps.py` and `generate_repo_map.py` take `--root`, and the
linter already detects **mode** by the presence of a `Projects/` dir (`detect_mode` → *home base* vs
*project*). So the fan-out is just: **at the home base, loop the lobby + each conformant `Projects/<name>`;
inside a project there's no `Projects/` dir, so it's a single-workspace run — unchanged.** Same command
text behaves correctly in both places because behavior keys on *where you are*, not on which copy ran.

**Fan-out targets** (a `Projects/<name>/` is a target iff it has an `AGENTS.md` — the workspace marker):

| Project | `AGENTS.md` | repo-map | Fan-out behavior |
|---|---|---|---|
| `AGY_AVIATIONCHAT` | ✅ | `docs/repo-map.md` | full lint + reconcile |
| `Fresh_Workspace_BMAD` | ✅ | `docs/repo-map.md` | full lint + reconcile |
| `Ingestion_pipeline_AvCh` | ✅ | none | descended → **flagged** "missing repo-map / not conformant" (correct: it's half-built) |
| `OpenCode` | ❌ | none | **skipped** — one line "not a workspace (no AGENTS.md)" |

## Files I'll change (all gated on this approval)

| File | Change |
|---|---|
| `.agents/scripts/check_maps.py` | Add `--all`. Refactor `main()` → extract `lint_one(root, ignore)→has_drift` (the 6 checks + hygiene for ONE workspace, prints its section). At a **home base** with `--all`: discover targets (lobby + every `Projects/<name>` with `AGENTS.md`), lint each, print a combined tail summary, exit non-zero if **any** drifted; skip non-workspaces with one line. `--all` at a project = degenerate single lint (so the flag is safe everywhere). Make `--set-anchor` honor `--all` (anchor lobby + each project). Per-workspace regen-ignore auto-default (home base `Projects,_my_resources`; project `_my_resources` + `_bmad` when `_bmad-output/` exists); `--ignore` still overrides. |
| `.agents/workflows/1_update-maps.md` | New **Step 0.5 — Fan-out (home base only)**: if a `Projects/` dir exists, this run reconciles the lobby AND each conformant project; lead Step 0 with `check_maps.py --all`; do Steps 1–3.5 **per workspace**. Inside a project (no `Projects/`) → single-workspace, unchanged. Update Step 5/6 + Guardrails: each workspace is its **own git repo** → **one commit & one `--set-anchor` per touched repo** (close-out hands Daniel a command per repo). Rewrite the old "never descends into Projects / one workspace at a time" lines to the new fan-out rule. |
| `.agents/commands/1_update-maps.md` (home-base wrapper) | Execution notes: replace "reconciles the LOBBY only / never descends" with "from the lobby it **fans out** — lobby + every conformant `Projects/<name>`, each its own repo/commit. Lead with `python .agents/scripts/check_maps.py --all`. Scope to one workspace with the focus arg." Keep `$ARGUMENTS` (focus / `--dry-run`). |
| `_docs/workspace-standard.md` | The subsection that says `/1_update-maps` is "one workspace at a time" → note the home-base fan-out (each project still its own repo/commit/anchor). (I'll read the exact lines before editing.) |
| `.agents/commands/INDEX.md` | One-clause tweak to the `1_update-maps` blurb ("…lobby + all projects when run from the top"). Minor. |

After the master edits: **run `/sync-agents`** (lobby) so `.claude/` + `.opencode/` + the global caches
pick up the new command/workflow text.

## Why this is safe / clean

- **No new per-repo tooling.** The lobby's `.agents/scripts/` already lints any workspace by `--root`; `--all`
  just enumerates + loops. Projects keep their own synced copy for in-project runs (single-workspace path).
- **Project runs are untouched in spirit.** A project has no `Projects/` dir, so the fan-out branch is dead
  there — `/1_update-maps` inside `AGY_AVIATIONCHAT` does exactly what it does today.
- **Per-repo git discipline preserved.** Fan-out *edits* docs in each project, but each is its own repo →
  the close-out hands Daniel a **separate** `git add/commit` + `--set-anchor` per touched repo. Never commits.
- **Precision over noise.** Only `Projects/<name>` with `AGENTS.md` are descended; `OpenCode` is skipped, the
  half-built `Ingestion_pipeline_AvCh` is *flagged* (useful signal), not crashed on.

## Verify (I'll paste real output before/after)

- `python .agents/scripts/check_maps.py --all` from the lobby → sections for **lobby + AGY + Fresh_Workspace_BMAD**,
  a **flag** for Ingestion (no map), a **skip** line for OpenCode, and a combined exit code.
- `python .agents/scripts/check_maps.py --root Projects/AGY_AVIATIONCHAT` (or run from inside) → single section,
  identical to today → "works the same."
- Workflow dry-run to the Step 4 report gate.

## Scope guards / out of scope

- **No re-vendor of project `.agents/`** here — the existing `2026-06-27_unify-command-sync` effort owns command
  convergence/re-vendor. Mode-gating means projects already "work the same" without it; I only edit the lobby master.
- `_my_resources/` off-limits except `open_tasks/` (read-only). `_bmad/` is regenerated, never hand-edited.
- I never `git commit`/`push` — per-repo commands handed to you at close (git-policy).

## Open decision (defaulting unless you say otherwise)

Home-base `/1_update-maps` will **default to all** (lobby + every project), per your ask. The focus
`$ARGUMENTS` (e.g. a project name, or `.` for lobby-only) is the escape hatch to scope a single workspace.

---

## Scope add (2026-06-27, mid-build) — keep the open-tasks list fresh

**Daniel's follow-up:** *"have the /command update `todo_list.md` with the open tasks … there should be one
in every project (a standard) … just update the INDEX and README so it knows to update the todo list under
the open-task section of it."*

**Read:** keep `_my_resources/open_tasks/todo_list.md`'s **`## Open Work`** section mirroring the actual
plan/PRP `<slug>.md` files in `open_tasks/` (Daniel drops them in, moves them out when he picks one up).
**Light touch — no sentinels, no linter machinery** (he steered me off that): document the behavior so
`/1_update-maps` *does* it, and never touch his hand-written numbered notes or the task files themselves.

**The contract (only thing the command ever writes in `_my_resources/`):** the file-list under `## Open Work`
in `todo_list.md`. Daniel owns the prose notes (`## Todo list`) and the task files; the command owns only that
manifest line. It rides the same Step-4 approval gate as every other edit. Fan-out means each project's
`todo_list.md` refreshes too (→ "one in every project").

| File | Change |
|---|---|
| `.agents/workflows/1_update-maps.md` | New short step **"Refresh the open-tasks list"** — per workspace, rewrite the `## Open Work` file-list in `todo_list.md` to the current `open_tasks/*.md` (excl. `todo_list.md`); preserve the `## Todo list` prose; never edit the task files. (The executable instruction — what makes the command "know.") |
| `.agents/commands/INDEX.md` · `.agents/workflows/INDEX.md` | The `/1_update-maps` rows: add "refreshes the open-tasks list" (and fix the stale "lobby-only / 4 checks" → fan-out / 6 checks). **(the INDEX)** |
| `_my_resources/README.md` (lobby + each project) | Note the `todo_list.md` `## Open Work` section is auto-refreshed by `/1_update-maps`; carve that one exception into the "agents don't edit `_my_resources/`" rule. **(the README)** |

**Guardrail moved (flagging explicitly):** `_my_resources/` was *read-only/off-limits*. This grants
`/1_update-maps` write access to **exactly one thing** — the `## Open Work` manifest in `todo_list.md` — and
nothing else in `_my_resources/` (the rest stays untouchable; task files stay Daniel's). The conformance check
already requires `_my_resources/open_tasks/todo_list.md` in every workspace, so the "one per project" standard
is enforced (Ingestion + OpenCode are flagged for lacking it).

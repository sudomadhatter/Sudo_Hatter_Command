---
IsArtifact: true
ArtifactMetadata:
  title: Roll out "story artifacts nest under their epic" to main + fresh-workspace
  type: implementation_plan
  date: 2026-06-27
---

# Roll out the AGY artifact-parent-routing fix → home base (`main`) + `Fresh_Workspace_BMAD`

Apply the fix already shipped + verified in `AGY_AVIATIONCHAT`
(`Projects/AGY_AVIATIONCHAT/_artifacts/_main/2026-06-27_artifact-parent-routing/`) to the two other
workspaces Daniel named: **`main`** (the home base) and **the fresh-workspace** (`Projects/Fresh_Workspace_BMAD`,
aka clean-bmad-workspace). The runbook is that folder's `cross-project-rollout-report.md`; this plan adapts it
to what each target actually has on disk (verified, not guessed).

## What the fix is (one line)
A story's artifacts nest under its **epic** folder (`_artifacts/epic_<E>/<story>/`), not the date-prefixed
`_artifacts/` root. The epic number is the leading number of the story id (`14.6` → `14`). Tool-agnostic:
autopilot, BMAD, or hand-dev all land in the same place.

## Per-target reality (verified this session)
| Site | `main` (home base) | `Fresh_Workspace_BMAD` |
|---|---|---|
| `scripts/autopilot-dev-story.ps1` | **absent** — skip | **present**, buggy block @175–185; `-Force` create @308 is *after* DryRun exit @304 ✅ |
| `.agents/commands/autopilot_mobile.md` | buggy Step 2 @34–36 | identical buggy Step 2 @34–36 |
| `.agents/commands/autopilot_claude.md` | buggy paths @74, @90 | identical buggy paths @74, @90 |
| `.agents/rules/artifacts-always-first.md` | buggy @78–79 + @83–89 | identical buggy @78–79 + @83–89 |
| `_artifacts/README.md` | home-base 3-rule model | BMAD project-local model |
| `_artifacts/INDEX.md` | home-base ledger header | BMAD ledger header |
| `.claude/commands/` mirrors | present (claude-only cmds) | present (claude-only cmds) |
| epic folders / stray root autopilot runs | none / none | none / none |

The mobile cmd + the rule are **byte-identical** between the two targets and differ from AGY's fixed copy
**only** in the fix region → one surgical edit text serves both. `autopilot_claude.md` carries an **unrelated**
extra block in AGY (a `_RUN-STATUS.md` orchestrator-PID liveness note) — **out of scope**; I edit only the two
path strings, never copy the file.

## Convention decision (flag at the gate)
Use **underscore** `epic_<E>` everywhere. Rationale: it's the canonical form (AGY, the rollout report, the ps1
literal `"epic_"`), fresh-ws already uses `epic_1/...` in its README example, and **neither target has any
`epic*` folder on disk** to force the hyphen variant. The home base README's lone `epic-9` example becomes
`epic_9`. (Open choice #1 below — say the word to switch to hyphen.)

---

## Change set — `main` (home base)

**M1. `.agents/commands/autopilot_mobile.md`** — replace Step-2 lines 34–36 with AGY's fixed three-bullet
epic logic (slug line 33 unchanged):
```
- Epic = the leading number of the story id (`14.6` → `14`). A story **nests under its epic bucket**
  `_artifacts/epic_<epic>/` — **create the epic folder if it isn't there yet** (per `artifacts-always-first`:
  stories live under their epic). If the id has no leading epic number, fall back to the `_artifacts/` root.
- Reuse an existing `_artifacts/epic_<epic>/*_<slug>/` folder (or a pre-fix `_artifacts/*_<slug>/` at the
  root) if one exists — prefer the one that already holds `implementation_plan.md` — so a resume finds prior
  artifacts; otherwise mint `_artifacts/epic_<epic>/<today>_<slug>/`. Create the folder.
```

**M2. `.agents/commands/autopilot_claude.md`** — two targeted path-string edits (leave the PID block alone):
- @74 `` `_artifacts/<date>_autopilot-<id>/` `` → `` `_artifacts/epic_<epic>/<date>_autopilot-<id>/` ``
- @90 `` `_artifacts/<date>_autopilot-<id>/`. Each team `` → `` `_artifacts/epic_<epic>/<date>_autopilot-<id>/`. Each team ``

**M3. `.agents/rules/artifacts-always-first.md`** — two hunks, AGY's exact fixed wording:
- (b) @78–79 — replace the "There is no `_main` inside a project — every task there is that project's work."
  tail with the cross-project/local-`_main` wording (project keeps a local `_main/` for system/infra; stories
  nest under `epic_<N>/`; random one-offs dated at root).
- (a) @83–89 — replace the 2-way "Random task / Story" list with the 3-way **Story (`epic_<E>/<story>/`,
  any tool) / System-infra (`_main/`) / Random one-off (root)** list.

**M4. `_artifacts/README.md`** (home-base) — minimal alignment:
- @12 rule 3 `**Stories** → ... `<epic>/<story>/`` → make explicit `epic_<E>/<story>/` + "any tool (autopilot/
  BMAD/hand-dev), parent = the story id".
- @15 "No `_main` inside a project." → "No *cross-project* `_main`; a project keeps a local `_main/` for its
  system/infra work."
- @20–22 "How to structure" mini-list: split the lumped **Random / system task** into **System/infra → `_main/`**
  and **Random → root**; story example `epic-9` → `epic_9`.

**M5. `_artifacts/INDEX.md`** (home-base) — @14 rule 3 `<epic>/<story>/` → `epic_<E>/<story>/` + the
tool-agnostic note. (Header already routes system → `_main` as rule 2.)

**M6. Mirror sync** — `cp .agents/commands/autopilot_mobile.md .claude/commands/` and
`cp .agents/commands/autopilot_claude.md .claude/commands/`; diff-verify identical. (Both are `platforms:[claude]`
→ claude-only; the rule isn't mirrored to `.claude/`, so nothing else to sync. A full `/sync-agents` is optional
and out of scope — targeted cp keeps it surgical.)

No ps1 here, no epic folders to create, no stray runs to relocate.

---

## Change set — `Fresh_Workspace_BMAD` (the fresh-workspace)

**F1. `scripts/autopilot-dev-story.ps1`** — replace the minting block @175–185 (keep `$slug` @174) with AGY's
fixed block: derive `$parent` = `epic_<n>` from `$storyId`'s leading number (else root); dual reuse-glob
(epic bucket **then** root) so pre-fix/in-flight runs still resume; mint under `$parent`. The existing
`New-Item -Force -Path $LogDir` @308 (after the DryRun `exit 0` @304) creates `epic_<E>/` then → **dry runs
stay inert** (verified the order on disk).

**F2.** `.agents/commands/autopilot_mobile.md` — same edit as **M1**.

**F3.** `.agents/commands/autopilot_claude.md` — same two path-string edits as **M2**.

**F4.** `.agents/rules/artifacts-always-first.md` — same two hunks as **M3**.

**F5. `_artifacts/README.md`** (project-local):
- @10–11 "**There is no `_main` bucket inside a project** — every task here is this project's work." → keep the
  *cross-project* sense but add: the project keeps a **local `_main/`** for system/infra work. (Resolves the
  contradiction created by adding a `_main/` placement rule — see Notes.)
- @13–19 "two shapes" list → three: **Random → root / System-infra → `_main/` / BMAD story → `epic_<E>/<story>/`**
  (its example is already `epic_1/...`).

**F6. `_artifacts/INDEX.md`** (project-local) — @8 `**Placement:** random task → ... · BMAD story →
`<epic>/<story>/` · retired` → add **system/infra → `_main/<date>_<slug>/`** and make story `epic_<E>/<story>/`.

**F7. Mirror sync** — `cp` both autopilot cmds into `Projects/Fresh_Workspace_BMAD/.claude/commands/`;
diff-verify. (Rule not mirrored to `.claude/` here either.)

No epic folders to create, no stray runs to relocate.

---

## Verify (no spend)
- **fresh-ws ps1 dry run** — `pwsh -File Projects/Fresh_Workspace_BMAD/scripts/autopilot-dev-story.ps1 -Story 1.1 -DryRun`:
  assert the printed `Folder :` resolves under `_artifacts\epic_1\<today>_autopilot-1-1`, and assert the fresh
  dry run did **not** create that folder (`Test-Path` → False). (Story 1.1 = the fresh-ws example id; pick any
  fresh id — there are no existing runs to reuse.)
- **grep gates** — both targets: `epic_<epic>`/`epic_<E>` now present in the two cmds + rule; zero remaining
  `_artifacts/<date>_autopilot-<id>/` (claude cmd) or `_artifacts/<today>_<slug>/` (mobile cmd) **outside** the
  "pre-fix root" fallback phrasing.
- **mirror diff** — `.claude/commands/autopilot_*.md` byte-identical to their `.agents/` sources in each target.
- **claude cmd PID block untouched** — confirm the AGY-only liveness block was NOT imported.

## Notes / deviations from AGY (surfaced, not silent)
1. **`autopilot_opencode.md` + `autopilot_bmad_dev_loop.md`** still reference the dated-root path (`@26` / `@138`,
   `@268`) in **all three** workspaces — AGY's fix left them untouched too, so I match that (out of scope). Flagged
   as a follow-up parity gap if Daniel wants the opencode lane + the workflow doc aligned later.
2. **README "no `_main` inside a project" contradiction.** AGY's README kept that sentence while *also* adding a
   `_main/` placement rule — internally inconsistent. For fresh-ws (M4/F5) I align that sentence with the
   authoritative rule wording so each workspace reads consistently. Tiny improvement over AGY's state; veto at the
   gate if you'd rather replicate AGY verbatim.

## Open choices (tell me to flip at the gate)
1. **Epic folder naming** = underscore `epic_<E>` (default, justified above). Switch to hyphen `epic-<E>`? 
2. **Mirror strategy** = targeted `cp` of the 2 claude-only cmds (default). Run a full `/sync-agents` instead?
3. **README consistency fix** (Note 2) — apply (default) or replicate AGY verbatim?

## Out of scope
The opencode command + the workflow doc (Note 1); any history relocation (no stray runs exist); committing
(Daniel commits — desktop git policy). Nothing outside `_artifacts/` is touched until you say **approved**.

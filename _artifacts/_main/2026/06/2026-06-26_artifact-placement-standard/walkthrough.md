---
IsArtifact: true
ArtifactMetadata:
  title: Artifact Placement Standard — clean-up + _home→_main rename (walkthrough)
  type: walkthrough
  date: 2026-06-26
---

# Walkthrough — Artifact Placement Standard clean-up

## What this did
Locked in ONE artifact-placement standard, stated as three rules, and made it consistent across Claude +
opencode and home base + projects:
1. **Project work** → per-project bucket `_artifacts/<project>/` (**create if missing, else reuse**).
2. **Main / home-base / cross-project work** → `_artifacts/_main/` (**renamed from `_home`**).
3. **Stories** → nest under the parent **epic folder** `<epic>/<story>/` (create epic if missing).
- **opencode** keeps its own `_artifacts/opencode/` namespace and applies the **same three rules inside it**.

## Step by step
1. **Renamed the folder** — `git mv _artifacts/_home _artifacts/_main`. All ~16 session folders +
   `active-context.md` moved with history intact.
2. **Fixed the SessionStart hook first** (`.claude/settings.json`) — it injects
   `_artifacts/_main/active-context.md` now; left unfixed, the rename would have silently broken continuity load.
3. **Updated the live standard docs** — `AGENTS.md` §5/§7 (recast §5 as the explicit 3 rules + opencode mirror),
   master `.agents/rules/artifacts-always-first.md` (intro callout + §2 placement), `_docs/workspace-standard.md`
   (Part 2 placement block), `_docs/repo-map.md` (curated header line), `_artifacts/INDEX.md` (header placement
   rules rewritten as 3 rules; historical Workspace-column `_home`→`_main` per Daniel's call).
4. **Made every artifact README clear** (Daniel's mid-run ask) — rewrote/clarified `_artifacts/README.md`,
   `_artifacts/opencode/README.md` (now spells out the 3 rules *inside* `opencode/`), the one-line
   `_artifacts/aviationChat-AGY/README.md`, and **added** new READMEs for `_artifacts/_main/` and
   `_artifacts/clean-bmad-workspace/` (parity — they had none).
5. **Re-vendored the standard into the 2 converted projects** — copied master `artifacts-always-first.md` +
   `_docs/workspace-standard.md` into `Projects/aviationChat-AGY/` and `Projects/clean-bmad-workspace/`.
   **Finding:** aviationChat's vendored `artifacts-always-first.md` was badly stale — it still described the
   OLD "single home-base store `_artifacts/<workspace>/`" model (pre work-from-cwd) and lacked the
   link-every-artifact + mobile-mode rules. Re-vendoring is the documented fix (edit master → re-sync; never
   hand-edit a vendored copy), so this brought the full current standard, not just the rename.
6. **Fixed the `_my_resources/` diagrams** (Daniel approved editing the protected area) — `_home`→`_main` in
   `gitnexus-usage-guide.md`, `updated_folder_file_structure_diagram.md` (incl. the Mermaid memory node +
   workflow node), and `complete-system-overview.md`; also corrected the two stale "bucket = the workspace the
   work primarily changes" lines to the current **work-from-cwd** framing.

## Test / verification output (real)
```
$ grep -rln "_home" --include=*.md --include=*.json .  | grep -v frozen-history-session-folders
(no output — zero live references)

$ test -f _artifacts/_main/active-context.md && echo OK ; test -d _artifacts/_home || echo "_home gone"
OK: _main/active-context.md exists
OK: _home gone

$ ls -1 _artifacts/
INDEX.md
README.md
_main/
aviationChat-AGY/
clean-bmad-workspace/
opencode/

$ diff -q .agents/rules/artifacts-always-first.md Projects/*/.agents/rules/artifacts-always-first.md
OK identical (both projects)
$ diff -q _docs/workspace-standard.md Projects/*/docs/workspace-standard.md
OK identical (both projects)
```
The only remaining `_home` strings are inside frozen session-folder history under `_artifacts/_main/<date>_*/`
(old walkthroughs/plans — left as-is by design) and the intentional "(formerly `_home`)" rename notes.

## Deviations from plan
- Added two NEW bucket READMEs (`_main/`, `clean-bmad-workspace/`) beyond the plan, to satisfy the mid-run
  "make all READMEs clear" ask and keep parity.
- Re-vendoring turned out to fix a much bigger staleness in aviationChat than the plan anticipated (full
  pre-work-from-cwd model, not just `_home`). Same action, bigger payoff — flagged here.

## Out of scope (left intentionally)
- Frozen history prose inside old session folders.
- `_docs/master-implementation-plan.md` (1 historical `_home` ref) — historical rollout record.
- `Projects/aviationChat-AGY/docs/file_structure_rules/*` — a separate older project-internal doc set
  (still references `_home`); not part of the canonical vendored set. **Flag for a later pass if you want it synced.**
- The 5 unconverted projects (B&L, NEXGen, NEXGen Films, jetChat, ingestion, openCode).

## Your Actions
1. Restart the session (or trigger SessionStart) to confirm the hook loads `_main/active-context.md` cleanly.
2. **Commit the home base** (run from `C:\Sudo_Hatter_Command`):
   ```
   git add AGENTS.md .claude/settings.json .agents/rules/artifacts-always-first.md \
     _docs/workspace-standard.md _docs/repo-map.md \
     _artifacts/INDEX.md _artifacts/README.md _artifacts/_main _artifacts/opencode/README.md \
     _artifacts/aviationChat-AGY/README.md _artifacts/clean-bmad-workspace/README.md \
     _my_resources/diagrams_guides/system/gitnexus-usage-guide.md \
     _my_resources/diagrams_guides/system/updated_folder_file_structure_diagram.md \
     _my_resources/diagrams_guides/system/complete-system-overview.md
   git commit -m "standard: rename _home->_main, codify 3-rule artifact placement + opencode mirror"
   ```
   (Note: `git mv` already staged the rename; the `git add _artifacts/_main` line re-stages the edited files inside it.)
3. **Commit each converted project** (separate repos under `Projects/`, their own git policy):
   - `Projects/aviationChat-AGY`: `git add .agents/rules/artifacts-always-first.md docs/workspace-standard.md && git commit -m "vendor: refresh artifact standard (work-from-cwd, _main, opencode mirror)"`
   - `Projects/clean-bmad-workspace`: same two paths + commit.

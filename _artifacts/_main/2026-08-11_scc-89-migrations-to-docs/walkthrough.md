---
IsArtifact: true
ArtifactMetadata:
  title: SCC-89 — relocate the migrations kit into docs/
  type: walkthrough
  date: 2026-08-11
---

# Walkthrough — SCC-89 (carries SCC-93)

**Branch:** `chore/SCC-89-migrations-to-docs` · **Epic:** SCC-48 · **Linked:** SCC-90
**Lane:** LOCAL — nothing deployable in the diff.

## What this is, and why the move IS the fix

`_my_resources/migrations/` holds what a **fresh machine follows**: the secrets restore, the venv
rebuild, the hooks arming, the memory link. It sat in a folder named in `SCAN_IGNORES`,
`DEFAULT_REGEN_IGNORE` **and** the GitNexus ignore list — the same three lists that made SCC-74 move
the SOPs out. So every drift-checker in the repo was *forbidden to look at it*, and it could not rot
loudly. **A guide nothing validates is worth less than no guide**, because it is trusted.

The move proved the point immediately. Three restore scripts had been broken since the SCC-26 reorg:
they walked up **two** directory levels to find the lobby root while sitting **three** deep, and
defaulted to a `_secrets/` folder the operator had relocated months earlier. The documented restore
path would have failed **on the machine it exists to rescue**, and nothing could have told us.

## Task Checklist

- [x] Kit relocated `_my_resources/migrations/` → `docs/migrations/` — git recorded all 12 as
      **renames** (R100/R99/R98/…), so history follows the files.
- [x] Root-walk + default-path bug fixed in `Export-EnvMaster.ps1`, `Restore-EnvMaster.ps1`,
      `restore-env-master.sh` — and in `rename-fix.ps1`, which had the identical defect and was not
      in the original scope (found by review).
- [x] Blast radius repaired: `AGENTS.md`, `router.md`, `docs/repo-map.md`, `docs/system-builder.md`,
      `docs/workspace-standard.md`, `.agents/scripts/link-memory.sh`, `.gitignore`, `.gitattributes`,
      6 memory bodies, and the two SOP links SCC-90 deliberately left for this ticket.
- [x] **SCC-93 carried** — the Antigravity IDE extension guide lands inside the folder this move
      creates, plus its artifacts folder and both INDEX rows.
- [x] `docs/repo-map.md` AUTO block regenerated (genuine stale — verified this checkout's basename is
      `Sudo_Hatter_Command`, not a worktree, before running the generator).
- [x] **Review findings applied** — see the Code Review section.

## Evidence

| Acceptance | Evidence |
|---|---|
| kit lives under `docs/migrations/`, no file lost | 12 tracked files before → 13 after; set diff is exactly one addition (the SCC-93 guide). Old path absent from disk and from the HEAD tree. |
| every old-path reference repointed | repo-wide sweep: remaining `_my_resources/migrations` hits are historical walkthroughs (immutable), provenance sentences ("moved from X to Y"), and `Projects/` copies excluded by ruling |
| credentials remain gitignored, NOT committed | **four independent proofs** — `git log --all --diff-filter=A --name-only \| grep -i auth_keys` → none · `git ls-files \| grep -i auth_keys` → none · `git check-ignore -v` → `.gitignore:51:**/auth_keys/` · `git add -n docs/migrations/` stages 13 files, **0** under `auth_keys/` |
| links resolve | 47 relative links across the kit and every changed doc → **0 dead** |
| gates green | below |

### Gate results (bare, at `7f59340`)

```
python3 .agents/scripts/tests/run_all.py                -> exit 0   12/12 files passed
python3 .agents/scripts/workflow_lint.py --toolkit-only -> exit 0   0 errors, 0 warnings, 8 info
python3 .agents/scripts/check_maps.py                   -> exit 0   "All maps & INDEXes agree with disk. [ok]"
python3 .agents/scripts/sop_currency.py                 -> exit 0
link sweep (47 relative links, kit + changed docs)      -> 0 dead
```

## Code Review (2026-08-11)

Verdict: PASS @ 7f59340
Suite evidence measured at 7f59340, after the fixes below. The pre-fix review verdict was **FAIL**
at `57723d0` — recorded here rather than overwritten, because the failure is the useful part.

**Scope:** `main...HEAD`, 3 commits. **Method:** clean-room adversarial subagent with no conversation
context — file-set accounting old-vs-new, four independent credential scans, repo-wide dead-reference
sweep, script-diff verification (including scripts the commit did *not* claim to fix), 46-link
resolution, commit-claim audit, then the machine gates bare.

### Findings

| # | file:line | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| R1 | `docs/migrations/INDEX.md:79` | **HIGH** | **Dead link the move introduced.** Step 7 of the numbered fresh-machine checklist pointed at `../open_tasks/…`, which resolved from the old home and 404s from `docs/`. It is the **git-hooks install** step — and an unarmed `core.hooksPath` fails *silently*, so the reader loses every gate and nothing says so. | **applied** — repointed to `../../_my_resources/open_tasks/…`, verified resolving |
| R2 | `.../antigravity…/implementation_plan.md:17,19` | MED | Dead links the diff introduced — one `../` too many lands above the repo root | **applied** |
| R3 | `sync-gemini-extensions.sh:6` | MED | Appended `/gemini_extensions` onto its own directory, which already **is** `gemini_extensions/`. Import found no `plugins/` or `skills/`, copied nothing, and printed **"Done."** — a silent success on the fresh-machine path. Pre-existing, but the 4th script in this kit with the same class of path bug the lane fixed in the other three. | **applied** — plus a comment recording why |
| R4 | `gemini-extensions-sync-guide.md:9,29` | MED | The guide's own `cd` landed one level above the script; both commands die. This diff *edited those exact lines* to repoint the prefix without checking the result resolves. | **applied** |
| R5 | `INDEX.md:3-9` + `new_machine-migration-guide.md:11-15` | MED | Both front doors still said the kit is *"disposable by design… can be deleted outright"* — contradicting `AGENTS.md`, `router.md` and `repo-map.md` **as changed by this same branch** to "standing reference, never deleted". An agent reading the INDEX would delete what the move exists to preserve. | **applied** — both rewritten, with the reversal and its reason stated |
| R6 | `docs/migrations/INDEX.md` | LOW | The new SCC-93 guide was not indexed — unreachable from the one front door a fresh machine reads. `check_maps` cannot catch this (folder coverage only). | **applied** — steps 9 and 10 added |
| R7 | `propagate-autopilot-glm-hybrid.md:8,50` | LOW | `[…](autopilot-glm-hybrid.patch)` labelled "(this folder)" — the patch is in `../scripts/` | **applied** |
| R8 | `Export-EnvMaster.ps1:77` | LOW | The refuse-to-ship guard's remediation text named `**/_secrets/` after the vault moved under `auth_keys/` | **applied** |
| R9 | `task.yaml` `secondary_repos` | LOW | Scoped AVCH-53 to 2 files; AGY actually has **5**. Whoever works it from this manifest misses three. | **applied** — all five listed, with the note that several were *already* dead before this branch |

**Lost files: none.** **Committed credentials: none** (four scans). **False claims in the commit
messages: none** — every one verified, including the script-bug claim, which was true *and* complete.

### Step 0.7 re-derivation

`main` moved under this diff exactly once during the session: SCC-90 landed at `0b380d4`. This branch
absorbed it before the work (it sat at main's tip). Nothing this diff references was moved by it —
the reverse, in fact: SCC-90 deliberately left its two migrations links for this ticket, and they are
repointed here.

**True overlap with live siblings:** `_artifacts/_main/INDEX.md` (SCC-83, SCC-88, SCC-94) — ledger,
keep all rows. ⚠ **This lane was the predicted 5th on that file:** its INDEX rows only appeared once
the untracked antigravity folder was committed, so no pairwise `git diff` could have seen the
collision in advance. **`_artifacts/_memory/agy-canonical-test-venv.md` (SCC-88)** — modify/delete:
this branch repoints a path *inside* a file SCC-88 relocates to AGY. Resolution ruled: **the deletion
wins** (SCC-73's two-tier law), and the path repair travels to AGY under **AVCH-53**.

**Landing-order dependency:** AVCH-53 must merge in the AGY repo **before** SCC-88 lands here, or
SCC-88's 33 relocated memories are stranded against an unmerged destination.

Changes applied: R1–R9, on this branch, before this verdict.

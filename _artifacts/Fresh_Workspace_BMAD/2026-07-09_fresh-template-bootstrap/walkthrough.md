---
IsArtifact: true
ArtifactMetadata:
  type: walkthrough
  workspace: Fresh_Workspace_BMAD
  date: 2026-07-09
  slug: fresh-template-bootstrap
  status: done
---

# Walkthrough — Fresh_Workspace_BMAD bootstrapped as the clone-and-rename template

**What this closes:** Daniel's directive that Fresh_Workspace_BMAD be "a ready to go project with all the
organization and tools I use ready to go so all I have to do is clone the project and rename it" — plus the
custom-BMAD question ("do we need this?"). It executes audit remediation **P2-9** (bootstrap Fresh before
story #1) and the **§5 dialect-mismatch note** (testing_audit_BDD.md:214) in one pass.

## Changes

### Fresh_Workspace_BMAD — 15 new files + 1 edit

**BMAD customization plumbing (copied from AGY, md5-verified identical):**
1. `_bmad/scripts/resolve_customization.py` — the three-layer TOML merge resolver every synced skill's
   activation step calls. Was MISSING → the whole `_bmad/custom/` mechanism was dead in Fresh.
2. `_bmad/scripts/resolve_config.py` — referenced by 3 synced skills.
3. `_bmad/custom/.gitignore` (`*.user.toml`) + `_bmad/custom/config.toml` (commented team template).

**Guardrails (copied from AGY, md5-verified identical):**
4. `_bmad/custom/bmad-dev-story.toml` + `bmad-quick-dev.toml` — the battle-tested guard tomls (plan-first
   gate + artifact-protocol persistent facts + `on_complete` walkthrough insurance; 3 fix iterations
   2026-05-30→06-27). `/sync-agents` excludes `_bmad/` by design, so these could only arrive by hand.
5. `.agents/rules/000-PLAN-FIRST-GATE.md` — the rule those tomls load; was AGY-project-owned. Project-owned
   in Fresh too (additive vendor preserves it).

**TDAD/BDD layer (new):**
6. `_bmad/custom/bmad-testarch-atdd.toml` — dialect pin: acceptance/red-phase = pytest + pytest-bdd, never
   Cypress/Jest, Playwright only for explicitly-E2E stories; house layout (`features/<domain>/*.feature` +
   self-binding `steps_<domain>.py`); bind to an existing ①b `.feature` contract instead of duplicating.
7. `_bmad/custom/bmad-testarch-automate.toml` — same dialect pin **+ `on_complete` that persists
   `automation-summary-<story>.md`** — the exact evidence the ③ gate's new check 5 looks for. Skill-layer
   belt to the command-layer suspenders shipped earlier today (P1-6).
8. `backend/tests/features/template/workspace_smoke.feature` + `backend/tests/bdd/steps_template.py`
   (+ `__init__.py`) — first `.feature` in the system; a smoke contract proving the Vision-Lock layer
   executes inside the normal pytest run on a fresh clone.
9. `pyproject.toml` (EDIT) — `python_files = ["test_*.py", "*_test.py", "steps_*.py"]` so self-binding
   steps modules are collected.

**Gate + CI (new):**
10. `_bmad-output/sudo-tests.yaml` — the gate ships **ARMED** (P2-9): `required_tiers [L1, L2]`,
    `l1_coverage_min: 0.0` (documented ratchet — AGY precedent 0.54), `agent_bearing: true`, `nfr: true`,
    `waive: false`, `baseline: at-opt-in`; tier_map/standards commented until a TEA-8-style story.
11. `.github/workflows/pr-check.yml` — `on: pull_request: branches: [main, main_debug]` (**P0-1 lesson
    baked in**); backend job = full pytest incl. BDD features + branch coverage (`--cov-fail-under=0`,
    ratchet comment); frontend job = `npm ci` + lint + build (no test script exists yet — noted inline;
    P0-2 deploy lesson in the header comment).

### AGY_AVIATIONCHAT — 2 new files
12. `_bmad/custom/bmad-testarch-atdd.toml` + `bmad-testarch-automate.toml` — byte-identical to Fresh's
    (md5-verified). This is the audit's §5 dialect note landed in the repo the note came from, and the
    automate-evidence insurance now fires at the skill layer there too.

### Lobby — carries the same layer (final; Daniel: "I also manage from here")
Scope moved twice and settled on **full 3-repo parity**. The verification that matters, both halves:
- **Story dev flow:** `sudo-*` / `autopilot_*` hard-refuse the lobby ("never the lobby itself") and bind
  `{project-root}` to the child project — those runs resolve the PROJECT's `_bmad/custom/`, so the project
  copies are what gate stories. (This half briefly argued for lobby-not-needed.)
- **Management lane (Daniel's point, decisive):** the lobby has the full BMAD install, and a **direct**
  skill run from the lobby seat — `/bmad-quick-dev` on a toolkit script, `/bmad-dev-story` on lobby work —
  binds `{project-root}` to the LOBBY and reads the lobby's `_bmad/custom/`. Without the tomls that lane
  had no in-skill plan-first/artifact enforcement. Proven live after restore:
  `resolve_customization.py --skill bmad-quick-dev --key workflow.on_complete` (lobby-rooted) returns the
  artifact-insurance override.

Landed in the lobby (all md5-identical to AGY/Fresh): the 2 guard tomls, the 2 dialect tomls (inert until
a lobby-rooted TEA run — included for one-mental-model uniformity), `.agents/rules/000-PLAN-FIRST-GATE.md`
(+ a rules-INDEX row). **Side effect to know:** the rule now lives in the master `.agents/rules/`, so other
projects (BRKN_Tattoos etc.) inherit it on their next `/sync-agents` — AGY + Fresh already carry
byte-identical copies, no-op for them. `_bmad/` itself still never syncs — toml parity stays a **3-way
hand-copy job** (lobby + AGY + Fresh).

### Daniel-directed doc syncs (same session)
- `_my_resources/docs/master-implementation-plan.md` — new §8 evolution-log entry (testing enforcement
  seam + living-template bootstrap, both walkthroughs linked); §9 "Fresh is the living template" extended
  with the born-enforcing inventory + the `_bmad/`-is-hand-copy rule.
- `_my_resources/diagrams_guides/system/file_folder_structure+maintaining.md` — §10 workspace-status rows
  updated (Fresh = born enforcing; AGY + guard/dialect tomls); §11 key-files gained the BMAD guard-layer
  row (and the sync-agents row now flags the `_bmad/` exclusion).
- `_my_resources/open_tasks/testing_audit_BDD.md` — P2-9 flipped ✅ DONE (core; TEA placeholder fill /
  v6.9 alignment noted as the minor remainder); §5.4 dialect note marked ✅ landed.

**Round 2 (Daniel: "update workspace-standard.md + make sure all of open_tasks/ is current"):**
- `docs/workspace-standard.md` — new Part-1 subsection **"The enforcement layer a dev workspace carries
  (standard since 2026-07-09)"** (guard/dialect tomls + armed gate + main+main_debug CI + self-binding
  BDD layout), 3 new format-checklist rows, and a Part-2 "Rules" bullet making `_bmad/custom/*.toml` the
  sanctioned per-repo exception. **Mirrored md5-identical to AGY + Fresh** (answering "may need to be
  added to the sub projects": both already vendored a copy per the PATH CONTRACT — AGY's was stale,
  missing the `debugging/` rows, and is now caught up).
- `_my_resources/open_tasks/todo_list.md` — statuses: task 1 ✅ (the audit answered it), task 2 ✅ (tea
  backlog closed, 7/03 PASS), task 3 🔄 (Epic 16 drafts await approval); "Tasks for Fable" marked 1✅ 2✅
  3🔄 / TEA audit ✅ / folder-verify ✅.
- `_my_resources/open_tasks/md_feedback_setup_guide.md` — Claude section CORRECTED to root `.mcp.json`
  (the `.claude/mcp.json` instruction was exactly the bug root-caused 2026-07-09).
- `_my_resources/open_tasks/tea_testing_guide.md` — header superseded: **2026-07-09 CURRENT** block
  (7/03 PASS P0 100%, ratchet 0.54, audit pointer, gate check 5 + dialect tomls, open P0-1..3/P1-4/P1-5);
  the 7/02 CONCERNS block demoted to historical. Open USER_MEMO blocks untouched (md-feedback owns them).
- `_my_resources/open_tasks/tdad_stack_install_guide.md` — What's-Next #1 updated (wiring PROVEN via
  Fresh's first green `.feature`; AGY Epic-8 pilot still open = P2-8) + #2 note (atdd toml binds red
  scaffolds to ①b contracts; the command edit itself still open).

### Design choices
- **Copies over rewrites** — every guard file is `cp`'d from AGY and md5-verified, so the two repos can't
  drift on day one.
- **Armed-but-zero gate** — presence arms the gate (traceability/regression teeth immediately); coverage
  floors start at 0.0 and ratchet UP, so day-one stories can't fail an impossible bar. Both ratchets
  (sudo-tests.yaml + pr-check.yml) cross-reference each other.
- **Self-binding steps convention** — `steps_*.py` call `scenarios()` themselves; dropping a feature+steps
  pair into the tree is all it takes for CI to run it. Documented in the module docstring, the tomls, and
  pyproject.
- **One dialect toml text for both repos** — worded so Playwright stays legal for explicitly-E2E journey
  stories (AGY legitimately has a Playwright pack planned; tea-16).

## Verification (all green)

- **BDD smoke end-to-end** (`.venv` Python 3.14, pytest-bdd 8.1.0):
  ```
  backend/tests/bdd/steps_template.py::test_a_cloned_workspace_executes_gherkin_contracts_inside_the_pytest_run PASSED [100%]
  ============================== 1 passed in 0.03s ==============================
  ```
  (First run FAILED on `pytest_bdd.__version__` — attribute removed in 8.x; probe switched to
  `importlib.metadata.version`. The Gherkin binding itself worked first try.)
- **Parses:** pr-check.yml + sudo-tests.yaml valid YAML; all 4 custom tomls + pyproject valid TOML.
- **Resolver chain proven in Fresh:** `resolve_customization.py --skill bmad-testarch-automate --key
  workflow.on_complete` returns the new team override (the automation-summary instruction) — the full
  custom-BMAD mechanism resolves end-to-end.
- **Copies:** 9/9 files md5-identical to their AGY sources (7 AGY→Fresh, 2 Fresh→AGY).

## Custom BMAD — the advisory answer (short form)

- **Interactive lane: yes, it earns its keep.** The tomls are the only enforcement layer that survives BMAD
  skill updates and fires *inside* the skill run (persistent_facts + un-skippable `on_complete`). AGY's
  3-iteration fix history on the dev-story toml is the proof the layer catches what command text alone
  misses.
- **BDD/ASDLC: yes** — the dialect pin is precisely the audit's §5 fix; without it the testarch skills
  scaffold in Playwright/Cypress dialect and every story pays a translation tax.
- **Autopilot: not required, small bonus.** The `_AP` commands don't invoke `bmad-dev-story` (they carry
  their own plan-stage separation + walkthrough requirement), so the guard tomls neither protect nor stall
  headless runs. But `sudo-code-review_AP` DOES invoke the testarch skills, so the new dialect tomls apply
  in the autopilot QA stage automatically.

## Not done here (unchanged scope)
- No frontend test runner (nothing to run yet — wire vitest + `npm test` with the first UI story).
- No BMAD core upgrade for Fresh (`_bmad` core layout is older than AGY's v6.9, but the *skills* are the
  synced set and only needed the resolver — verified working).
- `new-project.ps1` still scaffolds from `.agents/templates/project-template` (a second, lighter
  mechanism) — unifying it with Fresh-as-template is Daniel's call.
- AGY's `sudo-tests.yaml` untouched; audit P0-1..P0-3 CI holes in AGY still open.

## Task Checklist
- [x] implementation_plan.md written (approval on record: Daniel in-chat)
- [x] BMAD plumbing + guard tomls + plan-first rule copied into Fresh (md5-verified)
- [x] TDAD dialect tomls authored in Fresh + copied to AGY (md5-verified)
- [x] sudo-tests.yaml armed in Fresh; pr-check.yml created (main + main_debug)
- [x] BDD sample scaffolded; pytest green; YAML/TOML parsed; resolver chain proven
- [x] Lobby parity restored per Daniel ("I also manage from here"): 4 tomls + rule + rules-INDEX row; resolver proven lobby-rooted
- [x] Daniel-directed doc syncs: master-implementation-plan §8+§9 · file_folder guide §10+§11 · audit P2-9/§5 DONE
- [x] INDEX.md ledger row appended; memory updated (Fresh is the template)

## Your Actions

1. **Branch call for Fresh:** local checkout is on `main`; `origin/main_debug` exists but isn't checked
   out. If you want these on the integration branch first: `git switch main_debug` (the new files are
   untracked + one unstaged edit — they carry across the switch; if `pyproject.toml` conflicts, stash it
   over: `git stash && git switch main_debug && git stash pop`).
2. Commit per repo (scoped adds so unrelated drift stays out):

```powershell
# Fresh_Workspace_BMAD (c:\Sudo_Hatter_Command\Projects\Fresh_Workspace_BMAD)
git add pyproject.toml .github/workflows/pr-check.yml _bmad-output/sudo-tests.yaml _bmad/custom/.gitignore _bmad/custom/config.toml _bmad/custom/bmad-dev-story.toml _bmad/custom/bmad-quick-dev.toml _bmad/custom/bmad-testarch-atdd.toml _bmad/custom/bmad-testarch-automate.toml _bmad/scripts/resolve_customization.py _bmad/scripts/resolve_config.py .agents/rules/000-PLAN-FIRST-GATE.md backend/tests/bdd/ backend/tests/features/ docs/workspace-standard.md
git commit -m @'
feat(template): bootstrap clone-and-rename template — guardrails, armed TEA gate, CI, BDD layer

Fresh is the ready-to-go template (successor to clean-bmad-workspace):
AGY guard tomls + plan-first rule + customization resolver vendored in;
TDAD dialect tomls (testarch -> pytest-bdd) with automate-evidence on_complete;
sudo-tests.yaml ships ARMED (ratchet-from-zero); pr-check.yml gates PRs to
main AND main_debug (audit P0-1); first .feature smoke proves the BDD layer
(1 passed). testing_audit_BDD P2-9 + section-5 dialect note.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
'@

# AGY_AVIATIONCHAT (c:\Sudo_Hatter_Command\Projects\AGY_AVIATIONCHAT) — on main_debug
git add _bmad/custom/bmad-testarch-atdd.toml _bmad/custom/bmad-testarch-automate.toml docs/workspace-standard.md
git commit -m @'
feat(testing): TDAD dialect tomls for testarch skills + automate-evidence on_complete

Pins atdd/automate scaffolding to pytest + pytest-bdd (audit section-5 dialect
mismatch); automate now persists automation-summary-<story>.md on completion —
the exact evidence the sudo-code-review gate check 5 looks for.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
'@

# Lobby (c:\Sudo_Hatter_Command) — on main_debug
git add _bmad/custom/bmad-dev-story.toml _bmad/custom/bmad-quick-dev.toml _bmad/custom/bmad-testarch-atdd.toml _bmad/custom/bmad-testarch-automate.toml .agents/rules/000-PLAN-FIRST-GATE.md .agents/rules/INDEX.md docs/workspace-standard.md _artifacts/Fresh_Workspace_BMAD/2026-07-09_fresh-template-bootstrap/ _artifacts/INDEX.md _my_resources/open_tasks/testing_audit_BDD.md _my_resources/open_tasks/todo_list.md _my_resources/open_tasks/md_feedback_setup_guide.md _my_resources/open_tasks/tea_testing_guide.md _my_resources/open_tasks/tdad_stack_install_guide.md _my_resources/docs/master-implementation-plan.md "_my_resources/diagrams_guides/system/file_folder_structure+maintaining.md"
git commit -m @'
feat(agents): lobby _bmad/custom guard-layer parity + template-bootstrap artifacts

Lobby carries the same 4 custom-BMAD tomls as AGY/Fresh (direct BMAD runs
from the lobby seat bind project-root to the lobby - the management lane) +
000-PLAN-FIRST-GATE in master rules (projects inherit via /sync-agents).
Session artifacts + ledger row; master-implementation-plan section-8 entry +
section-9 living-template note; file_folder guide section-10/11 rows; audit
P2-9 + section-5 dialect note flipped DONE.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
'@
```

3. Optional next steps when ready: pin a real coverage baseline in both ratchets after the first stories;
   wire vitest with the first UI story; decide whether `new-project.ps1` should clone Fresh instead of
   `.agents/templates/project-template`.

<!-- CHECKPOINT id="ckpt_mre31coc_38yf9v" time="2026-07-09T22:32:41.580Z" note="auto" fixes=0 questions=0 highlights=0 sections="Verification (all green)" -->

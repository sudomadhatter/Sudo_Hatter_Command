review-runtime: fan-out

# SCC-304 — Give `/cicd-live-testing-team` its own eyes

**Lane:** `chore/SCC-304-playwright-frontend-check` · **Repo:** Sudo_Hatter_Command (lobby)
**Date:** 2026-08-23 · **Door:** `/smh-quick-dev` (lane_qualify: `TASK`) → `/smh-code-review` → `/smh-close-task-merge-tree`
**Plan:** [implementation_plan.md](implementation_plan.md) (carries the Self-Audit, verdict **GO**)

---

## What changed

| File | What, and why |
|---|---|
| `.agents/skills/playwright-frontend-check/SKILL.md` | **NEW.** Hand-authored, Node. The instrument: resolve Playwright out of a project's `node_modules` with `createRequire`, then capture console, `pageerror`, 4xx/5xx **with response bodies**, `requestfailed`, the rendered DOM and a full-page screenshot. Opens with the two traps that make it fail silently. |
| `.agents/commands/cicd-live-testing-team.md` | **EDIT.** Step 2's *"You cannot see the browser"* is gone — it was false. The skill is now the first frontend instrument, ahead of coaching the human; the human is the fallback for auth-gated / subjective / undrivable-by-script. Step 3's `## Evidence` requires the captured artifacts. Step 4 cleans up browsers and scratch scripts. `description:` updated (it is the router text). |
| `.agents/scripts/tests/test_live_testing_browser_instrument.py` | **NEW.** The permanent guard. Pins the WIRING chain, not prose. |
| `.agents/skills/INDEX.md` | **EDIT.** Frontend / UI family row — the skill's second, independent caller. |
| `docs/_scc_sops_prds/workflows_testing_SOP.md` | **EDIT.** §`/cicd-live-testing-team` blurb, its mermaid Step 2 node, the §16 cross-reference and the command table row. Adds *"what this means for you: stop retyping the Console"* + a `ⓘ Why it works this way` aside naming both traps in operator language. |
| `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` | **EDIT.** One provenance row (habit 4: the page states the present, the changelog records the change). |
| `_artifacts/_main/INDEX.md` | **EDIT.** The session row — `check_maps` fails without it. |
| 5 generated mirrors + `.agents/.sync-manifest.json` | **EDIT, by `/smh-sync-agents`.** The command's `description:` changed, so its four platform doors regenerate; `.claude/skills/INDEX.md` mirrors the skills INDEX. None hand-edited. Declared in the plan so the review's drift check sees them. |

### The research, and why the upstream skill was adapted rather than copied

Anthropic ships the canonical one — [`webapp-testing`](https://github.com/anthropics/skills/tree/main/skills/webapp-testing)
in `anthropics/skills`. Its decision tree and its reconnaissance-then-action discipline are good and
are carried over. **It is Python.** What is installed on this machine is Node
(`@playwright/test ^1.58.2` in `Projects/AGY_AVIATIONCHAT/frontend`; `pip3 list | grep -i playwright`
is empty). Copied verbatim it fails at `from playwright.sync_api import sync_playwright`. Also
surveyed and not used: `akaihola/playwright-py-skill` (Python), `lackeyjb/playwright-skill`,
`Jeffallan/claude-skills` `playwright-expert` (E2E authoring, not live diagnosis).

## Evidence

**Gates.** Run bare, never piped into anything that would eat the exit code.

All at the shipping sha `a3c0cebd`:

```
python3 .agents/scripts/tests/run_all.py                       EXIT=0   60/60 files passed
python3 .agents/scripts/workflow_lint.py --toolkit-only        EXIT=0   0 error(s), 0 warning(s), 8 info
python3 .agents/scripts/check_maps.py --depth3-only --strict   EXIT=0
python3 .agents/scripts/tests/test_sops_prds_folder.py         EXIT=0   61/61 passed
python3 .agents/scripts/sop_currency.py --paths <changed> …    EXIT=0   (no [sop-ok] needed on the surface commit)
python3 .agents/scripts/check_links.py --base origin/main      EXIT=1   3 unresolved, 0 bad anchors
python3 .agents/scripts/tests/test_command_surfaces.py         EXIT=0   216/216 (CS-04 door parity)
```

⚠ **`check_links` exits 1 and it is not this lane's defect.** All three hits are the same
pre-existing `<PROJECT_ROOT>/_bmad-output/…/active-context.md` placeholder at **line 19**
of the command and its two mirrors. Verified present on `origin/main` in all three files
(`git show origin/main:<path> | sed -n 19p`), and **`git diff` shows this lane never touches that
line** — it surfaces only because the lane brings those files into the checker's `--base` scope. Left
alone deliberately: the file uses bare `PROJECT_ROOT` in four places as its placeholder convention,
and rewriting one of them to satisfy a path-checker is scope drift into an unrelated line.

`run_all.py` first came back **59/60, FAILED: test_check_maps.py** — a real failure this lane caused:
`_artifacts/_main/INDEX.md: missing row for 2026-08-23_playwright-frontend-check/`. Fixed by adding
the row, not by waiving the gate.

**The new guard, RED before the edit** (anti-vacuity block A passed, so the failures are real
absences and not a broken read):

```
-- 4/10 passed --
FAILED: C1 the command body names the skill slug, C2 the slug resolves to a SKILL.md on disk,
        C3 the skill's frontmatter name matches its directory, C4 the skill carries a description,
        D1 the bare 'cannot see the browser' claim is gone, E2 the skills INDEX routes to the skill
```

**GREEN after:** `-- 10/10 passed --`

**Gate receipt (SCC-146), stamped on the clean tree at `c7abce5`:**

```
[PASS] suite exit=0 85.4s @ c7abce56
        receipt: gates/suite.json
```

`result: pass · exit_code: 0 · dirty_tree: False · dirty_paths: []` — so the review and the close-out
inherit this run instead of paying for it again.

**Mutation sweep — 9/9, and three of the nine are mutants that SURVIVED the first attempt.**
Run as a script ([`sweep.json`](sweep.json) → `mutation_sweep.py`) on a clean tree, drawn from the
shipped files rather than from this suite's own cases:

```
-- sweep: 9 mutant(s) over 4 file(s) @ a3c0cebd --
-- sweep clean: 9/9 killed by their declared case --
-- restore verified: bytes match, nothing was committed, and `git diff --quiet a3c0cebd` is clean --
-- full file, unfiltered: … -> exit 0 --   (26/26)
```

| Mutant | Killed by |
|---|---|
| M1 frontmatter `name:` stops matching its directory | `C3` |
| M2 the skill loses its `description:` | `C4` |
| M3 the skills INDEX stops routing | `E2` |
| M4 the blindness sentence returns in the master | `D1` |
| **M5** the routing instruction is **NEGATED** (slug still present) | `C1b` |
| **M6** the blindness claim is **REWORDED**, not respelled | `D1` |
| **M7** the skill body is **GUTTED** to a heading | `B3` |
| M8 *narrowing* — the instrument drops one channel (`pageerror`) | `B3` |
| M9 *narrowing* — the Antigravity **mirror alone** stops routing | `C1` |

⚠️ **M5, M6 and M7 each passed 10/10 against the first version of this guard.** They are in the table
because they survived, which is what a sweep is for. M8 and M9 are `WIDTH` narrowings rather than
deletions, per the mutation doctrine's "a deletion proves nothing about the boundary".

⚠️ **The sweep also caught two of my own errors, and both are worth more than a clean first run:**
- **M5 was declared against the wrong case.** It died at `C1b` (the negation ban), not the `C1`
  (imperative) I named — the negated bullet still *contains* "load the … skill", so `ROUTES` matches
  and only the negation check catches it. `mutation_sweep.py` refused to score it: *"something died,
  but not the declared case. The kill is not evidence about the declared case."* Re-declared.
- **M7 genuinely SURVIVED and exposed a real hole.** `js_fence()` read **raw** text, so an instrument
  commented out with `<!--` still satisfied block B — the same comment-blindness scar as `C1`, one
  level down. Fixed (`js_fence` strips comments first), and only then did M7 kill.

⚠️ **An earlier hand-run mutant "survived" for a bad reason and that was the mutant's fault, not the
guard's.** Commenting out ONE of the two slug references left the other, so `C1` correctly stayed
green. A survivor for that reason is indistinguishable in a transcript from a blind guard — which is
why every mutant now lives in the table and runs through the script.

**A2 — the recipe actually runs.** Not a suite row, by design (`run_all.py` is stdlib-only and must
pass on a machine with no Playwright and no browsers; block B pins what the recipe *says*, which is
deterministic and free).

⚠️ **The first transcript recorded here was produced by a PARAPHRASE of the instrument, not the
instrument.** Its keys (`RESOLVE / DOM / CONSOLE / NET_4xx5xx`) never appear in the shipped script,
so it evidenced a script nobody ships — caught by the acceptance lens. Replaced: everything below is
the shipped block **extracted verbatim from `SKILL.md` by regex** and executed, against a page built
to carry every hostile condition at once — an SSE stream that never goes idle, a 500 whose body
arrives 1200 ms late, an uncaught `TypeError`, and a button to find:

```
EXIT=0  PNG=6338 bytes                                  orphaned chromium: 0
navError:   None
console:    [{"type":"warning","text":"a warning"},
             {"type":"error","text":"Failed to load resource: … status of 500 …"}]
pageErrors: ["Cannot read properties of null (reading 'x')"]
httpErrors: [{"url":"…/api/thing","status":500,"body":"{\"error\":\"boom\"}"}]
reqFailed:  []
roles:      [{"tag":"button","role":null,"name":"Go"}]
html len:   263  | text: 'live\nGo'
```

Three separate runs of the same shipped script, each proving one repaired defect:

| Condition | Result |
|---|---|
| dev server **down** (`goto` rejects) | prints JSON anyway — `navError` names the cause, `reqFailed` carries `ERR_CONNECTION_REFUSED`. **Before the fix it printed nothing at all.** |
| 500 body **5 s** late | `body: "{\"error\":\"the real reason\"}"` captured. The edge lens proved widening the wait does **not** fix this; awaiting the pending body reads does. |
| page holding an **SSE** stream | `networkidle` → `Timeout 8000ms exceeded`; `domcontentloaded` → **OK in 14 ms**, DOM `APP RENDERED FINE`. The recipe now defaults to the second. |

⭐ **The finding that shaped the skill: the `TypeError` is in `pageErrors` and NOT in `console`.**
An agent listening on `console` alone reports "no JS errors" about a page that threw. Independently
reproduced by two review lenses.

**Trap 1, measured both ways.** Sandbox ON:
`FATAL:base/apple/mach_port_rendezvous_mac.cc:155] Check failed: kr == KERN_SUCCESS. bootstrap_check_in org.chromium.Chromium.MachPortRendezvousServer.<pid>: Permission denied (1100)`.
Sandbox OFF (operator toggled it mid-session, then re-probed with **no** override):
`SANDBOX: OFF - verified, no dangerouslyDisableSandbox used`. ⚠️ I claimed mid-lane that a toggle
could not reach a running session; that was **wrong** and the probe disproved it. The skill therefore
says *probe and read the result*, never *assume from the setting*.

**Trap 2, measured.** The same script from the scratchpad → `ERR_MODULE_NOT_FOUND`; from the owning
frontend, or via `createRequire(ownerDir + '/')` from anywhere → resolves.

**Publish.** `sync-agents.ps1` → `.claude\skills -> 74 skill dirs`;
`diff .agents/skills/playwright-frontend-check/SKILL.md .claude/skills/…` → identical;
`grep -c "GENERATED by sync-agents"` on the master → `0` (hand-authored content not clobbered, CS-05).

**Declared-set drift check:** `UNDECLARED (drift): none`.

**Working tree base:** `fa490f7` (`origin/main` at lane cut). Commit sha recorded by the commit itself.

## Code Review (2026-08-23)

### Step 0.7 — blast radius re-derived against current `origin/main`

what moved: nothing. `origin/main` is still `fa490f7`, which is this lane's own merge-base, so 0 files landed while this was built and the TRUE overlap with `main` is empty. `git merge-tree --write-tree HEAD origin/main` returns a clean tree (`bad84e2`) with no conflict messages.
what it changes here: nothing to re-resolve — no path this diff references was moved, renamed or deleted on `main`, and `check_links --base origin/main` re-resolved every path claim the diff touches (only the 3 pre-existing `<PROJECT_ROOT>` placeholders remain, all on line 19, all untouched by this lane).
what was re-measured: the full gate set at the shipping sha (suite 60/60 via receipt, toolkit lint 0/0, check_maps 0, SOP currency 0, door parity 216/216, guard 26/26, sweep 9/9), plus the declared-set reconciliation (0/0/0) and a fresh `git worktree list` — which surfaced a sibling lane that did not exist when this lane opened. See the landing-order note below.

⛔ **Landing-order dependency — `chore/SCC-293-bugs-cycle-7` (opened mid-lane, not on `main` yet).**
Three files overlap, and they are not all the harmless kind:

| Shared file | Kind | Resolution |
|---|---|---|
| `.agents/.sync-manifest.json` | generated | **regenerate**, never hand-merge — whoever lands second re-runs `/smh-sync-agents` |
| `docs/_scc_sops_prds/workflows_testing_SOP.md` | **hand-edited on both sides** | a real reconcile; the two edits are in different sections (that lane touches the `smh-quick-fix` / non-crit-push entries, this one the `/cicd-live-testing-team` entry) but a text conflict is likely |
| `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` | append-only ledger | both prepend a row under the same header — conflict is near-certain, resolution is to keep **both** rows |

⭐ **And the collision is GATES, not files.** That lane changes `check_links.py`, `lane_qualify.py` and
`jira_feed.py` — three of the scripts this lane RAN as gates. So whichever lands second owes more than
a text merge: it must re-run this lane's full gate set against **their** versions of those scripts,
because a green measured against the old `check_links.py` says nothing about the new one.

**Neither lane blocks the other and no order is required by correctness** — this one is review-complete
and theirs is still building, so this landing first leaves them the (smaller) reconcile.


Verdict: PASS @ a3c0cebd0aa4f5bbcb1d2fd6e4bcbbbdb42dcb0e
Suite evidence measured at the same sha: `gates/suite.json` — `result: pass`, `exit_code: 0`,
`dirty_tree: False`, 60/60 files.

review-runtime: fan-out

lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted:  5/5
lenses_na:       none
dispositions:    per-lens: blind-hunter=7/0/0 · edge-case-hunter=9/0/0 · literal-correctness-hunter=4/0/0 · acceptance-auditor=9/2/0 · test-adequacy-auditor=8/0/0
severity_floor:  CONCERNS (raised by test-adequacy's `critical`; cleared by fixing it in-thread and re-gating)
drift:           undeclared=0 · unimplemented=0 · incomplete=0 - dispositions in the findings table

⛔ **Disclosure — the fan-out ran at `18283ba`; this verdict is stamped at `a3c0cebd`.** The delta is
exactly the fixes the lenses asked for. They were applied in-thread as the door requires, then
re-gated (full suite, all floors) and re-swept (9/9) at the shipping sha. **The lenses did not see
the repaired text.** Recording this because a roster and a verdict at different shas is otherwise
indistinguishable from a review of the final artifact.

⛔ **Second disclosure — the patch handed to the lenses was INCOMPLETE and I did not say so at the
time.** One file was withheld: `docs/doc-graph.json`, a hook-regenerated map, excluded to keep the
patch readable. The engine's own rule is that a truncated hand-over must NAME the withheld paths, and
I named none. The acceptance lens caught it by counting hunks (21) against the diff (22 paths).
No lens judgement rested on that generated map, but the omission was mine and undisclosed, which is
the part that matters. *(This paragraph first claimed two files, naming a `repo-map.json` that does
not exist in this repo — corrected, because a disclosure about accuracy that is itself inaccurate is
worth less than none.)*

### Findings — 39 returned across 5 lenses, 37 survived assessment, 2 dismissed

Deduplicated across lenses that found the same thing, that is **31 distinct defects fixed in-thread**
(`require @playwright/test` was found by three lenses; the trailing slash, the missing `try/finally`
and the response race by two each). The table below names the ones that changed the shipped artifact;
the full per-lens counts are on the `dispositions:` line above.

Per `code-standards` §6.5 the assessor decides, not the lens. Named individually only where the
assessment disagreed with the label, or where the finding changed the shipped artifact materially.

| # | Finding | Lens | Disposition |
|---|---|---|---|
| 1 | **Guard green through a NEGATED routing instruction** — the defect this lane exists to remove, restored and certified clean | test-adequacy (`critical`) | **FIXED** — `C1` requires the imperative; `C1b` bans a negation on any slug line. M5 |
| 2 | **`D1` pinned one spelling** — "you have no eyes on the browser" passed | test-adequacy | **FIXED** — regex over the claim's shape + 4 CONTROL rows. M6 |
| 3 | **`C2` existence-only** — gutting the skill to a heading left the whole suite green | test-adequacy | **FIXED** — block B pins the channel roster inside the fence. M7 |
| 4 | **No `try`/`finally`** — a `goto` rejection discarded every captured line and never printed | blind, edge | **FIXED** — verified against a dead server |
| 5 | **Un-awaited `r.text()`** — a late 500 body absent from the JSON; widening the wait does not help | blind, edge | **FIXED** — verified at a 5 s delay |
| 6 | **`networkidle` hangs on SSE/long-poll** — 8 s timeout on a page that renders in 14 ms | edge | **FIXED** — default is `domcontentloaded` + a bounded settle |
| 7 | **`connectOverCDP` cannot attach to Chrome 151 on the default profile** | edge | **FIXED** — stated honestly; refusal string verified in the installed binary |
| 8 | **`require('playwright')` is a hoisted transitive**; projects declare `@playwright/test` | blind, literal, edge | **FIXED** — third trap row + specifier changed everywhere |
| 9 | **The trailing-slash note was INVERTED** — "usually still fine" is a hard failure every time | literal, edge | **FIXED** — measured both ways in the file |
| 10 | **Hardcoded `/Users/sudohatter/…` twice**, contradicting the plan's own Risks mitigation; the `2>/dev/null` made it silently read as "no project has Playwright" on the PC | acceptance | **FIXED** — owner is an argv, lobby resolved from git, `2>/dev/null` dropped |
| 11 | **`pages()[0]`** grabs the earliest tab, not the symptomatic one — a clean capture of the wrong page is indistinguishable from "the app is fine" | blind | **FIXED** — pick by URL, print the tab list |
| 12 | **Cleanup rule told the agent to close a browser it attached to**, killing the human's session | blind | **FIXED** — carve-out |
| 13 | **`read()` was `utf-8`, not `utf-8-sig`** — 8 command files carry a BOM today and a BOM makes frontmatter look absent | edge | **FIXED** — + CONTROL row with an on-disk BOM fixture |
| 14 | **`strip_comments` left an unterminated `<!--` intact** | edge | **FIXED** — + CONTROL row |
| 15 | **`docs/doc-graph.*` undeclared** while the walkthrough claimed no drift | acceptance | **FIXED** — declared; reconciliation now 0/0/0 |
| — | The guard's docstring mislabelled which case kills which mutant | blind, acceptance | **FIXED** — rewritten from measured results |
| — | The A2 transcript came from a paraphrase, not the shipped script | acceptance | **FIXED** — re-run from the regex-extracted block |
| — | The skill promised "dump the DOM" but emitted `innerText` only | acceptance | **FIXED** — `html` + `roles` added |
| — | Artifact path dropped the `PROJECT_ROOT` prefix, landing captures in the lobby | edge | **FIXED** |

**Dismissed, with reasons:** the orphaned-chromium claim (two independent measurements show Playwright
reaps its own browser — the skill's overclaim was **corrected** rather than the finding actioned);
`check_links` exit 1 (pre-existing, not in this lane's diff — see Evidence); the stale *"32 authored
skills"* count in `skills/INDEX.md` (pre-existing, no acceptance row, and correcting a count in a
file this lane merely touches is scope drift); A3's *"before coaching"* ordering (a disclosed,
reasoned deviation — source-grep guards cannot see order, and `D1` substitutes for it); the
unnecessary `[sop-ok]` on `18283ba` (an artifacts-only commit; the token is noise in the log, not a
bypass of anything that fired).

**Calibration note:** the one finding labelled `critical` was correctly labelled and is finding 1 —
it is the only one that restored the lane's own target defect. Two `important` findings from the
blind hunter (F1, F2) were reproduced live and were *understated*, not overstated: both produce a
confident wrong answer rather than a visible failure.

## Your Actions

- [x] Approve the plan — given in-session: **"approved"** (2026-08-23), after the Self-Audit returned GO.
- [x] Sandbox turned off so the browser probe could run — you did this mid-lane and confirmed
      **"it was on its off now"**; re-probed clean with no override. My earlier claim that a toggle
      could not reach a running session was wrong and the probe disproved it.
- [x] Confirmed the command centre keeps **no** Playwright — you asked, and it is measured: no
      `package.json`, no `node_modules`, no dependency file in the diff, and the enforcement suite
      imports only `re`/`sys`/`pathlib`. The driver stays with the project under test, and the skill
      now carries a full install procedure for a project that lacks it — including that the lockfile
      change needs **its own ticket in that project's tracker**.
- [ ] Decide whether `.agents/skills/INDEX.md:3`'s skill count should be corrected. It claims
      **"the 32 authored skills"**; measured today the directory holds **72** (49 hand-authored, 23
      generated). Stale before this lane and deliberately not fixed here — no acceptance row needs
      it, and correcting a count in a file this lane merely touches is scope drift. Your call whether
      it becomes a line on the rolling ticket or is left alone.

**Two things I got wrong that the review caught, worth knowing because they are the kind that hide:**
the guard I wrote to prevent this lane's defect would have passed a command that said *"do NOT load
the skill"*, and the instrument I shipped printed **nothing at all** when the dev server was down —
the exact case it exists to diagnose. Both are fixed and both now have a mutant in the sweep.

`check_links` exits 1 on three hits that are all one pre-existing placeholder at line 19 of the
command, present on `origin/main` and untouched by this diff. Nothing here is owed on it.

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

```
python3 .agents/scripts/tests/run_all.py          →  60/60 files passed
python3 .agents/scripts/workflow_lint.py --toolkit-only  →  (recorded below)
python3 .agents/scripts/check_maps.py --depth3-only --strict  →  (recorded below)
python3 .agents/scripts/tests/test_sops_prds_folder.py   →  (recorded below)
```

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

**Mutation sweep — the guard is not vacuous.** Run as a SCRIPT
([`sweep.json`](sweep.json) → `mutation_sweep.py`), not improvised one at a time; the mutants are
drawn from the shipped files, not from the test's own cases.

```
-- sweep clean: 4/4 killed by their declared case --
-- restore verified: bytes match, nothing was committed, and `git diff --quiet c7abce56` is clean --
-- full file, unfiltered: … -> exit 0 --  (10/10)
```

| Mutant | Killed by |
|---|---|
| M1 frontmatter `name:` stops matching its directory | `C3 the skill's frontmatter name matches its directory` |
| M2 the skill loses its `description:` | `C4 the skill carries a description (CS-06 loadability)` |
| M3 the skills INDEX stops routing to the skill | `E2 the skills INDEX routes to the skill` |
| M4 the browser-blindness sentence comes back beside the instrument | `D1 the bare 'cannot see the browser' claim is gone` |

**Two further mutants were run BY HAND and are labelled as such**, because neither is a single
unique-text swap the sweep script can express — one deletes a directory, the other edits two
separated lines:

| Manual mutant | Result |
|---|---|
| delete `.agents/skills/playwright-frontend-check/` | 7/10 — **killed** (`C2`) |
| comment out **every** reference to the slug in the command | 9/10 — **killed** (`C1`) |

⚠️ **The comment-out mutant SURVIVED on its first construction, and the MUTANT was wrong, not the
guard.** The slug appears in two live places in the command; commenting one out left the other, so
`C1` still found it (10/10, a false survivor). Rebuilt to comment every line carrying the slug, it
dies at `C1`. Recorded because a survivor for that reason reads identically in a transcript to a
genuinely blind guard, and telling them apart is the entire value of running the sweep.

**A2 — the recipe actually runs.** Not a suite row, by design (`run_all.py` is stdlib-only and must
pass on a machine with no Playwright and no browsers). Transcript, this machine, one script that
serves a real page over HTTP and drives it:

```
RESOLVE: ok from /Users/sudohatter/.../Projects/AGY_AVIATIONCHAT/frontend
DOM: live
CONSOLE: [{"type":"warning","text":"a warning"},
          {"type":"error","text":"Failed to load resource: … status of 500 …"},
          {"type":"error","text":"got boom"}]
PAGEERRORS: ["Cannot read properties of null (reading 'x')"]
NET_4xx5xx: [{"url":"http://localhost:63747/api/thing","status":500,"body":"{\"error\":\"boom\"}"}]
REQFAILED: []
SHOT: written                                    (6340-byte full-page PNG)
```

⭐ **The finding that shaped the skill: the `TypeError` is in `PAGEERRORS` and NOT in `CONSOLE`.**
An agent listening on `console` alone reports "no JS errors" about a page that threw. That is the
single most likely way this instrument produces a confident wrong answer, so it is called out in the
skill under its own heading rather than buried in the recipe.

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

## Your Actions

- [x] Approve the plan — given in-session: **"approved"** (2026-08-23), after the Self-Audit returned GO.
- [x] Sandbox turned off so the browser probe could run — operator did this mid-lane and confirmed
      **"it was on its off now"**; re-probed clean with no override.
- [ ] Decide whether `.agents/skills/INDEX.md:3`'s skill count should be corrected. It claims
      **"the 32 authored skills"**; measured today the directory holds **72** (49 hand-authored, 23
      generated). Stale before this lane and deliberately not fixed here — no acceptance row needs
      it, and correcting a count in a file this lane merely touches is scope drift. Your call whether
      it becomes a line on the rolling ticket or is left alone.

The skill is written against Node because Node is what is installed. If a project you want to test
has no Playwright, installing it edits that project's `package.json` and lockfile — the skill says to
ask before doing that rather than treating it as a drive-by.

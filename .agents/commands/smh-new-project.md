---
description: Scaffold a new project under Projects/ from the thin skeleton — two setup questions, name and Jira board, set its whole posture.
---

# /smh-new-project

Create a new workspace under `Projects/<name>` by cloning the **thin skeleton**
(`sudomadhatter/sudo-project-skeleton`): pointer `CLAUDE.md`/`GEMINI.md`, a workspace `AGENTS.md`
(Map/Mission/Support + routing table), a tier-2 `.agents/` holding only its OWN law, `_bmad/` +
`_bmad-output/`, `_artifacts/`, the FastAPI/Next stack, and its own git repo with hooks armed.

**It carries NO shared toolkit** — no `/` commands, no shared rules, no skills, no sync. Sessions run
from this command center, so tier 1 is already loaded (`.agents/rules/project-law.md`).

Argument (`$ARGUMENTS`): the new project's folder name.

---

## ⛔ STEP 1 — ask the operator BOTH questions, before you run anything

Setting up a project is **two questions, asked once**. Ask them together, in one message, and then
never ask again.

**Q1. What is the project called?** `$ARGUMENTS` if they gave it; confirm it, do not invent it.

**Q2. Do you have a Jira board for this project?** *"Yes — what site and key?"* / *"No."*

⭐ **The default is NO.** Many projects here are quick front-end work with no board and never want
one, and that is a complete, supported answer — not a deferral. Do not editorialise, do not warn,
and do not ask a follow-up on a "no".

---

## STEP 2 — the answer to Q2 IS the posture. There is no third state.

| | **Jira = yes** | **Jira = no** (the default) |
|---|---|---|
| What it is | the full enterprise dev system | a quick project, for speed |
| `.agents/jira.conf` | written, `JIRA_SITE` + `JIRA_KEYS`, `acli` site verified to match | nothing written |
| The three `*-ENFORCE` markers | **all three armed by setup** | **none** |
| Branches | `chore/<KEY>-<slug>`, the lane ceremony | `chore/<slug>`, or just commit on `main` |
| Reaching `main` | a pull request, the full gate | **push it** |

Run (PowerShell) — **the answers are arguments; the script does the rest:**

```
& ".agents/scripts/new-project.ps1" -Name "$ARGUMENTS"
```

```
& ".agents/scripts/new-project.ps1" -Name "$ARGUMENTS" -JiraSite "https://<site>.atlassian.net" -JiraKeys "<KEY>"
```

The first form is the "no" posture. The second is the "yes": it verifies `acli jira auth status`
names that same site **before cloning anything**, then writes `jira.conf` and arms
`JIRA-ENFORCE`, `MERGE-TARGET-ENFORCE` and `MAIN-PUSH-ENFORCE` inside the scaffold commit. It also
runs the skeleton's `scripts/rename-project.py` in both postures, so the placeholders are gone
before the project's first commit.

⛔ **Check the binding before you arm it, or the gate rejects every commit and names no reason.**
`JIRA_KEYS` alone is half an address: the hook matches a key prefix, but the CLI answers from
whatever site the machine is logged into, so a correct-looking `AVCH-12` can be validated against
somebody else's board — or none. The script refuses a mismatch; do not work around it. A
misconfiguration is fixed now, while the project has no history, not debugged on the first commit
that matters.

### On a "no", say exactly this once, then drop it

> No board. You can add one at any time — copy `.agents/jira.conf.example` and follow its four
> steps.

Then **stop**. Write nothing, arm nothing, and never raise it again. The absence of a board is not
a warning state and nothing in this system treats it as one — an unarmed gate exits 0 on its first
line (`pre-push-main-approval.sh`), the two merge guards share one flag of the same shape, and the
commit gate no-ops without a `jira.conf`. A boardless project also needs no ticket key: the guards
classify a branch by its PREFIX alone, so `chore/nav-fix` behaves exactly as `chore/NOVA-7-nav-fix`
would. Do not invent a local key scheme.

⭐ **Adding a board later costs nothing and undoes nothing**, because the "no" posture wrote
nothing — which is exactly why it writes nothing. That is what the one sentence promises, and it
is true by construction.

---

## STEP 3 — finish the wiring

The script prints these; do them in order.

1. **`router.md`** — add a row mapping the kind of work to `Projects/$ARGUMENTS/`.
2. **Submodule** — `git submodule add <remote-url> Projects/$ARGUMENTS` if it should travel with the
   lobby (`Projects/` is git-ignored here otherwise).
3. **Localize the map** — `python3 .agents/scripts/generate_repo_map.py --root "Projects/$ARGUMENTS"
   --ignore _my_resources,_bmad --mode auto` (run from the lobby; the template's AUTO tree carries the
   skeleton's own root name until you regenerate, so `check_maps` would flag it stale).

4. **Arm the rulesets** — the skeleton ships three recipes under `.github/rulesets/`
   (`main.json`, `epic-light.json`, `epic-full.json`) and arms **none** of them: until somebody runs
   this, the server requires nothing and the gate is a file rather than a rule. Run it from the new
   project's root; without `--apply` it writes nothing and just prints the diff. Arm **light before
   full** — `full` first writes the light-epic exclude while the light ruleset is still absent, which
   leaves a light epic branch claimed by no ruleset at all (the script refuses that order, and this
   is why).

   ```
   python3 .agents/scripts/arm_rulesets.py --repo <owner>/<name>
   python3 .agents/scripts/arm_rulesets.py --repo <owner>/<name> --only main  --apply
   python3 .agents/scripts/arm_rulesets.py --repo <owner>/<name> --only light --apply
   python3 .agents/scripts/arm_rulesets.py --repo <owner>/<name> --only full  --apply
   ```

   ⓘ Server-side rulesets are the **`main` is reached by a PR** half of the "yes" posture. On a
   "no" they are optional like everything else: a quick project that pushes to `main` has nothing
   to arm them for.

**Optional:** add it to `.agents/maintained-projects.txt` if the `check_maps --all` lint should cover it.

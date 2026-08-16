---
description: Adversarial audit for TASK work — pressure-tests an implementation_plan.md that has no story file and no story ACs against the repo it will actually modify. Two modes - PRE-WORK (the default; no plan means STOP) and POST-DEV/retroactive (audit the ticket's ACCEPTANCE block plus the change set, and label the run retroactive). Acts on the repo you are standing in, so the command centre is a valid subject. Auto-invoked by /smh-quick-dev; the stale half re-runs automatically as /smh-code-review Step 0.7. Use when the user says "audit the task plan" / "smh self audit".
platforms: [opencode, antigravity, claude, codex]
---

# /smh-self-audit — Pre-Work Adversarial Audit (the Task lane's ①.5)

Adversarial review of a Task's `implementation_plan.md` **before any file is edited.** Catch the flaw
while fixing it still costs nothing. Assume the plan is wrong somewhere, then try to prove it.

> **Rules in force for this command:**
> - `.agents/rules/artifacts-always-first.md` — the audit is **appended into the plan**, never a
>   standalone file; a Task's artifacts live in `_artifacts/_main/<YYYY-MM-DD>_<slug>/`
> - `.agents/rules/000-PLAN-FIRST-GATE.md` — this audit runs BEFORE the literal `approved`, not after
> - `.agents/rules/constitution.md` — the Ask-First and surgical-change obligations it audits against
> - `.agents/rules/worktree-per-story.md` §"cwd is not intent" — why Step 0 pins the repo from command
>   output, and why Phase 1 reads the sibling lanes instead of assuming this tree is the whole picture
> - `.agents/rules/tests-must-gate-for-real.md` — the plan's **test strategy** is audited against it.
>   Phase 2's "a gate that cannot fail" tripwire spans both halves of that rule: a *soft* gate is its
>   Rule 3, and *a check whose empty input reads as a pass* is its Rule 1 plus **§ Mutation Testing**.
>   A plan that names no way to prove its checks non-vacuous is missing that step (SCC-145)

**Why this exists as an `smh-*` command.** `/cicd-self-audit` binds
`.agents/rules/smh-target-resolution.md` — *"exactly ONE project, never the lobby"* — and every phase
of it assumes a story file, a sprint board and story acceptance criteria. Task work has none of those
and mostly lives **in** the command centre, so that command refuses the only repo this work happens
in. This is the same pressure-test with the story coupling cut out and the toolkit's real blast radius
put in. **The prefix is the permission; it is not cosmetic.**

> No build commands here — nothing has been written yet. This audits the *plan*, not a diff. For work
> already done, use `/smh-code-review`.

---

## Step 0 — Resolve the repo (FIRST) — from command output, never from belief

The subject is **where you are standing**, not a pointer. If `$ARGUMENTS` names a folder under
`Projects/` or a path, use that; otherwise the current repo. Do **not** read
`.agents/active-project.txt` — this command's whole point is that the command centre is a legitimate
subject.

```bash
REPO=$(cd "<the path you resolved>" && git rev-parse --show-toplevel)
BRANCH=$(git -C "$REPO" rev-parse --abbrev-ref HEAD)
echo "Repo: $(basename "$REPO") | Branch: $BRANCH"
```

⛔ **Echo that line from the commands, never from memory.** With sibling `chore/*` lanes live, where
you stand is not evidence of what you mean, and a self-reported echo can only confirm a wrong belief.

**Name the plan** you are auditing (its path) and **the ticket key** it belongs to.

**No plan file? The answer depends on which mode you are in — say which, out loud, before Phase 0:**

- **PRE-WORK (the default).** Nothing is built yet and there is no plan → **STOP and say so.** This
  command audits a written plan, and inventing one to audit is the exact failure it exists to catch.
  Write the plan, then come back.
- **POST-DEV (retroactive).** The work already exists and the plan gate was skipped or the plan was
  never written. Do **not** invent a plan. Audit against **the ticket's SCOPE + ACCEPTANCE block**
  (`acli jira workitem view <KEY>`) — Phase 0 already names it as the authority for the checkable list
  — plus the actual change set. **Label the run `retroactive` in the section you write**, because a
  retroactive audit cannot change a decision that is already built, and a reader must not mistake it
  for a gate that ran in time. See § Running it after the work is built.

---

## Phase 0 — Scope, right-size, and fix the checkable list

1. **Name the change set** — every file, folder, command, rule, script, hook or doc the plan proposes
   to add, move, rewrite or delete. Old → new for each.
2. **Right-size the audit** — brute-forcing every phase on a trivial plan is the slow path this gate
   exists to avoid:
   - **Skip** — a typo, a one-line doc tweak, a comment. Stop; say so; it does not need an audit.
   - **Light** — one command body, one doc, one contained script edit: Phases 1–2.
   - **Full** — touches a **rule**, a **gate or hook**, a **script other scripts import**, the
     **naming or door law**, more than one platform surface, or moves/renames a file that other files
     link to: all phases.
3. **⊕ Fix the checkable list — this is the Task lane's substitute for story ACs, and it is mandatory.**
   There is no story file here, so the acceptance list comes from, in this authority order:
   1. the ticket's own **ACCEPTANCE** block (`acli jira workitem view <KEY>`),
   2. the operator's stated intent in this session,
   3. nothing — in which case **you write 2–6 checkable statements and echo them for confirmation.**

   Each one must be verifiable by a command or an inspection, not by opinion. *"The gate rejects a
   commit that changes a command without touching the SOP"* is checkable. *"The docs are clearer"* is
   not — rewrite it or drop it.
4. **Traceability, both directions** — the #1 pre-work catch:
   - An acceptance item with no plan step → the plan will silently under-deliver. **Flag.**
   - A plan step tracing to no acceptance item → scope creep. **Flag for cut** (Phase 2).
5. **Lane check** — does the plan touch a **deployable** path (`backend/`, `frontend/`, `firebase/`,
   `functions/`, `mobile/`, `.github/`)? If so this is not Task work whatever the ticket says: it
   closes through `/cicd-push-e2e`, not `/smh-close-task-merge-tree`. Say so **now**, at plan time,
   rather than letting the close-out preflight discover it after the work is built.

---

## Phase 1 — Blast-Radius Trace  *(the command centre's radius is not a call graph)*

Toolkit work breaks things by **reference and by convention**, not by function signature. Grep is the
instrument here, and each row below is a real failure this system has already had. Fill only the rows
that carry risk; state the ones you cleared in one line each.

| The plan changes… | Then you must check… | Because |
|---|---|---|
| a **command** file (`.agents/commands/*.md`) | every platform door: `.claude/skills/<name>/`, `.agents/skills/<name>/`, `.opencode/commands/<name>.md`, `.agents/workflows/<name>.md` — and `commands/INDEX.md` | one door per platform per command (SCC-66); a rename orphans four caches at once |
| a command **name** | every reference across `.agents/`, `_my_resources/`, `docs/`, `_artifacts/`, and `AGENTS.md` | the `sudo-` retirement (SCC-63) proved a rename leaves live callers behind |
| a **rule** (`.agents/rules/*.md`) | every command that cites it, and `workflow_lint.py`'s `_RULE_POINTERS` | a command doing the thing must point at the rule governing it |
| a **script** (`.agents/scripts/*.py`) | its callers in `.agents/scripts/git-hooks/`, `.githooks/`, its test in `.agents/scripts/tests/`, and `scripts/INDEX.md` | a hook calling a changed signature fails at commit time, on someone else's commit |
| a **gate or hook** | does it ship ARMED or warn-only, and is the arming marker in the diff | VS Code renders hook output nowhere the operator looks — a warn-only gate reads as clean success |
| a **file path** (move / rename / delete) | every Markdown link and `#L` anchor pointing at it, repo-wide | a relocated doc's links are mis-pathed, not dead — they resolve to nothing and look fine |
| the **SOP doc** or a usage surface | that both halves land in the SAME commit | the armed `sop_currency.py` gate rejects the commit otherwise |
| anything under `_artifacts/_memory/` | whether this is the memory write flow at all | the store is READ-ONLY outside its own flows; another session's dirty memory is never swept under your task |

```bash
# The two sweeps worth running on almost every Task plan:
grep -rn "<the-old-name>" --include="*.md" --include="*.py" --include="*.ps1" --include="*.sh" --include="*.json" .
git grep -n "<the-path-being-moved>"
```

**⭐ Check the sibling lanes before you trust any of the above.** Task work runs on `chore/*` branches
off `main`, several at a time, and a sibling's uncommitted worktree is invisible to `grep` from here:

```bash
git worktree list                                       # who else is live
git -C <each-tree> status --short                       # what they are holding uncommitted
env -u GITHUB_TOKEN git fetch origin main               # a bare `main` is this checkout's LAST PULL
git -C <each-tree> diff --name-only origin/main...HEAD  # what they have already committed
```

Any file appearing in **both** your change set and a sibling's is a landing-order dependency, not a
detail. Name it in the verdict, say which lane should land first, and say what happens to your work
if it does not. Two lanes editing one file is allowed; two lanes *unaware* of it is the failure.

---

## Phase 2 — Over-Engineering & Drift Gate  *(STRICT — default NO-GO)*

> The simplest thing that satisfies the checkable list **wins.** Complexity is guilty until proven
> innocent: every abstraction, option, flag, or new file must trace to a **current** acceptance item —
> never a hypothetical future. *"might need," "for flexibility," "extensible," "future-proof,"* and
> *"reusable later"* are red flags, not justifications.

**Tripwires — if any fires, the plan is `NEEDS-REVISION` until that step is justified or cut:**

- [ ] A **new command** where an existing one should take a flag or a branch — the surface is a menu a
      human reads; every entry costs attention forever
- [ ] A **new rule file** restating law an existing rule already holds
- [ ] A **new script** where an existing script grows a subcommand
- [ ] **Clone-and-tweak** — the plan duplicates a command, script or test ("copy X and adjust") where
      extending X would do. *A deliberate, documented duplicate across families (`cicd-*` ⇄ `smh-*`)
      is legitimate — the prefix carries a different permission — but it must be **stated as such**,
      with the divergence named, not left to read as an accident.*
- [ ] A **config flag or option no acceptance item requires**
- [ ] **Generalizing for N when the work is N=1**
- [ ] **Error handling for states that cannot occur** in this flow
- [ ] A **gate that cannot fail** — report-only, `|| true`, `continue-on-error`, or a check whose
      empty input reads as a pass. A vacuous green is worse than no gate at all
- [ ] Plan size wildly out of proportion to the acceptance list
- [ ] **Rebuilding something that already exists** (Phase 1's reference sweep)

For each tripwire that fires, name the **simpler alternative** and what it saves. **Default
disposition for an unjustified tripwire is CUT IT.**

---

## Phase 3 — Pre-Mortem  *(Full audits; Light only when a gate or a hook is involved)*

Assume the plan shipped and **quietly broke the operator's next session** — what was the cause? Ask
whether the plan *accounts for* each row that can actually occur; skip the rest with a one-line why.

| Scenario | Does the plan handle it? | ✅/❌ |
|----------|--------------------------|-------|
| **The other machine.** Mac has no bare `python`; the PC has no `python3`. Is every command in the plan runnable on both? | | |
| **A fresh clone.** `core.hooksPath` is per-machine — does this ship a gate that is silently OFF until someone runs a setup step? | | |
| **The gate fires on someone else's commit.** Who hits this first, and does the message tell them what to do? | | |
| **The escape hatch.** A gate with no legitimate exit gets `--no-verify`d into oblivion. Is there one, and is it auditable? | | |
| **Empty input.** Does an empty diff / empty file set / missing tool read as PASS anywhere? | | |
| **The four platform caches.** Does a menu change reach Claude, Codex, opencode AND Antigravity — or three of them? | | |
| **A sibling lane lands first.** Does the plan still apply after their diff is on `main`? | | |
| **Rollback.** If this is wrong, what undoes it — and is anything here irreversible (a delete, a history rewrite, a Jira transition)? | | |

Then name the failure modes that survived the walk: the silent one (looks green, does nothing), the
one that only shows up on the other machine, the one that only shows up on a fresh clone.

---

## Phase 4 — Verdict

1. **Per-item:** SAFE / NEEDS REVISION / UNSAFE.
2. **Persist — ALWAYS.** Append the audit **into the plan you audited** as a `## Self-Audit (<date>)`
   section: the right-size level, ONE line per phase walked (what was checked and cleared), the
   findings table (`file:line` · severity · failure scenario · disposition), any sibling-lane
   landing-order dependency, and the canonical line:

   ```
   Audit verdict: GO | NO-GO
   ```

   Never write a standalone audit file (`artifacts-always-first` §7).
3. **Four quick gates**, one line each:
   - **Verification strategy present?** Does the plan say how each acceptance item gets *proved* — by
     which command, producing which output? No → flag. This is what `/smh-quick-dev` will run.
   - **Anything irreversible?** A delete, a rename that breaks history, a Jira transition, a
     force-push, a `main` merge → flag and gate it.
   - **Any step vague enough that the builder will guess?** Ambiguity gets filled in wrong. Tighten it.
   - **Convention fit?** Does the plan anchor to the conventions it should match — the naming law, the
     door model, where artifacts live, prose style — or leave them to improvisation?
4. **Final GO / NO-GO** for proceeding to the work.

If NEEDS-REVISION or UNSAFE → **bake the fix into the plan itself** (an inline `⚠️ AUDIT FINDING` in
the affected section, plus the findings table) so the builder reads it in context — then re-run only
the phases the change touched.

---

## Running it after the work is built

**Most of this audit does not go stale — two parts of it do, and only those are worth re-running.**

| Phase | Post-dev? | Why |
|---|---|---|
| **0** — scope, right-size, checkable list | **No** | A judgment about a plan. Once the thing is built the decision is made; re-asking it is theatre. The acceptance list still matters, but `/smh-code-review` Step 2 already audits the diff against it. |
| **1** — blast radius | **⭐ YES — this is the one** | It was traced against the `main` that existed when the plan was written. Sibling `chore/*` lanes land while you build, so the trace can describe a repo that no longer exists. |
| **2** — over-engineering gate | **No** | Cutting an abstraction is cheap in a plan and expensive in a diff. Post-dev, this is `/smh-code-review` Step 1's job, on the code that actually exists. |
| **3** — pre-mortem | **Partly** | Only the rows that depend on **external** state: *a sibling lane lands first*, *the four platform caches*, *a fresh clone*. The rest were settled by building it. |

**You do not invoke this command to get that.** The stale half runs automatically as
**`/smh-code-review` Step 0.7**, which re-derives the blast radius against current `main` before the
verdict. That placement is deliberate: an opt-in re-audit is one nobody runs — the memory audit sat
unused inside `/smh-update-maps-indexes` Step 3.9 for exactly that reason, because nobody opens a *map*
command when memory feels heavy, and nobody will open a *pre-work* command after dev.

**Invoke it directly post-dev only in the narrow case** where Step 0.7's three questions are not
enough: a long-lived branch that `main` has moved under repeatedly, a lane resumed after days away, or
work whose acceptance list itself is now in doubt. Then run it in **POST-DEV** mode (Step 0), walk
Phase 1 and the external-state rows of Phase 3, skip Phases 0 and 2 with a one-line why, and write the
section labelled `retroactive`.

## Stay in lane
Audit and annotate the plan; write no implementation, touch no file the plan is about, transition no
ticket. This command produces one thing: a `## Self-Audit` section and a verdict.

Optional additional input (a plan path, or a focus area): $ARGUMENTS

# SCC-263 — PreToolUse hook: auto-allow Bash commands confined to the session scratchpad

**Lane:** `chore/SCC-263-scratchpad-allow-hook` · **Epic:** SCC-33 (CI/CD For Sudo Dev System)
**Date:** 2026-08-22 · **Lane type:** TASK (`lane_qualify.py` → `TASK`, toolkit paths)

---

## The problem, measured

Every verification lane — `/smh-code-review` most of all — builds a throwaway runtime harness
under `/private/tmp/claude-<uid>/<project>/<session-uuid>/scratchpad/` and then runs it. Each
`mkdir` / `bash` / `python3` / `chmod` / `rm -rf` against that tree stops for an approval, twenty-odd
per review, against a directory the harness deletes when the session ends.

Measured in this session before the fix: `cat > .agents/hooks/…`, `python3 -m py_compile …`, and a
`cp && ls` compound were each refused by the auto-mode classifier. After the fix, a single compound
doing `mkdir` + write + `chmod +x` + execute + `rm -rf` inside the scratchpad ran with zero prompts.

**Why settings cannot fix this, and a hook can.** Two independent reasons, both structural:

1. `Bash(...)` permission rules match the **command string by prefix**. There is no path-scoped
   form — no `Bash(<anything touching /path/**>)`. Compound commands (`cd X && bash Y`) miss any
   prefix rule regardless.
2. Even if a path form existed, the scratchpad path carries a **per-session UUID**, so a literal
   rule written today matches nothing tomorrow.

A `PreToolUse` hook is the only layer that sees the *resolved* command and can answer "everything
this touches is disposable". So the hook answers exactly that and nothing wider.

---

## Acceptance (from SCC-263's ACCEPTANCE block — each row is one assertion)

| # | Statement | How it is checked |
|---|---|---|
| A1 | Emits `permissionDecision: allow` when ≥1 absolute path is inside the scratchpad root and **every** absolute path is inside it or a read-only system prefix | `test_allow_scratchpad.py` block A, the eight real harness shapes |
| A2 | Emits **nothing** for each of the six decline rules: no sandbox path · an absolute path outside · a `..` segment · an unexpanded `$`/`~`/`$(…)` · a deny-listed command · `git` with no `-C` or a `-C` outside | blocks B–G, one block per rule |
| A3 | **Never** emits `ask`, and always exits 0 — including on malformed, empty and non-Bash stdin | block H |
| A4 | The test fails when the hook's rule constants are mutated | `mutation_sweep.py` over the six constants |
| A5 | `.claude/settings.json` wires it **first** in the `PreToolUse` Bash matcher, and `.claude/hooks/` byte-matches the `.agents/hooks/` master | block I, reading the real repo files |
| A6 | `python3 .agents/scripts/tests/run_all.py` passes | the gate itself |
| A7 | The lane's artifact folder holds an `implementation_plan.md` carrying a parsing `## Declared Change Set` and an audit verdict, and a `walkthrough.md` carrying a `Verdict:` line | `declared_change_set.py parse` exits clean; `/smh-close-task-merge-tree` preflight reads both |

**A3 is the load-bearing one.** `ask` is auto-DENY in non-interactive mode (memory:
`hook-ask-becomes-autodeny-in-auto-mode`). A convenience hook that can deny would break the very
lane it exists to unblock, so this hook has exactly two legal outputs: `allow`, or silence.

---

## Steps

1. **`.agents/hooks/allow-scratchpad.py`** — the hook. Six rules, all must hold or it stays silent.
   Wrapped in a bare `except: pass` + `sys.exit(0)`: it may only ever *remove* a prompt it is
   certain about, never *add* one. → A1, A2, A3
2. **`.claude/hooks/allow-scratchpad.py`** — the deployed copy, byte-identical. Mirrors the
   `guard-cwd-escape.py` master/copy convention; `/smh-sync-agents` regenerates it. → A5
3. **`.agents/hooks/INDEX.md`** — one row, keeping the auto-listed contents honest. → A5
4. **`.claude/settings.json`** — wire it as the first `PreToolUse` Bash hook. First so its `allow`
   is recorded before the later gates speak; a sibling `ask`/`deny` still wins, which is correct. → A5
5. **`.agents/scripts/tests/test_allow_scratchpad.py`** — the retrofit suite, `_harness.Cases`,
   stdlib only, one `c.block` per rule. → A1–A3
6. **Mutation sweep** over the hook's six rule constants; every mutant must die. → A4

## Declared Change Set

- NEW `.agents/hooks/allow-scratchpad.py` — the hook itself, the canonical master → A1, A2, A3
- NEW `.claude/hooks/allow-scratchpad.py` — the deployed copy settings.json actually loads → A5
- EDIT `.agents/hooks/INDEX.md` — one row, keeping the auto-listed contents honest → A5
- EDIT `.claude/settings.json` — wires the hook first in the PreToolUse Bash matcher → A5
- NEW `.agents/scripts/tests/test_allow_scratchpad.py` — the retrofit suite → A1, A2, A3, A4
- NEW `_artifacts/_main/2026-08-22_scc-263-scratchpad-allow-hook/implementation_plan.md` — this plan → A7
- NEW `_artifacts/_main/2026-08-22_scc-263-scratchpad-allow-hook/walkthrough.md` — the closing record → A7

---

## Honesty about the RED phase

⛔ **This is a characterization retrofit, not a true RED-first lane.** The hook was written and
verified before the ticket existed — the operator hit the friction live and asked for the fix in the
chat, so the code preceded the ceremony. The test therefore passes green on first run, which is the
`test-debt-stories-are-characterization` convention, not the `tests-must-gate-for-real` RED.

**What replaces the red, so the suite is not vacuous:** Step 6's mutation sweep. Each of the six
rule constants is mutated in turn and the suite must fail for each. A retrofit test that cannot kill
a mutant is a test that pins nothing, and this is the only evidence available once the green came
first. The operator chose this over reverting-and-re-adding the hook, to avoid churning a
verified-working fix.

## Landing-order dependency

`chore/SCC-244-bugs-updates-cycle-4` is live in a sibling worktree. **Zero file overlap** with this
set — but it edits `.agents/scripts/mutation_sweep.py` and eight files under
`.agents/scripts/tests/`, which is the gate machinery this lane runs (memory:
`lane-collision-is-gates-not-files` — zero file overlap still breaks).

**Order:** either lane may land first, but whichever lands second re-runs the combined gate on the
merged tree. If SCC-244 lands first, this lane absorbs `main` and re-runs `run_all.py` **and** the
mutation sweep before its PR, because SCC-244 changes the sweep itself.

---

## Self-Audit (2026-08-22)

**Level: LEDGER+BLAST** — the Declared Change Set touches a hook, a door surface
(`.claude/settings.json`), and a file that exists in more than one place (`.agents/hooks/` master +
`.claude/hooks/` deployed copy). Mode: **PRE-WORK** for the test and rule 7; the hook itself is
**retroactive** (see § Honesty about the RED phase).

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  every declared path exists on disk (ls, quoted below)
             declared_change_set.py parse -> initially 7/7 incomplete, re-parsed clean after fix
             both-machines command check: hook is dispatched by run-hook.sh, which probes
               python3|python|py; the test uses sys.executable; stdlib only, no venv
             lane fit: no deployable path (backend/ frontend/ firebase/ functions/ mobile/ .github/)
               in the set -> /smh-close-task-merge-tree is the right door
             Scope Ledger: 4 NEW artefacts x the acceptance row requiring each
             acceptance precondition: 7 rows, each naming a concrete observable
read:        .agents/scripts/declared_change_set.py:5-25 (the bullet grammar)
             .agents/hooks/INDEX.md, .claude/settings.json, .agents/hooks/allow-scratchpad.py
             .claude/hooks/allow-scratchpad.py, .agents/scripts/tests/run_all.py
             .agents/scripts/mutation_sweep.py, .agents/scripts/risk_seam.py (unclassified)
verdict:     findings below
```

```
lens:        2 Parity + Blast
checks_run:  gate-or-hook: ships ARMED? -> yes, wired in .claude/settings.json, verified by
               reading the parsed JSON: PreToolUse[Bash] = [allow-scratchpad, require-push-approval,
               guard-cwd-escape], SessionStart = 4 entries, no stray copy
             file in >1 place: cmp .agents/hooks/allow-scratchpad.py .claude/hooks/... -> identical
             sibling worktrees: fetched origin, git worktree list, per-tree diff --name-only +
               status --short -> chore/SCC-244-bugs-updates-cycle-4 live, ZERO file overlap
             twins: no cicd-*/smh-* sibling — this is a hook, not a command surface
             command doors: none touched, so no four-door / commands/INDEX.md obligation
             .agents/hooks/INDEX.md row added, keeping the auto-listed contents honest
read:        .agents/.sync-manifest.json (no "hooks" key), .agents/commands/smh-sync-agents.md
               (no "hooks" match), .agents/scripts/tests/test_command_surfaces.py:1820
               ("SWEEP_ROOTS = (... , \".claude/hooks\", ...)"), .agents/scripts/workflow_lint.py
               (no "hooks" match)
verdict:     findings below
```

```
lens:        3 Pre-Mortem (bounded — attaches narratives, originates nothing)
checks_run:  the silent one · the other-machine one · the fresh-clone one · the sibling-lands-first one
read:        the two-machines and hook-ask-becomes-autodeny memories; .agents/hooks/run-hook.sh
verdict:     one narrative attached to F2; the rest are Observations
```

### Findings

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `_artifacts/_main/2026-08-22_scc-263-scratchpad-allow-hook/implementation_plan.md` (Declared Change Set) | `declared_change_set.py parse` returned `"entries": []` with all 7 bullets in `incomplete`: *"the left side is not `<OP> <path>`"* | `/smh-code-review` Step 2 diffs the real diff against this block. An unparseable block means the drift check reads **nothing** and silently passes. | **HIGH — FIXED INLINE** |
| `.agents/hooks/allow-scratchpad.py` rule list (docstring, "THE RULE — all six must hold") | The six rules constrain **absolute** paths only: *"EVERY absolute path is inside the scratchpad root or a read-only system prefix"* | A **relative redirect target** escapes every rule. `bash /<sandbox>/run.sh > out.txt` has exactly one absolute path, inside the sandbox, so it is auto-allowed — and `out.txt` is written into whatever cwd the Bash tool currently holds, which is the repo working tree. Breaks acceptance row **A2**, which claims the hook declines anything reaching outside the sandbox. | **HIGH — plan amended, see F2** |

**F2 fix, baked into the plan (⚠️ AUDIT FINDING):** add **rule 7** to the hook and a matching test
block — every redirect target (`>`, `>>`, `2>`, `&>`) and every `tee` argument must be **absolute
and sandboxed** (or `/dev/null`-class). Anything else, including any relative target, declines. The
acceptance table's A2 row gains the seventh decline rule, and `test_allow_scratchpad.py` gains
block **J** covering it. This is the one genuinely new piece of work the audit found; everything
else is already built.

**Pre-mortem narrative attached to F2 (the silent one):** this hole fails in the exact shape the
house keeps paying for — a write lands in the wrong tree, nothing errors, both paths are valid, and
the transcript is byte-identical to a correct run (the `bash-cwd-resets-to-main-checkout` scar).
Rule 7 is what makes it loud.

### Observations (uncounted, no severity)

- `.agents/hooks/INDEX.md:3` claims the masters mirror to *"project vendored copies via
  `/smh-sync-agents`"*. Measured: `.agents/.sync-manifest.json` has no `hooks` key,
  `smh-sync-agents.md` never says `hooks`, and none of `AGY_AVIATIONCHAT`, `NEXgen-VR-Director`,
  `sudo-project-skeleton` has a `.claude/hooks/` directory at all. **The claim is stale.** Pre-existing
  doc drift, not this lane's to fix — but it means this hook is **lobby-only**, so `/cicd-code-review`
  in a child project keeps the friction. A follow-on if the operator wants it there.
- **The PC gets nothing.** The scratchpad root on Windows is not `/private/tmp/claude-<uid>/`, so
  `SANDBOX_RE` never matches and the hook is a silent no-op there. Degradation to today's behaviour,
  not a break — but `.claude/settings.json` is shared, so the wiring travels while the benefit does not.
- **What this deliberately does not defend against:** `bash /<sandbox>/anything.sh` runs whatever the
  agent wrote, and writing into the scratchpad was never gated. The hook removes the prompt on
  *running* agent-authored code, not on *authoring* it. Accepted, and stated in the hook's docstring.

### Landing-order dependency

`chore/SCC-244-bugs-updates-cycle-4` — zero file overlap, but it edits `mutation_sweep.py` and eight
files under `.agents/scripts/tests/`, which is the machinery this lane's A4 and A6 run on. Either may
land first; whichever lands **second** re-absorbs `main` and re-runs `run_all.py` **and** the
mutation sweep before opening its PR.

```
Audit verdict: GO
```

Both findings are answerable inside this plan — F1 is already fixed, F2 is one rule and one test
block. Neither breaks a hard gate.

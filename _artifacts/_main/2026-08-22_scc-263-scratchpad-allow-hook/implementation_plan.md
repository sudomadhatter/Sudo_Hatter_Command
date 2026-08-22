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
| A1 | Emits `permissionDecision: allow` for one simple command whose executable is an allow-listed bare name and whose every non-flag token is an absolute path inside **this session's** scratchpad | `test_allow_scratchpad.py` block A, 11 real harness shapes |
| A2 | Emits **nothing** for each of the four decline rules — a shell metacharacter · an executable that is not an allow-listed bare name · a non-flag token that is not a sandboxed absolute path · a path outside this session's scratchpad — **and for every escape the two review rounds reproduced** | blocks B, C, D, E, `ESCAPES` (16 v1 escapes) and `TRAVERSAL` (9 round-2 escapes) |
| A3 | **Never** emits `ask` or `deny`, and always exits 0 — malformed, empty, null and non-Bash stdin are all SILENT, asserted as silence rather than merely not-`ask` | block G |
| A4 | The suite fails when any of the hook's rule constants is mutated | `mutation_sweep.py` over `sweep.json` — 23 mutants, each killed by its declared case |
| A5 | `.claude/settings.json` wires it **first** in the `PreToolUse` Bash matcher and dispatches it through `run-hook.sh` (never a named interpreter), and `.claude/hooks/` byte-matches the `.agents/hooks/` master | blocks WIRING and E2E, reading the real repo files |
| A6 | `python3 .agents/scripts/tests/run_all.py` passes | the gate itself |
| A7 | The lane's artifact folder holds an `implementation_plan.md` carrying a parsing `## Declared Change Set` and an audit verdict, and a `walkthrough.md` carrying a `Verdict:` line | `declared_change_set.py parse` exits clean; `/smh-close-task-merge-tree` preflight reads both |
| A8 | The review-runtime probe law states that a `/` command **is** a user request, and names a third door — a blocked `inline` must say what blocked it — in all five carriers and their five mirrored `.opencode/` doors | `test_review_engine.py` pins all four clauses and twin-agreement; `test_twin_parity.py` holds the two fenced copies byte-identical |

**A3 is the load-bearing one.** `ask` is auto-DENY in non-interactive mode (memory:
`hook-ask-becomes-autodeny-in-auto-mode`). A convenience hook that can deny would break the very
lane it exists to unblock, so this hook has exactly two legal outputs: `allow`, or silence.

---

## Steps

1. **`.agents/hooks/allow-scratchpad.py`** — the hook. Seven rules (the seventh added by this
   plan's own self-audit, below), all must hold or it stays silent.
   Wrapped in a bare `except: pass` + `sys.exit(0)`: it may only ever *remove* a prompt it is
   certain about, never *add* one. → A1, A2, A3
2. **`.claude/hooks/allow-scratchpad.py`** — the deployed copy, byte-identical. Mirrors the
   `guard-cwd-escape.py` master/copy convention; `/smh-sync-agents` regenerates it. → A5
3. **`.agents/hooks/INDEX.md`** — one row, keeping the auto-listed contents honest. → A5
4. **`.claude/settings.json`** — wire it as the first `PreToolUse` Bash hook. First so its `allow`
   is recorded before the later gates speak; a sibling `ask`/`deny` still wins, which is correct. → A5
5. **`.agents/scripts/tests/test_allow_scratchpad.py`** — the retrofit suite, `_harness.Cases`,
   stdlib only, one `c.block` per rule. → A1–A3
6. **Mutation sweep** over the hook's seven rule constants plus the two safety guarantees (the
   `ask` ban and the fail-silent wrapper); every mutant must die. Table: `sweep.json`. → A4

## Declared Change Set

- NEW `.agents/hooks/allow-scratchpad.py` — the hook itself, the canonical master → A1, A2, A3
- NEW `.claude/hooks/allow-scratchpad.py` — the deployed copy settings.json actually loads → A5
- EDIT `.agents/hooks/INDEX.md` — one row, keeping the auto-listed contents honest → A5
- EDIT `.claude/hooks/INDEX.md` — the deployed copy of that index, re-paired with its master → A5
- EDIT `.claude/settings.json` — wires the hook first in the PreToolUse Bash matcher → A5
- NEW `.agents/scripts/tests/test_allow_scratchpad.py` — the suite → A1, A2, A3, A4
- EDIT `.agents/scripts/tests/test_review_engine.py` — re-pins the probe law to its new clauses → A8
- EDIT `.agents/commands/smh-code-review.md` — the probe law, long form → A8
- EDIT `.agents/commands/cicd-code-review.md` — the probe law, long form, twin of the above → A8
- EDIT `.agents/commands/smh-quick-dev.md` — the probe law, twin-fenced short form → A8
- EDIT `.agents/commands/cicd-quick-dev.md` — the probe law, twin-fenced short form → A8
- EDIT `.agents/commands/cicd-dev-story-tests.md` — the probe law, compact form → A8
- EDIT `.opencode/commands/smh-code-review.md` — mirrored door, byte-identical → A8
- EDIT `.opencode/commands/cicd-code-review.md` — mirrored door, byte-identical → A8
- EDIT `.opencode/commands/smh-quick-dev.md` — mirrored door, byte-identical → A8
- EDIT `.opencode/commands/cicd-quick-dev.md` — mirrored door, byte-identical → A8
- EDIT `.opencode/commands/cicd-dev-story-tests.md` — mirrored door, byte-identical → A8
- NEW `_artifacts/_main/2026-08-22_scc-263-scratchpad-allow-hook/implementation_plan.md` — this plan → A7
- NEW `_artifacts/_main/2026-08-22_scc-263-scratchpad-allow-hook/walkthrough.md` — the closing record → A7
- NEW `_artifacts/_main/2026-08-22_scc-263-scratchpad-allow-hook/sweep.json` — the mutant table → A4
- EDIT `_artifacts/_main/INDEX.md` — the session row → A7

---

## Honesty about the RED phase

⛔ **This is a characterization retrofit, not a true RED-first lane.** The hook was written and
verified before the ticket existed — the operator hit the friction live and asked for the fix in the
chat, so the code preceded the ceremony. The test therefore passes green on first run, which is the
`test-debt-stories-are-characterization` convention, not the `tests-must-gate-for-real` RED.

**Superseded by the Amendment below.** v1's suite was a retrofit; v2's `ESCAPES` block is a
genuine red — every one of its sixteen cases returned `allow` against the code that shipped as
`8479bc8`, and block `TRAVERSAL` is the same again against the rewrite at `46a67bb6`, and they were written from reproductions the review lenses executed, not from
imagination. The mutation sweep remains the guard against vacuity for the rest of the suite.

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

---

## Amendment (2026-08-22) — the review threw the first hook away

**`/smh-code-review` returned FAIL on the v1 hook. Five lenses reproduced twelve escapes, every
one in the granting direction, and the operator's call was to rewrite rather than patch.** The
plan above described v1; this section is what replaced it, and the acceptance rows A1–A6 are now
read against the new design.

**What every escape had in common.** v1 asked *"are all the ABSOLUTE PATHS I can find inside the
sandbox?"* — a deny-list over a surface it had to recognise first. Anything not recognised AS a
path was treated as harmless:

| Reproduced escape | Why v1 allowed it |
|---|---|
| `rm -rf /<sb>/rt .agents` | `.agents` is relative; nothing collected it |
| `rm -rf .git # cleanup /<sb>` | a path in a **comment** satisfied "a sandbox path is present" |
| `bash /<sb>/r.sh > "out.txt"` | the redirect regex excluded quote characters, so it matched nothing and `all([])` is True |
| `bash /<sb>/r.sh >\| out.txt` | same, for `\|` |
| `bash /<sb>/r.sh >&out.txt` | `>&FILE` writes a **file**; `writable()` read the `&` as an fd duplication |
| `tar -C/<repo> -xf /<sb>/p.tar` | `ABS_PATH`'s lookbehind hides a path glued to a flag |
| `python3 /<sb>/h.py --out=/<repo>/x` | same, for `=` |
| `"curl"` · `\curl` · `/usr/bin/curl` | `DENY_WORDS` needed a delimiter immediately before the word |
| `/usr/bin/git clean -fdx` | `GIT_CALL` needed the same delimiter, so an absolute git skipped rule 6 |
| `git -C /<sb>/r log && git reset --hard` | rule 6 checked *every `-C` is sandboxed*, never *every git has one* |
| `cp /<sb>/x /opt/homebrew/bin/git` | `SAFE_PREFIXES` was reasoned about as read-only but enforced that way only for redirects |
| `rm -rf /private/tmp/claude-501/` | the root stopped at the **uid**, two levels above the session |

⭐ **That is not twelve bugs. It is what a deny-list over shell syntax always degrades into** — the
parser becomes the security boundary, and a regex is not a shell parser. Rule 7 is the proof: the
self-audit correctly generalised to *"a write target need not be absolute"*, and the fix covered
the two syntactic forms its author happened to think of.

**v2 inverts it into an allow-list of SHAPES.** Four rules, and anything not positively recognised
is refused:

1. **No shell metacharacters at all** — one simple command per call. This kills the comment escape,
   both redirect escapes, every quoting escape and every chaining escape at once, because none of
   those constructs survives to be misparsed. It costs less than it looks: `chmod +x X && bash X`
   becomes two Bash calls and **both** are auto-allowed.
2. **The executable is a bare name from a literal list** — never a path, so the whole
   `/usr/bin/<anything>` class is unreachable by construction. `SAFE_PREFIXES` is gone entirely,
   which removes the read/write asymmetry that leaked write permission into `/opt/homebrew`.
3. **Every non-flag token is an absolute path inside the sandbox** — relative arguments are refused
   outright, and a `--flag=VALUE` is split so its value is checked rather than hidden.
4. **The sandbox is this SESSION's scratchpad**, pinned against the payload's `session_id` when one
   arrives, so one lane can no longer delete another's harness.

**Evidence at the shipping sha `7ba2d09`.** All **16 replayed v1 escapes** refused (block
`ESCAPES`) · all **9 round-2 escapes** refused and the legal interior `..` still allowed (block
`TRAVERSAL`) · all **15 real harness shapes** still allowed (block `A`) · suite **163/163** ·
sweep **23/23 killed**, restore verified · full floor **48/48 files** · twin parity **65/65** ·
engine contract **868/868**.

⭐ **The sweep earned its place twice over.** It rejected four of my own mutant attributions — three
where a *different* rule caught the mutant first (so the declared case proved nothing about the
rule it named), and one, `M2`, that was an **equivalent mutant**: `SANDBOX_RE` starts with `^`, so
`search()` and `match()` cannot differ and no test could ever kill it. Replacing it with the
`scratchpad` word-boundary mutant found a real uncovered constant.

### A8 — the review-runtime probe law (folded in on operator instruction)

The probe law forbade both stopping to ask AND downgrading to `inline`, while naming **no third
move**. An agent that believed itself forbidden had no legal option, and the cheapest illegal one
is a silent `inline` that reads exactly like a runtime with no subagent tool — SCC-203 again. Two
changes, in all five carriers plus their five mirrored `.opencode/` doors:

- ***"Am I permitted?"* is answered by the invocation** — a `/` command **is** a user request, so a
  session directive gating subagent use on being asked is satisfied by it.
- **A third door that is legal but visible:** `inline (blocked: <what blocked you>)`. A bare
  `inline` from a runtime that has the tool is a false record; naming the blocker puts the belief
  where `walkthrough_roster.py` can see it instead of laundering it into a clean-looking `inline`.

⛔ **This lane hit that exact ambiguity live** — the builder stopped and asked the operator, which
the law forbids, because the law offered nothing else. The fix is the finding.

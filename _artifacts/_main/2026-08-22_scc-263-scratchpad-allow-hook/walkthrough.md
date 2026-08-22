# SCC-263 — walkthrough

**Lane:** `chore/SCC-263-scratchpad-allow-hook` · **Ticket:** SCC-263 (Task, under SCC-33)
**Tree:** `.claude/worktrees/scc-263-scratchpad-allow-hook`

review-runtime: fan-out

---

## What shipped

A `PreToolUse` hook that auto-allows the narrow shape of Bash command which can only touch this
session's scratchpad — so a verification lane stops asking for twenty-odd approvals to run a
harness it just wrote into a directory that dies with the session.

**Why nothing else could do it.** `Bash(...)` permission rules match the command string by
**prefix, never a path**, and the scratchpad path carries a **per-session id**, so no settings rule
can pre-grant it. A hook is the only layer that sees the resolved command.

**The four rules.** All must hold, and anything not positively recognised is refused:

| # | Rule |
|---|---|
| 1 | **No shell metacharacters at all** — one simple command per call |
| 2 | **The executable is a bare name from a literal allow-list** — never a path |
| 3 | **Every non-flag token is an absolute path inside the sandbox** — `--flag=VALUE` is split and its value held to the same bar |
| 4 | **The sandbox is THIS SESSION's scratchpad**, pinned against the payload's `session_id` when one arrives |

**Two legal outputs: `allow`, or silence. Never `ask`, never `deny`.** `ask` is auto-DENY in
non-interactive mode, so a convenience hook that emitted it would block the lanes it exists to
unblock. The body is wrapped in a bare `except` + `exit(0)`: it may only ever *remove* a prompt it
is certain about, never *add* one.

## The first implementation was thrown away, and that is the story

v1 asked *"are all the absolute paths I can find inside the sandbox?"* — a deny-list over a surface
it had to recognise first. **Five clean-context lenses reproduced twelve escapes**, every one in the
granting direction, every one the same shape: something not recognised **as** a path was treated as
harmless.

```
rm -rf /<sandbox>/rt .agents          → ALLOW   (.agents is relative; nothing collected it)
rm -rf .git # cleanup /<sandbox>      → ALLOW   (a path in a COMMENT satisfied "sandbox present")
bash /<sandbox>/r.sh > "out.txt"      → ALLOW   (the redirect regex excluded quote characters)
bash /<sandbox>/r.sh >&out.txt        → ALLOW   (>&FILE writes a FILE; read as an fd duplication)
tar -C/<repo> -xf /<sandbox>/p.tar    → ALLOW   (a path glued to a flag is invisible to a lookbehind)
"curl" … / \curl … / /usr/bin/curl    → ALLOW   (the deny-list needed a delimiter before the word)
git -C /<sandbox>/r log && git reset --hard → ALLOW  (one well-formed -C licensed every bare git)
cp /<sandbox>/x /opt/homebrew/bin/git → ALLOW   (read prefixes leaked WRITE permission)
rm -rf /private/tmp/claude-501/       → ALLOW   (the root stopped at the uid, two levels too high)
```

⭐ **That is not twelve bugs — it is what a deny-list over shell syntax always degrades into.** The
parser becomes the security boundary, and a regex is not a shell parser. Rule 7 of v1 is the proof:
the self-audit correctly generalised to *"a write target need not be absolute"*, and the fix covered
only the two syntactic forms its author thought of.

The rewrite removes the entire attacked surface rather than patching it: no `SAFE_PREFIXES`, no
`DENY_WORDS`, no redirect parsing, no `tee` handling, no `git -C` logic, no path-scavenging regex.

## Evidence

| Claim | Command | Result |
|---|---|---|
| Every reproduced escape is dead | `ESCAPES` block, 16 cases | **all refused** |
| Real harness traffic still passes | `A` block, 11 shapes | **all allowed** |
| The hook behaves as specified | `python3 .agents/scripts/tests/test_allow_scratchpad.py` | **107/107** |
| The suite is not vacuous | `mutation_sweep.py --table …/sweep.json` | **15/15 killed** by their declared case; restore verified |
| The command centre still passes | `python3 .agents/scripts/tests/run_all.py` | **44/44 files** |
| The probe-law edit holds twin parity | `test_twin_parity.py` · `test_review_engine.py` | **64/64** · **856/856** |

⭐ **The sweep earned its place twice.** It rejected four of my own mutant attributions — three where
a *different* rule killed the mutant first (so the declared case proved nothing about the rule it
named), and one, `M2`, that was an **equivalent mutant**: `SANDBOX_RE` starts with `^`, so `search()`
and `match()` cannot differ and no test could ever kill it. Replacing it with a `scratchpad`
word-boundary mutant found a genuinely uncovered constant.

## A8 — the review-runtime probe law

Folded into this ticket on operator instruction. The law forbade both stopping to ask **and**
downgrading to `inline`, while naming **no third move** — so an agent that believed itself forbidden
had no legal option, and the cheapest illegal one is a silent `inline` that reads exactly like a
runtime with no subagent tool. That is SCC-203's defect, re-enterable through the fix for it.

Two changes across five carriers plus their five mirrored `.opencode/` doors:

- ***"Am I permitted?"* is answered by the invocation** — a `/` command **is** a user request, so a
  session directive gating subagent use on being asked is satisfied by it.
- **A third door that is legal but visible:** `inline (blocked: <what blocked you>)`.

⛔ **This lane hit that ambiguity live.** The builder stopped and put the question to the operator —
which the law forbids — because the law offered nothing else to do. The fix is the finding.

## Scope this deliberately does not cover

- **`bash /<sandbox>/x.sh` runs whatever the agent wrote there.** Writing into the scratchpad was
  never gated, so the script's *contents* were never the thing under review — only the act of
  running it. That is the deliberate trade; the twelve escapes were not.
- **`&&` chains are refused.** `chmod +x X && bash X` becomes two Bash calls — and **both** are
  auto-allowed, so the prompt count is unchanged. Over-refusal is the correct direction for a
  component whose only failure mode is granting too much.
- **The PC gets nothing.** Its scratchpad root is not `/private/tmp/claude-<uid>/`, so the hook is a
  silent no-op there while the shared `.claude/settings.json` wiring travels.
- **Lobby-only.** `.agents/hooks/INDEX.md:3` claims the masters mirror to *"project vendored copies
  via `/smh-sync-agents`"*. Measured false — no `hooks` key in `.sync-manifest.json`, no `hooks` in
  the sync command, and none of `AGY_AVIATIONCHAT`, `NEXgen-VR-Director` or `sudo-project-skeleton`
  has a `.claude/hooks/` at all. Pre-existing drift, not this lane's to fix.

---

## Code Review — round 1 (2026-08-22, v1 @ `141a6ff1`)

review-runtime:  fan-out
lenses_run:
- Blind Hunter · ok
- Edge Case Hunter · ok
- Literal-Correctness Hunter · ok
- Acceptance Auditor · ok
- Test-Adequacy Auditor · ok
lenses_counted:  5/5
lenses_na:       none
findings:        0 decision · 20 patch · 0 defer   (0 noise-dismissed · 8 relevance kills)
dispositions:    per-lens: Blind Hunter=9/0/1 · Edge Case Hunter=8/0/0 · Literal-Correctness Hunter=11/0/1 · Acceptance Auditor=9/0/0 · Test-Adequacy Auditor=6/0/6
severity_floor:  FAIL
notes:           Reviewed at 141a6ff1. All five lenses ran in clean contexts; none degraded.
                 Every hunter reproduced its findings by executing the hook rather than
                 inferring. The floor is FAIL on the reviewed sha: twelve escapes, all in the
                 granting direction. Every one is fixed in-lane by the rewrite; the eight
                 relevance kills are findings about constants the rewrite DELETED
                 (SAFE_PREFIXES, DENY_WORDS, ABS_PATH, REDIRECT, TEE, WRITE_OK, the git -C
                 scrape) plus one over-refusal that fails safe.

**Round-1 verdict: CONCERNS @ `141a6ff1` → rewritten.** Every finding was fixed, but ⛔ **the code
that would have shipped had never itself been hunted** — the `ESCAPES` block and the replay harness
were builder-run evidence over the builder's own design, which is exactly what this lane proves
misses things. CONCERNS therefore obliged a second fan-out against the rewrite. Round 2 is that
fan-out, and it found two escape classes nobody would have found from the inside.

### Fixed in-lane — round 1

| Finding | Lens(es) | Fix |
|---|---|---|
| Relative arguments unconstrained (`rm -rf /<sb>/rt .agents`) | Blind · Edge · Test-Adequacy | rule 3 — every non-flag token must be a sandboxed absolute path |
| A sandbox path in a `#` comment satisfies "sandbox present" | Edge | rule 1 — `#` is a forbidden metacharacter |
| Quoted / `>\|` / `>&FILE` redirect targets | Blind · Edge · Literal · Acceptance | rule 1 — no redirection survives at all |
| Path glued to a flag (`-C/dir`, `--out=/dir`) | Blind · Edge · Literal · Acceptance | rule 3 — `--flag=VALUE` is split and checked |
| Quoted / escaped / absolutely-pathed deny words | Blind · Edge · Literal | rule 2 — bare-name allow-list; the whole class is unreachable |
| `git` bypasses (absolute path; one `-C` licensing bare gits; a non-git `-C`) | Blind · Edge · Literal | rule 2 — `git` is not on the allow-list |
| Read prefixes leaked WRITE permission via arguments | Blind · Literal · Test-Adequacy | `SAFE_PREFIXES` deleted |
| Tilde-user expansion (`~user/...`) | Blind | rule 1 — `~` is forbidden |
| Sandbox root was the uid, not the session | Blind · Edge | rule 4 — full session path + `session_id` pin |
| Block H's non-Bash case was VACUOUS | Test-Adequacy | the probe now carries a real allowable command |
| Fail-silent pinned only against `ask`, not `deny` | Test-Adequacy | block G asserts `silent()`, not `!= "ask"` |
| No tier exercised the `run-hook.sh` seam | Test-Adequacy | block E2E, plus a WIRING assertion |
| `walkthrough.md` untracked and carried no `Verdict:` | Acceptance | this file, committed |
| `sweep.json` and `_artifacts/_main/INDEX.md` absent from the ledger | Acceptance | ledger rebuilt — 21 entries, 0 incomplete |
| Plan said "six constants" against a 12-mutant table | Acceptance · Literal | acceptance rows A1–A5 rewritten for v2 |
| `.claude/settings.json` lost its trailing newline | all four | restored |
| `.claude/hooks/INDEX.md` left unpaired with its master | Literal | re-paired |

### Relevance kills — round 1 (reported, not fixed, with the reason)

- **Six Test-Adequacy findings** about untested constants — per-word `DENY_WORDS`, `SAFE_PREFIXES`
  widening, the `ABS_PATH` lookbehind, `tee`'s flag skip, `WRITE_OK` membership, `git`'s multi-`-C`
  `all()`. **Every one of those constants was deleted by the rewrite.** Adding tests for them would
  pin code that no longer exists.
- **Blind Hunter #10, over-broad declines** (`git … a..b`, `grep -C 3`). Correct direction — they
  fail safe to a normal prompt — and v2 refuses far more by design.
- **Test-Adequacy: block WIRING's byte-identity check confounds hand mutation** of the master. Real,
  and kept deliberately: `sweep.json` filters by `--case` so the declared sweep is unaffected, and
  the check is the only thing that catches a stale deployed copy.

---

## Code Review — round 2 (2026-08-22, the rewrite @ `46a67bb6`)

review-runtime:  fan-out
lenses_run:
- Blind Hunter · ok
- Edge Case Hunter · ok
- Literal-Correctness Hunter · ok
- Acceptance Auditor · ok
- Test-Adequacy Auditor · ok
lenses_counted:  5/5
lenses_na:       none
findings:        0 decision · 14 patch · 0 defer   (0 noise-dismissed · 3 relevance kills)
dispositions:    per-lens: Blind Hunter=4/0/1 · Edge Case Hunter=3/0/0 · Literal-Correctness Hunter=3/0/1 · Acceptance Auditor=2/0/1 · Test-Adequacy Auditor=2/0/0
severity_floor:  FAIL
notes:           Reviewed at 46a67bb6, in clean contexts, none degraded. The floor is FAIL on
                 the reviewed sha: two NEW escape classes, both in the granting direction and
                 both invisible to round 1's design because they are not deny-list holes —
                 they are tokens the allow-list correctly recognises and correctly matches
                 that still resolve outside. Every one is fixed at 7ba2d09.

⭐ **The allow-list closed all twelve of round 1's escapes and opened a class of its own.** Both new
findings share one shape: **a token that IS recognised as a path, DOES match the sandbox, and still
lands outside it.** No amount of "is this argument in the sandbox?" reaches either one.

| # | Escape | Lens(es) | Why the allow-list allowed it | Fix |
|---|---|---|---|---|
| 1 | `rm -rf /<sb>/../../../../../../Users/…/.agents` | Blind · Edge | The hook compares **strings**; the kernel resolves a **graph**. `SANDBOX_RE.match` stops at `scratchpad/` and never looks further, and the session pin passes because the real id genuinely is in the string. ⛔ **A regression I introduced** — v1 banned `..` outright and the rewrite dropped the ban without replacing it. | rule 5 — `posixpath.normpath` **before** matching, so the string the hook checks is the path the kernel will walk |
| 2 | `ln -sf /<sb>/AGENTS.md` | Blind | One operand, no `..`, every argument legitimately inside the sandbox — and POSIX puts the link in the **CWD**, which `-f` unlinks first. The destination is never in the string, so **no argument inspection can see it.** | rule 6 — `ln` removed from `ALLOWED`, with the property to test before any future addition written beside it |
| 3 | The session pin was **containment, not position** | Edge · Literal | Any string containing this session's id anywhere passed, and **a missing `session_id` downgraded to shape-only** — so a concurrent lane's scratchpad was writable. | one pattern built around the asking session, uid pinned to `os.getuid()`, and **no session id means no grant** |

⛔ **The Test-Adequacy Auditor was the most useful lens and the most damning.** It hand-wrote 22
mutants against the audited sha and **all 22 survived**. One root cause: every set in the hook was
pinned by *examples*. **Adding `env` to `ALLOWED` left the entire suite green** — and `env` runs any
binary, so the allow-list's whole guarantee was untested. `ALLOWED`, `FORBIDDEN` and `VALUE_FLAGS`
are now pinned as **closed sets** imported from the module, with a positive case per member.

It also caught two of my own tests being vacuous while looking rigorous, and one took **two** goes
to fix: `cat X\nrm -rf .agents` and `cat X\nbash Y` both still refuse with `\n` removed from
`FORBIDDEN`, because the second command's own token fails a *different* rule. The only shape that
isolates rule 1 is one where the second command **is itself** a sandbox path — `cat X\n/<sb>/evil.sh`.

### Fixed in-lane — round 2

| Finding | Lens(es) | Fix |
|---|---|---|
| `..` traversal out of the sandbox (also inside a `--flag=` value) | Blind · Edge | `posixpath.normpath` before every match; block `TRAVERSAL`, incl. a positive case that an interior `..` staying inside is still allowed |
| `ln`'s implicit CWD destination | Blind | `ln` off the allow-list; the comment states the property, not the instance |
| Session pin was containment, and absent id fell back to shape-only | Edge · Literal | per-session compiled pattern, `os.getuid()`, no id → no grant |
| 22 hand-written mutants all survived — sets pinned by example | Test-Adequacy | block `CLOSED`: `ALLOWED`, `FORBIDDEN`, `VALUE_FLAGS` asserted as closed sets against the imported module |
| Sweep table did not reach the new rules | Test-Adequacy | table grown 15 → **23** mutants: normpath, boundary, uid, positional session, `#`/`\n` drops, `env`/`tar`/`ln` additions, `FLAG_RE` widening, the chmod mode slots |
| `chmod <path> +x` allowed — my own fix for `chmod -R 755 X` | Literal (caught by existing block F) | `saw_mode` requires `not saw_path`, so the mode may only be a leading token |
| Ordinary harness spelling refused (`chmod -R 755 X`, `head -n 5 X`, `tail -c 100 X`, `rm -rf -- X`) | Acceptance · Edge | value-flag slot + `--` handling; each is a prompt this hook exists to remove, so all four are pinned ALLOWED |
| Two "non-vacuous" tests were vacuous | Test-Adequacy | rewritten until each isolates its own rule; the newline case needed a sandbox-path second command |
| E2E measured the wrong tree | Literal | `run-hook.sh` reads `CLAUDE_PROJECT_DIR` before `cwd`; the test now passes it explicitly |
| Probe-law clause selectors drifted from the new wording | Acceptance | `test_review_engine.py` re-pinned to `IS a user request` / `may not record a bare`; `cicd-dev-story-tests.md` added as a carrier without joining `CALLER_FILES` |

### Relevance kills — round 2

- **`bash /<sb>/x.sh` still runs agent-authored code.** Restated by two lenses. Out of scope by
  design and stated in the docstring — writing into the scratchpad was never gated, so the script's
  *contents* were never what this hook reviews.
- **Over-refusal of legitimate non-sandbox work** (`grep -C 3 pat file`). Correct direction: it
  falls through to the normal prompt, which is the pre-hook behaviour.
- **No `task.yaml` manifest** (Acceptance). Close-out warns, does not fail; the artifact folder
  carries the plan, the walkthrough and the sweep table.

---

## Verdict

**Verdict: PASS @ `7ba2d09`**

- **Both rounds' findings are fixed at the shipping sha**, and round 2's were fixed *after* being
  found by lenses that did not design the code — which is precisely the obligation round 1's
  CONCERNS imposed.
- **The evidence is no longer builder-run over its own design.** Sixteen v1 escapes and nine
  round-2 escapes are replayed as tests; the sweep is 23/23 killed with restore verified; the three
  sets that carry the security guarantee are pinned closed, not by example.
- **Gates at `7ba2d09`:** suite **163/163** · sweep **23/23 killed** · floor **48/48 files**
  (`run_all.py`, 59/59 tests) · twin parity **65/65** · engine contract **868/868**.

⚠️ **What PASS does not claim.** This hook grants permission, and its guarantee is *"every argument
resolves inside a directory that dies with the session"* — not *"this command is safe"*. Running
agent-authored scripts from the scratchpad is deliberately in scope for `allow`, and the two review
rounds are the record of how much a permission-granting component gets wrong when only its author
looks at it.

# SCC-267 — walkthrough

**Lane:** `chore/SCC-267-scratchpad-hook-cross-platform` · **Ticket:** SCC-267 (Task, under SCC-33)
**Tree:** `.claude/worktrees/scc-267-scratchpad-hook-cross-platform` · **Follows:** SCC-263 (`2756b5a`)


---

## Step 0.7 — re-derivation (what moved under this lane, and what it changed)

- **What moved:** SCC-263 landed as `2756b5a` (PR #47) and SCC-186 as `780bf85` (PR #48). This lane
  is cut from `780bf85`, so both are already in its base — the hook this lane edits is the one that
  merged hours earlier, not a copy of it.
- **What it changes here:** nothing to re-absorb and no sibling lane live. The dependency runs the
  other way for once: **this lane edits the file SCC-263's mutant table anchors on**, which is what
  the third section below is about.
- **What was re-measured:** the full floor `run_all.py` **48/48 files (61/61 tests)** and again
  **48/48 under a simulated foreign uid**; the hook suite **187/187** both ways; **both** mutant
  tables — this lane's **4/4** and SCC-263's **24/24** — with restore verified; lint 0/0;
  `check_maps --depth3-only --strict` exit 0.

---

## What shipped

**Two defects, and the smaller one is the one the ticket was opened for.**

### 1. The hook crashed on Windows — on every Bash call

```
exit: 1
Traceback (most recent call last):
  File ".agents/hooks/allow-scratchpad.py", line 106, in <module>
    _UID = re.escape(f"claude-{os.getuid()}")
AttributeError: module 'os' has no attribute 'getuid'
```

SCC-263 recorded this hook as *"Mac-only — a silent no-op on the PC."* ⛔ **The claim was wrong in
the dangerous direction.** `_UID` was a module-level constant, evaluated at import — **outside** the
`try/except` that carries the hook's entire promise:

> *it may only ever REMOVE a prompt it is certain about, never ADD one*

⭐ **A wrapper cannot catch a crash that happens before the wrapper is installed.** The single code
path its safety net could not cover is the one that ran first, every time, on the second machine.
A convenience hook had become a noisy blocker there, and nothing on the Mac could ever show it.

**Fix:** nothing that can raise runs at module level. Every resolver is a function called from
inside the wrapper, and every one answers `None` — which reads as *no grant* — rather than raising.

### 2. The sandbox root is now per-machine

`/(?:private/)?tmp/claude-<uid>` is POSIX. The PC's root is a different shape **and machine-specific**,
so it does not belong in shared code at all: committing one machine's root points every other
machine's hook at a directory that does not exist there. Same class as `core.hooksPath` and
`~/.zshenv` — set once per machine, never travels.

⭐ **It widens the ROOT, never the SHAPE.** Whatever the file names is still followed by
`/<project>/<session-id>/scratchpad`, pinned to the asking session and normalised, so a wrong entry
cannot grant more than one session's disposable directory. Refused outright — falling back to the
built-in root, which on a uid-less machine means no grant at all — when it is relative,
native-Windows, `/`, `//`, one segment, or carries a shell metacharacter.

⛔ **What this lane deliberately does not paper over.** The hook bans `\` (rule 1) and requires
paths to start with `/`. So a git-bash spelling (`/c/Users/…`) is grantable and a native one is not
— and the guide makes the operator **measure which their Bash tool emits** before writing anything.
Admitting backslashes re-opens exactly the ambiguity rule 1 exists to remove: on Windows `\` is both
an escape character and a separator. That is a design change with its own review, not a config value.

---

## ⚠️ This lane disarmed the previous lane's evidence, and only running it found that

Three of SCC-263's twenty-four mutants anchored on lines this lane rewrote:

| Mutant | What happened |
|---|---|
| `M1` (stop normalising) | anchor line gone — **sweep error**, loud |
| `M3` (accept any uid) | same; the root moved into `_uid_root()` |
| `M24` (hardcode the uid) | ⭐ **worse than an error.** It found its anchor string inside a **comment** — the one I wrote explaining the old bug, which quoted the old code verbatim. The sweep mutated *prose*, the declared case passed unchanged, and the only thing that noticed was the byte-identity check firing for an unrelated reason |

`M24` is `comment-literals-invert-source-grep-tests` arriving from a new direction: **a comment that
re-types code becomes an anchor.** The comment now describes the line instead of quoting it, all
three are re-anchored onto live code, and SCC-263's table is back to **24/24 killed**.

**The rule this adds:** a lane that edits a file another lane's sweep table anchors on must **run
that table too.** Nothing else catches it.

---

## Three of six mutants survived the first sweep, and each was a different lesson

| Survivor | Why | What it became |
|---|---|---|
| `M5` — drop the two-segment root floor | ⛔ **Mis-attribution.** Every bad-root case sent one probe command built under the *good* root, so each passed because the command was not under the tested root **at all** — a different rule refusing it. The same shape SCC-263's sweep caught four times | each probe is now built **under the root it tests**; `M5` and `M6` both die |
| `M4` — honour a relative or metacharacter root | **Equivalent.** `sandboxed()` already refuses any token not starting with `/`, and `re.escape` reduces a metacharacter to a literal. No external observer can tell | declared as an equivalent mutant **with the reasoning in `sweep.json`**; the guard stays, because it is what keeps this file correct if that downstream check is ever relaxed |
| `M1` — read `os.getuid` directly again | **I mutated the wrong thing.** Inside a function the raise is absorbed by `sandbox_root()`'s own `try/except`, so it is equivalent. The bug is evaluation at **module level**, before the wrapper exists | re-aimed: `M1` now appends a module-level `_UID = os.getuid()` and dies on `PLATFORM · exit 0 where there is no uid` |

⭐ **Two equivalent mutants are recorded, not deleted.** `sweep.json` carries an
`equivalent_mutants_not_declared` block saying which mutation no test can kill and *why the guard
stays anyway* — the same discipline SCC-263 used for its `search()`/`match()` mutant.

---

## Evidence

| Claim | Command | Result |
|---|---|---|
| A uid-less platform gets silence, not a traceback | block `PLATFORM`, hook run with `os.getuid` deleted | **exit 0, empty stdout and stderr** |
| ...and grants once a root is configured | block `PLATFORM` | **allow** |
| The override widens root, never shape | block `CONFIG`, 6 shape + 8 refusal cases | **all as required** |
| The Mac default is untouched with no file | block `CONFIG` | **allow**, unchanged |
| The suite | `test_allow_scratchpad.py` | **187/187**, and 187/187 under a simulated foreign uid |
| This lane's rules are not vacuous | `mutation_sweep.py` (this table) | **4/4 killed**, restore verified |
| The previous lane's evidence still holds | `mutation_sweep.py` (SCC-263's table) | **24/24 killed** |
| The floor | `run_all.py` | **48/48 files (61/61)**, both ways |
| Lint · maps | `workflow_lint --toolkit-only` · `check_maps --depth3-only --strict` | **0/0** · **exit 0** |
| The guide's own commands work | §4's grant and refusal probes, run verbatim | **allow**, then **silence** |

---

## Code Review — NOT RUN

⛔ **No lens review happened, so this file carries no `Verdict:` line and no roster.**
Operator call. The ask behind this lane was *"stop making me approve
twenty Bash calls"*, and it had already grown into two tickets and three lens review rounds. The
operator called the ceremony overkill for the size of the change, and that ruling stands.

**What that costs, stated rather than hidden:** no clean-context lens has looked at the two new
resolvers. The mechanical evidence below is builder-run — which is exactly the thing SCC-263's own
review proved can miss a whole class. Weighed against it: the change is small, the fail-safe
direction is the safe one (every new path answers *no grant*), the Mac behaviour is asserted
byte-for-byte unchanged, and **both** mutant tables are clean.


---

## Your Actions

- [x] The merge itself — lands via this branch's PR

**One thing to do on the PC, and it is the point of the lane:** follow
[`scratchpad-allow-hook-per-machine.md`](../../../docs/migrations/install_guides/scratchpad-allow-hook-per-machine.md)
— measure the scratchpad root there, write it to the gitignored file, run §4's verify. ⚠️ **Read §3
first:** if that machine's Bash tool spells paths natively (`C:\…`) rather than git-bash style
(`/c/…`), this hook cannot grant there and that needs a ticket, not a config value.

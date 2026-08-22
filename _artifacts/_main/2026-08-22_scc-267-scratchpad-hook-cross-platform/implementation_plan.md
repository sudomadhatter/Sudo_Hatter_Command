# SCC-267 — the scratchpad hook on the second machine: stop crashing, and learn the root

**Lane:** `chore/SCC-267-scratchpad-hook-cross-platform` · **Epic:** SCC-33 (CI/CD For Sudo Dev System)
**Date:** 2026-08-22 · **Lane type:** TASK (toolkit paths) · **Follows:** SCC-263, merged `2756b5a`

---

## The problem, measured

SCC-263 shipped the scratchpad auto-allow hook and recorded it as *"Mac-only — a silent no-op on the
PC."* ⛔ **That claim was wrong in the dangerous direction.** On Windows the hook does not fall
silent. It **crashes on every single Bash call.**

```
$ python allow-scratchpad.py   # with os.getuid removed, as on Windows
exit: 1
Traceback (most recent call last):
  File ".agents/hooks/allow-scratchpad.py", line 106, in <module>
    _UID = re.escape(f"claude-{os.getuid()}")
AttributeError: module 'os' has no attribute 'getuid'
```

`_UID` was a **module-level constant**, evaluated at import — **outside** the `try/except` at the
bottom of the file. That wrapper is the whole basis of the hook's promise:

> *it may only ever REMOVE a prompt it is certain about, never ADD one*

⭐ **A wrapper cannot catch a crash that happens before the wrapper is installed.** The one code
path the safety net could not cover is the one that ran first, on every invocation, on the
operator's other machine. That is the finding; the Windows path shape is the smaller half.

**The second half.** The sandbox root is a POSIX literal — `/(?:private/)?tmp/claude-<uid>` — and
the PC's root is a different shape. It is also **machine-specific**, which is why it does not belong
in shared code at all: committing one machine's root points every other machine's hook at a
directory that does not exist there. Same class as `core.hooksPath` and `~/.zshenv`.

---

## Acceptance

| # | Statement | How it is checked |
|---|---|---|
| A1 | The hook **imports and answers** on a platform with no `os.getuid`, and answers **silence** there rather than raising — exit 0, empty stdout, nothing on stderr | block `PLATFORM`, running the hook in a child with `os.getuid` deleted |
| A2 | **Nothing that can raise runs at module level.** The fail-safe covers the whole body, not just `main()` | block `PLATFORM`, and sweep mutant **M1** — which reintroduces module-level evaluation and must die |
| A3 | The sandbox root is resolvable **per machine** from a gitignored file, and an absent file leaves the POSIX behaviour byte-for-byte unchanged | block `CONFIG`, including the no-file regression case |
| A4 | An override widens the **root** only, never the **shape**: `<root>/<project>/<session_id>/scratchpad`, session-pinned, normalised, absolute-only. A relative, native-Windows, `/`, one-segment or metacharacter-bearing root does **not** grant | block `CONFIG`, six shape cases + eight refusal cases, **each probed under the root it tests** |
| A5 | Every new rule fails when mutated | `mutation_sweep.py` — this lane's table (4 mutants) **and SCC-263's (24)**, both clean |
| A6 | `run_all.py` passes, and passes again under a simulated foreign uid | the gate, run both ways |
| A7 | A guide tells the operator how to **measure** their root, set it, and **verify** the hook grants — linked from the migrations INDEX | the guide's own commands, run verbatim here |
| A8 | The SOP stops claiming *"Mac-only, a silent no-op there"* | the row, rewritten |
| A9 | The lane's artifact folder holds a parsing `## Declared Change Set` and a `walkthrough.md` carrying a `Verdict:` line and a task manifest | `declared_change_set.py parse` exits clean; the close-out preflight reads both |

**A2 is the load-bearing one.** Every other row is about the PC getting a benefit. A2 is about the
Mac's guarantee being true in the first place.

---

## Design

**Everything is a function, called from inside the wrapper, and every resolver answers `None`
rather than raising.** `None` means *no grant*: the hook falls silent and the operator gets the
ordinary prompt they had before it existed.

| Resolver | Answers |
|---|---|
| `_configured_root()` | the machine-local root as a regex fragment, or `None` to fall through |
| `_uid_root()` | the built-in POSIX root, or `None` where the process has no uid |
| `sandbox_root()` | `_configured_root() or _uid_root()`, wrapped — or `None` |
| `sandbox_re(session)` | the one pattern, or `None` when there is no root |

**The override widens the root and nothing else.** Whatever it names is still followed by
`/<project>/<session_id>/scratchpad`, pinned to the asking session and normalised, so a wrong entry
cannot grant more than one session's disposable directory. It is refused outright — falling back to
the built-in root — when it is relative, native-Windows, `/`, `//`, one segment, or carries a shell
metacharacter.

⛔ **Windows has a precondition this lane does not paper over.** The hook bans `\` (rule 1) and
requires paths to start with `/`. So a git-bash spelling (`/c/Users/…`) is grantable and a native
one (`C:\Users\…`, or even `C:/Users/…`) is not — and the guide's §3 makes the operator *measure*
which their Bash tool emits before writing anything. Admitting backslashes is a design change with
its own review, not a config value: `\` is both an escape and a separator on Windows, which
re-opens exactly the ambiguity rule 1 exists to remove.

## Declared Change Set

- EDIT `.agents/hooks/allow-scratchpad.py` — no module-level evaluation; per-machine root resolvers → A1, A2, A3, A4
- EDIT `.claude/hooks/allow-scratchpad.py` — the deployed copy, byte-identical → A1
- EDIT `.agents/scripts/tests/test_allow_scratchpad.py` — blocks `PLATFORM` and `CONFIG` → A1, A3, A4
- EDIT `.gitignore` — the machine-local root file never travels → A3
- NEW `_artifacts/_main/2026-08-22_scc-267-scratchpad-hook-cross-platform/sweep.json` — this lane's mutant table → A5
- EDIT `_artifacts/_main/2026-08-22_scc-263-scratchpad-allow-hook/sweep.json` — re-anchored onto the rewritten lines → A5
- NEW `docs/migrations/install_guides/scratchpad-allow-hook-per-machine.md` — measure, set, verify → A7
- EDIT `docs/migrations/INDEX.md` — step 11 in the machine-setup table → A7
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — the hook's row, corrected → A8
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — the two delta lines → A8
- NEW `_artifacts/_main/2026-08-22_scc-267-scratchpad-hook-cross-platform/implementation_plan.md` — this plan → A9
- NEW `_artifacts/_main/2026-08-22_scc-267-scratchpad-hook-cross-platform/walkthrough.md` — the closing record → A9
- EDIT `_artifacts/_main/INDEX.md` — the session row → A9
- NEW `_artifacts/_main/2026-08-22_scc-267-scratchpad-hook-cross-platform/task.yaml` — the close-out manifest → A9

---

## ⚠️ What this lane changed about the PREVIOUS lane's evidence

⛔ **Rewriting the hook silently disarmed part of SCC-263's mutant table, and only running it
found that.** Three of its twenty-four mutants anchored on lines this lane rewrote:

| Mutant | What happened |
|---|---|
| `M1` (stop normalising) | its anchor line no longer existed — **sweep error**, not a silent pass |
| `M3` (accept any uid) | same; the root moved into `_uid_root()` |
| `M24` (hardcode the uid) | ⭐ **worse than an error — it found the string in a COMMENT.** The comment explaining the old bug quoted the old code verbatim, so the sweep mutated *prose*, the declared case passed unchanged, and the only thing that noticed was the byte-identity check firing for an unrelated reason |

`M24` is the `comment-literals-invert-source-grep-tests` scar arriving from a new direction: a
comment that re-types code becomes an anchor. **The comment now describes the line instead of
quoting it**, and all three mutants are re-anchored onto live code. SCC-263's table is back to
**24/24 killed**.

**The rule this lane adds:** a lane that edits a file another lane's sweep table anchors on must
**run that table too.** Nothing else catches it — a stale anchor either errors loudly or, in the
`M24` case, reports a kill that proves nothing.

---

## Honesty about the RED phase

**A1 and A2 are a genuine red.** The crash was reproduced against the shipped code before anything
was written — exit 1 with a traceback — and block `PLATFORM` asserts exit 0 and silence, which that
code could not deliver. **A3 and A4 are new capability**, so their tests pass green-first; the
mutant table is what makes them non-vacuous rather than decorative.

⭐ **Three of six declared mutants survived the first sweep, and each survival was a different
lesson** — recorded in the walkthrough rather than quietly re-declared.

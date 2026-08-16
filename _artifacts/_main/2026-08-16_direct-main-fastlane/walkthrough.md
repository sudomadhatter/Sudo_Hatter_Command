# Walkthrough — SCC-183: the direct-to-main prose lane

A third door to `main`. One commit of **prose** — `docs/**`, `_my_resources/**`, `_artifacts/**`,
root `*.md` — goes straight to `main` with a `--direct` token, skipping the branch, worktree,
`--no-ff` merge and close-out that a code change rightly pays for.

Operator ruling, 2026-08-16, verbatim:

> "yes delete then you take on this task. I do want it, the little changes to documents and updating
> things that dont touch any code are frustrating."

**This is a rebuild.** A first implementation (`chore/SCC-183-direct-main-push`, commit `3c66dee`)
was reviewed **FAIL** and deleted on operator instruction. Its two exploits are the first two tests
here.

## Task Checklist

- [x] Delete the failed lane (worktree + branch), artifacts backed up first
- [x] Replace the denylist with a **fail-closed allowlist** in one shared predicate
  - the sourced-predicate design is not tidiness: two copies of a security rule drift, and drift in
    this exact predicate is what the first attempt died of
- [x] `--key` mandatory in direct mode, and the key assertion **not** conditional on a key existing
- [x] Refuse every degenerate input: absent remote ref, empty change set, merge commit, symlink,
      submodule, missing predicate file
- [x] RED first — 8 named blocks, both halves (refuse **and** allow)
  - the first RED had a **fixture bug**: the `.githooks/pre-push` case overwrote the scratch repo's
    own dispatcher, and because it was untracked the next `git reset --hard` deleted it, so five
    later cases ran with no gate at all. Tracking it made the reset self-healing.
- [x] Mutation sweep drawn from the shipped code
  - first pass left **4 survivors, all one class** — see Findings
- [x] Wire every pre-existing case under a `c.block` guard (obligated by the ORPHAN rule)
- [x] Policy + SOP + `_artifacts` INDEX row

## Evidence

| # | Acceptance item | Proving assertion | RED → GREEN |
|---|---|---|---|
| 1 | `--key` mandatory in direct mode | `--case "direct: minter refuses --direct with no --key"` | RED (minter had no `--direct`) → **PASS** |
| 2 | Gate refuses a keyless token | `--case "direct: gate refuses a token with an empty key"` | RED → **PASS** |
| 3 | Allowlist is fail-closed | `--case "direct: allowlist"` refuse half, ×8 paths ×2 layers | RED (5 of 8 landed) → **PASS** |
| 4 | Gate cannot be used to ship the gate | `--case "direct: gate refuses a commit that rewrites the gate itself"` | RED → **PASS** |
| 5 | Allow half genuinely allows | `--case "direct: allowlist"` allow half, ×5 paths | RED (all 5 refused) → **PASS** |
| 6 | One commit, never a merge/batch | `--case "direct: shape"` | RED → **PASS** |
| 7 | Merge path untouched | full file, 73 pre-existing checks | 73/73 → **103/103** |
| 8 | Policy + SOP current | `workflow_lint --toolkit-only`, `sop_currency`, link+anchor | **0 errors, 0 warnings** |
| 9 | Minter pre-checks the allowlist | `--case "direct: minter refuses a disallowed path before minting"` | RED → **PASS** |
| 10 | Fail-closed on degenerate input | `--case "direct: fail-closed"` ×3 | RED → **PASS** |
| 11 | No symlinks | `--case "direct: refuses a symlink at an allowed path"` | RED → **PASS** |

**Gate results** — run bare, exit codes read directly:

```
test_main_push_gate.py           -- 103/103 passed --          (73 pre-existing preserved)
run_all.py                       29/29 files passed   exit 0   receipt: pass @ fefa1dbc, clean tree
workflow_lint.py --toolkit-only  0 error(s), 0 warning(s), 8 info   exit 0
sop_currency.py                  exit 0
check_maps.py --depth3-only --strict   exit 0
sh -n / dash -n / zsh -n         all three scripts OK on all three shells
```

**Mutation sweep — 13 mutants drawn from the shipped code, 13 killed / 0 survived / 0 defective.**

| Mutant | Killed by |
|---|---|
| allowlist: law arm stops refusing | `direct: allowlist` |
| allowlist: fail-closed arm opens | `direct: allowlist` |
| allowlist: nested-path sweep opens | `direct: allowlist` |
| allowlist: prose trees stop being allowed | `direct: allowlist` |
| allowlist: root markdown stops being allowed | `direct: allowlist` |
| gate: key-absence check inverted | `direct: gate refuses a token with an empty key` |
| gate: zero-remote refusal inverted | `direct: fail-closed` |
| gate: empty-changeset refusal removed | `direct: fail-closed` |
| gate: missing-predicate refusal removed | `direct: fail-closed` |
| gate: symlink mode check blinded | `direct: refuses a symlink at an allowed path` |
| gate: allowlist verdict ignored | `direct: allowlist` |
| gate: merge-commit refusal removed | `direct: shape` |
| minter: --key requirement dropped | `direct: minter refuses --direct with no --key` |

## Findings that changed the work

**The sweep's first pass left 4 survivors, and they were all one mistake.** The refuse-half cases
went through `mint_direct`, and the minter now refuses those paths itself — so the push was rejected
for *"no approval token"* and the **gate's own allowlist was never reached**. Blinding the gate's
allowlist verdict changed nothing, because nothing had ever exercised it. Every refuse path is now
pushed **twice**: once through the minter (layer 1) and once with a forged `mode=direct` token that
skips the minter entirely (layer 2, the authority). Two fail-closed cases were additionally pinned to
their *specific* refusal string, because a later check was silently covering for an inverted earlier
one.

**The H3 test as first written proved nothing, and the original exploit probe had the same flaw.**
Writing a *neutered* gate into the working tree and pushing it does land — but only because the hook
git runs **is** the working-tree copy, so it disabled itself before the allowlist was consulted. That
is `--no-verify` spelled slowly and is out of scope for any pre-push hook. The property that matters
is distribution: a fast-lane push puts a modified gate on the **remote**, where every machine that
pulls will run it. The test now commits a *benign* edit to the gate file with the running gate fully
intact, and asserts the refusal names the allowlist.

**Portability: `case` inside `$( )` does not parse on the operator's machine.** macOS `/bin/sh` is
bash 3.2, whose parser dies on the first `;;` of a `case` inside command substitution. `dash` and
`zsh` both accept it, so this would have passed on Linux CI and failed on the Mac. Both path loops use
`if`/`elif`. A called *function* is fine — its body is parsed outside the substitution — which is why
the allowlist keeps its own `case`.

**The pre-work audit caught the same failure class as the deleted attempt, before any code.** The
direct block was going to be nested inside the merge path's `if [ "$remote_sha" != "$ZERO" ]` guard,
which is correct for a merge and **fail-open** here: an all-zero remote sha would have skipped the key
check, the allowlist and the shape checks in one go.

**Introducing `c.block` obligated wiring the whole file.** `test_suite_runner.py`'s ORPHAN rule says a
file containing any `c.block(` must have *every* `c.check` under one — an unguarded check runs under
every filter and pollutes attribution, which would have corrupted this sweep's own results. The three
pre-existing sections are now wrapped; no assertion was changed.

## Deliberately not in this lane

- **Wiring `--direct` into `/smh-quick-fix`.** That file is owned by the live **SCC-164** lane
  (69 files, mid-flight). The mechanism ships here and the SOP documents the manual three-step
  procedure; the command wiring is a follow-on once SCC-164 lands. Deferred against a named blocker.
- **AVCH-63** — the port into `Projects/AGY_AVIATIONCHAT`, its own ticket in its own repo. Note for
  that lane: AVCH keeps `Dockerfile`, `.firebaserc`, `.gcloudignore` and `.dockerignore` at the
  **repo root**, which a denylist of directories would miss entirely.

## Landing order

**SCC-164 lands first.** Sole overlap is `docs/_scc_sops_prds/workflows_testing_SOP.md`; re-applying
one added section onto their rewritten SOP is far cheaper than the reverse.

## Your Actions

- [ ] Merge this lane to `main` — invoking `/smh-close-task-merge-tree` is the sign-off, and it should
      wait until **SCC-164** has landed (see Landing order).
- [ ] Confirm or carve out root `AGENTS.md` / `CLAUDE.md` / `GEMINI.md`. They are inside the allowlist
      you approved (root `*.md`), and are arguably *law* rather than prose. They are not unguarded —
      the armed `sop_currency` commit-msg gate already treats root `AGENTS.md` as a usage surface — but
      the call is yours, and changing it is a one-line edit to `direct-push-allowlist.sh`.

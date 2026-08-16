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

## Code Review (2026-08-16)

Verdict: FAIL @ 3e4d4f5de8814777012745a68079e3443335acba
Suite evidence measured at fefa1dbc (receipt `pass`, clean tree); no code changed between that sha
and the reviewed HEAD except the two in-thread fixes noted below, which were re-run.

**Scope:** the 6 code/doc files of SCC-183 plus artifacts. **Method:** `/smh-code-review` — Step 0.7
re-derivation, a 5-lens clean-room fan-out, acceptance audit against the plan's 11 items, the
command-centre gate, and a 13-mutant sweep.

**Lenses: 3 ran + 1 ran + 1 DEAD.** Blind Hunter `ok` · Edge Case Hunter `ok` · Acceptance Auditor
`ok` · Test-Adequacy Auditor `ok` · **Literal-Correctness Hunter `dead`** — stopped mid-run and not
recovered, so the symbol-level surface is **unexamined**. An unknown is not a pass; on its own that
caps this verdict at CONCERNS, and the findings below carry it past that.

### ⛔ The verdict-deciding finding: the lane cannot land on the real `main`

**This feature is non-functional against the actual remote, and every test passed anyway.**

| Fact | Evidence |
|---|---|
| `main` carries an ACTIVE GitHub ruleset requiring the `main-write-gate` check | `test_main_ruleset_armed.py` → 5/5, *"ruleset 'main write gate (SCC-118)' … active"* |
| Nobody may bypass it | *"the bypass list is EMPTY: 0 actor(s)"* |
| That check is published only on `pull_request` into `main`, or a push to `gate/**` | `.github/workflows/main-write-gate.yml:29-39` |
| The existing doors earn it by pushing a pre-flight ref first | `smh-close-task-merge-tree.md:309` — `git push origin HEAD:refs/heads/gate/main-$SHA` |
| The gate script **hard-fails any non-merge commit** | `main_write_gate.py:145` — *"is not a merge commit — it has 1 parent(s). main advances by exactly one merge commit."* |
| The procedure this lane documents has no pre-flight step at all | `workflows_testing_SOP.md` § direct lane — commit, mint, `git push origin main` |

A single-parent prose commit therefore **can never obtain the required check**, and the push is
refused server-side by a ruleset with an empty bypass list. The three-step procedure shipped in the
SOP and `git-policy.md` describes something that cannot happen.

⛔ **And this is a vacuous green of exactly the class this repo gates hardest against.** All 103
checks pass because `direct_repo()` builds its remote with `git init --bare` — a remote with no
ruleset and no CI. The suite proves the *local hook* behaves; it cannot see the *server* half, and
nothing in the harness says so. The local gate and the server gate are deliberately different halves
(authorisation vs fitness, per the workflow header), and this lane only ever tested one.

### Findings

| # | file:line | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| 1 | `.github/workflows/main-write-gate.yml:29` + `main_write_gate.py:145` | **critical** | A prose commit cannot earn the required check; the ruleset refuses the push. The documented procedure cannot work. | **DECISION — the design must change; options in `## Your Actions`** |
| 2 | `direct-push-allowlist.sh:48` | **critical** | `docs/**` is not a prose tree. It holds `docs/migrations/scripts/install-git-hooks.sh` (the script that ARMS the gates on a fresh machine) and `restore-env-master.sh` (the secrets kit). Reproduced end-to-end: a neutered hook-installer landed via `--direct` with an innocent subject. | **DECISION — narrow the allowlist; blocked on #1's direction** |
| 3 | `pre-push-main-approval.sh:136` (dispatch on `t_mode`) | **important** *(downgraded from critical — see note)* | The gate dispatches on a value the *pusher* writes, so the allowlist is opt-in: omit `--direct` and the merge arm takes it, where a plain commit passes (`parent1 == remote_sha`) and the `t_branch` check evaporates when the named branch does not resolve. Reproduced landing a gate-rewriting commit. Pre-existing — reproduces identically on `main` as shipped today, and NOT introduced here. | **DECISION — the fix adds a refusal to the *shipping* merge path, which is new blocking law and needs the operator's quoted ruling** |
| 4 | plan `[!NOTE]` boundary call | **important** | The mitigation offered to the operator is false for 2 of 3 files: `sop_currency.classify()` special-cases **only** `AGENTS.md`; `CLAUDE.md` and `GEMINI.md` match no surface and return `None` — no backstop at all. The operator approved a boundary against a guard that does not exist for them. | **corrected in `## Your Actions`; allowlist change blocked on #1** |
| 5 | `mint-push-token.sh` (allowlist source) | important | Present-but-empty predicate file → `command -v` absent → `! cmd` inverts exit 127 to false → no path ever flagged. The mint-side check disappears rather than fails. | **applied** — `command -v` guard added |
| 6 | both scripts, `diff-tree` | suggestion | `-M`/`-C` added later would emit `R100\tsrc\tdst`; `${line#*"$TAB"}` yields both paths as one string, which `docs/*` matches. Not live today (plumbing ignores `diff.renames`). | **applied** — `--no-renames` pinned |
| 7 | `pre-push-main-approval.sh:147` | suggestion | `[ -f ]` is not `[ -r ]`. An unreadable predicate dies with a raw shell error, **no refusal banner, and the token is NOT consumed** — breaking the file's own "every refusal consumes the token" invariant. | **deferred to the #1 rework** |
| 8 | `pre-push-main-approval.sh:56` | nitpick | The refusal banner still says *"main is reached exactly three ways"* and omits the lane the operator just used. Header and minter usage string likewise. | **deferred to the #1 rework** |
| 9 | tests | important | `160000` (gitlink) and the `command -v` arm have **no case** — deleting either survives the sweep. AC 11 and AC 10 are partially unproven. | **deferred to the #1 rework** |
| 10 | tests | important | One unexplained **flake**: `direct: shape` failed once in a full run, then passed in isolation and in two consecutive full runs. Unreproduced, cause unknown. A flaky security test is a real defect. | **open — named, not dismissed** |
| 11 | walkthrough AC 7 | nitpick | "73 pre-existing checks" is wrong; `main`'s file has 58 `c.check` calls / 64 checks. No regression (all 64 labels present in the new run). | noted |
| 12 | `.agents/scripts/INDEX.md` | nitpick | `direct-push-allowlist.sh` is undocumented; nothing enforces it. | **deferred to the #1 rework** |

### Gates

```
run_all.py                     29/29 files, exit 0    receipt pass @ fefa1dbc, clean tree
test_main_push_gate.py         103/103 (×2 consecutive)   ⚠ one unreproduced flake, finding #10
workflow_lint --toolkit-only   0 error(s), 0 warning(s), 8 info
sop_currency.py                exit 0
check_maps.py --depth3-only    exit 0
sh / dash / zsh -n             all three scripts clean on all three shells
mutation sweep                 13 killed / 0 survived / 0 defective  (blind to findings #9)
```

### ⚠ Correction on finding #3, and a history check

Finding #3 was first written as **critical** on the strength of a probe that landed a gate-rewriting
plain commit "on main". That probe used a **local bare remote** — no ruleset, no CI — so it was blind
to the server half, which is the *same* blind spot finding #1 is about. Against the real `main` the
attack is refused: a single-parent commit cannot earn the required `main-write-gate` check. Downgraded
to **important**, scoped to the local hook. It still deserves closing — the two halves are meant to be
independent and one of them currently is not — but `main` is not exposed by it.

**Was it ever used?** Checked, not assumed. Of 391 first-parent advances of `main`, 113 are merges.
Nearly all plain commits predate the local gate (armed `c007594`, 2026-08-10 12:43). Exactly **one**
landed after it: `05938cf`, 2026-08-10 17:47, a one-line edit to `docs/repo-map.md`, authored as
`sudomadhatter` — an identity shared by the operator and every agent, so it does not attribute.
**Zero** plain commits have advanced `main` since the server ruleset was armed (2026-08-12), which is
causal rather than lucky: `main_write_gate.py:145` refuses exactly that shape.

### Step 0.7 re-derivation

`main` did not move (`a0aceaf` = merge-base = `origin/main`); nothing this diff references was moved,
renamed or deleted; `merge-tree` clean, nothing absorbed. Sibling lane `chore/SCC-164-command-surface-family`
is live at `13906ec` and overlaps on two additive ledgers — `workflows_testing_SOP.md` and
`_artifacts/_main/INDEX.md` — touching neither the hooks nor the gate suite. **SCC-164 still lands first.**

## Your Actions

⛔ **This lane is FAIL and does not merge.** The merge row that stood here has been removed: the
feature cannot land on the real `main` (finding #1), so there is nothing to sign off yet.

Changes applied this review: findings #5 and #6, in thread. Everything else is blocked on the
direction decision below, because patching an allowlist for a lane that cannot reach `main` is work
in the wrong order.

- [ ] **Decide the direction on finding #1 — the lane cannot obtain the required status check.**
      Three routes, and they are materially different:
      **(a)** teach `main_write_gate.py` a *direct* mode — it runs the same allowlist server-side and
      accepts a single-parent commit whose paths are all prose, and the lane pushes a `gate/**`
      pre-flight ref first like the other two doors do. Keeps one bypass-free ruleset; most work.
      **(b)** make the fast lane a **one-commit auto-merged PR** instead of a direct push. The check
      already runs on `pull_request`, so nothing server-side changes, and the local `--direct` token
      work here becomes unnecessary. Least new law, but it is no longer a "direct push".
      **(c)** add a bypass actor to the ruleset. ⛔ I do not recommend this — it re-opens SCC-118,
      whose own test asserts the bypass list is empty.
- [ ] **Rule on finding #3 — the merge-arm hole, which exists on `main` right now.** A token naming a
      branch that does not resolve locally will land *any* single commit, including one that rewrites
      the gate. Closing it means adding a refusal to the **shipping** merge path, which is new blocking
      law and needs your words before I touch it. It is independent of this ticket and could be its own.
- [ ] **Re-decide the allowlist boundary** once #1 is settled, now that two of its premises are wrong:
      `docs/**` contains `install-git-hooks.sh` and `restore-env-master.sh` (finding #2), and the
      `sop_currency` backstop I offered you covers **only** `AGENTS.md` — `CLAUDE.md` and `GEMINI.md`
      have none (finding #4).

# Implementation Plan — SCC-183: Direct-to-Main Fast Lane for Non-Deployable Diffs

Let a single commit of **prose** — docs, resources, artifacts, top-level READMEs — go straight to
`main` with an approval token and a Jira key, skipping the branch, worktree, `--no-ff` merge and
close-out ceremony that a code change rightly pays for.

This is a **rebuild**. A prior implementation (branch `chore/SCC-183-direct-main-push`, commit
`3c66dee`) was reviewed **FAIL** and deleted on operator instruction. Its two proven exploits are the
first two RED tests here, so this lane cannot repeat them silently.

---

## Operator ruling (verbatim, 2026-08-16)

A new door to `main` is new law, so it carries the operator's own words rather than a derived
corollary:

> "yes delete then you take on this task. I do want it, the little changes to documents and updating
> things that dont touch any code are frustrating."

And, on the safety boundary, chosen from three options presented this turn — **"Prose only, law
excluded"**:

> `docs/**` · `_my_resources/**` · `_artifacts/**` · `*.md` at repo root — everything else refused,
> with `.agents/**`, `.githooks/**` and `tests/**` named as explicit hard refusals.

## User Review Required

> [!IMPORTANT]
> **This lane widens the road to `main`.** Until now two doors reached it, each dragging a full review
> ladder behind it. This adds a third with no review at all, so the *only* thing standing between it
> and an unreviewed change to `main` is the path allowlist. That allowlist is therefore **fail-closed**:
> a path is refused unless it is explicitly permitted. A denylist was tried in the deleted attempt and
> is what made it exploitable.

> [!NOTE]
> **One boundary call to confirm, since it cuts close to the line you drew.** Root-level `*.md`
> includes `AGENTS.md`, `CLAUDE.md` and `GEMINI.md` — which are arguably *law*, not prose, since
> `AGENTS.md` is the system's brain. They were listed as allowed in the option you picked, so this plan
> implements that. They are **not** unguarded: the armed `sop_currency` commit-msg gate already treats
> root `AGENTS.md` as a usage surface and refuses a commit that changes it without staging the SOP. Say
> the word and I will carve them out; the default here is what you approved.

---

## Why the prior attempt failed (this is the spec, in negative)

Both proven by real pushes at a real bare remote through the real `.githooks/pre-push` dispatch:

| # | Exploit | Root cause |
|---|---|---|
| H1 | `--direct` with **no `--key`** landed a commit carrying **no Jira key at all** | `--key` was optional, and the gate's key assertion was wrapped in `if [ -n "$t_key" ]` — absent key, check skipped |
| H3 | `--direct` landed a commit that **rewrote `pre-push-main-approval.sh` to approve everything** | the path check was a **denylist** of six product dirs; `.agents/` was not on it, so the gate permitted a commit that disables the gate |

The generalisation: **a denylist authored against a product repo's layout is vacuous in a governance
repo**, where the crown jewels are `.agents/` and `.githooks/`, not `backend/`.

---

## Checkable Acceptance Criteria

- [ ] **1. `--key` is mandatory in direct mode.** `mint-push-token.sh --direct` without `--key` exits
      non-zero and mints nothing. *Assertion:* `test_main_push_gate.py --case "direct: minter refuses --direct with no --key"`.
- [ ] **2. The gate refuses a keyless direct token even if one is hand-written.** A token carrying
      `mode=direct` and an empty `key=` is refused at push. *Assertion:* `--case "direct: gate refuses a token with an empty key"`.
- [ ] **3. The allowlist is fail-closed.** Every changed path must match the allowlist or the push is
      refused; a path on no list at all is **refused**, not permitted. *Assertion:* the refuse half of
      `--case "direct: allowlist"` — `.agents/`, `.githooks/`, `tests/`, a root non-`.md`, `backend/`,
      and a mixed commit where one good file rides with one bad one.
- [ ] **4. The gate cannot be used to rewrite the gate.** A direct push touching
      `.agents/scripts/git-hooks/pre-push-main-approval.sh` is refused. *Assertion:* `--case "direct: gate refuses a commit that rewrites the gate itself"`.
- [ ] **5. The allow half genuinely allows.** `docs/**`, nested `docs/a/b.md`, `_my_resources/**`,
      `_artifacts/**` and root `README.md` each land. *Assertion:* the allow half of `--case "direct: allowlist"`, remote sha advancing to the pushed sha.
- [ ] **6. One commit, never a merge, never a batch.** 2-ahead is refused at the minter *and* at the
      gate; a merge commit with a direct token is refused. *Assertion:* `--case "direct: shape"`.
- [ ] **7. The existing merge path is untouched.** The 73 pre-existing checks in
      `test_main_push_gate.py` still pass. *Assertion:* full-file run, `>= 73` passing, exit 0.
- [ ] **8. Policy and SOP record the third door.** `.agents/rules/git-policy.md` and
      `docs/_scc_sops_prds/workflows_testing_SOP.md` document the lane, its allowlist and its limits.
      *Assertion:* `workflow_lint.py --toolkit-only` exit 0, link+anchor sweep clean, `sop_currency.py` satisfied.
- [ ] **9. The minter pre-checks the allowlist**, so an honest mistake is caught before the operator's
      approval is spent. *Assertion:* `--case "direct: minter refuses a disallowed path before minting"`.
      *(Added by audit — traces the mint-time check that otherwise mapped to no acceptance item.)*
- [ ] **10. The gate fails CLOSED on every degenerate input**, never open: a missing/unsourceable
      allowlist predicate, a remote ref that does not yet exist (`remote_sha` all-zero), and an empty
      changed set are each **refused**. *Assertion:* `--case "direct: fail-closed"`.
      *(Added by audit — findings A1, A3.)*
- [ ] **11. No symlinks via the fast lane.** A commit introducing a symlink (git mode `120000`) or a
      gitlink is refused even at an allowed path. *Assertion:* `--case "direct: refuses a symlink at an allowed path"`.
      *(Added by audit — finding A4.)*

---

## Proposed Changes

### [ADD] `.agents/scripts/git-hooks/direct-push-allowlist.sh`

One shared predicate, `direct_push_path_allowed()`, sourced by **both** the minter and the gate.

*Why a third file rather than the same `case` block pasted twice:* a security predicate duplicated
across two files is a drift hazard, and drift in exactly this predicate is what the deleted attempt
died of. One definition, two callers, and the file itself sits under `.agents/` — so the fast lane
cannot edit its own allowlist.

```sh
direct_push_path_allowed() {
  case "$1" in
    .agents/*|.githooks/*|tests/*)        return 1 ;;  # law + gates, named explicitly
    docs/*|_my_resources/*|_artifacts/*)  return 0 ;;  # prose trees (case globs cross '/')
    */*)                                  return 1 ;;  # any other nested path
    *.md)                                 return 0 ;;  # root-level markdown only
    *)                                    return 1 ;;  # fail closed
  esac
}
```

Ordering is load-bearing: the explicit refusals are read before the allows, and `*/*` sweeps every
remaining nested path, so the trailing `*.md` can only match a root-level file.

### [MODIFY] `.agents/scripts/git-hooks/mint-push-token.sh`

- `--direct` / `--direct-push` sets `MODE=direct`; `--branch` defaults to `main`.
- **`--key` becomes REQUIRED in direct mode** (AC 1). Costs no friction: the armed `commit-msg` hook
  already requires a Jira key on every commit in this repo.
- Refuse at mint if HEAD is a merge commit, or not exactly 1 above `origin/main` — the existing
  first-parent check already covers the second; the merge check is new for direct mode.
- Refuse at mint if any changed path fails the allowlist, so an honest mistake is caught **before** the
  operator's approval is spent rather than after the token is discarded.
- Write `mode=direct` into the token.

### [MODIFY] `.agents/scripts/git-hooks/pre-push-main-approval.sh`

Source the allowlist; **fail closed if the source is missing or the function is undefined** (a missing
predicate must refuse, never skip). When `t_mode = direct`:

1. `parent1 == remote_sha` — exactly one commit.
2. no second parent — not a merge.
3. **`t_key` non-empty** — refuse outright if absent (AC 2). *Not* conditional.
4. commit message carries `t_key`.
5. **every changed path satisfies the allowlist** (AC 3, 4).
6. **the changed set is non-empty**, and **no entry is a symlink or gitlink** (AC 10, 11).

> ⚠️ **AUDIT FINDING A1 (Critical) — do not nest the direct block inside the existing
> `if [ "$remote_sha" != "$ZERO" ]` wrapper at [`pre-push-main-approval.sh:148`](.agents/scripts/git-hooks/pre-push-main-approval.sh#L148).**
> That wrapper guards the *merge* invariants, and skipping them when the remote ref does not exist is
> correct for a merge. Inheriting it for direct mode is **fail-open**: an all-zero `remote_sha` would
> skip the key check, the allowlist and the shape checks in one go, approving an arbitrary first push.
> The deleted attempt had exactly this shape. **Direct mode must handle `remote_sha == ZERO` itself,
> and REFUSE** — a direct token authorises advancing an existing `main` by one commit, never creating
> the ref.

> ⚠️ **AUDIT FINDING A2 (Important) — do not copy the dispatch's fail-open when sourcing.**
> [`.githooks/pre-push:73-77`](.githooks/pre-push#L73) handles a missing gate with
> *"push allowed, UNCHECKED"* and `exit 0`. That is a deliberate pre-existing choice for a worktree
> that predates the gate, and it is **not** the right pattern for the allowlist source: by the time the
> gate is running, direct mode has already been requested. A missing or unsourceable predicate must
> **refuse the push**, and AC 10 tests that by running the gate with the file removed.

When `t_mode != direct`, the existing merge invariants run byte-identical.

Path iteration reads one path per line (`while IFS= read -r f`) so filenames with spaces are handled;
git quotes control characters, and a quoted path matches no allow rule and is therefore refused —
fail-closed by construction.

⛔ **The comment block explaining SCC-71/SCC-77 stays.** The deleted attempt stripped it; that
provenance is why the check exists and is not incidental commentary.

### [MODIFY] `.agents/scripts/tests/test_main_push_gate.py`

New `c.block(...)` sections — `direct: minter`, `direct: shape`, `direct: allowlist`, `direct: gate
refuses a commit that rewrites the gate itself` — covering **both halves**: every refuse case above,
and the five allow cases. Harness gains the new allowlist file in its copy set.

### [MODIFY] `.agents/rules/git-policy.md` · `docs/_scc_sops_prds/workflows_testing_SOP.md`

Document the third door, the allowlist, the operator ruling, and the explicit statement that it
carries **no review ladder** — which is why its scope is prose only.

---

## Deliberately NOT in this lane

- **Wiring `--direct` into `/smh-quick-fix`.** That file is owned by the live SCC-164 lane (69 files,
  mid-flight). Editing it here guarantees a conflict on the door command itself. This lane ships the
  mechanism and documents the manual three-step procedure; the command wiring is a follow-on once
  SCC-164 lands. **Deferred against a named blocker, not dropped.**
- **AVCH-63.** The port into `Projects/AGY_AVIATIONCHAT` is its own ticket in its own repo, per the
  one-ticket-per-repo rule. It runs after this lands, and its allowlist maps to AVCH's layout —
  where `Dockerfile`, `.firebaserc` and `.gcloudignore` sit at **root**, which a denylist of
  directories would have missed entirely.

## Landing order

**SCC-164 lands first.** It is the only overlap (`workflows_testing_SOP.md`) and it is a 69-file
rewrite of the command surface against my 5-file additive change; re-applying one SOP section onto a
rewritten SOP is far cheaper than the reverse. If this lane lands first, SCC-164 absorbs a conflict in
a file it is already rewriting wholesale.

## Verification Plan

```bash
python3 .agents/scripts/tests/test_main_push_gate.py          # both halves, full file
python3 .agents/scripts/tests/run_all.py                      # through gate_receipt.py
python3 .agents/scripts/workflow_lint.py --toolkit-only
python3 .agents/scripts/sop_currency.py --paths <changed> --message "<subject>"
```

Plus a **mutation sweep** drawn from the shipped code — not from the cases — over the allowlist
predicate and the direct-mode checks: invert each `return 0`/`return 1`, delete each refuse
branch, and name the case that must kill each mutant. A survivor is a finding.

---

## Self-Audit (2026-08-16)

**Mode:** PRE-WORK. **Level:** Full — the plan touches a gate, a hook, a rule, a script that other
scripts source, and the SOP. **Lane:** `chore/SCC-183-direct-main-fastlane`, no deployable path in the
change set, so `/smh-close-task-merge-tree` is the correct close-out.

### Phases walked

- **Phase 0 — scope & traceability.** 11 acceptance items, each naming the command that proves it.
  Both directions checked: every item maps to a step, and one step (the minter's mint-time path
  pre-check) traced to **no** item — flagged as untested scope and resolved by adding AC 9 rather than
  cutting it, because without it an honest mistake burns the operator's approval words. Lane check:
  no `backend/ frontend/ firebase/ functions/ mobile/ .github/` path in the set. ✅
- **Phase 1 — blast radius.** The predicate was executed, not eyeballed: 19/19 paths classified
  correctly, including `.Agents/x.sh` (macOS APFS is case-insensitive; git is not, and the glob is
  case-sensitive so it falls through to the fail-closed arm) and `Projects/AGY/backend/x.py`. Callers
  of the two scripts: `.githooks/pre-push:71` and the two door commands
  (`cicd-push-e2e.md:93`, `smh-close-task-merge-tree.md:332`) — all pass `--branch`, none pass
  `--direct`, so the merge path is unaffected. `sop_currency.py:60` pins exactly one SOP doc and it is
  in the change set. No rule is renamed, so `_RULE_POINTERS` is untouched. No command file changes, so
  door parity across the four platforms is not in play.
- **Phase 2 — over-engineering.** One new file. Justified: it is a *security predicate with two
  callers*, and a duplicated copy is the drift hazard that killed the prior attempt. Rejected as
  unjustified: a `--allow-path` override flag (no acceptance item needs it, and an override on a
  fail-closed allowlist is the allowlist deleted), and a config file for the path list (N=1).
- **Phase 3 — pre-mortem.** Both machines: pure POSIX `sh`, no bashism, no `python`/`python3` split in
  the hook path. Fresh clone: `core.hooksPath` is per-machine and this ships no new arming marker, so
  the existing `MAIN-PUSH-ENFORCE` posture is unchanged. Escape hatch: `git push --no-verify`, already
  documented and already tested. Empty input: **was** a pass — now AC 10. Rollback: a plain revert; the
  lane creates no ticket transition and no history rewrite, so nothing here is irreversible.

### Findings

| Item | Severity | Failure scenario | Disposition |
|---|---|---|---|
| `pre-push-main-approval.sh:148` — `remote_sha != ZERO` wrapper | **Critical** | Direct block nested inside it ⇒ an all-zero remote sha skips key check, allowlist and shape checks; arbitrary content approved | Direct mode handles ZERO itself and **refuses**. Inline finding A1 + AC 10 |
| Sourcing the shared predicate | **Important** | Copying `.githooks/pre-push`'s "not present ⇒ exit 0" pattern makes a deleted allowlist file a full bypass | Fail closed; AC 10 runs the gate with the file removed. Inline finding A2 |
| Empty changed set | Moderate | A commit changing nothing produces no disallowed path ⇒ reads as pass (`tests-must-gate-for-real` Rule 1) | Refuse an empty set. AC 10 |
| Symlink at an allowed path | Moderate | `docs/x -> ../.agents/…` reports as `docs/x` and lands unreviewed. Does **not** rewrite the gate (git stores the link, not the target) so it is not the H3 escape — but this lane has no review ladder, so it must be mechanical | Refuse mode `120000`/`160000`. AC 11 |
| `grep -q "$t_key"` | Minor | `$t_key` is an unanchored BRE, so a metacharacter in a key behaves oddly | Use `case "$msg" in *"$t_key"*)` — no regex. Substring nuance (`SCC-18` inside `SCC-183`) accepted: the key comes from the operator, not an attacker |
| Mint-time path pre-check | Minor | Traced to no acceptance item ⇒ shipped untested | Kept, and AC 9 added to test it |

### Landing-order dependency

**SCC-164 (`chore/SCC-164-command-surface-family`, 69 files, live) lands first.** Sole overlap:
`docs/_scc_sops_prds/workflows_testing_SOP.md`. It also owns `.agents/commands/smh-quick-fix.md`,
which is why wiring `--direct` into that command is explicitly out of scope here. If the order
reverses, SCC-164 absorbs a conflict in a file it is rewriting wholesale — recoverable, but wasteful.

### Four gates

- **Verification strategy present?** Yes — every one of the 11 items names the `--case` label or the
  command that proves it, and the mutation sweep is specified as drawn from the code, not the cases.
- **Anything irreversible?** No. No delete, no rename, no history rewrite, no Jira transition in this
  lane; the ticket is already `In Progress`.
- **Any step vague enough to be guessed?** The allowlist was the one candidate; it is now pinned as
  literal shipped code with an executed truth table, so there is nothing left to interpret.
- **Convention fit?** Artifacts in `_artifacts/_main/<date>_<slug>/`, POSIX `sh` to match the existing
  hooks, SOP staged in the same commit, provenance comments preserved.

Audit verdict: GO

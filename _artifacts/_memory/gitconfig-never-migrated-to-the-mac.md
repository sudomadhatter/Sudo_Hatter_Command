---
name: gitconfig-never-migrated-to-the-mac
description: "~/.gitconfig does not travel — the ten documented settings were Windows-only until applied on the Mac 2026-08-07; autoSetupRemote can't fix branches pushed before it."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8bc78088-0a6e-4b75-b4eb-edc817c5fe79
  modified: 2026-08-07T12:55:53.629Z
---

`docs/_scc_sops_prds/git_walkthrough_settings.md` documents ten global git settings and its
frontmatter says *"machine-wide … applies to every repo on this machine."* That was written on the
**Windows** box (2026-06-24). `~/.gitconfig` is **per-machine and does not travel** — verified
2026-08-07 that **none of the ten are set on the Mac**; `/Users/sudohatter/.gitconfig` holds only
`user.name`/`user.email` and the `gh` credential helper.

So on the Mac, git has been running **stock defaults** the whole time:

- `git pull` on a diverged branch **silently creates a merge commit** (no `pull.ff=only` stop)
- deleted remote branches pile up as stale `origin/*` refs (no `fetch.prune`) — costly under
  [[git-branch-model-standard]], where every epic and story branch is deleted after it merges
- a new branch's first push needs `--set-upstream` (no `push.autoSetupRemote`); an explicit
  `git push origin <branch>` succeeds but leaves **no upstream**, so `rev-list HEAD...@{u}` fails
  with *"no upstream configured"* — that error is this gap, not a broken push
- no `rerere`, no `zdiff3` conflict markers

**Why:** the doc reads like a record of live state, so a Mac session trusts settings that aren't there.
The `0 0` ahead/behind verification habit silently degrades to an error on any freshly-pushed branch.

**RESOLVED 2026-08-07** — Daniel approved and the appendix block was applied on the Mac; all ten now
read back set, and both machines match. The doc carries the dated status under §0.

**How to apply:** on any *next* machine, never infer git config from that doc — run
`git config --global --get <key>` (silent + exit 1 = not set) before trusting it. **The lasting trap:
`push.autoSetupRemote` only binds an upstream on a branch's FIRST push** — anything pushed before the
setting existed still has none, so `git status` shows no ahead/behind and the `0 0` verification habit
([[commit-and-push-are-one-action]]) errors out instead of failing loudly. Repair with
`git branch --set-upstream-to=origin/<branch>`. Same failure shape as
[[zshrc-is-invisible-to-automation]] and [[windows-authored-code-hides-posix-bugs]]: Windows-era setup
assumed to be universal. Machine-portable secrets/config live in [[env-migration-kit]].

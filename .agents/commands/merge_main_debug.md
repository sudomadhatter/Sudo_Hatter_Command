---
description: Approve & merge the active PR into main_debug — mark it ready, verify it's mergeable and not red, then squash-merge. main_debug ONLY (never main). Invoking it IS the per-action merge approval.
---

# /merge_main_debug — Approve & merge the active PR into `main_debug`

**Invoking this command IS the owner's explicit, per-action approval** to merge into their branch.
It merges exactly one PR into `main_debug`, with guards. If any guard fails, **STOP and report**.
Requires the GitHub MCP tools (`pull_request_read`, `update_pull_request`, `merge_pull_request`);
if absent, say so and hand over the equivalent step.

**Optional argument** — a PR number. If omitted, resolve the PR for the current `claude/*` branch: $ARGUMENTS

## Steps
1. **Resolve the PR.** Use the given number, else the open PR whose head is the current branch
   (`git rev-parse --abbrev-ref HEAD`). Zero/multiple matches -> STOP and list.
2. **Guard the base — `main_debug` ONLY.** If the PR's base is not `main_debug` (e.g. `main`),
   **STOP and refuse** — `main` promotion is a deliberate manual decision.
3. **Verify mergeable + not red** (`pull_request_read` -> `get_status`/`get_check_runs`):
   conflicted/`dirty`/`blocked` -> STOP; any check failing or in-progress -> STOP.
   No checks at all is fine (PRs into `main_debug` don't trigger the gate).
4. **Mark ready.** If draft, un-draft (`update_pull_request` -> `draft:false`).
5. **Merge.** Squash-merge (`merge_pull_request` -> `merge_method:"squash"`,
   `commit_title:"<PR title> (#<num>)"`). This tool is gated in settings — approve the prompt.
6. **Report + cleanup.** Confirm merge SHA; list the now-stale `claude/*` branch for deletion;
   offer to `git pull origin main_debug` locally.

## Never
- Never merge into `main` or any base other than `main_debug`.
- Never merge a red/conflicted/in-progress PR — STOP and report.
- Never treat one invocation as approval for a second merge.

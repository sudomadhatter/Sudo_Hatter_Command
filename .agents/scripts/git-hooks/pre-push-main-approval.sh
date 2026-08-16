#!/bin/sh
# pre-push-main-approval — nothing reaches `main` without a single-use approval token.
#
# The law: .agents/rules/git-policy.md § "The write gate". Two commands mint a token, plus the
# operator's direct word. This file is the machine half of that table and nothing more.
#
#   /cicd-push-e2e              epic/<KEY>-<slug>  -> main   (full gate + e2e)
#   /smh-close-task-merge-tree  chore/<KEY>-<slug> -> main   (preflight + the lane's gate)
#
# /cicd-update-sprint-memory is the EPIC-BRANCH key and is deliberately NOT here. Its own body
# says "main is untouched" — see git-policy.md's permission table.
#
# ─── Why this is a git hook and not a Claude hook ──────────────────────────────────────────
# It ran nowhere for weeks. `.claude/settings.json` invoked the PreToolUse gate as
# `powershell -Command "python ..."`, and the Mac has NEITHER binary — it exited 127, silently,
# every time. Six merges reached main on one sign-off because of it (2026-08-09, SCC-71/SCC-77).
# A git hook is the only layer both machines, all four agent platforms, and the operator's own
# terminal share. So this file is POSIX sh with no interpreter probe and no Python: the gate must
# not depend on the class of thing that broke it.
#
# ─── What this does and does not buy ───────────────────────────────────────────────────────
# An agent can write files, so an agent can write a token. This is NOT a security boundary
# against a determined agent, and it is not sold as one. It converts a silent violation into a
# deliberate, traceable one, and it kills the real SCC-71 failure mode: a close-out command whose
# body stays in context and still reads exactly as valid on task six as it did on task one.
#
# Kill switch:      .agents/scripts/git-hooks/DISABLE     (the file every gate here honors)
# Disarm entirely:  delete .agents/scripts/git-hooks/MAIN-PUSH-ENFORCE
# Bypass once:      git push --no-verify

PROTECTED_REF="refs/heads/main"
TTL_SECONDS=1800          # 30 minutes — a sign-off is for the merge in front of you, not the session

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
cd "$REPO_ROOT" || exit 0

[ -f .agents/scripts/git-hooks/DISABLE ] && exit 0
[ -f .agents/scripts/git-hooks/MAIN-PUSH-ENFORCE ] || exit 0

# The token lives in the COMMON git dir, never the per-worktree one: every lane on this machine
# shares a single token, so a sign-off cannot be minted in one worktree and silently spent in
# another. Under .git/, so it never travels with a clone and can never land in a commit.
GIT_COMMON=$(git rev-parse --git-common-dir 2>/dev/null) || exit 0
case "$GIT_COMMON" in
  /*) : ;;                                  # already absolute
  *)  GIT_COMMON="$REPO_ROOT/$GIT_COMMON" ;;  # relative to the toplevel — resolve it
esac
TOKEN="$GIT_COMMON/main-push-approval"

ZERO="0000000000000000000000000000000000000000"

refuse() {
  echo ""
  echo "  ⛔ PUSH TO main REFUSED — $1"
  echo ""
  echo "     main is reached exactly three ways (.agents/rules/git-policy.md):"
  echo "       /cicd-push-e2e               an epic branch, after the full gate + /cicd-e2e green"
  echo "       /smh-close-task-merge-tree   a chore branch, after the preflight + the lane's gate"
  echo "       the operator's direct in-the-moment approval"
  echo ""
  echo "     A sign-off authorises ONE merge and never carries forward (SCC-71)."
  echo "     Bypass once: git push --no-verify"
  echo ""
  exit 1
}

# stdin: <local ref> <local sha> <remote ref> <remote sha>, one line per ref being pushed.
# Whole-token match on the remote ref, so `epic/main-fix` and `chore/main-gate` never trip this.
while read -r local_ref local_sha remote_ref remote_sha; do
  [ "$remote_ref" = "$PROTECTED_REF" ] || continue

  if [ "$local_sha" = "$ZERO" ]; then
    refuse "this would DELETE main. There is no approval path for that."
  fi

  [ -f "$TOKEN" ] || refuse "no approval token."

  # Parse the token. Unknown keys are ignored so the format can grow without breaking old hooks.
  t_branch=""; t_tip=""; t_command=""; t_key=""; t_mode=""; t_minted=""; t_approval=""
  while IFS='=' read -r k v; do
    case "$k" in
      branch)   t_branch=$v   ;;
      tip)      t_tip=$v      ;;
      command)  t_command=$v  ;;
      key)      t_key=$v      ;;
      mode)     t_mode=$v     ;;
      minted)   t_minted=$v   ;;
      approval) t_approval=$v ;;
    esac
  done < "$TOKEN"

  # Every refusal below CONSUMES the token. A sign-off that failed its own checks is spent —
  # otherwise a stale token sits there inviting a retry until one push happens to match it.
  if [ -z "$t_tip" ] || [ -z "$t_minted" ]; then
    rm -f "$TOKEN"
    refuse "the approval token is malformed (no tip / no timestamp). It has been discarded."
  fi

  # ⛔ NO APPROVAL RECORD, NO PUSH (SCC-37). The minter refuses to write a token without the
  # operator's words, so a WELL-FORMED token lacking them was written by hand or by a pre-SCC-37
  # flow — either way it carries a sign-off nobody can point at. After the malformed check on
  # purpose: garbage is reported as garbage, not as a missing approval. Consumed like every refusal.
  if [ -z "$t_approval" ]; then
    rm -f "$TOKEN"
    refuse "the token carries no operator-approval record.
        A main merge needs the operator's explicit words for THIS merge, recorded at mint time
        (mint-push-token.sh --operator-approval '<their exact words>', or typed at a terminal).
        Ticket-status permission is never merge permission. Token discarded."
  fi

  # ⛔ VALIDATE BEFORE ARITHMETIC. `$(( ))` in POSIX sh recursively expands its operands, so a
  # token containing `minted=z[$(...)]` EXECUTES that command, and a token containing `minted=now`
  # resolves to this script's own `now` variable — age 0, forever, TTL bypassed. Both were live
  # (SCC-77 review). Digits only, checked as a string, before the value goes anywhere near `$(( ))`.
  case "$t_minted" in
    ''|*[!0-9]*)
      rm -f "$TOKEN"
      refuse "the approval token's timestamp is not a number. It has been discarded." ;;
  esac

  now=$(date +%s)
  age=$((now - t_minted))
  if [ "$age" -lt 0 ] || [ "$age" -gt "$TTL_SECONDS" ]; then
    rm -f "$TOKEN"
    refuse "the approval token is stale — minted ${age}s ago, limit ${TTL_SECONDS}s. It has been discarded."
  fi

  # The token names the sha it was minted for. A different sha means work appeared AFTER the
  # sign-off, so no gate has seen it.
  if [ "$t_tip" != "$local_sha" ]; then
    rm -f "$TOKEN"
    refuse "the approval token is for $t_tip but this push carries $local_sha.
        Commits appeared after the sign-off, so no gate has seen them. Token discarded."
  fi

  if [ "$t_mode" = "direct" ]; then
    # ══ SCC-183 — THE DIRECT-TO-MAIN FAST LANE, AND WHY IT IS SHAPED LIKE THIS ═══════════
    #
    # A third door to main, and the ONLY one with no review ladder behind it. The path
    # allowlist is what stands in for that review, so it is sourced rather than inlined
    # (`mint-push-token.sh` applies the identical predicate, and two copies drift) and every
    # degenerate input below REFUSES rather than falling through.
    #
    # A first cut of this feature was reviewed FAIL and deleted (commit 3c66dee). Its two
    # proven exploits are marked H1 and H3 at the checks that now stop them.
    ALLOWLIST="$(dirname "$0")/direct-push-allowlist.sh"
    if [ ! -f "$ALLOWLIST" ]; then
      rm -f "$TOKEN"
      refuse "direct mode was requested but the path allowlist is missing.
        expected: $ALLOWLIST
        A missing predicate REFUSES — it never falls through to allow. The dispatcher's own
        'not present, push allowed UNCHECKED' is for a worktree that predates the gate; by
        here, direct mode has been ASKED for. Token discarded."
    fi
    . "$ALLOWLIST"
    if ! command -v direct_push_path_allowed >/dev/null 2>&1; then
      rm -f "$TOKEN"
      refuse "$ALLOWLIST defines no direct_push_path_allowed(). Token discarded."
    fi

    # ⛔ DELIBERATELY NOT NESTED IN THE `remote_sha != ZERO` GUARD THE MERGE PATH USES.
    # That guard is right for a merge — there are no merge invariants to check against a ref
    # that does not exist yet. Inheriting it here would skip the key check, the allowlist AND
    # the shape checks in one go, for a push that creates main out of nothing. A direct token
    # authorises advancing an EXISTING main by one commit; it never creates the ref.
    if [ "$remote_sha" = "$ZERO" ]; then
      rm -f "$TOKEN"
      refuse "a direct token cannot CREATE main — there is no remote main to advance.
        Token discarded."
    fi

    # ⭐ H1 — THE KEY ASSERTION MUST FIRE ON ABSENCE.
    # The deleted cut wrapped this in `if [ -n "$t_key" ]`, so minting without --key did not
    # fail the check, it DELETED the check, and a commit carrying no ticket reference of any
    # kind landed on main. Proven with a real push before this rebuild.
    if [ -z "$t_key" ]; then
      rm -f "$TOKEN"
      refuse "the direct token carries no Jira key.
        Direct mode requires --key: an unreviewed commit on main must at least be traceable.
        Token discarded."
    fi

    parent1=$(git rev-parse --verify --quiet "${local_sha}^1") || parent1=""
    if [ "$parent1" != "$remote_sha" ]; then
      rm -f "$TOKEN"
      refuse "this direct push does not advance main by exactly one commit.
        remote main is at $remote_sha
        the pushed commit's first parent is ${parent1:-<none>}
        One sign-off authorises ONE commit (SCC-71). Token discarded."
    fi

    if git rev-parse --verify --quiet "${local_sha}^2" >/dev/null 2>&1; then
      rm -f "$TOKEN"
      refuse "this direct push carries a MERGE commit.
        Direct mode authorises one plain commit; a merge lands through the merge path, which
        checks the branch the token names. Token discarded."
    fi

    # `case`, not `grep`: $t_key in a grep pattern is a REGULAR EXPRESSION, so a key carrying
    # a metacharacter matches something other than itself.
    commit_msg=$(git log -1 --format=%B "$local_sha")
    case "$commit_msg" in
      *"$t_key"*) : ;;
      *) rm -f "$TOKEN"
         refuse "the commit message does not carry the approved Jira key '$t_key'.
        Token discarded." ;;
    esac

    # ⭐ H3 — THE ALLOWLIST. The deleted cut used a DENYLIST of six product directories, five
    # of which do not exist in this repo, so `.agents/` was permitted: a `--direct` push
    # carrying a rewritten `pre-push-main-approval.sh` was ACCEPTED and landed. The gate
    # approved the commit that disables the gate.
    #
    # `--raw` rather than `--name-only` because the MODE is load-bearing too: a symlink at an
    # allowed path (`docs/x -> ../.agents/…`) reads as `docs/x` to any name-only check.
    TAB=$(printf '\t')
    raw=$(git diff-tree -r --no-commit-id --raw "$remote_sha" "$local_sha")
    if [ -z "$raw" ]; then
      rm -f "$TOKEN"
      refuse "this direct push changes nothing.
        An empty change set satisfies 'every path is allowed' vacuously. Token discarded."
    fi

    # Collected through a command substitution: a `while` on the right of a pipe runs in a
    # SUBSHELL, so a flag set inside it would be lost by the time this `if` reads it.
    # ⛔ `if`, NOT `case`, and that is not a style choice. macOS `/bin/sh` is bash 3.2, whose
    # parser cannot handle a `case` statement inside `$( )` — it dies on the first `;;` with
    # "syntax error near unexpected token". `dash` and `zsh` both accept it, so this reads as
    # correct everywhere except the machine the operator actually runs. A called FUNCTION is
    # fine (its body is parsed outside the substitution), which is why the allowlist below can
    # keep its own `case`; only inline `case` text inside `$( )` trips it.
    bad=$(printf '%s\n' "$raw" | while IFS= read -r line; do
      [ -n "$line" ] || continue
      dstmode=$(printf '%s' "$line" | cut -c9-14)   # :<srcmode> <dstmode> ... — cols 9-14
      path=${line#*"$TAB"}
      if [ "$dstmode" = "120000" ]; then
        printf '%s\n' "       $path   (symlink)"
      elif [ "$dstmode" = "160000" ]; then
        printf '%s\n' "       $path   (submodule)"
      elif ! direct_push_path_allowed "$path"; then
        printf '%s\n' "       $path"
      fi
    done)
    if [ -n "$bad" ]; then
      rm -f "$TOKEN"
      refuse "direct mode is for prose, and this commit touches paths that are not:
$bad
        Allowed: docs/** · _my_resources/** · _artifacts/** · *.md at the repo root.
        Everything else — .agents/, .githooks/, tests/, code, config — lands through
        /smh-close-task-merge-tree or /cicd-push-e2e, which run a review first.
        Token discarded."
    fi
  else
    # ⭐⭐ THE CHECK THAT ACTUALLY ENFORCES ONE-SIGN-OFF-ONE-MERGE.
    #
    # The sha check above is NOT sufficient and the first cut of this gate wrongly claimed it was.
    # A token authorises a PUSH; what SCC-71 needs gated is a MERGE. Merge six branches into main
    # locally, then mint once, then push once — `t_tip == local_sha` holds the whole way and six
    # merges land on one approval, which is the exact failure this gate exists to stop. Reproduced
    # during the SCC-77 review: one token, six merges on the remote, the approval line naming one
    # of them.
    #
    # The invariant that actually holds: `main` advances by EXACTLY ONE merge commit sitting
    # directly on top of what the remote already has. So the pushed commit's FIRST parent must be
    # the remote's current tip. Batching breaks it (the previous merge sits in between), and so
    # does a force-push rewind (the rewound tip is not a child of the remote's).
    if [ "$remote_sha" != "$ZERO" ]; then
      parent1=$(git rev-parse --verify --quiet "${local_sha}^1") || parent1=""
      if [ "$parent1" != "$remote_sha" ]; then
        rm -f "$TOKEN"
        refuse "this push does not advance main by exactly one merge.
        remote main is at $remote_sha
        the pushed commit's first parent is ${parent1:-<none>}
        One sign-off authorises ONE merge (SCC-71). Batching several merges into a single push,
        or rewinding main and force-pushing, both land here. Token discarded."
      fi

      # And the merge must be OF the branch the token names — otherwise the token is a blank cheque
      # that any merge can spend.
      if [ -n "$t_branch" ]; then
        merged=$(git rev-parse --verify --quiet "${local_sha}^2") || merged=""
        claimed=$(git rev-parse --verify --quiet "refs/heads/$t_branch") || claimed=""
        if [ -n "$claimed" ] && [ "$merged" != "$claimed" ]; then
          rm -f "$TOKEN"
          refuse "the token authorises landing '$t_branch' ($claimed),
        but this merge's second parent is ${merged:-<none> (not a merge commit)}.
        A sign-off is for one named branch, not for whatever happens to be on main. Token discarded."
        fi
      fi
    fi
  fi

  # Consumed BEFORE the push. There is no post-push hook, so this is the only available order —
  # and it fails in the safe direction: a rejected push (remote moved) needs a fresh sign-off,
  # which is correct, because re-running the door command re-runs the preflight against the
  # remote that moved.
  rm -f "$TOKEN"
  echo "  ✅ main push approved — ${t_command:-<unrecorded>} · ${t_key:-<no key>} · ${t_branch:-<no branch>} @ $local_sha"
  echo "     AUTHORIZED BY OPERATOR: \"$t_approval\""
  echo "     Token consumed. The next merge needs its own sign-off."
done

exit 0

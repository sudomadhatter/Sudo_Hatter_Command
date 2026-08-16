#!/bin/sh
# mint-push-token — write the single-use approval token that pre-push-main-approval.sh spends.
#
# Called by the two commands that are allowed to land on `main`, at their sign-off step, AFTER the
# merge commit exists and immediately BEFORE the push:
#
#   /smh-close-task-merge-tree   Step 3
#   /cicd-push-e2e               Step 4
#
# Usage:
#   sh .agents/scripts/git-hooks/mint-push-token.sh \
#        --command /smh-close-task-merge-tree --branch chore/SCC-77-main-write-gate --key SCC-77
#
# POSIX sh, no Python, by the same rule as the gate itself: nothing in this path may depend on an
# interpreter that exists on one machine and not the other. That defect is what SCC-77 is fixing.
#
# The token records the sha it was minted for. Anything committed after this runs will be REFUSED
# at the push — which is the point. Mint last, then push.

usage() {
  echo "usage: mint-push-token.sh --command <cmd> --branch <branch> [--key <JIRA-KEY>] --operator-approval '<the operator's verbatim words>'" >&2
  exit 2
}

# `shift 2` with fewer than 2 args left returns non-zero WITHOUT shifting, so the loop spins
# forever. A trailing `--key` with its value dropped (both door commands template exactly that
# shape) hung the minter indefinitely — after the merge, before the push. Guard every shift.
need() { [ $# -ge 2 ] || { echo "mint-push-token: '$1' needs a value." >&2; usage; }; }

CMD=""; BRANCH=""; KEY=""; APPROVAL=""; MODE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --command)           need "$@"; CMD="$2";      shift 2 ;;
    --branch)            need "$@"; BRANCH="$2";   shift 2 ;;
    --key)               need "$@"; KEY="$2";      shift 2 ;;
    --operator-approval) need "$@"; APPROVAL="$2"; shift 2 ;;
    --direct|--direct-push) MODE="direct";         shift 1 ;;
    -h|--help) usage ;;
    *) echo "mint-push-token: unknown argument '$1'" >&2; usage ;;
  esac
done

[ -n "$CMD" ] || { echo "mint-push-token: --command is required — the token records WHICH door authorised this." >&2; exit 2; }
if [ "$MODE" = "direct" ]; then
  # ⭐ SCC-183 H1: --key is REQUIRED in direct mode, and this is not belt-and-braces.
  # The deleted first cut left it optional, and the gate's key assertion was conditional on
  # the key being present — so omitting it did not fail the check, it removed it, and a
  # commit with no ticket reference landed on main. The gate now refuses a keyless token on
  # its own; this makes the failure land at MINT, where the message can still name the fix.
  # It costs nothing: the armed commit-msg hook already requires a key on every commit here.
  [ -n "$KEY" ] || { echo "mint-push-token: --key is required in --direct mode." >&2
    echo "  A direct push skips the review ladder entirely, so the one thing it must never" >&2
    echo "  skip is being traceable to a ticket." >&2; exit 2; }
  [ -n "$BRANCH" ] || BRANCH="main"
else
  [ -n "$BRANCH" ] || { echo "mint-push-token: --branch is required — the token records WHAT is being landed." >&2; exit 2; }
fi

# ⛔ THE APPROVAL IS THE OPERATOR'S WORDS, NOT THE AGENT'S INFERENCE (SCC-37, 2026-08-14).
# The SCC-71 failure recurred in a new coat: an agent read "you can move the ticket to done" as
# merge authorization — ticket-status permission taken as a main-merge sign-off, standing context
# read as consent. The command doc is the primary fix; this is the machine half: a token cannot be
# minted without APPROVAL EVIDENCE, and the evidence is the operator's own words for THIS merge.
#
#   - At a terminal (a human, by definition): prompted to type the branch's ticket key — a
#     conscious, per-merge yes. No flag needed.
#   - Non-interactive (every agent shell): --operator-approval '<verbatim quote>' is REQUIRED.
#     The quote is recorded in the token and PRINTED BACK by the push gate, so what the agent
#     claims authorised the merge is visible at mint time, at push time, and in the transcript.
#     "when you finish you can move it to done" printed as a merge authorization exposes itself.
#
# Same honesty note as the gate's own header: an agent can type any quote, so this is not a lock
# against fabrication — it converts a silent inference into a visible, falsifiable claim, which is
# exactly what the silent version could never do.
if [ -z "$APPROVAL" ]; then
  if [ -t 0 ]; then
    printf "  This mints a ONE-merge approval for '%s' -> main.\n" "$BRANCH"
    printf "  Type the ticket key (%s) to approve: " "${KEY:-the branch key}"
    read -r typed
    if [ -n "$KEY" ] && [ "$typed" != "$KEY" ]; then
      echo "mint-push-token: '$typed' does not match '$KEY' — not approved, nothing minted." >&2
      exit 2
    fi
    [ -n "$typed" ] || { echo "mint-push-token: empty response — not approved, nothing minted." >&2; exit 2; }
    APPROVAL="typed at terminal: $typed"
  else
    echo "mint-push-token: REFUSED — no operator approval." >&2
    echo "  A main merge needs the operator's explicit, this-turn approval — their words, not" >&2
    echo "  your reading of them. Ticket-status permission is NEVER merge permission." >&2
    echo "  If you do not have an unambiguous merge yes from this turn, STOP and ask; when" >&2
    echo "  you have it, pass it verbatim:" >&2
    echo "    --operator-approval '<the operator exact words>'" >&2
    exit 2
  fi
fi
# One line in the token, whatever was pasted.
APPROVAL=$(printf '%s' "$APPROVAL" | tr '\n' ' ')

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || {
  echo "mint-push-token: not inside a git repository." >&2; exit 2; }
cd "$REPO_ROOT" || exit 2

# The token authorises a push of THIS commit to main, so HEAD must already be the merge commit on
# main. Minting from anywhere else records a tip the push will not carry, and the gate would refuse
# it — better to fail here, with a reason, than at the push with a mismatch.
HEAD_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
if [ "$HEAD_BRANCH" != "main" ]; then
  echo "mint-push-token: HEAD is '$HEAD_BRANCH', not 'main'." >&2
  echo "  Mint AFTER 'git merge $BRANCH --no-ff' and BEFORE 'git push origin main'." >&2
  exit 2
fi

TIP=$(git rev-parse HEAD) || exit 2

# ⛔ Refuse to mint for a BATCH. One sign-off authorises one merge, so HEAD must be exactly one
# merge ahead of what the remote has — the same invariant the gate enforces at push time, caught
# here where the error message can still name the fix. Without this, merging six branches and then
# minting once produced six merges on one approval (SCC-77 review, reproduced).
REMOTE=$(git rev-parse --verify --quiet refs/remotes/origin/main) || REMOTE=""
if [ -n "$REMOTE" ]; then
  PARENT1=$(git rev-parse --verify --quiet "${TIP}^1") || PARENT1=""
  if [ "$PARENT1" != "$REMOTE" ]; then
    if [ "$MODE" = "direct" ]; then
      echo "mint-push-token: HEAD does not sit exactly one commit above origin/main." >&2
    else
      echo "mint-push-token: HEAD does not sit exactly one merge above origin/main." >&2
    fi
    echo "  origin/main:               $REMOTE" >&2
    echo "  HEAD's first parent:       ${PARENT1:-<none>}" >&2
    echo "  One sign-off authorises ONE action (SCC-71). If several are stacked here, land" >&2
    echo "  them one at a time - each with its own invocation of the close-out command." >&2
    exit 2
  fi
fi

# ── SCC-183: everything below is direct mode only ────────────────────────────────────────
# The gate re-checks every one of these and IS the authority. They are here because failing
# at the mint is failing before the operator's approval has been spent: a token refused at the
# push is discarded, and recovering costs another round of asking for their words.
if [ "$MODE" = "direct" ]; then
  if git rev-parse --verify --quiet "${TIP}^2" >/dev/null 2>&1; then
    echo "mint-push-token: HEAD is a MERGE commit, so --direct does not apply." >&2
    echo "  Mint without --direct and let the merge path check the branch you are landing." >&2
    exit 2
  fi

  # Same predicate the gate applies, sourced from the same file — never a second copy.
  ALLOWLIST="$(dirname "$0")/direct-push-allowlist.sh"
  if [ ! -f "$ALLOWLIST" ]; then
    echo "mint-push-token: --direct needs $ALLOWLIST, which is missing." >&2
    exit 2
  fi
  . "$ALLOWLIST"

  if [ -n "$REMOTE" ]; then
    TAB=$(printf '\t')
    # `if`, not `case`: bash 3.2 (macOS /bin/sh) cannot parse `case` inside `$( )`.
    # See the same note in pre-push-main-approval.sh — it is a real portability trap, not style.
    BAD=$(git diff-tree -r --no-commit-id --raw "$REMOTE" "$TIP" | while IFS= read -r line; do
      [ -n "$line" ] || continue
      dstmode=$(printf '%s' "$line" | cut -c9-14)
      path=${line#*"$TAB"}
      if [ "$dstmode" = "120000" ]; then
        printf '%s\n' "    $path   (symlink)"
      elif [ "$dstmode" = "160000" ]; then
        printf '%s\n' "    $path   (submodule)"
      elif ! direct_push_path_allowed "$path"; then
        printf '%s\n' "    $path"
      fi
    done)
    if [ -n "$BAD" ]; then
      echo "mint-push-token: --direct is for prose, and this commit touches paths that are not:" >&2
      printf '%s\n' "$BAD" >&2
      echo "  Allowed: docs/** · _my_resources/** · _artifacts/** · *.md at the repo root." >&2
      echo "  Anything else lands through /smh-close-task-merge-tree or /cicd-push-e2e." >&2
      exit 2
    fi
  fi
fi

GIT_COMMON=$(git rev-parse --git-common-dir 2>/dev/null) || exit 2
case "$GIT_COMMON" in
  /*) : ;;
  *)  GIT_COMMON="$REPO_ROOT/$GIT_COMMON" ;;
esac
TOKEN="$GIT_COMMON/main-push-approval"

# An unspent token already sitting there is a prior sign-off that never became a push. Overwriting
# is correct — the new one is the current intent — but it is never silent: an un-spent token means
# a merge was authorised and then abandoned, and that is worth a look.
if [ -f "$TOKEN" ]; then
  echo "  ⚠ an unspent approval token was already present — overwriting it."
  echo "    A previous sign-off never reached a push. Previous contents:"
  sed 's/^/      /' "$TOKEN"
fi

umask 077
{
  echo "branch=$BRANCH"
  echo "tip=$TIP"
  echo "command=$CMD"
  echo "key=$KEY"
  [ -n "$MODE" ] && echo "mode=$MODE"
  echo "minted=$(date +%s)"
  echo "approval=$APPROVAL"
} > "$TOKEN"

echo "  🔑 main-push token minted — $CMD · ${KEY:-<no key>} · $BRANCH @ $TIP"
echo "     AUTHORIZED BY OPERATOR: \"$APPROVAL\""
echo "     Read that line back. If those words are not an unambiguous yes to THIS merge, delete"
echo "     the token ($TOKEN) and ask."
echo "     Single use, 30-minute limit, spent by the next push to main. Do not commit after this."

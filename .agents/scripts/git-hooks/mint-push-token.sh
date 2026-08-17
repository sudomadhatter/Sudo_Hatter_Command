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

CMD=""; BRANCH=""; KEY=""; APPROVAL=""
while [ $# -gt 0 ]; do
  case "$1" in
    --command)           need "$@"; CMD="$2";      shift 2 ;;
    --branch)            need "$@"; BRANCH="$2";   shift 2 ;;
    --key)               need "$@"; KEY="$2";      shift 2 ;;
    --operator-approval) need "$@"; APPROVAL="$2"; shift 2 ;;
    -h|--help) usage ;;
    *) echo "mint-push-token: unknown argument '$1'" >&2; usage ;;
  esac
done

[ -n "$CMD" ]    || { echo "mint-push-token: --command is required — the token records WHICH door authorised this." >&2; exit 2; }
[ -n "$BRANCH" ] || { echo "mint-push-token: --branch is required — the token records WHAT is being landed." >&2; exit 2; }

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
    echo "mint-push-token: HEAD does not sit exactly one merge above origin/main." >&2
    echo "  origin/main:               $REMOTE" >&2
    echo "  HEAD's first parent:       ${PARENT1:-<none>}" >&2
    echo "  One sign-off authorises ONE merge (SCC-71). If several merges are stacked here, land" >&2
    echo "  them one at a time - each with its own invocation of the close-out command." >&2
    exit 2
  fi
fi

GIT_COMMON=$(git rev-parse --git-common-dir 2>/dev/null) || exit 2

# ⛔⛔ THE ANSWER IS USED AS GIT GIVES IT, and the `cd "$REPO_ROOT"` above is what makes that safe.
#
# This used to normalise by hand:
#
#     case "$GIT_COMMON" in
#       /*) : ;;
#       *)  GIT_COMMON="$REPO_ROOT/$GIT_COMMON" ;;
#     esac
#
# which is correct on POSIX and WRONG on the PC — the identical trap `.githooks/pre-push` already
# documents for `--git-path`. `--git-common-dir` answers RELATIVE (`.git`) in a plain main checkout
# and ABSOLUTE in a worktree, and git-for-windows spells the absolute one `C:/Users/...`, which
# does NOT match `/*`. So the repo root got prepended to an already-absolute path:
#
#     in : C:/Users/dan/Sudo_Hatter_Command/.git/worktrees/<lane>
#     out: <repo_root>/C:/Users/dan/.../main-push-approval        ← the parent cannot exist
#
# The write then fails, the gate looks in the same broken place, finds nothing, and REFUSES EVERY
# PUSH TO main. On the PC that bricks the only road to main — and every lane here is a worktree.
# A relative answer needs no fixing because we have already `cd`'d to the toplevel; an absolute
# one needs no fixing either. So: no `case`. Pinned by `test_main_push_gate.py` case C1, which
# drives a `git` shim answering the way the PC answers — a source grep could not see this.
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

# ⭐ printf, NOT echo. POSIX leaves backslash handling in `echo` implementation-defined, and
# dash/ash/BusyBox expand `\n` and `\c` inside the operand. The approval line carries arbitrary
# operator prose, so an `echo` here can split the record onto a second line the parser silently
# drops — or truncate it outright at a `\c`. The whole mechanism is a claim about VERBATIM words;
# it has to store them verbatim.
{
  printf '%s\n' "branch=$BRANCH"
  printf '%s\n' "tip=$TIP"
  printf '%s\n' "command=$CMD"
  printf '%s\n' "key=$KEY"
  printf '%s\n' "minted=$(date +%s)"
  printf '%s\n' "approval=$APPROVAL"
} > "$TOKEN" 2>/dev/null

# ⛔⛔ THE OUTCOME IS VERIFIED, NOT INFERRED FROM AN EXIT CODE — and the obvious remedy is broken.
#
# This block used to end at the redirect and walk straight into the success banner. With an
# unwritable path the shell printed "No such file or directory", the block never ran, and the
# script still printed "🔑 main-push token minted" and exited 0 with nothing on disk. The close-out
# then pushed and the gate refused for having no token: a success message and a refusal that
# contradict each other, with the real reason two steps upstream.
#
# The natural fix — `if ! { … } > "$TOKEN"; then` — fires on dash and DOES NOTHING on bash or
# macOS /bin/sh, because bash does not propagate a compound-command redirect failure through `!`
# in an `if` condition. Measured on all three (AVCH-59). On the operator's Mac that "fix" printed
# the banner and exited 0 — the exact defect, reproduced inside its own remedy.
#
# `[ -s ]` asks the only question that matters — IS THE TOKEN THERE — and asks it of the
# filesystem rather than of a shell's error-propagation semantics. Same class of answer as the
# gate's own `[ -f "$TOKEN" ]`, and portable by construction.
if [ ! -s "$TOKEN" ]; then
  echo "mint-push-token: FAILED to write the approval token." >&2
  echo "  path: $TOKEN" >&2
  echo "  No token was written, so the push would be refused for having none. Reported here," >&2
  echo "  where the reason is still in scope, rather than as a contradictory refusal later." >&2
  exit 2
fi

echo "  🔑 main-push token minted — $CMD · ${KEY:-<no key>} · $BRANCH @ $TIP"
printf '     AUTHORIZED BY OPERATOR: "%s"\n' "$APPROVAL"
echo "     Read that line back. If those words are not an unambiguous yes to THIS merge, delete"
echo "     the token ($TOKEN) and ask."
echo "     Single use, 30-minute limit, spent by the next push to main. Do not commit after this."

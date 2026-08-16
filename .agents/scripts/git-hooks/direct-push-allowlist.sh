#!/bin/sh
# direct-push-allowlist.sh — what the direct-to-main fast lane may touch (SCC-183, 2026-08-16).
#
# Sourced by BOTH `mint-push-token.sh` (fails early, before the operator's approval is spent)
# and `pre-push-main-approval.sh` (authoritative, at the push). One definition, two callers:
# a security predicate pasted into two files is a predicate that drifts, and drift in exactly
# this predicate is what the first attempt at this feature died of.
#
# ⭐ THIS IS AN ALLOWLIST, AND THE DISTINCTION IS THE WHOLE FEATURE.
#
# The deleted first cut (commit 3c66dee) used a DENYLIST — refuse `backend/ frontend/
# firebase/ functions/ mobile/ .github/`, permit everything else. In a PRODUCT repo that reads
# as reasonable. In THIS repo it was vacuous: five of those six directories do not exist here,
# and the things actually worth protecting — `.agents/` (every rule, command, script and hook)
# and `.githooks/` (the gates themselves) — were on nobody's list, so they were permitted.
#
# It was proven, not theorised: a `--direct` push carrying a commit that rewrote
# `pre-push-main-approval.sh` to `return 0` from `refuse()` was ACCEPTED by that gate and
# landed on main. The gate approved the commit that disables the gate.
#
# An allowlist cannot fail that way. A directory nobody thought of is refused by default
# rather than permitted by default, so the next surface added to this repo is safe before
# anyone remembers this file exists.
#
# ⛔ WHY THIS FILE ITSELF IS UNREACHABLE BY THE LANE IT GOVERNS: it lives under `.agents/`,
# which the first arm refuses. The fast lane cannot edit its own allowlist.

# direct_push_path_allowed <path>  ->  0 = may go direct, 1 = must use the reviewed lane
#
# ⚠ ORDER IS LOAD-BEARING, and the arms are not interchangeable:
#   1. the explicit refusals run FIRST, so no later arm can widen them by accident;
#   2. the prose trees are permitted (a `case` glob's `*` DOES cross `/`, so these are
#      whole subtrees, nested to any depth);
#   3. `*/*` then sweeps every OTHER nested path — which is what leaves the final `*.md`
#      arm able to match root-level files only;
#   4. the last arm refuses. Anything unrecognised is refused, never permitted.
direct_push_path_allowed() {
  case "$1" in
    # ── law and enforcement: reviewed lane only, no exceptions ──
    .agents/*|.githooks/*|tests/*)        return 1 ;;
    # ── prose trees ──
    docs/*|_my_resources/*|_artifacts/*)  return 0 ;;
    # ── any other nested path is not prose ──
    */*)                                  return 1 ;;
    # ── root-level markdown (README, AGENTS, CLAUDE, GEMINI, router) ──
    *.md)                                 return 0 ;;
    # ── fail closed ──
    *)                                    return 1 ;;
  esac
}

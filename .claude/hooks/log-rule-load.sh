#!/bin/sh
# log-rule-load — the receipt that says a path-scoped rule ACTUALLY loaded.
#
# An `InstructionsLoaded` hook. Claude Code fires it when it pulls a file into the session as
# instructions, and with the `path_glob_match` matcher that means: a rule in `.claude/rules/` whose
# `paths:` globs matched a file just read. This appends the path to a log so the load can be OBSERVED
# instead of assumed.
#
# ─── Why it exists ──────────────────────────────────────────────────────────────────────────────
# `sync-agents.ps1` emits six path-scoped rules and `test_rule_frontmatter.py` proves the frontmatter
# is right. Neither proves the platform ACTS on it. That gap is exactly the shape of the exit-127 bug
# (SCC-77): five hooks wired to binaries that did not exist, failing silently for weeks, because a
# mechanism that never fires is indistinguishable from a mechanism with nothing to say. This is the
# cheapest possible observation — one line per load, in a file you can `cat`.
#
# ⛔ It is a PROBE, not a gate. Nothing reads this log but a human running the canary. It writes to a
# temp dir on purpose: this is diagnostic exhaust, not an artifact, and it must never accumulate in
# the tree or in git.
#
# Read it with:   cat "${TMPDIR:-/tmp}/claude-rule-loads.log"
# See `_routing-canary/README.md` § "Probe 2" for the full activation check.

LOG="${TMPDIR:-/tmp}/claude-rule-loads.log"
PAYLOAD=$(cat)

# `file_path` out of the event JSON without a JSON parser — this is `sh`, and adding a python
# dependency to a diagnostic probe would give it the same fragility the probe exists to detect.
# No match (a payload shaped differently by a future version) leaves FP empty and logs the raw
# event instead of nothing, which is still more than the silence it replaces.
FP=$(printf '%s' "$PAYLOAD" | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
[ -n "$FP" ] || FP="(no file_path in payload) $PAYLOAD"

# `printf`, never `echo`: this system's `echo` truncates at a literal `\c` and eats backslashes in
# a path. A probe that mangles what it observes is worse than no probe.
printf '%s\t%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$FP" >> "$LOG" 2>/dev/null

# ⛔ Silent on stdout. `InstructionsLoaded` output would be injected into the session, and a probe
# that narrates every rule load turns the thing it measures into noise. Always 0 — see
# `.agents/hooks/INDEX.md`: this whole layer degrades to silence, never to a blocked session.
exit 0

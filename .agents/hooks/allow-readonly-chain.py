#!/usr/bin/env python3
"""PreToolUse hook: auto-ALLOW a COMPOUND command when every atom of it is something the
operator already allows on its own (SCC-287).

⛔ THE MEASURED PROBLEM. Two layers can auto-approve a Bash call, and neither one can read a
compound command:

  * `settings*.json` `Bash(...)` rules match the command string by PREFIX, over the WHOLE string.
    `grep -n x f` matches `Bash(grep:*)`; `git diff | grep -n x` matches nothing at all, because
    no rule begins with `git diff | grep`. 81 allow rules were in force and the second shape
    prompted every time.
  * `allow-scratchpad.py`, the only other layer, REFUSES every shell metacharacter by design
    (SCC-263, rule 1) - so it cannot cover a pipe either, and must not be taught to.

Measured over one session's transcript: 246 Bash calls, 224 of them (91%) carried a
metacharacter - 149 pipes, 95 redirects, 89 semicolons, 54 chains, 54 heredocs. Twenty-two were
eligible for auto-approval. The operator was clicking approve on nine calls in ten, and the cause
was architectural, not a missing rule. Writing more rules cannot fix it: no prefix rule can ever
match a string that contains a pipe.

⭐ WHAT THIS GRANTS: NOTHING NEW. That is the whole design, and it is testable rather than
asserted. An atom is permitted only when BOTH hold:

    (A) its VERB is on a read-only allow-list COMPILED INTO THIS FILE, with a per-verb
        allow-list of FLAGS, and
    (B) the atom text already matches one of the operator's own `permissions.allow` rules.

(B) is the "nothing new" proof: every atom would auto-approve on its own, as a separate Bash
call, with no prompt. This hook removes the prompt on running them in one call instead of three.
(A) is the committed floor that travels to the other machine, and it is what stops (B) from
inheriting the MUTATING rules the operator also has - `Bash(git checkout *)`, `Bash(git add:*)`,
`Bash(cp:*)` all match atoms this file refuses.

⛔ THE SPLIT MUST BE THE SHELL'S SPLIT, OR THERE IS NO ARGUMENT AT ALL. SCC-263's fourteen
escapes were all one shape: something the hook did not recognise was treated as harmless. The
defence here is the same inversion - an allow-list of shapes, refusing everything else:

  1. A CHARACTER ALLOW-LIST, IN THE SHELL'S THREE MODES. Unquoted, a character must be in
     `SAFE`, which leaves out `$`, backtick, `<`, `>`, `(`, `)`, `[`, `]`, `{`, `}`, `*`, `?`,
     `!`, `#`, `\\` and newline - so command substitution, every redirect spelling, heredocs,
     subshells, globs, history expansion, comments and line continuation are unreachable BY
     CONSTRUCTION, not by a pattern the next escape works around. Inside DOUBLE quotes only what
     the shell still acts on stays banned (`$`, backtick, `\\`); inside SINGLE quotes nothing is
     banned but a newline, because the shell acts on nothing there. That distinction is not a
     softening - it is what lets `--include='*.md'` and `--jql 'project = SCC AND …'` through
     while `--include=*.md` unquoted still refuses, and it was worth 103 commands in the
     measurement below. Quotes, `|`, `&` and `;` are the additions over
     `allow-scratchpad.py`'s rule 1, and rules 2-3 are what pay for them.
  1b. ONE ENUMERATED REDIRECT CARVE-OUT. `>/dev/null`, `2>/dev/null`, `&>/dev/null` and `2>&1`
     name no destination - one discards, one duplicates a descriptor - and they sat on 201 of the
     commands this hook could not otherwise read. They are STRIPPED before rule 1 runs, so the
     text that gets judged has no `>` in it, and any redirect that is not one of those four
     spellings still meets rule 1 and is still refused. An allow-list of four strings, not a rule
     about redirects.
  2. QUOTES ARE TRACKED, AND A SEPARATOR INSIDE ONE IS A REFUSAL. `grep -n a;b f` and
     `grep -n "a;b" f` are different commands, and a splitter that cannot tell them apart is
     guessing. Rather than guess, this refuses outright whenever `|`, `&` or `;` appears inside
     a quoted region, or the quotes do not balance. What survives is a split that provably
     equals the shell's.
  3. SEPARATOR RUNS ARE EXACT. `&` must be exactly `&&` - a lone `&` BACKGROUNDS the command,
     which detaches it from the approval that authorised it. `;` must be exactly one (`;;` is
     case-statement syntax). `|` may be one or two. No empty atom, so a leading or trailing
     separator is refused.
  4. FLAGS ARE AN ALLOW-LIST, PER VERB, and this is what keeps "read-only" true. A read-only
     VERB is not enough: `sort -o out.txt f` writes, `sed -i s/a/b/ f` writes, `find . -delete`
     deletes and `find . -exec rm {} +` runs anything. None of `-o`, `-i`, `-delete` or `-exec`
     is on its verb's list, so all four refuse - and every future flag refuses too, which is the
     opposite of a deny-list's failure mode.
  5. A QUOTED FLAG IS STILL A FLAG. `sort "-o" out.txt f` reaches sort as `-o`: the shell strips
     the quotes. So every token is DEQUOTED before the flag test, which can only ever pull more
     tokens into the check.
  6. AN INTERPRETER MAY NOT BE A PIPE SINK. `python3` and `node` are permitted, because the
     operator's rules already name the exact script paths they may run (`Bash(python3
     .agents/scripts/:*)`) - `python3 x.py | tail -5` is the same execution as `python3 x.py`
     with a reader bolted on. But `something | python3` feeds the interpreter its program on
     stdin, which is a different act, so an interpreter is refused in any non-first pipe
     position. `bash` and `sh` are off the list entirely: there is no useful chain-position rule
     for them, and `allow-scratchpad.py` already covers the sandbox case they are needed for.
  7. `cd` ONLY TO AN ABSOLUTE PATH INSIDE THIS WORKSPACE. `guard-cwd-escape.py` runs in the same
     chain and flags a top-level `cd` LEAVING the workspace, because that is what silently resets
     the session's cwd to the main checkout (SCC-182). It says of the rest: "any `cd` that stays
     inside all pass untouched." This permits exactly that set, so the two hooks cannot disagree
     about the same command and the one that removes a prompt can never speak over the one that
     raises a question. A RELATIVE target is refused: it resolves against a cwd this process
     cannot see, so there is nothing to verify.
  8. A NEWLINE IS A SEPARATOR, exactly as `;` is. Ninety of the unreadable commands were
     multi-line - a `cd` and then two or three reads - and every line is still an atom that must
     satisfy rules 4-6 and condition (B) by itself.

⛔ TWO LEGAL OUTPUTS: `allow`, or SILENCE. Never `ask`, never `deny`. `ask` is auto-DENY in
non-interactive mode, so a hook that emitted it would block the very lanes it exists to unblock.
Refusing here means printing NOTHING and letting the normal approval prompt happen - this hook
can only ever REMOVE a prompt it is certain about, never ADD one.

⛔ FAILS SILENT, always. Unparseable stdin, any exception at all -> print nothing, exit 0. And
NOTHING AT MODULE LEVEL MAY RAISE (SCC-267): every resolver is a function, called from inside the
wrapper, and answers `None`/`False` rather than raising. A crash before the wrapper is installed
is not covered by the wrapper.

WHAT THIS STILL DOES NOT DO, stated plainly: heredocs, redirects and `for` loops still prompt.
They are unreachable by construction above, and that is deliberate - a redirect names a
destination the allow-list cannot vet. Writing `python3 x.py > out.txt` instead of two calls is an
authoring habit, not a gap in this file.

Canonical source: `.agents/hooks/`. Deployed to `.claude/hooks/` - never hand-edit the copy."""
from __future__ import annotations

import functools
import json
import os
import posixpath
import re
import sys

# ── Rule 1 · the character allow-list, which is THREE lists because the shell has three modes ─
# ⛔ WHAT IS ABSENT UNQUOTED IS THE POINT: no `$` (expansion), no backtick or `(`/`)`
# (substitution, subshell), no `<`/`>` (every redirect and heredoc spelling), no `*`/`?`/`[`/`]`/
# `{`/`}` (a glob expands AFTER this hook has judged the tokens, so a file named `-o` sitting in
# the directory is flag injection straight past rule 4), no `!` (history), no `#` (a comment
# hides the tail of the command from the reader while the shell still runs the head), no `\`
# (continuation, and quote escaping - which is what makes rule 2's tracker sound), no newline.
# `~` IS here: it expands to a path and nothing else, and with a read-only verb list a path is
# all it can ever be.
SAFE = frozenset(
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    "/._-=+,:@%^~ \t\n'\"|&;"
)

# ⭐ INSIDE DOUBLE QUOTES most of that list stops being dangerous, and refusing it there was
# costing more than it bought: measured over one session, 103 of the commands this hook could not
# read carried an excluded character and the commonest by far was a QUOTED glob -
# `--include='*.md'`, `--fields '*all'`, `grep -v '.git/'`. Quoted, they are text: the shell
# passes them to the verb verbatim. What stays banned in double quotes is what the shell still
# ACTS on there - `$`, backticks, and `\`, the last because `\"` would close the quote for the
# shell and not for this scanner, and a scanner out of step with the shell is the whole failure
# mode rule 2 exists to prevent.
DQ_SAFE = SAFE | frozenset("*?[]{}()<>!#")

# Inside SINGLE quotes the shell acts on nothing at all, including `$`, backticks and `\` - which
# is exactly why the scanner cannot drift out of step there. Only a newline is refused: a
# multi-line command is a script, and this hook judges one line.
SQ_FORBIDDEN = frozenset("\n\r")

# ⭐ A NEWLINE IS A SEPARATOR, EXACTLY AS `;` IS. Ninety of the commands this hook could not read
# were multi-line - `cd <dir>` on line one, then two or three reads - and treating a newline as
# text refused all of them. It grants nothing: every line is still an atom, and every atom still
# has to satisfy rules 4-6 and condition (B) on its own. Inside quotes a newline is still refused
# (a quoted newline is a script, and this hook judges commands).
SEPARATORS = "|&;\n"
QUOTES = "'\""

# ⭐ THE ONE REDIRECT CARVE-OUT, AND IT NAMES NO DESTINATION. `2>/dev/null` and `2>&1` were on
# 201 of the still-prompting commands in the same measurement, and neither can write anywhere:
# one discards, the other duplicates a file descriptor onto another. They are stripped BEFORE the
# character check, so the surviving text is judged with no `>` in it at all - and anything the
# strip leaves behind (`>out.txt`, `>&file`) still meets rule 1 and is still refused. This is an
# enumerated allow-list of four spellings, not a rule about redirects.
NULL_REDIRECT = re.compile(
    r"(?:^|(?<=\s))(?:\d?>{1,2}\s*/dev/null|&>{1,2}\s*/dev/null|2>&1|1>&2)(?=[\s|;&]|$)")

# ── Rule 4 · the verbs, and the flags each one may carry ─────────────────────────────────────
# ⛔ EVERY SET IS CLOSED. A flag that is not listed is REFUSED, and refusing costs nothing - the
# hook falls silent and the operator gets the prompt they get today. That asymmetry is why this
# is an allow-list: the failure mode of forgetting a flag is friction, and the failure mode of
# forgetting one on a deny-list is a write.
#
# ⛔ THE FLAGS THAT ARE MISSING ON PURPOSE, each one a write hiding under a read-only verb:
#   sort   `-o` / `--output`      writes its result to a named file
#   sed    `-i`                   edits in place (and `-i.bak` glues the value to the flag)
#   find   `-exec` `-execdir`     runs an arbitrary command per hit
#          `-ok` `-okdir`         the same, with a prompt this hook would have removed
#          `-delete`              unlinks every hit
#          `-fprint` `-fprintf` `-fls`   write to a named file
#   tee    (the whole verb)       its entire job is to write
#   ln     (the whole verb)       an IMPLICIT destination the command string never names -
#                                 the SCC-263 rule 6 lesson, and it applies here unchanged.
READONLY_FLAGS: dict[str, frozenset[str]] = {
    "ls": frozenset({"-l", "-a", "-A", "-h", "-t", "-r", "-S", "-R", "-d", "-1", "-F", "-i",
                     "-p", "-n", "-u", "-c", "-G", "--color", "--time-style", "--group-directories-first"}),
    "cat": frozenset({"-n", "-b", "-s", "-v", "-e", "-t", "-A", "--number"}),
    "head": frozenset({"-n", "-c", "-q", "-v", "--lines", "--bytes", "--quiet", "--verbose"}),
    "tail": frozenset({"-n", "-c", "-q", "-v", "-f", "--lines", "--bytes", "--quiet", "--verbose"}),
    "wc": frozenset({"-l", "-w", "-c", "-m", "-L", "--lines", "--words", "--bytes", "--chars"}),
    "grep": frozenset({"-i", "-n", "-r", "-R", "-l", "-L", "-c", "-v", "-w", "-x", "-E", "-F",
                       "-G", "-P", "-o", "-q", "-s", "-h", "-H", "-a", "-e", "-f", "-A", "-B",
                       "-C", "-m", "-z", "-Z", "-U", "-b",
                       "--include", "--exclude", "--exclude-dir", "--color", "--colour",
                       "--line-number", "--recursive", "--files-with-matches",
                       "--files-without-match", "--only-matching", "--count", "--invert-match",
                       "--ignore-case", "--word-regexp", "--fixed-strings",
                       "--extended-regexp", "--perl-regexp", "--no-filename", "--with-filename",
                       "--binary-files", "--max-count", "--after-context", "--before-context",
                       "--context", "--quiet", "--no-messages"}),
    "rg": frozenset({"-i", "-n", "-l", "-c", "-v", "-w", "-x", "-F", "-e", "-t", "-T", "-g",
                     "-A", "-B", "-C", "-m", "-o", "-q", "-s", "-S", "-N", "-H", "-P", "-u",
                     "-U", "-p", "-z", "-L",
                     "--files", "--files-with-matches", "--files-without-match", "--hidden",
                     "--no-heading", "--heading", "--line-number", "--no-line-number",
                     "--color", "--colors", "--type", "--type-not", "--glob", "--iglob",
                     "--max-count", "--max-depth", "--sort", "--sortr", "--vimgrep", "--json",
                     "--count", "--count-matches", "--only-matching", "--multiline",
                     "--multiline-dotall", "--fixed-strings", "--word-regexp", "--regexp",
                     "--case-sensitive", "--smart-case", "--ignore-case", "--invert-match",
                     "--context", "--after-context", "--before-context", "--no-ignore",
                     "--with-filename", "--no-filename", "--stats", "--trim", "--column"}),
    # ⛔ `find`'s predicates are SINGLE-DASH LONG WORDS (`-name`), so the bundled-short-flag
    # branch below must never reach them - it would read `-name` as `-n -a -m -e`. It cannot:
    # an exact-set hit is tested first, and every predicate here is an exact member.
    "find": frozenset({"-name", "-iname", "-path", "-ipath", "-type", "-maxdepth", "-mindepth",
                       "-newer", "-newermt", "-size", "-empty", "-print", "-print0", "-not",
                       "-o", "-a", "-and", "-or", "-prune", "-mtime", "-mmin", "-perm", "-user",
                       "-group", "-regex", "-iregex", "-depth", "-readable", "-links", "-follow",
                       "-L", "-H", "-P", "-s", "-x", "-xdev"}),
    "sort": frozenset({"-n", "-r", "-u", "-f", "-b", "-h", "-V", "-k", "-t", "-s", "-c", "-C",
                       "-z", "-d", "-g", "-M", "-i", "--numeric-sort", "--reverse", "--unique",
                       "--key", "--field-separator", "--version-sort", "--human-numeric-sort",
                       "--ignore-case", "--check", "--stable"}),
    "uniq": frozenset({"-c", "-d", "-D", "-u", "-i", "-f", "-s", "-w", "-z",
                       "--count", "--repeated", "--unique", "--ignore-case"}),
    "cut": frozenset({"-d", "-f", "-c", "-b", "-s", "-n", "-z",
                      "--delimiter", "--fields", "--characters", "--bytes", "--complement",
                      "--output-delimiter", "--only-delimited"}),
    "tr": frozenset({"-d", "-s", "-c", "-C", "-t", "-u",
                     "--delete", "--squeeze-repeats", "--complement", "--truncate-set1"}),
    # ⛔ `-i` ABSENT. `sed -i.bak s/a/b/ f` rewrites the file, and the operator's own rule is
    # `Bash(sed -n:*)`, which a prefix matcher happily satisfies with `sed -n -i.bak …`.
    "sed": frozenset({"-n", "-E", "-e", "-r", "--quiet", "--silent", "--regexp-extended"}),
    "diff": frozenset({"-u", "-r", "-q", "-i", "-w", "-b", "-B", "-N", "-a", "-y", "-c", "-U",
                       "-s", "-x", "-X", "-Z",
                       "--brief", "--recursive", "--unified", "--color", "--exclude",
                       "--new-file", "--report-identical-files", "--ignore-all-space",
                       "--ignore-space-change", "--side-by-side", "--text"}),
    "cmp": frozenset({"-s", "-l", "-i", "-n", "--silent", "--quiet", "--verbose"}),
    "stat": frozenset({"-f", "-c", "-L", "-t", "-x", "-n", "-s", "--format", "--printf",
                       "--dereference", "--terse"}),
    "file": frozenset({"-b", "-i", "-L", "-h", "-z", "-s", "--brief", "--mime", "--mime-type",
                       "--mime-encoding", "--dereference"}),
    "du": frozenset({"-h", "-s", "-a", "-c", "-d", "-k", "-m", "-x", "-L", "-r",
                     "--human-readable", "--summarize", "--max-depth", "--total", "--all"}),
    "df": frozenset({"-h", "-k", "-m", "-i", "-P", "-T", "--human-readable", "--portability"}),
    "basename": frozenset({"-s", "-a", "-z", "--suffix", "--multiple", "--zero"}),
    "dirname": frozenset({"-z", "--zero"}),
    "readlink": frozenset({"-f", "-e", "-m", "-n", "-q", "-s", "--canonicalize", "--no-newline"}),
    "printf": frozenset(),
    "which": frozenset({"-a", "-s", "--all"}),
    "nl": frozenset({"-b", "-n", "-w", "-s", "-v", "-i", "--body-numbering", "--number-width"}),
    "date": frozenset({"-u", "-r", "-R", "-I", "--utc", "--iso-8601", "--rfc-3339", "--date"}),
    "pwd": frozenset({"-L", "-P"}),
    "true": frozenset(),
    "false": frozenset(),
}

# `git` is not one verb, it is dozens, and the SUBCOMMAND is what decides whether it reads or
# writes. Handled separately for exactly that reason.
GIT_READONLY = frozenset({
    "status", "log", "diff", "show", "rev-parse", "merge-base", "ls-files", "check-ignore",
    "merge-tree", "describe", "blame", "shortlog", "cat-file", "diff-tree", "rev-list",
    "count-objects", "ls-tree", "name-rev", "whatchanged", "grep", "version",
})

# Two-word read-only forms of subcommands whose one-word form MUTATES. `git branch` alone lists,
# but `git branch -d chore/x` deletes and `git worktree remove` removes a tree - so the second
# token is pinned rather than the first.
GIT_READONLY_PAIRS = frozenset({
    ("worktree", "list"), ("stash", "list"), ("branch", "--list"), ("branch", "-a"),
    ("branch", "--show-current"), ("remote", "-v"), ("remote", "show"),
    ("config", "--get"), ("config", "--list"), ("config", "--get-all"),
    ("tag", "--list"), ("tag", "-l"), ("submodule", "status"), ("notes", "list"),
})

# ⛔ `-o` AND `--output` ARE ABSENT. `--output=<file>` is a diff option, so it is accepted by
# `git diff`, `git show` AND `git log` - three of the most-used read-only subcommands, each of
# which would write an arbitrary file with it. `-c` is absent too: `git -c key=value …` rewrites
# configuration for the duration of the call.
GIT_FLAGS = frozenset({
    "-C", "-p", "-s", "-n", "-u", "-U", "-M", "-w", "-b", "-r", "-v", "-a", "-l", "-z", "-L",
    "-S", "-G", "-i", "-E", "-P", "-F", "-q", "-t", "-e", "-m", "-R", "-B", "-D", "-W", "-I",
    "--no-pager", "--oneline", "--stat", "--shortstat", "--numstat", "--dirstat",
    "--compact-summary", "--name-only", "--name-status", "--summary", "--graph", "--decorate",
    "--no-decorate", "--all", "--branches", "--tags", "--remotes", "--merges", "--no-merges",
    "--first-parent", "--follow", "--date", "--format", "--pretty", "--abbrev",
    "--abbrev-commit", "--no-abbrev", "--full-index", "--cached", "--staged", "--short",
    "--branch", "--porcelain", "--untracked-files", "--ignored", "--verbose", "--list",
    "--verify", "--quiet", "--exit-code", "--unified", "--diff-filter", "--find-renames",
    "--find-copies", "--ignore-all-space", "--ignore-space-change", "--ignore-blank-lines",
    "--word-diff", "--color", "--no-color", "--relative", "--show-toplevel", "--git-dir",
    "--absolute-git-dir", "--abbrev-ref", "--is-inside-work-tree", "--symbolic-full-name",
    "--symbolic", "--max-count", "--skip", "--since", "--until", "--author", "--grep",
    "--committer", "--merged", "--no-merged", "--contains", "--points-at", "--sort", "--count",
    "--others", "--modified", "--deleted", "--stage", "--error-unmatch", "--full-name",
    "--no-renames", "--patch", "--no-patch", "--raw", "--no-index", "--text", "--binary",
    "--show-current", "--get", "--get-all", "--no-textconv", "--textconv", "--reverse",
    "--topo-order", "--date-order", "--boundary", "--left-right", "--cherry-pick",
    "--show-signature", "--stat-width", "--indent-heuristic", "--histogram", "--patience",
})

# `acli` is the Jira CLI, and it splits exactly the way git does: `jira workitem view` and
# `… search` READ, while `create`, `edit`, `transition`, `delete` and `assign` all write to a
# live board. The operator already carries `Bash(acli jira workitem view:*)` and `… search:*`, so
# condition (B) covers the reads; this is the (A) half that keeps the writes out of a chain.
ACLI_READONLY = frozenset({("jira", "workitem", "view"), ("jira", "workitem", "search")})
ACLI_FLAGS = frozenset({"--json", "--yaml", "--csv", "--plain", "--fields", "--jql", "--limit",
                        "--paginate", "--help", "-h"})

CD_FLAGS = frozenset({"-L", "-P"})

# Verbs that can only ever write to stdout, whatever they are handed - so there is no flag on
# them worth checking, and checking anyway is a false refusal. `echo` only: `printf` reads its
# first argument as a FORMAT, which is a different kind of surface, and `cat` takes files.
TEXT_ONLY = frozenset({"echo"})

# Rule 6. Permitted, but never on the receiving end of a pipe.
INTERPRETERS = frozenset({"python3", "python", "node"})

# A bare name, never a path: `/usr/bin/sudo` and `"cat"` are refused by construction rather than
# by a delimiter the next escape works around (SCC-263 rule 2).
VERB_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.+-]*$")
# `-20`, `-5` - a count. It cannot name a destination, so it is accepted for every verb.
COUNT_FLAG_RE = re.compile(r"^-\d+$")
BUNDLE_RE = re.compile(r"^-[A-Za-z]{2,}$")
UNIVERSAL_FLAGS = frozenset({"--"})


def dequote(token: str) -> str:
    """Rule 5. `sort "-o" out.txt f` reaches sort as `-o`, because the shell strips the quotes.
    Dropping them here can only pull MORE tokens into the flag check, never fewer."""
    return token.replace('"', "").replace("'", "")


def quote_mask(command: str) -> list[bool]:
    """True at every index the shell is inside a quoted region (the quote characters included)."""
    mask, quote = [], None
    for ch in command:
        if quote is not None:
            mask.append(True)
            if ch == quote:
                quote = None
            continue
        if ch in QUOTES:
            quote = ch
            mask.append(True)
            continue
        mask.append(False)
    return mask


def strip_null_redirects(command: str) -> str:
    """Remove the four enumerated no-destination redirections, and only outside quotes.

    ⛔ IT REMOVES, IT NEVER REWRITES. Whatever is left is judged by rule 1 exactly as though it
    had been typed that way, so a redirect that is NOT one of the four spellings still carries a
    `>` into the character check and is still refused. `grep -n x "2>/dev/null"` keeps its
    argument, because inside quotes that text is an operand, not a redirection.
    """
    text = command
    for _ in range(8):                      # a bounded loop: `>/dev/null 2>&1` is two removals
        mask = quote_mask(text)
        hit = next((m for m in NULL_REDIRECT.finditer(text)
                    if not any(mask[m.start():m.end()])), None)
        if hit is None:
            return text
        text = text[:hit.start()] + " " + text[hit.end():]
    return text


def split_atoms(command: str) -> list[tuple[str, str | None]] | None:
    """Rules 1, 2 and 3 in one pass, because the character check depends on the quote state.

    Returns `[(atom_text, separator_before_it), ...]`, or None when the command is not a shape
    this hook is willing to claim it understands. The separator is what makes rule 6 possible:
    only an atom introduced by a single `|` is a pipe SINK.

    ⛔ IT REFUSES RATHER THAN GUESSES. A separator inside quotes is refused outright even though
    the scan handles it correctly, and that is a deliberate cost: `compile_rule` forbids a
    permission rule from stretching across `;`, `|` or `&`, so an atom carrying a quoted
    separator could never match one anyway - and refusing here keeps the two halves consistent
    instead of quietly disagreeing. Unbalanced quotes are the same class.
    """
    atoms: list[tuple[str, str | None]] = []
    buf: list[str] = []
    quote: str | None = None
    sep: str | None = None
    i, n = 0, len(command)
    while i < n:
        ch = command[i]
        if quote is not None:
            if ch in SEPARATORS:
                return None
            if quote == '"' and ch not in DQ_SAFE:
                return None
            if quote == "'" and ch in SQ_FORBIDDEN:
                return None
            if ch == quote:
                quote = None
            buf.append(ch)
            i += 1
            continue
        if ch not in SAFE:
            return None
        if ch in QUOTES:
            quote = ch
            buf.append(ch)
            i += 1
            continue
        if ch in SEPARATORS:
            j = i
            while j < n and command[j] == ch:
                j += 1
            run = j - i
            # A LONE `&` BACKGROUNDS. The command detaches from the approval that authorised it
            # and keeps running after the turn ends, so `&&` is the only accepted spelling.
            if ch == "&" and run != 2:
                return None
            if ch == ";" and run != 1:
                return None
            if ch == "|" and run not in (1, 2):
                return None
            if ch == "\n":
                # Blank lines and indentation are layout, not structure - a run of newlines and
                # the whitespace around them is ONE separator, so `a\n\n  b` is two atoms and not
                # an empty one in the middle.
                while j < n and command[j].isspace():
                    j += 1
            atoms.append(("".join(buf).strip(), sep))
            sep = "|" if (ch == "|" and run == 1) else ("||" if ch == "|" else ch * run)
            buf = []
            i = j
            continue
        buf.append(ch)
        i += 1
    if quote is not None:
        return None
    atoms.append(("".join(buf).strip(), sep))
    if any(not text for text, _ in atoms):
        return None
    return atoms


def tokenize(text: str) -> list[str]:
    """Whitespace-split, but NEVER inside quotes: `--jql 'a = b'` is two tokens, not five.

    ⛔ A NAIVE `.split()` INVENTS FLAGS THAT NOBODY TYPED. `acli jira workitem search --jql
    'project = SCC AND created >= -3d'` split into twelve pieces, one of them `-3d'`, and the
    flag check refused a read-only Jira query over a flag that exists only in the splitter. The
    shell hands the verb ONE argv element for that quoted string, and rule 4 has to judge what
    the verb will actually receive - in BOTH directions: `grep "a -o b" f` is a grep for the text
    `a -o b`, not a grep with an `-o` flag, and refusing it was wrong for the same reason.
    """
    out: list[str] = []
    buf: list[str] = []
    quote: str | None = None
    for ch in text:
        if quote is not None:
            buf.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in QUOTES:
            quote = ch
            buf.append(ch)
            continue
        if ch.isspace():
            if buf:
                out.append("".join(buf))
                buf = []
            continue
        buf.append(ch)
    if buf:
        out.append("".join(buf))
    return out


def flags_ok(tokens: list[str], allowed: frozenset[str]) -> bool:
    """Rule 4. Every flag token must be an exact member, or a bundle of exact members.

    Exact FIRST, bundling second - `find -name` is a single predicate and must never be read as
    `-n -a -m -e`. `--flag=VALUE` is checked on the flag half; the value is an operand, and an
    operand cannot smuggle anything past rules 1-3.
    """
    for token in tokens:
        bare = dequote(token)
        if not bare.startswith("-") or bare == "-":
            continue
        if bare in UNIVERSAL_FLAGS or COUNT_FLAG_RE.match(bare):
            continue
        name = bare.split("=", 1)[0]
        if name in allowed:
            continue
        if BUNDLE_RE.match(name) and all(f"-{c}" in allowed for c in name[1:]):
            continue
        return False
    return True


def git_ok(args: list[str]) -> bool:
    """The subcommand decides. Skip leading flags, honour `-C <path>`, then pin what is left."""
    i = 0
    while i < len(args):
        token = dequote(args[i])
        if token == "-C":
            i += 2                       # its value is a path operand, not a subcommand
            continue
        if token.startswith("-"):
            i += 1
            continue
        break
    if i >= len(args):
        return False                     # flags only, no subcommand: not a shape we can vet
    sub = dequote(args[i])
    if sub in GIT_READONLY:
        return True
    nxt = dequote(args[i + 1]) if i + 1 < len(args) else ""
    return (sub, nxt) in GIT_READONLY_PAIRS


def _is_abs(p: str) -> bool:
    """Absolute in EITHER spelling: POSIX `/x`, or a Windows drive root `C:\\x` / `C:/x`.

    ⛔ Deliberately not `os.path.isabs`. That answers about the machine this process runs on, and
    a drive-lettered path must be recognised as absolute wherever this hook reads it — a fixture
    or a transcript from the other machine must not read as a RELATIVE path, which is the one
    shape `cd_ok` refuses outright. A bare `C:` with no root is NOT absolute (it means "the
    current directory on drive C", which is exactly the unverifiable case).
    """
    if p.startswith("/"):
        return True
    return len(p) > 2 and p[1] == ":" and p[0].isalpha() and p[2] in "\\/"


def _canon(p: str) -> str:
    """One spelling for comparison: forward slashes, no trailing slash, case-folded on Windows.

    ⛔ The rewrite is Windows-only. On POSIX a backslash is a legal FILENAME character, so
    rewriting it there would turn the sibling `/ws\\x` into `/ws/x` and read it as inside a
    workspace rooted at `/ws` — a separator fix for one machine widening the other's guard.

    ⛔ AND WINDOWS HAS A THIRD SPELLING, WHICH IS THE ONE THE SHELL PRODUCES. The Bash tool runs
    Git Bash, whose own spelling of `C:\\ws` is `/c/ws` — and agents type that constantly because
    it is what `pwd` hands back. `_is_abs` accepts it (it starts with `/`), so it arrives here and
    used to be compared, unrewritten, against a root of `c:/ws`: never equal, so EVERY
    `cd /c/<repo> && …` chain fell through to a prompt. Measured over 18 transcripts: 114 calls,
    7.0% of every prompt the operator answered. Fourth instance of this bug in the house after
    SCC-321 (`C:/` vs `/`) and SCC-171/172. It fails SAFE — a prompt, never a wrong grant — which
    is why it survived a fixture set that spells the root `C:/…` every time.

    The rewrite is exact and cannot widen anything: only a SINGLE letter between the leading
    slash and the next separator is a drive, so `/etc`, `/tmp` and `/private` are untouched, and
    `/d/Somewhere` becomes `d:/somewhere` — still outside a `c:` root, still refused.
    """
    if os.name == "nt":
        p = p.replace("\\", "/").casefold()
        p = re.sub(r"^/([a-z])(?=/|$)", r"\1:", p)
    p = posixpath.normpath(p)
    # ⛔ `rstrip` must not be able to EMPTY the root. A root of "/" would become "", and the
    # caller's `target.startswith(root + "/")` would then be true of every absolute path on the
    # machine — a containment test that contains everything. Strip only a real trailing slash.
    return p[:-1] if len(p) > 1 and p.endswith("/") else p


def cd_ok(args: list[str]) -> bool:
    """`cd` to ONE absolute path inside this workspace, and nowhere else.

    ⛔ THIS IS NOT A RELAXATION OF `guard-cwd-escape.py`, IT IS ITS COMPLEMENT. That hook exists
    because a Bash call that ENDS outside the workspace silently resets the session's cwd to the
    main checkout, so every later relative path reads the wrong tree (SCC-182). It flags a
    top-level `cd` LEAVING the workspace and, in its own words, "any `cd` that stays inside all
    pass untouched". This permits exactly that set and no more - so the two hooks can never
    disagree about the same command, and the one that removes a prompt can never speak over the
    one that raises a question.

    ABSOLUTE ONLY. A relative target resolves against a cwd this process cannot see, so there is
    nothing here to verify, and `cd ../..` is the escape the guard was written for.

    ⛔ AND "ABSOLUTE" HAS TWO SPELLINGS (SCC-321). This asked `startswith("/")`, which is the POSIX
    one only — so on Windows, where the repo root is `C:\\…` and a Bash-tool command names it
    `C:/…`, EVERY `cd` failed the test and this hook could never grant one. It fails safe (no
    grant, so the operator just gets the ordinary prompt), which is why it went unnoticed: the
    only symptom is the prompt this hook exists to remove, on every command, on one machine.
    Third instance of this exact bug in the house — `run-hook.sh` and the push-gate scripts
    (SCC-171/172) were the other two.
    """
    paths = [dequote(a) for a in args if not dequote(a).startswith("-")]
    if len(paths) != 1 or not _is_abs(paths[0]):
        return False
    root = _canon(_repo_root())
    target = _canon(paths[0])
    return target == root or target.startswith(root + "/")


def acli_ok(args: list[str]) -> bool:
    """The first three non-flag tokens are the command path (`jira workitem view`)."""
    words = tuple(dequote(a) for a in args if not dequote(a).startswith("-"))[:3]
    return words in ACLI_READONLY


def verb_ok(verb: str, args: list[str], is_pipe_sink: bool) -> bool:
    """Condition (A): the committed read-only floor. Travels with the repo, unlike (B)."""
    if verb in INTERPRETERS:
        # Rule 6. Permitted because condition (B) pins the exact script path the operator already
        # allows - but never reading its program off a pipe.
        return not is_pipe_sink
    if verb == "git":
        return git_ok(args) and flags_ok(args, GIT_FLAGS)
    if verb == "acli":
        return acli_ok(args) and flags_ok(args, ACLI_FLAGS)
    if verb == "cd":
        return cd_ok(args) and flags_ok(args, CD_FLAGS)
    if verb in TEXT_ONLY:
        # ⭐ NO FLAG CHECK, BECAUSE THERE IS NO FLAG THAT COULD MATTER. `echo` writes to stdout
        # and nowhere else, whatever it is handed. Flag-checking it refused `echo "--- x ---"` -
        # the dequoted argument starts with `-`, so rule 4 read a section header as a flag - and
        # that one shape was on dozens of the commands this hook exists to unblock.
        return True
    allowed = READONLY_FLAGS.get(verb)
    if allowed is None:
        return False
    return flags_ok(args, allowed)


def _repo_root() -> str:
    """The repo this hook was loaded from. `CLAUDE_PROJECT_DIR` first (run-hook.sh exports it),
    then this file's own location - `<repo>/.agents/hooks/` and `<repo>/.claude/hooks/` are the
    same depth, so the master and the deployed copy resolve identically."""
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return env
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def compile_rule(inner: str) -> "re.Pattern[str]":
    """One `Bash(...)` permission rule, as the matcher Claude Code applies to it.

    `Bash(cmd:*)` is an open-ended PREFIX; `Bash(git -C * status:*)` also carries a wildcard.
    ⛔ The open end is anchored at a TOKEN BOUNDARY when the prefix ends in a word character, so
    `Bash(cat:*)` cannot be satisfied by `category-tool x`. Where the prefix ends in punctuation
    (`Bash(python3 .agents/scripts/:*)`) the continuation is the rest of the path, so no boundary
    applies.

    ⛔ NEITHER THE WILDCARD NOR THE OPEN END MAY CROSS A SEPARATOR - both are `[^;|&]*`. A rule
    the operator wrote to describe ONE command must never be stretched to cover a chain, and the
    first cut of this used a bare `.*`: `Bash(git status:*)` then matched the whole string
    `git status && git checkout main`. Inside this hook it was harmless (rule 2 guarantees an
    atom has no separator in it), but it is the exact fail-open that would appear the moment
    anything else asked this matcher a question - and it is what made the first before/after
    measurement report 82% already-covered against an operator who was approving nine calls in
    ten.
    """
    open_ended = inner.endswith(":*")
    base = inner[:-2] if open_ended else inner
    rx = re.escape(base).replace(r"\*", "[^;|&]*")
    if open_ended:
        rx += r"(?:\s[^;|&]*)?" if (base and base[-1].isalnum()) else "[^;|&]*"
    return re.compile("^" + rx + "$", re.S)


def _rules_from(path: str, key: str) -> list[str]:
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception:  # noqa: BLE001 - absent or malformed settings means no grant, not a crash.
        return []
    out = []
    for entry in (data.get("permissions", {}) or {}).get(key, []) or []:
        if isinstance(entry, str) and entry.startswith("Bash(") and entry.endswith(")"):
            out.append(entry[5:-1])
    return out


@functools.lru_cache(maxsize=1)
def permission_rules() -> tuple[tuple["re.Pattern[str]", ...], tuple["re.Pattern[str]", ...]]:
    """(allow, blocked) — the operator's OWN rules, which is what makes (B) a proof and not a
    second opinion. `deny` and `ask` are read too: an atom the operator marked either way is
    refused outright, so this hook can never talk over a decision they already recorded."""
    root = _repo_root()
    files = [
        os.path.join(root, ".claude", "settings.json"),
        os.path.join(root, ".claude", "settings.local.json"),
        os.path.join(os.path.expanduser("~"), ".claude", "settings.json"),
    ]
    allow, blocked = [], []
    for path in files:
        allow += _rules_from(path, "allow")
        blocked += _rules_from(path, "deny") + _rules_from(path, "ask")
    return (tuple(compile_rule(r) for r in allow),
            tuple(compile_rule(r) for r in blocked))


def already_allowed(atom: str) -> bool:
    """Condition (B): would this atom, sent on its own, have auto-approved with no prompt?"""
    allow, blocked = permission_rules()
    if any(p.match(atom) for p in blocked):
        return False
    return any(p.match(atom) for p in allow)


def permitted(command: str) -> bool:
    if not command.strip():
        return False
    atoms = split_atoms(strip_null_redirects(command.strip()))   # rules 1, 2, 3 and 8
    if not atoms:
        return False
    for text, sep in atoms:
        tokens = tokenize(text)
        if not tokens:
            return False
        verb = tokens[0]
        if not VERB_RE.match(verb):              # bare name, never a path, never quoted
            return False
        if not verb_ok(verb, tokens[1:], sep == "|"):   # (A), rules 4-6
            return False
        if not already_allowed(text):                   # (B)
            return False
    return True


def main() -> None:
    payload = json.load(sys.stdin)
    if payload.get("tool_name") != "Bash":
        return
    command = payload.get("tool_input", {}).get("command", "")
    if not isinstance(command, str) or not command.strip():
        return
    if not permitted(command):
        return
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "allow",
        "permissionDecisionReason": "read-only chain: every atom is an allow-listed read-only "
                                    "command that already matches one of your own permission "
                                    "rules on its own",
    }}))


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001 - a convenience hook must never become a blocker.
        pass
    sys.exit(0)

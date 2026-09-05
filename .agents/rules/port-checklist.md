---
name: port-checklist
description: "Fires at PLAN TIME, before a line is written, whenever a file being changed exists in more than one repo — a lobby→project port, a project→lobby port back, or a fix landing in two copies at once. Six checks, each with the command that answers it: (1) use a path git gave you exactly as git gave it — never re-normalise `--git-common-dir` / `--git-path`; (2) `printf`, not `echo`, for any operator-facing line; (3) on a write, verify the FILE, not `$?` — `|| exit` on the redirect and no success banner above the check; (4) no `.agents/rules/` path a thin repo does not carry (project-law.md); (5) it runs on BOTH sides of the one PC — `python3` vs `python`, and `core.hooksPath` is per-machine config; (6) hooks stay repo-local and the port needs the target repo's OWN Jira key (project-law.md § carve-out). Runs in BOTH directions. From the AVCH-59 retro (2026-08-15): all four divergences came from this list, and three of them were reachable at plan time."
trigger: model_decision
triggers: [port, both repos, exists in more than one repo, lobby to project, project to lobby]
# Intent-shaped: no glob can catch it, because the trigger is what the operator ASKS,
# not what gets opened. Antigravity judges `description:` against the request;
# `.agents/hooks/rule-trigger.py` matches these keywords and injects a pointer.

---

# Port Checklist — the six questions to answer BEFORE a line is written

> **Why this exists (AVCH-59 retro, 2026-08-15).** Every port so far — AVCH-54, then AVCH-59 — took
> an afternoon and found the *same class* of defect: the centre's copy is subtly wrong the moment it
> runs in a **submodule**, on **Windows**, inside a **worktree**, in a **thin** repo. All four AVCH-59
> divergences came from one short list. Nothing at plan time asked these questions, so they surfaced
> at review, or in production on the other machine. *"A port checklist run at plan time would have
> caught three of those four before a line was written."*

**⭐ It runs in BOTH directions.** Lobby → project and project → lobby are the same operation with the
copies swapped. The AVCH-59 → lobby port back (SCC-164 Parts C and D) is a port, and reading this
one-way is how you skip the half you are actually doing.

## When it fires

At plan time, when either is true — the trigger is **mechanical**, never self-reported:

- the plan's SCOPE names a file that **exists in more than one repo**, or
- the ticket says the work is a port.

Answer it with the diff, not with memory:

```bash
git diff --no-index -- <lobby>/<path> <project>/<path> ; echo "differ=$?"   # 0 identical, 1 differ
```

**Both copies differ → every check below is due, and the plan carries a section answering them.**
Identical → say so in the plan in one line and move on.

## The six checks

### 1. A path git gave you is used exactly as git gave it

`--git-common-dir` and `--git-path` answer **relative** in a plain main checkout and **absolute** in a
worktree — and git-for-windows spells absolute as `C:/Users/…`, which does not match a `/*` glob. A
`case … /*) … *) prepend the repo root` normaliser therefore *corrupts* the path on Windows and in a
submodule, where the answer was already absolute. Use it as given; `cd "$REPO_ROOT"` is what makes a
relative answer safe.

```bash
grep -n 'git-common-dir\|--git-path' -A 6 <script>      # any `case … /*)` below it is the defect
cd <repo> && git rev-parse --git-common-dir                # main checkout, worktree, submodule: 3 answers
```

### 2. Operator-facing text goes through `printf`, never `echo`

`echo` interprets escapes on some shells and **truncates at `\c`** — `.claude\commands` has one, so the
line silently ends mid-sentence. The PowerShell console additionally *renders* correct UTF-8 as
mojibake, so a screenshot proves nothing: check the bytes.

```bash
grep -n 'echo .*\\' <script>                            # any backslash in an echo'd literal
```

### 3. On a write, verify the FILE — not `$?`

A redirect that fails still leaves the shell's exit code from the last *command inside* the block, so
the success banner prints over a file that was never written. Put `|| exit <n>` on the redirect itself,
and never print "done" above the check that it is.

```bash
grep -n '} *> *"\?\$' <script>                          # every redirect needs `|| exit`
grep -n 'minted\|written\|installed' <script>           # is the banner ABOVE or BELOW the check?
```

### 4. No `.agents/rules/` path the target repo does not carry

A thin project holds **only its own** law — see [`project-law.md`](project-law.md) (tier table +
§ Binding). A message or `Read` that names `.agents/rules/<x>.md` resolves in the lobby and resolves to
nothing in the project. Point at the centre's copy by name, or drop the path.

```bash
grep -n '\.agents/rules/' <script>
ls <target-repo>/.agents/rules/                         # what actually exists there
```

### 5. It runs on BOTH sides

`python3` on the Ubuntu side, `python` on the Windows side — a hook hard-coding either exits **127 silently** on the other,
which reads as success. And `core.hooksPath` is **local config**: it does not travel with a clone, so a
fresh checkout of the target has no gates at all until it is armed on that machine.

```bash
command -v python3 python                               # on each side
cd <target-repo> && git config --get core.hooksPath        # empty = every gate is OFF here
```

### 6. Hooks stay repo-local, and the port needs the target's OWN key

Enforcement that git executes inside a repo cannot be centralised without disarming it — the carve-out
in [`project-law.md`](project-law.md) § *repo-local enforcement*. The corollary that gets missed: the
ported hook reads that repo's `.agents/jira.conf`, so the port needs a work item in **that project's**
Jira key, not the one the source repo used.

```bash
ls <target-repo>/.githooks <target-repo>/.agents/scripts/git-hooks
cat <target-repo>/.agents/jira.conf                     # which key must the port's ticket carry?
```

## What the plan must show

One section, named for this rule, answering all six for the files in SCOPE — an answer per check, with
the command output that produced it. **A check answered "n/a" needs the reason.** `/smh-plan-task`
writes it; `/smh-self-audit` and `/cicd-self-audit` refuse a port plan that lacks it.

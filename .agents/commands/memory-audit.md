---
description: Audit the shared memory store (`_artifacts/_memory/`) and compact it — ground-truth every candidate memory against the live repo (does the rule/script/flag it names still exist? is the thing it calls CLOSED actually gone?), then propose retire / merge / compress with bytes freed and apply ONLY what the operator approves per item. Triggered by `tests/test_memory_store.py` at 90% of the 25 KB index cap; also runnable any time recall feels noisy. Never auto-deletes.
---

# /memory-audit — Ground-truth the memory store, then compact it

> **Rules in force for this command:**
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never force-push
> - `.agents/rules/artifacts-always-first.md` — the proposal at Step 4 IS this command's plan gate
> - root `AGENTS.md` §7 — the memory store is READ-ONLY outside the sanctioned flows. **This command
>   is one of them**, and only for the items the operator approves in Step 5.

**What this is.** `_artifacts/_memory/MEMORY.md` is loaded whole into **every session, on every
platform, on both machines** before any work happens. That makes it the one document in the system
whose upkeep everyone pays for and nobody owns. This command is the owner.

**Why it is not part of `/update-maps-indexes` any more (SCC-68).** It used to be that workflow's
Step 3.9, and it therefore never ran: nobody reaches for a *map* command because memory feels
heavy. The store reached 99.5% of cap with its remedy parked somewhere no one had a reason to go.
Upkeep now hangs off the **gate**, which runs in `run_all` on every close-out, on every machine.

**Why it is not `sudo-*`.** Every `/sudo-*` command binds `sudo-target-resolution.md` — *"operates
on exactly ONE target — never the lobby."* The store lives in the lobby. Same family as
`/sync-agents`, `/update-maps-indexes`, `/new-project`, and the naming is the permission.

## 🛑 MANDATORY RULES (before you start)

1. **Nothing is deleted, merged, or rewritten without per-item approval.** Not "the batch looks
   fine" — each retirement is its own yes. A wrong deletion destroys exactly the recall the store
   exists for, and unlike a bad edit it leaves no trace in the running system.
2. **A dirty memory file you did not write is another session's work in flight.** Two lanes share
   one store. **Park it or leave it** — never sweep, delete, or commit it under this audit. If
   `git status` shows memory files you did not touch, say so and exclude them from scope.
3. **Never raise the cap yourself.** 25 KB ≈ 6,000 tokens charged to every session on every platform
   before a single useful token. If the index will not fit, first assume the index is carrying content
   that belongs in the memory *files*. Compress; don't budget more. The cap moved once (20 → 25 KB,
   2026-08-09) **on the operator's ruling, after an audit proved the store had no slack** — that is the
   only way it ever moves. Report the finding; let them decide.
4. **The signals are not verdicts.** Everything the gate hands you is a candidate. A `CLOSED` row
   whose lesson still bites stays. A dangling `[[link]]` is the sanctioned way to mark a memory
   worth writing later. Ground-truth first, always.

## Step 0 — Bind the store

The store is `_artifacts/_memory/` **in the lobby** (`Sudo_Hatter_Command`) — the repo path is
canonical because it travels via git. Claude's `~/.claude/projects/<slug>/memory` is a per-machine
symlink *into* it, never the mechanism. Echo `Store: <abs path> | index: <bytes> / 25600` before
any work, read from disk, not from belief.

If you are standing in a project rather than the lobby, say so and stop — there is one store.

## Step 1 — Run the floor

```bash
python3 .agents/scripts/tests/test_memory_store.py
```

Mechanical integrity first: index ≤ 25 KB · every link resolves · no orphan files · frontmatter
present. **Any red here is a repair, not a judgment call** — fix it in this pass (add the missing
index line, repair or drop the dead link) and note it in the report as a repair.

The run also prints the **candidate worklist** — `CLOSED`/`RETIRED`/`FIXED` index rows, dangling
`[[link]]` targets, memory bodies over 4 KB. That is your starting evidence, not your conclusion.

## Step 2 — Widen the candidate set

The gate sees the store. You can see the repo. Add what it cannot:

```bash
git -C . log --format='%ad %h' --date=short -1 -- _artifacts/_memory/<file>.md   # per file, last touch
```

- **Stale** — no touch in ~6 months **and** its subject has not changed either.
- **Duplicated** — two memories carrying one idea, usually written months apart by different
  sessions that each thought they were first.
- **Superseded** — a later memory states the opposite ruling. The old one is not history, it is a
  live landmine: whichever the model reads first wins.

## Step 3 — ⭐ Ground-truth each candidate against the live repo

**This is the step that makes the command worth running.** Every memory makes a *claim about the
system*, and claims outlive their subjects in silence. For each candidate, verify the claim:

| The memory says… | Check |
|---|---|
| a rule / script / command / flag exists | is it on disk? `ls`, `grep -rn` — a memory naming a deleted script teaches a dead move |
| something is `CLOSED` / `FIXED` / `RETIRED` | is the subject actually gone? A row marked RETIRED whose subject is still live is **worse than no memory** |
| a ticket or epic is in some state | `acli jira workitem view <KEY> --fields "status"` — states rot fastest of all |
| a path, cache, or surface is at `<location>` | does that location exist *on this machine*, and is it the current one? |
| a `[[link]]` points somewhere | does the target file exist — and if not, is it a deliberate forward reference or a dangler left by a past retirement? |

A candidate that **fails** its check is a retirement or a correction. A candidate that **passes** is
kept, no matter how old — age is not the criterion, truth is.

## Step 4 — Propose (STOP)

One scannable block, **before touching anything outside `_artifacts/`**. Every line carries what it
is, why, and what it frees:

```
## Memory audit — <date>
Index: <before> / 25600 bytes (<pct>%)  →  projected <after> (<pct>%)

### 🔧 Repairs (mechanical, from the gate — I will apply)
- add index line for `<file>.md`                          [orphan; gate red]

### 🗑️ Retire (delete file + index line — git is the undo)
- `<file>.md` — claims `<X>`; verified gone at <where I looked>     [frees ~<N> B]

### 🔀 Merge
- `<a>.md` → into `<b>.md` — same ruling, written twice             [frees ~<N> B]

### 🗜️ Compress (index line only, body untouched)
- `<a>` + `<b>` + `<c>` → one grouped row                           [frees ~<N> B]

### ✅ Kept despite the signal
- `<file>.md` — marked CLOSED but the lesson still bites: <why>

### 🚩 Not mine to touch
- `<file>.md` — dirty in git, written by another session            [parked, excluded]
```

**Wait for explicit approval, per item.** "Approve the retirements but keep #3" is a normal answer
and must be honored exactly.

## Step 5 — Apply only what was approved

```bash
git rm _artifacts/_memory/<retired>.md          # tracked → git rm, so the delete is staged, not just gone
```

Then edit `MEMORY.md`: drop the retired lines, rewrite compressed rows, repoint any `[[link]]` that
referenced a retired memory (a retirement that leaves danglers just moves the mess).

**Compression is a rewrite of the index line, never of a memory body.** If a lesson genuinely needs
shortening, that is a per-file approval of its own — the body is where the content is supposed to
live.

## Step 6 — Verify this machine's harness link

```bash
ls -la ~/.claude/projects/ | grep -i sudo
```

The lobby slug's `memory` entry must resolve into `_artifacts/_memory/`. Missing or dangling → 🚩
**flag it, do not "fix" it by editing the repo**: on a machine without the link, Claude's harness
writes memory to a local orphan dir and the shared store silently stops growing — no error, just
lessons that never reach the other box or the other models. Fix is
`link-memory.sh` / `link-memory.ps1` (migrations kit §1 step 8). Machine plumbing, per-machine,
never travels.

## Step 7 — Re-run the gate, THEN report

```bash
python3 .agents/scripts/tests/test_memory_store.py     # must be N/N, and the trigger block GONE
```

The trigger block still printing means the audit did not achieve its purpose — say so plainly
rather than reporting success. Then print:

`✅ Memory audit complete:`
- `Index: <before> → <after> bytes (<pct>% of cap) — trigger <cleared | still firing>`
- `Retired: <n> (<names>)` · `Merged: <n>` · `Compressed: <n> rows`
- `Kept despite signal: <n>` · `Parked (another session's): <n>`
- `Harness link: ✅ resolves | 🚩 missing — run migrations kit §1 step 8`
- `Gate: <N/N> passed`

Commit with explicit paths under whatever key the current task carries — this command does not own
a ticket, and memory upkeep rides along with the work that prompted it.

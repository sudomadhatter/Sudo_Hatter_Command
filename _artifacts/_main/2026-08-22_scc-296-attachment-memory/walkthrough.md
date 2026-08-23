# SCC-296 — walkthrough

**Lane:** `chore/SCC-296-attachment-memory` · **Ticket:** SCC-296 (Task)
**Tree:** `.claude/worktrees/SCC-296-attachment-memory` · **Base:** `origin/main` @ `be61799`
**Lane type:** lightweight — one memory file and one index line, nothing that can break.
**Verdict:** no LLM review; the deterministic gates are the verdict.

---

## What shipped

**SCC-294 wrote a memory and it never rode the lane.** It sat uncommitted in the shared checkout
after that lane closed — one new file plus one `MEMORY.md` index line. This lands it.

| | |
|---|---|
| `_artifacts/_memory/jira-attachments-need-the-rest-token.md` | **NEW** — `acli` cannot attach a file; upload is REST; the token lives in keychain item `sudo-jira`; both silent-corruption traps |
| `_artifacts/_memory/MEMORY.md` | **one** index line, under *Jira & tickets* |

## ⛔ Why this needed a second lane at all — the symlink points at `main`

This is the failure `AGENTS.md` §7 already records as **SCC-246**, hit again exactly as written.
`~/.claude/projects/<slug>/memory` is a per-machine symlink to **`<repo>/_artifacts/_memory` in the
MAIN working tree** — hardcoded. So an agent working in `.claude/worktrees/<lane>/` still writes its
memory into `main`'s tree, where it misses that lane's PR and sits until someone else cleans it up.

§7's four-step remedy (write · copy onto the lane · restore the shared checkout · commit with
explicit paths) **assumes the lane is still open.** SCC-294 was already merged, Done, and its branch
deleted, so steps 2–4 had nowhere to go. Hence a new key and a new lane — the follow-on shape from
`followon-fixes-are-not-a-new-story`, not a new story.

⭐ **Nothing mechanical caught it.** `task_preflight.py`'s `sync` check reads the **worktree**, and
the worktree was genuinely clean; the dirty file was one directory up, in a tree the preflight never
looks at. The rule exists and is written down — but on this lane it was prose, and prose lost.

## ⛔ What was deliberately NOT touched

`_my_resources/open_tasks/todo_list.md` is also modified in the shared checkout. **It is not this
session's work**, and `AGENTS.md` §8 puts `_my_resources/` off limits without the operator's word.
Left exactly as it was found — the distinction §7 draws is **authorship**, not tidiness.

The shared checkout's `MEMORY.md` also carried a stray blank-line deletion. Only the **one index
line** was carried onto this lane; the whitespace change was dropped rather than shipped.

## A defect found while filing SCC-294's Dev Record — recorded, not fixed here

`jira_feed.py` `scrape_bucket` (`:479`) applies its bullet regex **per physical line**, so it reads
only the **first line** of a wrapped markdown bullet and appends mid-sentence fragments to the Dev
Record. Every walkthrough in this repo wraps at ~100 characters, so the safety-net scrape truncates
on all of them. Visible on SCC-294's Dev Record as short duplicate pitfall lines below the full ones.

Not fixed here on purpose: this lane is `_artifacts/_memory/` only, and `.agents/scripts/*.py` is a
**SOP usage surface** — touching it turns a two-file memory lane into a scripts change with a
mandatory SOP edit and its own tests. It is written down where the next lane will find it.

## Gates

Bare, never piped — each line carries its own exit code, on the **absorbed** tree (`52273a4`):

```
task_preflight.py --fetch --expect-key SCC-296 -> exit 1  VERDICT: clear to close out and merge
                                                  LANE: LOCAL · 0 error(s), 1 warning(s)
                                                  children: SCC-296: no subtasks (board reachable)
run_all.py                                     -> exit 0, 54/54 files passed
workflow_lint.py --toolkit-only                -> exit 0, 0 error(s), 0 warning(s), 8 info
check_maps.py --depth3-only --strict           -> exit 0, silent
check_links.py --base origin/main              -> exit 0, 4 files, 125 path claims, clean
```

⛔ **That `exit 1` was first written down as `exit 0`, and the reason is worth keeping.** The
preflight was run as `… | tail -14`, so `$?` reported **`tail`'s** exit, not the script's — the
exact trap `piping-a-gate-hides-its-exit-code` names, walked into while running a gate whose
purpose is to be trusted. Caught by reading the committed `preflight-receipt.json`, which records
`"exit": 1` from the script itself and cannot be fooled by a pipe. Re-run bare to confirm. **Run
gates bare; the receipt is the second witness.**

The single warning is the worktree, which Step 5 prunes. `_artifacts/` is not an SOP usage
surface, so no SOP hunk was owed and no commit here carries `[sop-ok]`.

⭐ **`check_links.py` is run, not improvised.** SCC-285 landed it *during* this lane and the
close-out door now says so in as many words — *"Run the command; never improvise a matcher. An
improvised one reported 31 unresolved paths of which ~30 were false."* SCC-294, an hour earlier,
used a hand-rolled matcher. It happened to agree (0 broken), but agreeing by luck is not the same
as being right, and this lane used the real one.

## ⚠ Landing order — the SAME collision, twice in one night

**SCC-285 landed as PR #58 while this lane was being built**, and before that SCC-281 landed as
PR #56 during SCC-294. Both times the conflict was one file and the same file:
`_artifacts/_main/INDEX.md`, because two lanes appended a row for the same date. Both times the
resolution is *keep both rows, and count*:

```
common base be61799   -> 181 rows
this lane             -> 182  (+1, SCC-296)
origin/main           -> 182  (+1, SCC-285)
resolution (52273a4)  -> 183
```

That file was the only overlap; everything else auto-merged. SCC-285 also edited **this lane's own
close-out door** and added `.agents/scripts/check_links.py` — which is why the door tells you to
check that the copy you are following is current, and why the preflight was re-read after the
absorb rather than assumed unchanged.

## Your Actions

- [x] The merge itself — lands via this branch's PR.
- [x] The memory file and its single index line — carried onto the lane and committed here.
- [x] The shared checkout — restored, and only the files this session wrote were removed from it.
- [x] The `_artifacts/_main/INDEX.md` collision with SCC-285 — resolved here, both rows kept,
      counted (181 → 183).

Nothing is owed. The `jira_feed.py` scrape defect above is recorded for a later lane, not held here.

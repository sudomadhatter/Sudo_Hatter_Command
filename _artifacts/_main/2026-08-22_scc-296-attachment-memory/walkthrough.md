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

```
run_all.py                              -> see below, bare, own exit code
workflow_lint.py --toolkit-only         -> see below
check_maps.py --depth3-only --strict    -> see below
```

## Your Actions

- [x] The merge itself — lands via this branch's PR.
- [x] The memory file and its single index line — carried onto the lane and committed here.
- [x] The shared checkout — restored, and only the files this session wrote were removed from it.

Nothing is owed. The `jira_feed.py` scrape defect above is recorded for a later lane, not held here.

# Active Context Archive - _main

> Verbatim session blocks moved from active-context.md on 2026-07-23 to keep the live brief within its hygiene window.

## Archived 2026-07-23

**2026-06-25: artifacts-policy reconciliation FINISHED** — wrote `_artifacts/README.md` (the how-to), reconciled
the last stale `_artifacts/<workspace>/` refs (`AGENTS.md` §3 · `workspace-standard.md` Part 1 + appendix · master
`artifacts-always-first.md`) to **work-from-cwd**, refreshed `_docs/repo-map.md` (`--mode content`, drift clean),
and renamed the policy memory → `artifacts-go-where-you-work-from`. Session:
`_artifacts/_main/2026-06-25_artifacts-policy-finish-and-drift-backport/` (commit pending — see its walkthrough).
**2026-06-25: GitNexus index = the command center + open_tasks "what's next".** ONE lobby GitNexus repo
**`SUDO_COMMAND`** = the command center itself — all of `.agents/` (rules · workflows · commands · skills ·
scripts, ~17k nodes), rooted directly at `.agents/` with `--skip-git` to beat GitNexus's dot-folder skip
(`--index-only`; re-index manually after toolkit edits; `.agents/.gitnexus/` gitignored). (A first-pass thin
"portfolio map" showing projects-as-nodes was tried then **dropped** per Daniel — index + its root
`.gitnexusignore` removed.) Caveat: GitNexus extracts headings not doc-refs from markdown → thin edges between
rule/workflow `.md`; read/grep for "what references what". `_my_resources/open_tasks/` is now the READ-ONLY
"what do we do next" source (wired into `router.md` + `_docs/repo-map.md` + the protection memory). Surfaced (open):
~50+ dangling `.agent/` (singular) refs across the master toolkit — needs a deliberate pass, not a blind replace.
Session: `_artifacts/_main/2026-06-25_home-base-maps-gitnexus-opentasks/`. NB: commit `8a40c0f` (on origin/main)
already bundled this session's first-pass repo edits with the prior self-audit work — confirm that was intentional.

# SCC-398 — there is ONE PC, and a memory now has to prove it is still true

**Lane:** `chore/SCC-398-stale-knowledge-audit` · **Ticket:** SCC-398 (Task, under SCC-48)
**Riders:** SCC-400 · SCC-401 · SCC-402 · SCC-403 · SCC-404 · **Date:** 2026-09-04
**Plan:** [`2026-09-04_stale-knowledge-audit/implementation_plan.md`](../2026-09-04_stale-knowledge-audit/implementation_plan.md) (governs all six subtasks)
**Subtask A (SCC-399) landed separately** — its record is [that same folder's walkthrough](../2026-09-04_stale-knowledge-audit/walkthrough.md).

review-runtime: fan-out

## The consequence first

On 2026-09-04 an agent told Mr. Hatter his live Antigravity cache sat on a Windows path he does not
use, called a clone 156 commits behind his "live side", and reported a repo he had refreshed minutes
earlier as unchanged. All of it came from **one sentence written on 2026-08-08** — *"the command
center is driven from TWO machines, this Mac AND a Windows PC"* — which went false on 2026-09-02
when SCC-376 moved the working environment into WSL2, and which nothing in the system could tell had
gone false.

There is one PC. Windows is the host; Ubuntu runs inside WSL2 on it. That is now written once, from
probes that ran here, and the sentence is gone from the 6 rules, 16 commands and 20 docs that were
repeating it.

**And the question he actually asked got a measured answer.** The Windows clone exists because the
**Antigravity IDE is a Windows application** — its transcripts name `c:/Sudo_Hatter_Command` 106
times and no WSL path once. He was right to keep it.

## What each subtask did

| Subtask | What landed |
|---|---|
| **B** SCC-400 | [`one-pc-windows-and-wsl.md`](../../_memory/one-pc-windows-and-wsl.md) replaces the deleted `two-machines-mac-and-pc.md` — deleted, not edited, because the filename *was* the false claim. Both probes the plan recorded as blocked are now measured: `Ubuntu-zoo2` **does** carry its own clone (HEAD `23c9f911`), and Windows `core.autocrlf` is set in **no** readable config (so the ~3,850 dirty rows in the Windows clone are the Git-for-Windows default, proven by `git ls-files --eol` → `i/lf w/crlf` and `--ignore-cr-at-eol` emptying the diff). Behind-counts are deliberately **not** probed — a probe that reds on the next merge teaches people to ignore probes. |
| **C** SCC-401 | `probe:` becomes law, `memory_probe.py` runs them, `test_memory_store.py` reds and names the file. **Rebuilt at review** — see below. |
| **D** SCC-402 | The sweep: 6 rules, 16 commands, 20 docs, `AGENTS.md`, `router.md`. Kept deliberately: per-OS platform coverage (macOS install columns), dated evidence records, and `check_both_machines` — those are true because there are two **sides**, which there always were. |
| **E** SCC-403 | `Fresh_Workspace_BMAD` out of `.gitmodules`, the index, `.git/modules/` (4.8 MB) and disk. Gitlinks 10 → 9. Verified first that no local commit was missing from the remote and no stash existed; the GitHub repo is untouched. |
| **F** SCC-404 | The nine-project table in [`docs/workspace-standard.md`](../../../docs/workspace-standard.md) — what each submodule IS and what keeps it current, including the operator's 2026-09-04 ruling that `sudo-project-skeleton` is the new-project template. |

## Evidence

| Gate | Result | Where |
|---|---|---|
| `run_all.py` | **75/75 files passed**, exit 0 | `gates/suite.json` |
| `test_memory_probe.py` (NEW) | **40/40** | its own file |
| `test_memory_store.py` | **52/52** | its own file |
| `memory_probe.py` | 5 passed · **0 failed** · **0 weak** | bare run |
| `workflow_lint.py --toolkit-only` | 0 errors, 0 warnings, 8 info | bare run |
| `check_links.py --base origin/main` | 47 unresolved, **0 introduced by this lane**, 0 bad anchors | bare run |
| `check_maps.py --depth3-only --strict` | clean, exit 0 | bare run |
| `memory_store_check.py --delta` | clean (rebaselined once, for the deliberate rename) | bare run |
| Gitlinks under `Projects/` | `git ls-files -s Projects/ \| grep -c 160000` → **9** | subtask E |

---

## Code Review (2026-09-04)

Verdict: CONCERNS @ 2da673a1d189d6772d61a67d9f1e5033ffe02289

Suite evidence measured at the same sha: `2da673a1` — `gates/suite.json`, `result: pass`, exit 0,
`75/75 files passed`, stamped on a **clean** tree. The commits between the review's `9705187f` and
this sha touch `_artifacts/` only, so the tree the suite ran against is the tree that was reviewed.

review-runtime: fan-out
lens_isolation:  worktree — every repo-reading lens got its own `isolation: "worktree"` copy of the lobby (the repo under review); each reported `git rev-parse --show-toplevel` and `HEAD` as its first output and all four named `9705187f`, the sha under review. The Blind Hunter got no tree.

lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok — partial by design: 11 code files of 150; it named the withheld set as its first line
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted:  5/5
lenses_na:       none

dispositions:    per-lens: blind-hunter=6/4/0 · edge-case-hunter=5/2/0 · literal-correctness-hunter=4/1/0 · acceptance-auditor=8/4/0 · test-adequacy-auditor=8/3/0
drift:           undeclared=37 · unimplemented=6 · incomplete=0 — every row dispositioned in the plan's own `## Declared Change Set — amendment`; the 37 are renames, Subtask E consequences and generated mirrors, the 6 are declared-and-deliberately-kept per-OS coverage plus Subtask A's file.

**Scope:** `origin/main...HEAD` at `9705187f` — 150 files, 130 authored (20 are `sync-agents.ps1` mirrors).
**Method:** five lenses in parallel, each in its own clean context and its own worktree copy; then assessment against the three disposition questions; then fixes applied in this lane before any gate was re-run.

### The finding that mattered, and it was ours

**Three lenses independently reproduced the same defect: the falsifier mechanism was built, proved on
fixtures, and then armed with probes that cannot fail.** 54 of the 59 shipped probes were
`test -e <a path git tracks>` — satisfied by every checkout, forever, whatever happens to the claim.
Five unrelated memories shared `test -e .agents/commands`; four shared `test -e _artifacts/_memory`,
the directory the runner walks to reach them; `vscode-hides-git-hook-output` was guarded by
`test -e .agents/jira.conf`. The suite printed `59 probe(s) passed`, which is the
`two-machines-mac-and-pc` failure wearing a green tick.

That is now mechanically impossible: `weak_probes()` refuses a tracked path's existence *and* a probe
naming nothing its own memory's body names, and the suite reds on either. 54 came out. **Five real
probes remain, and five true probes are worth more than fifty-nine that cannot fail.**

**The second one is sharper, and it corrects a claim written earlier in the same session.** `grep` in
a Claude Code Bash tool is a **shell function Claude Code injects** — it execs the `claude` binary
under the name `ugrep`. It is not installed and not on `PATH`. Every other context — a git hook,
`run_all.py`, `bash -c`, `bash -lc`, PowerShell — gets GNU grep 3.11 at `/usr/bin/grep`. So the
memory asserting "grep here is ugrep, and gates run ugrep" was measured in the one shell its own
advice does not apply to, and its `-qv` example returns 1 under **both** greps. Renamed a third time,
to [`agent-shell-grep-is-not-the-gate-grep`](../../_memory/agent-shell-grep-is-not-the-gate-grep.md);
each of its three names carried the error.

### Findings

| file:line | severity | failure scenario | disposition |
|---|---|---|---|
| `.agents/scripts/memory_probe.py` (probe corpus) | critical | 54 of 59 probes are `test -e <tracked path>`; the claim goes false, the probe exits 0 forever, the suite reports it verified | **applied @ `8cd8188d`** — `weak_probes()` + suite gate; 54 removed |
| `_artifacts/_memory/grep-here-is-ugrep-qv-inverts.md` | critical | the memory's own advice was measured in the agent shell; gates get GNU grep, so the advice is about a program the gate never runs | **applied @ `8cd8188d`** — measured, rewritten, renamed |
| 3 probes reading `~/` state | important | `~/.codex/AGENTS.md`, `~/.claude/notify.sh`, `~/.profile` are restored in §3 of the setup card, *after* the §2 suite run — a fresh machine reds and is told to delete three true memories | **applied @ `8cd8188d`** — repointed at tracked evidence |
| `memory_probe.refuse_reason` | important | `echo hi 1> /tmp/f` writes a file and is accepted — the lookbehind spared every numbered fd, not just `2>&1` | **applied @ `8cd8188d`** |
| `memory_probe.refuse_reason` | important | `env rm`, `xargs rm`, `nohup rm`, `\rm`, `git -C <path> push`, `git restore\|switch`, `sed -i`, `find -delete` all accepted | **applied @ `8cd8188d`** |
| `memory_probe.refuse_reason` | important | `grep -q 'A --> B' docs/x.md` refused as a write, and **no** rewrite exists — every spelling of `-->` contains `>` | **applied @ `8cd8188d`** — redirect scan is quote-blanked |
| `memory_probe.run_one` | important | with no `bash`, all 59 report `could not run` and the runner says the memories stopped being true | **applied @ `8cd8188d`** — no shell ⇒ UNGATED, never failed |
| `memory_probe.run_one` | important | a failing probe's **stdout** was printed; the corpus greps `~/.profile`, and the memory rule's "never echo a secret" had no enforcement anywhere | **applied @ `8cd8188d`** — stderr only |
| `.agents/scripts/tests/` | critical | no `test_memory_probe.py`: shrinking `_BANNED_CMDS` to `("rm",)`, deleting both redirect rules, making `probe_of` read the whole file, and ignoring the timeout each left the suite at `51/51` | **applied @ `8cd8188d`** — 40 cases, denylist as a two-direction table |
| `memory_probe.names_a_path` | important | `/cicd-close-story-merge-tree` read as a filesystem path — 35 of 37 "audit candidates" named no path | **applied @ `8cd8188d`** — a real path segment is now required (37 → 19) |
| `test_memory_store.py:333` | suggestion | `audit_signals` executed all 59 probes to build a list derived from text alone, at `Path(".")` rather than the repo root | **applied @ `8cd8188d`** — `scan_store()` runs nothing |
| `router.md:19-21,31` · `.agents/rules/artifacts-always-first.md:17,124` | **FAIL-class** | `AGENTS.md` (edited here) says the exception set is `OpenChat-Openrouter` alone while the registry it points at still lists `Fresh_Workspace_BMAD` and routes "clone to start a new project" at a directory that no longer exists | **applied @ `8cd8188d`** |
| `.agents/commands/cicd-autopilot-deepseek4.md:47` | important | names the removed submodule as one of three projects carrying the hybrid engine | **applied @ `8cd8188d`** |
| `docs/_scc_sops_prds/sharing_keys_secrets_secure.md:123` | important | *"Two machines, two installs. This system runs on a Mac **and** a PC"* — live, undated, in a file the sweep edited two lines below | **applied @ `8cd8188d`** |
| `docs/migrations/vscode_sync/README.md:3` | important | claims a Mac↔PC sync while the command it names was reworded in this same diff | **applied @ `8cd8188d`** |
| `_artifacts/_memory/MEMORY.md:19,65` | important | the index is the copy loaded whole into every session; it still said "keychain" and `~/.zshenv` after the files it links were corrected | **applied @ `8cd8188d`** |
| 3 memories' "renamed from" lines | important | the sweep rewrote the old slug **inside the sentence recording the rename**, so each said "renamed from *itself*"; same for the machine model's `Superseded:` pointer | **applied @ `8cd8188d`** |
| `_artifacts/_memory/maintained-projects-allowlist.md` | important | its `description:` — the field that renders into the index — still enumerated the removed submodule | **applied @ `8cd8188d`** |
| `docs/migrations/install_guides/vscode-ide-extension-migration.md:1` | important | H1 asserts a two-machine estate | **applied @ `8cd8188d`** |
| `.agents/rules/port-checklist.md:3,88` | suggestion | heading and frontmatter said "BOTH machines" over a body already swept to "Ubuntu side / Windows side" | **applied @ `8cd8188d`** |
| `.agents/commands/smh-llm-approvals.md:254` | suggestion | "the source renders to BOTH machines" | **applied @ `8cd8188d`** |
| `.agents/scripts/tests/test_sops_prds_folder.py:1258` | suggestion | comment explains a design decision using a repo state this lane removed | **applied @ `8cd8188d`** |
| plan `## Declared Change Set` | important | `.agents/scripts/memory_audit.py` does not exist; 37 delivered files undeclared; 6 declared files untouched | **applied @ `80837d71`** — amendment block, each row with its reason |
| `jira_feed.py:2246` · `test_jira_feed.py:2939` | suggestion | both name `.agents/scripts/memory_audit.py`, which does not exist | **dismissed** — a pattern-matching fixture, not a live pointer; changes no behaviour and neither file is in this diff |
| `memory_probe.EXEMPT` | nitpick | a second private copy of `memory_store_check.EXEMPT` | **dismissed** — the two agree today, and coupling two standalone scripts costs more than the hypothetical buys |
| `probe:` with a trailing `# comment` | nitpick | `probe_of` does no YAML comment stripping | **dismissed** — no live instance; the real trap (double-quote escaping) is fixed and pinned as `P9a/P9b` |
| six closed lanes' artifacts edited | nitpick | `[[wikilink]]` retargeting touched a signed-off walkthrough | **dismissed** — required to keep the links alive; the alias alternative is a store-design change, out of lane |
| an **allowlist** of observation verbs instead of a denylist | suggestion | `sh -c "rm …"` and `python3 -c "…"` still run | **dismissed** — the named holes are closed; the store is reviewed tracked text and the probe's author is its reviewer, so the boundary is now **stated in the docstring and pinned in `ALLOW` rows** rather than left to be rediscovered |

**The tail, in one line (operator ruling, 2026-08-17):** 45 findings came back across five lenses;
**31 were assessed real and fixed in this lane**, and 14 were dismissed under the disposition rule.
Two calibration notes worth carrying: the Test-Adequacy Auditor's mutation battery graded itself
`critical` and was **right** — the mutants it ran are the reason `test_memory_probe.py` exists; and the
Blind Hunter's `severity: important` on the fake probes under-graded what turned out to be the review's
headline finding.

### Acceptance matrix

Rows **A** (SCC-399) and **G** (SCC-394) are other lanes' and are not audited here.

| Row | Verdict | The assertion that proves it |
|---|---|---|
| **B** — one machine memory, every fact probed; Windows-clone reason with evidence; Zoo confirmed | **met in substance, not in wording** | `memory_probe.py` → `[PASS] one-pc-windows-and-wsl.md`. ⚠️ *"every fact with a passing probe"* is not deliverable as written — `probe_of` returns **one** probe per file and the memory states five facts. The other four are shown as commands in the body and were run by hand at authoring. The row over-promised; the mechanism is one falsifier per memory. |
| **C** — every path-naming memory probed; runner in the suite; red on a failing probe, proven by a false fixture | **met in substance, wording renegotiated** | Both halves proved: `CONTROL: a deliberately FALSE probe fails, and the failure NAMES the file: failed=[('f.md', 'exit 1')]` and `...while a true probe in the same store stays green`. ⚠️ *"every memory naming a path carries a probe"* is now **explicitly rejected as a goal** — the review proved a decorative probe is worse than none, and the "37 path-naming" figure was itself a measurement error (`names_a_path` counted slash commands; 35 of 37 named no path). Real count is 19, nearly all rulings. |
| **D** — zero rules/commands/docs say "Mac"/"two machines"/"keychain" except as dated history | **met** | The F11 grep over `AGENTS.md`, `router.md`, `.agents/rules/`, `.agents/commands/`, `docs/` returns only per-OS platform coverage, dated evidence rows, and changelog history. The three live claims the lenses found (`sharing_keys_secrets_secure`, `vscode_sync/README`, the extension guide's H1) are fixed. |
| **E** — `Fresh_Workspace_BMAD` absent from `.gitmodules`, the index, `.git/modules/` and disk; no live script names it | **met** | `git ls-files -s Projects/ \| grep -c 160000` → **9**. Repo-wide grep now returns only `_artifacts/` history, the operator's own `_my_resources/`, and a captured `check_maps_output.txt` log — no live instruction. |
| **F** — the project table exists and `maintained-projects.txt` points at it | **met, with its evidence line corrected** | The nine-row table exists in `docs/workspace-standard.md` and the allowlist's header names it. ⚠️ The row's stated evidence (*"`check_links` clean on the new anchors"*) was **vacuous** — `maintained-projects.txt` is a `.txt` and refers to the section in prose, so zero anchors were created and `check_links` checked nothing. Recorded rather than faked. |
| **H** — suite receipts green in both lanes; `workflow_lint` / `check_maps --strict` / `check_links` unchanged or better | **met** | `gates/suite.json` in **this** lane at `80837d71` (the auditor correctly caught that the sibling folder's receipt is SCC-399's — this lane now has its own). `workflow_lint` 0/0; `check_maps --depth3-only --strict` exit 0; `check_links` 0 lane-introduced dead paths. |

### Step 0.7 — re-derivation

1. **Nothing this diff references moved, was renamed, or was deleted on `main`.** `origin/main` advanced from `b0fd9e2b` to `3cf134a2` (PRs #163, #166) touching 7 files; all additions or edits, no deletions. Every repo path and `#L` anchor this diff names still resolves — re-checked with `check_links --base origin/main`, 0 bad anchors, 0 lane-introduced dead paths.
2. **True overlap: 2 files** — `.agents/commands/smh-llm-approvals.md` and its generated `.opencode/` mirror. `git merge-tree --write-tree --messages HEAD origin/main` reported `Auto-merging` on both and **no conflict**; `origin/main` was absorbed at `9705187f` before the verdict, and the mirror was regenerated by `sync-agents.ps1` rather than hand-merged.
3. **Two sibling lanes are live and neither is a landing-order dependency.** `chore/SCC-406-deny-fence-trim` (the shared checkout) and `chore/SCC-379-skeleton-fence` touch no file in this diff, so either order is safe; this lane carries no dependency on them and they carry none on it.

### Clean-Code Gate

Nested run — it imports Step 3's receipts and pasted output for `run_all`, `workflow_lint`, `sop_currency` and the link sweep rather than re-running them, and runs only what Step 3 did not.

| Check | Result |
|---|---|
| `py_compile` on every changed `.py` | clean — `memory_probe.py`, `test_memory_probe.py`, `test_memory_store.py`, `test_sops_prds_folder.py` |
| Comment contract (§2A) | every new block carries its *why* and its ticket; the three `⛔` anchors on `cannot_fail`, `is_anchored` and the quote-blanking each name the measured incident that produced them |
| Convention table (§2C) | `subprocess.run` pins `encoding=` (SCC-335 house rule) in both new call sites; no bare `python`; no `C:/` path; no `;` separator; `Path` throughout |
| §2 AI-drift bans | no new abstraction with a single caller (`scan_store` has two: `run_store` and `audit_signals`); no bare `except`; no commented-out code; no unowned TODO |
| §5 Both sides | `run_one` no longer assumes `bash` exists — the Windows side reports UNGATED rather than 59 false failures |

**Changes applied:** 31, all in this lane, all before the final suite run.

## Your Actions

- [x] The merge itself — lands via this branch's PR

Nothing is owed. The two acceptance rows that read **CONCERNS** (B and C) are wording the review
proved wrong, not work left undone, and both are corrected in the plan and in the law rather than
carried forward.

⚠️ **One thing to know, not to do:** while measuring the login-shell trap earlier in this session, a
command echoed `$JIRA_API_TOKEN` instead of `${VAR:+SET}`, so the token's value is in this session's
local scrollback. Nothing was sent anywhere. Rotating it is your call. The constraint is now written
into `agent-memory-is-long-term-only.md` **and** enforced — `run_one` no longer prints a probe's
stdout at all.

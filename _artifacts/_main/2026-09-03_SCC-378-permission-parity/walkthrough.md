---
IsArtifact: true
ArtifactMetadata:
  title: SCC-378 - one permission fence, three platforms - walkthrough
  type: walkthrough
  date: 2026-09-03
---

review-runtime: fan-out

# SCC-378 — Fence Antigravity + Gemini as a live platform: permission parity with Claude and Zoo

**Lane:** `chore/SCC-378-permission-parity` · **HEAD at review:** `3f6f42e7` (reviewed diff taken at `59e15eff`; review fixes `744b9f4c`, `96837cf2`, `3f6f42e7`) · **Plan:** [implementation_plan.md](implementation_plan.md) (Audit verdict: GO) · **Child:** SCC-382 (the Mac application, the operator's, separately)

**What changed, in one sentence.** The three terminal-approval fences — Zoo Code's, Claude Code's and the
Antigravity extension's — are now rendered from ONE source and proven to give the same verdict on the same
command, and the Antigravity extension that asked for approval on everything this morning runs the same
fence as the other two, on this machine, with the Mac one apply away.

## Task Checklist

- [x] Step 0 — absorb `origin/main` (SCC-383 had landed: `1909df46`); move the five parked artifacts from the SCC-376 folder into this lane (a filesystem move — git had never tracked them); restore main's outline; first commit artifacts-only
- [x] Step 1 — the checkable list A–G (plan §2)
- [x] Step 1.5 — plan, self-audit GO (7 findings, all baked in), the operator's `approved`
- [x] Step 1.6 — subtasks: nothing beyond SCC-382 clears the branch-and-worktree bar
- [x] Step 2 — RED first: `test_permission_parity.py` 1/19 (only the mirror-identity row passed, because the mirror was identical *before* the edit) — every other row failed because the module, file or sentence did not exist
  - pitfall: a `//` comment INSIDE the Zoo array carried one `"` and desynced the JSONC scanner's string state → `KeyError: zoo-code.deniedCommands` on the first render; the scanner now skips line comments (B12 pins it on a fixture the real file cannot rescue)
  - pitfall: the seed keyed Claude's `Bash(cd:*)` as `cd:*`, so `cd`/`ls`/`cat` looked Claude-only; strip the wildcard before keying (77 families, not 107)
  - pitfall: two derivation bugs found while writing the derivation test — a Zoo path prefix (`backend/.venv/bin/`) got a trailing space it must not have; Antigravity derived rows were not regex-escaped (`.` matches any char)
- [x] Step 3 — GREEN, minimal: matchers · renderer · source (seeded from today's three lists) · apply · `.ps1` call site · `/smh-llm-approvals` retarget + byte-copied opencode mirror · SOP rows + changelog · INDEX rows · guide §1/§13/§3A · two memory entries. 46/46
  - the `.claude/settings.json` render ran ONCE unsandboxed (Claude protects its own settings inside its sandbox), as the plan said it would
  - the battery's A-block reds were the MEASUREMENT: 3 Antigravity deny gaps closed in-lane (HEAD:main, `--prune=now`, `mkfs.ext4`); 17 cross-platform disagreements pinned by name as the operator's rulings (see below)
- [x] Step 3 — mutants declared FROM the code, one sweep: 10/10 killed on the third run (M8 survived twice — see Evidence)
- [x] Step 3 — STAMP: `run_all.py` through the receipt writer, PASS exit 0 @ `5f9ce171`; re-stamped after the review at `3f6f42e7`
- [x] Step 4 — `/smh-code-review` (the `## Code Review` section below): five lenses + verify wave + compound; 16 patches fixed in-lane, 1 decision handed over, CONCERNS
- [x] Step 5 — Dev Record posted to SCC-378 (stage quick-dev); branch pushed; close-out is the operator's (`/smh-close-task-merge-tree`)
- [x] Close-out — `origin/main` absorbed (nine commits: SCC-384, SCC-385; the guide auto-merged, the artifacts index kept both sides' rows, the doc graph regenerated); `landing_mode: partial` declared because SCC-382 (the Mac apply) lands in its own lane, so SCC-378 stays open until it does
- [x] The merge itself — lands via this branch's PR

## Evidence

| Row | Assertion | RED | GREEN |
|---|---|---|---|
| **A** one battery, three matchers, identical verdicts | `test_permission_parity.py` block `A ·` | `[FAIL] A0 permission_matchers imports` · `[FAIL] A1 the three rendered lists exist: antigravity.json=False` | A0–A11 all `PASS`; A2: 52 destructive → deny on Zoo and Antigravity; A4: 35 ceremony → allow on all three; A5: 12 unknown → ask on all three; A6 parity holds; A11 every pinned disagreement still live |
| **B** one source, three rendered outputs, drift is red | block `B ·` | `[FAIL] B0 permission_render imports` · `[FAIL] B1 the source exists` | `permission_render: in sync (zoo, claude, antigravity)` · B6 one-char Zoo edit → `file has 1 row(s) the source does not render ['git  ']` · B7 added AG row → names `antigravity.json` · B8 render ⊇ baseline (6 rows superseded by name) · B10a–c derivation · B11 `write()` round-trip · B12 scanner on a one-quote comment |
| **B** the seed reproduces today | one-off `seed_families.py` (scratchpad, never in the renderer — B9) | — | Zoo render SET-equal to `origin/main` (124 allow / 105 deny; `test_zoo_permissions.py` 25/25, `test_guide_currency` green) · Claude render set-equal (141 rows → 140: the duplicate `Bash(cd:*)` collapsed; `test_settings_allowlist.py` 29/29, sentinels A2/A6/B1 intact) · Antigravity render ⊇ the 2026-09-03 hand-built list (`+10 / -6`: 6 old spellings replaced by their anchored-regex form) |
| **C** the apply is scoped and safe | block `C ·` on a temp store | `[FAIL] C0 antigravity_permissions_apply imports` | C1 grants replaced · C2 `remoteControlHostname`, `conversationWidth`, `plugins` preserved · C3 backup once · C4 second apply keeps the backup · C5 `--status` → `in sync with tracked file` · **live Ubuntu store:** `--apply` → `in sync with tracked file` (allow=116 deny=204 at build; **re-applied after the review: allow=116 deny=384**, in sync; *Live store* below) |
| **D** rendering rides sync-agents, runs without pwsh | block `D ·` | `[FAIL] D1 …calls permission_render.py` · `[FAIL] D2 -Status path runs --check` · `[FAIL] D3 …rc=2` (no script) | D1 live `.ps1` code calls it · D2 `Invoke-PermissionRender -Check` in the `-Status` block · D3 standalone `--check` rc=0 here (no `pwsh` on this machine — the `.ps1` half is exercised on the Mac) |
| **E** `/smh-llm-approvals` writes the source, reads Antigravity | block `E ·` | `[FAIL] E1/E2/E3/E5` | E1 `families.json` · E2 `permission_render.py` · E3 `~/.gemini/config/config.json` · E4 opencode mirror byte-identical (`cmp`) · E5 commands/INDEX row 65 rewritten · `workflow_lint.py --toolkit-only` → 0 errors · `test_command_surfaces.py` 322/322 |
| **F** the record tells the truth | block `F ·` | `[FAIL] F1…F5` | F1 guide's two Antigravity rows carry no "retired" · F2 store + both rule types named · F3 "sandbox does NOT auto-approve" recorded · F4/F5 memory entries corrected · `check_maps.py` clean for `.agents/permissions/INDEX.md` |
| **G** suite green through the receipt writer | `gate_receipt.py run --task SCC-378 --gate suite` | — | `[PASS] suite exit=0 28.0s @ 5f9ce171` → `gates/suite.json` · `dirty_paths` = the operator's own seven pending `.claude/` files (his restored files, awaiting his commit on `main`; see *Your Actions*) |

**Mutation sweep** (`mutation_sweep.py --table sweep.json`, third run, restore verified against the
pre-sweep sha and bytes):

```
KILLED  M1 antigravity deny never fires            ← A8   KILLED  M6 antigravity derived deny drops the env twin ← B10c
KILLED  M2 antigravity token match unanchored      ← A7   KILLED  M7 only: scope ignored                      ← B10b
KILLED  M3 zoo shortest prefix wins                ← A9   KILLED  M8 JSONC scanner stops skipping comments    ← B12
KILLED  M4 claude judges the compound as one       ← A10  KILLED  M9 backup overwritten on every apply        ← C4
KILLED  M5 --check always clean                    ← B6   KILLED  M10 apply writes a second key               ← C2
```

M8 survived runs one and two, and the reason is worth keeping: the real Zoo list carries **nine** rows with an
escaped `\"` — an odd count — so once a planted comment flipped the scanner's string parity, those nine flipped
it back before the closing `]`, and the mutant landed on the right bracket by luck of the file's contents. B11
(the real-file round-trip) could never kill it; B12 runs the scanner on a synthetic JSONC with no escapes, where
the one quote desyncs the scan to EOF. A mutant that survives is a finding about the test, not the code.

**Review sweep** (`mutation_sweep.py`, table extended to 25 mutants over 3 files @ `744b9f4c`, then re-run after two
rows were hardened): **25/25 killed by their declared case**, restore verified byte-for-byte, closing full file
58/58. M11–M25 are drawn from the review's own code — the house twin, the cluster class and `.*` tail in
derivation, the three source refusals, the JSONC loader's two comment shapes and trailing comma, `check()`'s
drift-not-traceback, the Claude/Antigravity write branches, the write ORDER, `ensure_ascii`, the `--rendered`
refusal and `status()`'s DRIFT arm. First run: M15 and M24 came back as SWEEP ERRORS (the test file crashed
instead of failing a row) — the two rows now report a raise as red, which is the fix the sweep was asking for.

### Live store

The Antigravity extension's own store on this machine, before and after `antigravity_permissions_apply.py --apply`
(the `--status` lines are pasted from the run):

```
before  status  : DRIFT allow: store-only=0 tracked-missing=0 | deny: store-only=6 tracked-missing=10
apply   backup  : /home/dlohn/.gemini/config/config.json.scc-backup (kept, already existed - the morning's install wrote it)
        wrote and read back: allow=116 deny=204
        preserved keys: ['remoteControlHostname']
after   status  : in sync with tracked file
```

The `6 / 10` is exactly the three deny fixes: six morning spellings replaced by their anchored-regex form, ten
rows added (`HEAD:(main|master)` with its twins, `--prune.*`, `mkfs.*`). Nothing else in the store moved.

### The three-way disagreements (pinned in the battery as KNOWN; each is the operator's ruling)

The three lists were seeded from what each platform decided **before** SCC-378, and this lane changed no Zoo or
Claude decision (plan §5 Q1). Where they disagree, the battery pins the disagreement by name, excludes it from
A2–A6, and A11 demands it stay LIVE — a row that stops being true must be deleted. Each is one source edit and a
render when ruled:

| Command | Zoo | Claude | Antigravity | Where the difference comes from | The row that would settle it |
|---|---|---|---|---|---|
| `rm -fr /tmp/x` | **ask** | ask | deny | Zoo denies `rm -rf` / `rm -r`; the `-fr` spelling asks (never runs) | a Zoo deny `rm -f` — a fence edit |
| `git push origin main` | deny | **allow** | deny | Claude's list allows it on purpose: the fence is `require-push-approval.py` + git-policy | none unless the hook is retired |
| `git add -A` · `git add .` · `git add -u` · `git add --all` | deny | **allow** | deny | Claude's broad `Bash(git add:*)`; the sweep ban is git-policy law + review | narrow the Claude row, or leave to law |
| `git checkout .` · `git checkout -- .` | deny | **allow** | deny | Claude's broad `Bash(git checkout *)`; Zoo denies the spelling | narrow the Claude row |
| `find . -delete` · `find . -exec rm {} ;` | ask | **allow** | ask | Claude allows `Bash(find:*)`; Zoo refuses `find` on purpose (guide §8: `-delete`/`-exec rm` ride behind the prefix) | remove Claude's `find:*`, or accept |
| `npm test` | **ask** | **ask** | allow | promoted on Antigravity this morning; Zoo has `npm run `/`npm ci `, Claude `npm run lint` | `npm test` allow on Zoo + Claude |
| `git push origin HEAD:epic/…` | allow | **ask** | allow | Claude allows `chore/*`, `claude/*`, `main*` pushes, not the `HEAD:epic/` landing (the hook still gates it) | `Bash(git push origin HEAD:epic/*)` |
| `git push origin --delete claude/x` | allow | **ask** | allow | Claude allows `--delete chore/*` only | `Bash(git push origin --delete claude/*)` |
| `git config --list` | allow | **ask** | allow | Claude allows `git config --get:*` only | `Bash(git config --list)` |
| `git clean -n` | allow | **ask** | allow | Claude has no `git clean` row (safe: the dry run asks) | `Bash(git clean -n)` |
| `python3 -m pytest -q` | allow | **ask** | allow | Claude scopes python3 to `.agents/scripts/*`, `-m py_compile`, the venv door | `Bash(python3 -m pytest:*)` |

### The old Windows install's lists, harvested as a measurement (plan §2, ticket line 7)

`C:\Users\dlohn\.gemini\config\config.json` carried a hand-built 27-allow / 37-deny pair from 2026-09-01. Nothing
was copied blind — every word was classed against the source (`python3` and `pytest` were re-classed by hand after
a `py` prefix mis-tag in the first pass):

| Class | Allow (27) | Deny (37) |
|---|---|---|
| already in the source | `git` `gh` `acli` `npm` `node` `ls` `cat` `pwd` `echo` `head` `tail` `python3` (12) | `rm -rf` `git reset --hard` `git clean` `git push --force` `git push -f` `git push origin --delete` (target-scoped on Antigravity) `git branch -D` (target-scoped) `mkfs` `dd` `sudo` (10) |
| Windows / bare spellings SCC-376 retired | `type` `where` `where.exe` `Test-Path` `Get-ChildItem` `dir` `findstr` `winget list` `python` `py` `powershell` `pwsh` (12) | `del` `del /f` `del /q` `rmdir` `rd` `rd /s` `Remove-Item` `Remove-Item -Recurse` `format` `diskpart` `diskpath` `Restart-Computer` `Stop-Computer` `reg delete` `reg add` `takeown` `icacls` `iwr` `Invoke-WebRequest` `Invoke-Expression` `iex` (21) |
| deliberately absent (asks) | — | bare `rm` — Zoo's design: `rm <file>` asks, only recursive spellings deny |
| **NEW — the operator's rulings** | `pytest` `cargo` `ruff` as bare allows (the source has `.venv/bin/python -m pytest` and `.venv/bin/ruff check`; bare `cargo` has no row) | `fdisk` `shutdown` `chmod 777` (source has `chmod -R 777`) `curl` `wget` (both ASK on all three today — denying them is a fence change) `drop table` `drop database` `truncate` (SQL, not shell) |

The folder itself is **not** deleted here — it holds 24 Antigravity conversation databases, five from 2026-09-02,
including the AVCH-114 session the operator named as work still in flight on the Windows clone. Deletion is the
desktop team's, after those two stories land (ticket line 7; *Your Actions*).

### Declared vs. built — the drift, named

- **Cut:** `EDIT .agents/rules/jira.md` — declared to correct "`workitem view` returns `parent`". Measured on SCC-382 at build time: `acli jira workitem view SCC-382 --fields parent --json` **does** return `parent` (→ SCC-378). The rule is right; the plan line and my earlier claim to the operator were wrong. Not edited.
- **Added then reverted (net zero):** `.gitignore` — I ignored seven untracked `.claude/` entries believing them Claude Code runtime files; the operator corrected me (they are his restored files, awaiting commit). Commit `d712b9c5` added, `5f9ce171` reverted with the reason in its message.
- **Hook-staged:** `docs/doc-graph.json` / `docs/doc-graph.md` were regenerated and staged by the commit hook into `05824421` (generated files, never hand-edited).
- **Added, declared by the door not the plan:** `sweep.json`, `task.yaml`, `gates/suite.json`, `.agents/permissions/INDEX.md` (`check_maps.py`: a level-2 folder requires one).
- **Fixed in the renderer beyond the plan's wording:** the JSONC comment-skip; two derivation bugs; both found by tests written first.

## Your Actions

Everything that landed is above; what follows is what only you can decide or do.

- [ ] **The `deny` half is unverified until you run two harmless commands.** In Antigravity, after a window reload, ask it to run **`git push --force`** with `/tmp` as the folder (not a repo, so it cannot do anything even if it runs), then **`cd /tmp && git push --force`**. Both must be **refused outright**, not asked. Three outcomes: (1) both refused — the `deny` array is honoured and the `cd .* &&` twin works, nothing to change; (2) the bare one refused, the chained one asks or runs — the extension reads a line whole and the twin did not match; tell me the exact wording it showed and the twin is respelled in one source edit; (3) the bare one asks — the extension ignores the `deny` array in that file and the renderer's deny output moves to the field it honours (plan §5 Q3), one edit, no battery change. (The review replaced the earlier `git clean -fd` probe: run inside the repo it would have deleted your seven untracked `.claude/` files if the fence had failed.)
- [ ] **DECISION — five push/branch spellings Zoo and Antigravity both auto-approve today:** `git push origin refs/heads/main`, `git push origin -d main`, `git push -d origin main`, `git branch --delete --force main`, `git branch --move main x`. Each is the same operation as a row already denied, in a different token order. Adding them changes a Zoo decision, which this lane's plan froze (§5 Q1), so it is yours: say **"add the five"** and they go into the source as deny rows on both platforms in one edit and one render; say nothing and they stay allowed, recorded in the guide §7 as the prefix residual. My recommendation is to add them. (`git restore --source=HEAD .`, `git checkout origin/main -- .`, `git switch -C main`, `git checkout -B main` are the same class but reach into ceremony Zoo allows today; I would leave those as residuals.)
- [ ] **Your seven pending `.claude/` files** (`hooks/`, `launch.json`, `loop.md`, `output-styles/`, `routines/`, `scheduled_tasks.json`, `workflows/`) sit untracked in the main checkout and this worktree. Commit them on `main` before this lane lands so the landing absorbs them once; the receipt's `dirty_paths` names exactly these and nothing else.
- [ ] **Delete `C:\Users\dlohn\.gemini`** with the desktop team **after** the two in-flight Windows stories land — it holds their 24 conversation databases. The lists inside it are harvested above; nothing else in it is needed.

Owed to you but not holding this ticket: the eleven three-way rulings in the table above (each a one-row source edit
and a render; `/smh-llm-approvals` is the door), the nine NEW rows from the old Windows lists, and the Mac application
(SCC-382, its own ticket, one `--apply` on that machine). The Zoo and Claude project copies under `Projects/*` are
untouched by design — AVCH-116 / AVCH-114 own that port (guide §13).

## Code Review (2026-09-03)

Verdict: CONCERNS @ 3f6f42e7
Suite evidence measured on 3f6f42e7 (`gates/suite.json`, PASS exit 0; the tree is dirty only with the operator's seven untracked `.claude/` files).

review-runtime: fan-out
lens_isolation: worktree
lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- acceptance-auditor · ok
- test-adequacy-auditor · ok
- literal-correctness-hunter · ok — 20 of 33 changed files received (lens_budget standard; 13 withheld and named; one top-up spent on the guide)
lenses_counted: 5/5
lenses_na: none
findings: 1 decision · 16 patch · 0 defer   (1 noise-dismissed · 9 relevance kills)
dispositions: per-lens: blind=8/0/1 · edge=8/0/4 · literal=3/0/2 · acceptance=5/1/4 · test-adequacy=6/0/5 · compound=3/0/0
severity_floor: CONCERNS
drift: undeclared=3 · unimplemented=1 · incomplete=0
notes: verify wave ran (47 raw findings; Evidence Verifier 47/47 verified true, dossier built; Compound Synthesis 3 findings, dossier built); reviewed sha 59e15eff, diff re-taken there; review_level standard; vendor docs fetched for the chain question (antigravity.google/docs/permissions, silent on chains)

**What the review found, in plain terms.** The code that ships is sound where the tests looked, and the weight of the review fell on the Antigravity deny rows themselves. Three lenses independently found the same class of hole: the push, branch, add and config denies were spelled as one literal anchored token each, so a clustered flag (`git push -fu origin main`), an attached value (`--force-with-lease=main:abc`), a scope flag (`git config --local core.hooksPath /dev/null`) or a target Zoo denies by prefix (`git push origin --delete develop`) slipped past the deny and was auto-approved by the broad `git` allow, where Zoo refused each. The compound role then raised the one that matters most: the vendor documents per-token matching on a line's leading tokens and says nothing about `&&`, so if the extension reads a whole line, the house shape every door command takes (`cd <abs> && git <verb>`) begins with the allowed token `cd` and no deny could see past it. Every one of these is closed in-lane and pinned in the battery; the vendor's chain behaviour is the one fact the repo cannot settle, so the render fences the house shape either way and the live probe in `## Your Actions` settles the residual.

**Reviewed → fixed, in this lane, before this verdict** (commits `744b9f4c`, `96837cf2`, `3f6f42e7`):

| # | Finding (merged) | src | sev | Disposition |
|---|---|---|---|---|
| F1 | Antigravity denies as literal single tokens bypassed by clusters, `=`-attached values, scope flags and non-main targets (`-fu`, `--force-with-lease=`, `-Df`, `-Av`, `./`, `--local core.hooksPath`, `--unset`, `user.email`, `--delete origin main`, `HEAD:develop`, `--delete develop`) | blind+edge+compound | important | **fixed** — source renders re-spelled as cluster classes and lookaheads that leave exactly Zoo's re-allows legal; 16 spellings added to DESTRUCTIVE; live store re-applied (allow 116, deny 384) |
| F2 | Antigravity may judge only the leading tokens of a chain — the house `cd <abs> && …` shape would bypass every deny; vendor docs silent | edge+compound | important | **fixed** — `house_twin_prefix` renders every deny behind `cd .* && ` (dead row if the vendor splits, the fence if it does not); A12–A14 pin it; guide §3A.3/§7 record it; the live probe in Your Actions is now house-shaped and harmless |
| F3 | `[A-Z_]+=.*` allow approved ANY uppercase assignment prefix (`HOME=/x rm -rf /`) | blind | suggestion | **fixed** — the named door variables only; `HOME=/x rm -rf /` in UNKNOWN |
| F4 | `_derive_antigravity` emitted a never-matching rule for prefix families (`backend/.venv/bin/` without `.*`) and literal flags for derived denies; B10c pinned the wrong output | blind+compound | suggestion | **fixed** — `.*` tail after a separator, cluster class for a deny's single-letter flag; B10c/B10d assert the derived rows match what the Zoo twins match |
| F5 | Source validation: empty `cmd` was a bare IndexError; a string `render` spread into one-letter Zoo allows (`g`, `i`, `t` → `gcc` auto-approved); duplicate id `deny-git-c` | blind+literal+edge+acceptance | suggestion | **fixed** — `_validate_source` refuses each by row name; B2 checks shape and uniqueness; B2b sees the refusals; second row renamed `deny-git-c-lower` |
| F7 | JSONC shapes VS Code accepts (inline `//` after a value, `/* */`, trailing comma) crashed `check()` and the parity file at B4; `write()` spliced into a block comment | literal+edge | suggestion | **fixed** — quote-aware comment/comma stripping in the loader and scanner; an unreadable file is a DRIFT line naming the file; B13/B14 |
| F8 | Apply: missing `--rendered` tracebacked; non-ASCII store values re-escaped against the docstring | blind+edge+acceptance | suggestion | **fixed** — ERROR line + rc 2; `ensure_ascii=False`; docstring corrected; C2/C7 |
| F9 | AG denies scoped to `main\|master` where Zoo denies every non-chore/claude/epic target | blind+acceptance | suggestion | **fixed** — folded into F1's lookaheads |
| F13 | ps1 sync-path call site unpinned (D1 matched the definition); D2 blind to order | test-adequacy | suggestion | **fixed** — D1 asserts the call line after `Sync-ZooSurfaces`; D4 pins the `$LASTEXITCODE` read |
| F14 | `write()`'s Claude and Antigravity branches never driven | test-adequacy | suggestion | **fixed** — B11 drifts all three files |
| F15 | `status()` never seen saying DRIFT; CLI untested | test-adequacy | suggestion | **fixed** — C6 (DRIFT with counts), C7 (`--apply` refusal); the remaining CLI rc rows dismissed under §6.5 (code correct, symmetry only) |
| F16 | Render `main()` never seen exiting 1; `--root` unpinned | test-adequacy | suggestion | **fixed in part** — D3 now demands rc 0 + "in sync"; a drifted-root rc-1 row dismissed under §6.5 (B6 already proves `check()` red) |
| F19 | sweep.json lacked mutants for the new surfaces | test-adequacy | suggestion | **fixed** — 25 mutants declared from the code, 25/25 killed (see the review sweep under *Mutation sweep*) |
| F22 | Memory `description:` and MEMORY.md hook still taught "not in sync-agents" | acceptance | suggestion | **fixed** — both corrected; F4 greps frontmatter and the hook |
| F23 | Suite receipt stamped two commits before the landing sha | acceptance | suggestion | **fixed** — re-stamped at 3f6f42e7 |
| F26 | `write()` not atomic: from Claude Code the sandbox refuses `.claude/settings.json`, leaving the Zoo list ahead; ps1 swallowed the renderer's exit code | edge+compound | suggestion | **fixed** — all three rendered to text first, Claude file written first (B15 proves a refused Claude write leaves Zoo untouched); ps1 names a failed render |
| F27 | Five push/branch spellings both Zoo and Antigravity auto-approve (`git push origin refs/heads/main`, `git push origin -d main`, `git push -d origin main`, `git branch --delete --force main`, `git branch --move main x`) | edge | important | **DECISION** — adding them changes a Zoo decision, which plan §5 Q1 froze; recorded in `## Your Actions` with my recommendation (add the five); guide §7 names them as the residual until then |

**Dismissed (relevance gate / §6.5), one line each:** F6 `--check` compares sets while `write()` compares order — the next sync corrects it, no verdict changes (blind+literal+acceptance) · F10 Zoo double-space defeats a deny prefix — pre-existing Zoo grammar, Zoo lists unchanged by this lane, shape law (edge) · F11 Zoo `$()` inside a word not scored — the mirror equals the extracted v3.80.1 parser (edge) · F12 Claude mirror does not split on `&`/newline — no battery row, vendor unverified (edge) · F17 Zoo splitter / Claude boundary / AG token-count untested in the new module — code correct, coverage for symmetry (test-adequacy) · F18 `not:` arm, `_dedupe`, A6 redundancy — nitpicks (test-adequacy) · F21 plan rows A/B wording vs KNOWN and containment; Zoo/Claude set-equality unpinned — prose pins, and a pin that expires at merge; the measured values are in the acceptance matrix below (acceptance) · F24 `agy_fence_apply.py` reads a file not in the tree — superseded artifact history (literal) · F25 `write()` with a wrong `--root` tracebacks — ps1 always passes `$HomeRoot` (edge) · **noise:** F20 jira.md row F "never made" — cut on a live measurement, recorded under Declared vs built (acceptance).

**Why CONCERNS and not PASS.** The engine's floor is CONCERNS: two `important` findings were real and fixed (F1, F2) and one `important` is the operator's decision (F27). Independently of the floor, the Antigravity deny half is proven against the mirror and the guide's model, not against the running extension — the repo holds no first-party statement of how it reads a chained line — so the fence's last inch is the two-command live probe in `## Your Actions`. Nothing else holds the ticket.

### Gates (all bare, at 3f6f42e7 unless noted)

| Gate | Result |
|---|---|
| `run_all.py` through `gate_receipt.py` | PASS exit 0 @ 3f6f42e7 (28.8 s at 96837cf2 on the first stamp; re-stamped after the provenance commit) |
| `test_permission_parity.py` | 58/58 (46 before the review; blocks A 15 · B 20 · C 8 · D 4 · E 5 · F 6) |
| `test_command_surfaces.py` | 328/328 |
| `test_settings_allowlist.py` · `test_zoo_permissions.py` | 29/29 · 25/25 |
| `workflow_lint.py --toolkit-only` | 0 errors, 0 warnings |
| `permission_render.py --check` | in sync (zoo, claude, antigravity) |
| `antigravity_permissions_apply.py --status` (live Ubuntu store) | in sync with tracked file — allow 116, deny 384 |
| `mutation_sweep.py` (25 mutants, 3 files) | 25/25 killed by declared case; restore verified; closing full file 58/58 |
| `sop_currency.py` | silent with and without the opt-out (the SOP is in the lane's changed set) |
| `check_links.py --base origin/main` | clean |
| `py_compile` (7 changed `.py`) · `pwsh` parser on `sync-agents.ps1` | OK · 0 parse errors |
| Declared Change Set vs diff | undeclared: `.agents/permissions/INDEX.md` (check_maps demanded it), `docs/doc-graph.{json,md}` (commit hook) · unimplemented: `.agents/rules/jira.md` (cut, measured) · incomplete: none |

### Acceptance matrix (plan §2)

| Row | Verdict | Evidence |
|---|---|---|
| A — one battery, identical verdicts | **satisfied, modulo the 20 named rulings** | A2–A6, A12–A14 green over 66 destructive · 36 ceremony · 13 unknown; KNOWN pins each Zoo/Claude ruling with the row that would settle it (17 at build, +3 `git add` cluster spellings on Claude by the same ruling) |
| B — one source, three renders, drift red | **satisfied** | B4–B7, B11, B13–B15; Zoo allow 124/124 and deny 105/105 set-equal to `origin/main`, Claude 141→140 (one duplicate collapsed) — measured by the review, not pinned (a pin would expire at merge); Antigravity keeps every baseline DECISION (B8, behavioural) with 64 rows re-spelled by the review |
| C — apply is scoped and safe | **satisfied** | C1–C7 |
| D — rides sync-agents | **satisfied (static)** | D1 call site after the Zoo surfaces, D2 `-Status` path, D3 rc 0, D4 failure named; `pwsh` parses the file |
| E — `/smh-llm-approvals` retargeted, mirror exact | **satisfied** | E1–E5, 328/328 surfaces |
| F — the record tells the truth | **satisfied** | F1–F6; the jira.md row was cut on a live measurement (Declared vs built) |
| G — receipt | **satisfied** | PASS @ 3f6f42e7 |

### Clean-Code Gate — PASS

**Machine floor**
- run_all.py       : PASS — exit 0 @ 3f6f42e7 (receipt `gates/suite.json`)
- workflow_lint    : PASS — 0 errors, 0 warnings, 8 info (`--toolkit-only`)
- sop_currency     : PASS — silent on the lane's changed paths with and without `[sop-ok]`
- py_compile       : PASS — 7 changed `.py`; `pwsh` parser on `sync-agents.ps1` 0 errors
- link + anchor    : PASS — `check_links.py --base origin/main` clean
- door parity      : n/a — no command added, renamed or deleted (the opencode mirror is byte-identical, E4)
- lint / types     : not applicable to this repo (no venv, no ruff, no tsc)

**Findings**
| # | file:line | Severity | Category | Finding | Disposition |
|---|-----------|----------|----------|---------|-------------|
| 1 | .agents/scripts/permission_render.py:73 | CONCERNS | comment-contract | the review's new docstrings named the date but not the ticket key | applied (`3f6f42e7`) |

The AI-drift half imports Step 1's findings above (no re-walk). Conventions: both-machines probe (`python3 → python → py`) intact; no generated file hand-edited; no new gate; artifacts in the tree. Tail: 1 finding came back, 1 real and fixed, 0 dismissed.

### Step 0.7 — re-derivation

1. `origin/main` = `1909df46` = merge-base; unchanged since the lane was cut, so the radius is the lane's own 35 files and nothing has moved under it.
2. Zero overlap with any live sibling; `merge-tree` clean; the only sibling (SCC-383) landed before the lane opened.
3. Level standard, because the radius holds the propagation engine (`sync-agents.ps1`), the SOP, a command surface and three new scripts — more than three source files.

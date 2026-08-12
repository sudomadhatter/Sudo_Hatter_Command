---
IsArtifact: true
ArtifactMetadata:
  title: SCC-123 evidence_extract.py - pure-Python fact-fetcher (pack + findings modes)
  type: implementation_plan
  date: 2026-08-12
---

# SCC-123 — `evidence_extract.py`

Lane: `chore/SCC-123-evidence-extract` · tree `.claude/worktrees/scc-123-evidence-extract` · off `main` @ `8556e81`
Ticket: SCC-123 (Subtask of SCC-116) · Spec: [SCC-116 plan §SCC-123](../2026-08-12_scc-116-house-review-engine/implementation_plan.md)
Port source: `github.com/Agent-Field/pr-af` @ `8593130` — `src/pr_af/evidence.py` (629 lines),
`src/pr_af/config.py` (351), `src/pr_af/orchestrator.py` call sites 799 / 892 / 977.

## What this is, in one paragraph

The review engine's lenses currently cold-read the repo: they open files one at a time over many
turns, and what they never happen to open, they never reason about. This script does that reading
**in code, with zero LLM calls**, and hands the lens a dossier up front. Two modes: `--pack` primes
a lens *before* it reviews (the changed files' content plus who imports them), and `--findings`
pulls ground truth *for* a finding after one is asserted (the code at the line, its callers, the
diff hunk, cross-referenced files). Nothing here judges anything — it fetches facts. SCC-127 is
what consumes `--findings`; SCC-125 is what wires `--pack` into the lens prompts. **This subtask
ships the script and its guard only.**

## Ground truth — two corrections to the spec, found by reading the port SHA

**① The evidence caps are not in `config.py`.** The SCC-116 plan says *"caps re-read from pr-af
`config.py` AT THE PORT SHA."* They were read, and at `8593130` `config.py` carries **no evidence
caps at all** — only the on/off toggle `evidence_pack_reviewers` (`config.py:77`). Every cap lives
in `evidence.py` itself, as module constants and function defaults, and the orchestrator calls
`build_dimension_pack` with **no overrides** (`orchestrator.py:799-800`), so those defaults *are*
the effective caps. The plan's caution ("post-#68 caps moved") was right about direction and wrong
about destination: they moved out of config, not around inside it. The plan's stated numbers
(6 files / 400 lines / 16k chars, semaphore 10, ≤8 identifiers, 10s, byte-bounded cache, stop-words)
are all **confirmed correct** — only the sentence naming their location was wrong.

The full set this port pins, each verified at the port SHA:

| Cap | Value | Source @ `8593130` |
|---|---|---|
| pack: files | 6 | `evidence.py:486` default, uncalled-over at `orchestrator.py:799` |
| pack: lines per file | 400 | `evidence.py:487` |
| pack: total chars | 16000 | `evidence.py:488` |
| pack: import-context slice | 1200 chars | `evidence.py:516` |
| per-finding concurrency | 10 | `evidence.py:152` (`asyncio.Semaphore(10)`) |
| identifiers per finding | 8 | `evidence.py:28` |
| seconds per repo-wide search | 10 | `evidence.py:279`, `:421` (grep `timeout=`) |
| file cache | 128 MiB / 2000 entries | `evidence.py:23-24` |
| primary snippet context | ±30 lines | `evidence.py:166` |
| caller snippet context | ±5 lines | `evidence.py:301` |
| caller snippets kept | 10 total, 10 per identifier | `evidence.py:205`, `:305` |
| cross-ref files | 10, read from line 1 ±30 | `evidence.py:208-209` |
| blast-radius snippets | 5, ±10 lines | `evidence.py:470-478` |
| imports / imported-by listed | 30 each | `evidence.py:430-431` |
| diff hunk | 200 lines | `evidence.py:372-377` |
| skip dirs | 6 | `evidence.py:57` |
| text extensions | 31 | `evidence.py:58-90` |
| identifier stop-words | 35 | `evidence.py:91-127` |

**② The `IMPORTED BY` gap is not only TS/JS — it silently swallows this repo's own Python.**
The spec flags `_path_to_module` (`evidence.py:582`) for having no TS/JS branch. Reading it against
*this* repo found the same failure on the Python side. It builds one dotted name from the repo-root
path, so `.agents/scripts/wf_common.py` becomes `.agents.scripts.wf_common` — a string that appears
in no file anywhere, because the scripts here are imported as bare `wf_common` off a `sys.path`
entry (`tests/_harness.py:14-15`). Every safety-net script in this repo would report
`IMPORTED BY: none`, which reads as *"nothing depends on this"* — the most dangerous possible
false statement to prime a reviewer with. Both branches are fixed, for one reason (§Design D2).

## Design decisions

**D1 — Pure Python search, and the guard is behavioural, not a source grep.**
pr-af shells out to `grep` twice (`evidence.py:259`, `:401`). This system runs on a Mac and a
Windows PC, so a `grep` subprocess is banned. The replacement walks once with `os.walk`, prunes
`_SKIP_DIRS`, and matches compiled `re` patterns over the byte-bounded file cache — the same work
`grep -RIn` does, in-process. The **file-path list is built once per repo and reused**; only the
reads are repeated, and those hit the cache. That is why this is not slower than 8 grep children.
⛔ The proof that no subprocess grep survives is not `"subprocess" not in source` — a comment
inverts that check (a known house pitfall). The source ban ships too, as a cheap tripwire, but it
is not the evidence.

⛔ **CORRECTED DURING THE BUILD — `PATH=""` proves nothing, and this plan said it did.** The
method written here was *"run with `PATH` emptied so no `grep` binary is reachable."* That is
false, and it is left on the record rather than quietly swapped because it is the more useful
half. When `PATH` is empty CPython does **not** give up: `subprocess` falls back to
**`os.defpath`** (`:/bin:/usr/bin`), so `/bin/grep` is still found and still runs. A guard built
that way passes against a script that shells out on every call — it proves the opposite of what it
claims. The real proof installs a `sitecustomize.py` on `PYTHONPATH` that makes process creation
itself raise, so a shell-out **dies** instead of silently succeeding, and asserts byte-identical
output under it. It ships with a control row that shells out deliberately and must die, because a
blocker that is not installed is indistinguishable from a script that never spawns.

**D2 — `_path_to_module` is replaced by per-importer resolution.** (As built, that is
`_python_module_names` + `_python_importers` on the Python side and `_ts_importers` +
`_resolve_specifier` on the TS side — the single name `_import_specifiers` this plan first used
was never shipped, and the review caught the repo map pointing at the phantom.)
A single module string cannot express how JS/TS names a module. The function returns the set of
ways a file can be referred to, and matching is exact rather than fuzzy:

- **Python:** the full dotted path from the repo root **plus** the longest suffix that forms a real
  package chain — walking up from the file, each parent must contain `__init__.py` to stay in the
  name. `src/pr_af/evidence.py` (no `src/__init__.py`) → `pr_af.evidence` *and* `src.pr_af.evidence`;
  `.agents/scripts/wf_common.py` → `wf_common`. This is Python's own import semantics, not a
  heuristic. Matched forms: `import X`, `from X import ...`, and `from <parent> import <leaf>`.
- **TS/JS:** each candidate importer's own specifiers are extracted (`import … from '<s>'`,
  `export … from '<s>'`, `require('<s>')`, `import('<s>')`) and **resolved against that importer's
  directory** — `./foo`, `../bar/foo`, with or without extension, and `index.*` for a directory.
  A specifier is a hit only when it resolves to the target path. Alias specifiers (`@/…`) resolve
  against alias roots read from `tsconfig.json` / `jsconfig.json` `compilerOptions.paths`.

> ⚠️ **AUDIT FINDING F3 — the alias root is not at the repo root, and assuming it is reproduces the
> exact bug this subtask exists to kill.** The one real frontend in this system keeps its config at
> `Projects/AGY_AVIATIONCHAT/frontend/tsconfig.json` with `"@/*": ["./src/*"]` — so `@/x` means
> `frontend/src/x`, not `src/x`. Therefore: **alias roots resolve relative to the directory of the
> config file that declared them**, and those config files are discovered by the same bounded walk
> (skip-dirs pruned) rather than assumed at the repo root. The bare `src/` default survives only for
> a repo that carries no `tsconfig`/`jsconfig` at all. That file parses as strict JSON today, so the
> stdlib reader is enough; a file that does not parse degrades to the default per D6 and says so.

Resolving per importer instead of matching a basename is the whole correctness of this: `Foo.tsx`
matched by name would claim every `Foo` in the repo imports it.

**D3 — pr-af's direct-join-first path normalization is ported, the naive one is not.**
`_normalize_relative_path` (`evidence.py:522`) strips a `<repo-name>/` marker anywhere in the path,
which mangles any path where the repo name recurs as a directory (their own comment,
`evidence.py:496-498`). The fix they applied in `build_dimension_pack` — try the direct join first,
fall back to normalization only when that file does not exist — is ported to **every** path entry
point here, not just the pack.

> ⚠️ **AUDIT FINDING F4 — the cap-override flags are cut.** An earlier draft of this plan gave
> `--pack` three flags (`--max-files`, `--max-lines`, `--max-chars`). No acceptance item requires
> them, and *"SCC-126 might want a capped mode"* is a hypothetical future, which the over-engineering
> gate names as a red flag rather than a justification. The caps are module constants. SCC-126 adds
> the flag it actually needs, when it needs it — and a constant is cheaper to prove than a flag.

**D4 — the caller's diff is a unified diff, not pr-af's `dict[str, str]`.**
pr-af receives per-file patches from its own diff engine. Our callers hold a single unified diff, so
`--diff <path>` (or `-` for stdin) is split per file in this script. Same downstream semantics:
locate the hunk containing the finding's line; fall back to the file's first 200 patch lines.

**D5 — concurrency by `ThreadPoolExecutor(max_workers=10)`, over an immutable path index.**
The direct analogue of pr-af's `asyncio.Semaphore(10)` without asyncio. The repo path index is built
**before** the pool starts, so no thread mutates shared state; the file cache takes a lock. Output
is sorted and deterministic **while the searches complete inside their 10s deadlines** — the same
inputs then give byte-identical output, which is what makes the guard's discrimination proofs
meaningful. ⚠️ Scoped during review: on a repo big enough to blow a deadline, the cut-off is
load-dependent by design (bounded seconds, not bounded files), so a partial result is possible and
now announces itself with a stderr note. The guard's determinism row runs on a fixture the deadline
cannot touch.

**D6 — it degrades, it does not die.** SCC-116 §SCC-127 sets the contract: *"extractor is code, not
a lens — if it dies, the verifier runs cold; it does NOT cap the verdict."* So: a missing file, an
undecodable file, a search that blows its 10s deadline, a malformed finding — each yields an empty
or partial field and a note, never a traceback. Exit **2** is reserved for a genuine usage error
(bad flags, unreadable findings JSON), because that is the operator's mistake, not the repo's.

**D7 — the GitNexus decision is recorded in the module docstring**, per spec: fresh search beats
the GitNexus index *here on purpose* — that index is machine-local, does not travel via git, is
stale after a pull, and misses attribute-dispatch call sites. Written where the next person to think
*"this duplicates GitNexus"* will actually read it, with the standing instruction not to grow this
into a blast-radius tool.

## Acceptance — the checkable list

1. **`.agents/scripts/evidence_extract.py` exists** and runs on `python3` and `python` (stdlib only,
   no third-party import; its own labels ASCII, with both output streams forced to UTF-8
   `errors="replace"` because repo content is arbitrary and a cp1252 console must degrade a
   character, not kill the run — review H-5).
2. **`--pack` mode** emits the primed dossier and honours all four pack caps: ≤6 files, ≤400 lines
   per file with a truncation notice, ≤16000 chars total, import context sliced at 1200.
3. **`--findings` mode** emits a JSON **list** of packages in finding order, each carrying
   `finding_title` plus the six `EvidencePackage` fields (`primary_code`, `caller_snippets`,
   `cross_ref_snippets`, `diff_hunk`, `import_context`, `related_code`), and honours ≤8 identifiers,
   ≤10 caller snippets, ≤10 cross-ref files, ≤5 blast-radius snippets. ⚠️ **This item originally
   said "keyed by finding title" and that shape was wrong**: duplicate titles are the expected case
   for a multi-lens fan-out over one diff, and a title-keyed dict silently collapsed them onto one
   package carrying the wrong file's code (review H-2). Corrected before any consumer existed —
   SCC-127 builds against the list.
4. **No `grep` subprocess** — proven by running with **process creation blocked at the interpreter**
   (a `sitecustomize.py` on `PYTHONPATH` that raises) and getting byte-identical output, in **both**
   modes, not by grepping the source. ⚠️ **This item originally said "with `PATH` emptied" and that
   was wrong** — see D1: CPython falls back to `os.defpath`, so `/bin/grep` stays reachable and the
   check would pass against a script that shells out every time. A control row asserts a deliberate
   shell-out really does die under the blocker, or "no spawn happened" is unfalsifiable.
5. **`IMPORTED BY` is non-empty where an import genuinely exists, and empty where it does not** —
   for a flat `sys.path` Python script, a packaged Python module, a TS relative import, a TS
   `index.*` directory import, and a TS `@/` alias import; and a file that imports a *different*
   module does not appear.
6. **Caps, skips and stop-words discriminate** — a `node_modules/` match is absent, a stop-word-only
   finding body yields no callers, a 12-identifier body searches at most 8.
7. **It degrades instead of dying** — missing repo path, missing file, binary file, malformed
   findings JSON entry: exit 0 with an empty/partial field; a usage error is exit 2.
8. **Deterministic** — the same inputs twice give byte-identical output.
9. **Registered** — a row in `.agents/scripts/INDEX.md` and a row in the SOP's §10 table
   (see §SOP below); `run_all.py` picks up `tests/test_evidence_extract.py` by auto-discovery.
9b. **Both suite counts are true after this lands** — measured, not believed. Operator ruling,
   2026-08-12: the SOP is referenced in real use and a wrong number there is a defect, not cosmetics.
   Today they are both already wrong — the SOP says *"646 checks across 16 files"* and
   `.agents/scripts/INDEX.md` says *"262 cases across 8 files"*, against a measured **17 files**.
   This lane makes it 18, so a stale count is a number **this change makes more wrong**; correcting
   both is a consequence of the change, not a drive-by. ⚠ The mechanism is worth recording because
   the gate is not at fault: `.agents/scripts/tests/` is an explicit exemption
   (`sop_currency.py:82`), so SCC-122's new test file moved the total from 16 to 17 inside a commit
   that was **correctly** exempt end to end. A blocking gate cannot catch this — there is nothing to
   block. Closing it needs a nagging check, which is **its own ticket, not this one**.
10. **The guard can fail** — every content check ships a counter-example and is proven to reject it
    (the SCC-122 lesson, applied to a script instead of markdown). ⚠️ **AUDIT FINDING F5:** for a
    *script*, the counter-example is **inverted output**, never an absent file. `--pack` over zero
    files legitimately prints nothing and exits 0 — correct for the script, and lethal for a guard
    that asserts only on the exit code, because that guard scores a clean green against a script
    that does nothing at all. Every check asserts on **content**.
11. **A path whose repo name recurs still resolves** (D3) — a fixture repo containing a directory
    named after the repo itself yields the same package as one that does not. This is the failure
    pr-af documented in its own source and the reason the naive normalizer is not ported.
12. **The GitNexus decision is in the module docstring** (D7) — required by the SCC-116 spec;
    checkable by inspection and asserted by the guard, so a later refactor cannot quietly drop it.

## SOP currency — the call, made now rather than at commit time

`.agents/scripts/*.py` is a usage surface (`sop_currency.py:77`), so the commit is refused unless
`docs/_scc_sops_prds/workflows_testing_SOP.md` is staged with it. `[sop-ok]` is **not** taken here.
§10 of that page calls its table *"the live list"*, and a new script in `.agents/scripts/` missing
from it makes that sentence false. The row will say plainly what this one is: **not a gate** — it
refuses nothing and the operator never types it; it is the engine's fact-fetcher, and it is listed
so the list stays honest. The `[sop-ok]` opt-out is for changes that alter no usage; this alters the
inventory the page claims to hold.

⛔ **Operator ruling, 2026-08-12 — do not re-litigate this at commit time.** An earlier draft offered
`[sop-ok]` as an alternative if the operator preferred to keep §10 to commit-blocking checks. That
offer was withdrawn on his word: *the SOP is a document he actually reads and references, the gate
exists precisely so it does not go stale, and weakening it is not on the table.* The row goes in.

## Verification

```bash
python3 .agents/scripts/tests/test_evidence_extract.py    # red first, then green — run bare
python3 .agents/scripts/tests/run_all.py                  # N/N files, exit 0
python3 .agents/scripts/workflow_lint.py --toolkit-only   # 0 errors, 0 warnings, exit 0
python3 -m py_compile .agents/scripts/evidence_extract.py
python3 .agents/scripts/sop_currency.py --paths <changed> --message "<subject>"
```

Every gate run **bare** — a piped gate returns the pipe's exit code, not the gate's. Red-first
evidence is per-check discrimination, not "the file did not exist yet".

⚠️ **AUDIT FINDING F2 — `run_all` is `N/N`, and N is not written down here.** The draft said `18/18`
(17 today plus this lane's one). The live sibling lane `chore/SCC-118-server-side-main-gate` already
carries **three** new test files, so 18 is wrong the moment either lane lands. A hardcoded total is a
check that must either lie or break; the suite prints its own total and that number outranks any
sentence in this plan. The walkthrough records the number the run actually printed.

## Boundaries

- **Script + guard + registration only.** No caller is rewired: `--pack` reaches the lens prompts in
  SCC-125, `--findings` reaches the verify wave in SCC-127. The engine's step files are **not**
  edited here — step-02 already names this script as future work and that text stays true.
- **No LLM call, no network, no writes outside stdout.** It reads a repo and prints.
- **Not a blast-radius tool** (D7). Not a GitNexus wrapper. Not a linter.
- **pr-af's noise/worthiness gate is not ported** at any layer — standing epic ruling, recall over
  precision, recorded so nobody adds one later "for free".
- Files touched: `.agents/scripts/evidence_extract.py` · `.agents/scripts/tests/test_evidence_extract.py`
  · `.agents/scripts/INDEX.md` · `docs/_scc_sops_prds/workflows_testing_SOP.md` · this artifact dir.
- Sibling lane `chore/SCC-118-server-side-main-gate` is live and **the overlap is confirmed, not
  hypothetical** — see F1 below.

## Self-Audit (2026-08-12)

Mode: **PRE-WORK.** Right-size: **Full** — the plan adds a file under `.agents/scripts/`, which is a
usage surface behind an armed commit gate, and a sibling `chore/*` lane is live.
Repo and branch echoed from `git rev-parse`, not from belief:
`Repo: scc-123-evidence-extract | Branch: chore/SCC-123-evidence-extract` @ `8556e81`.

**Phase 0 — scope, list, traceability.** Change set is five paths (§Boundaries), all additive except
two doc rows. Traceability run **both ways**, and it caught two gaps that are now closed: D3
(path normalization) and D7 (the GitNexus docstring) traced to **no acceptance item** — they are now
items 11 and 12. No acceptance item lacked a plan step. Lane check: the change set touches none of
`backend/ frontend/ firebase/ functions/ mobile/ .github/`, so this is genuinely Task work and closes
through `/smh-close-task-merge-tree`.

**Phase 1 — blast radius.** Cleared, one line each: no command, rule or skill is added, so there is
no door and nothing for the four platform caches · `sync-agents.ps1` copies `commands`/skills/
workflows only and never mirrors `.agents/scripts/` to a project, so there is no propagation debt ·
no rule is added or cited, so `workflow_lint._RULE_POINTERS` is untouched · a brand-new script has no
caller in `.githooks/` or `git-hooks/` · `_artifacts/_memory/` is untouched · no file is moved,
renamed or deleted, so no Markdown link or `#L` anchor can be orphaned. **Not cleared: the sibling
lane** — F1.

**Phase 2 — over-engineering gate.** One tripwire fired and the step was **cut** (F4). The
*new-script* tripwire was tested and does **not** fire: four scripts here walk a tree
(`check_maps`, `generate_doc_graph`, `parallel_check`, `link-worktree-assets`) and not one extracts
code context for a reviewer, so there is no host to grow a subcommand on; GitNexus is an MCP index,
already ruled out on the record in D7 for reasons that are properties of the index, not preferences.

**Phase 3 — pre-mortem.** The other machine: stdlib only, no interpreter name hardcoded anywhere, and
the guard spawns via `sys.executable` (`tests/_harness.py:37`) — ✅. A fresh clone: this ships no gate
and no arming marker, and the new test joins `run_all` by auto-discovery, so there is no setup step
that can be skipped — ✅. Empty input reading as PASS: **the live risk**, now F5 — ✅ once applied.
Escape hatch: n/a, not a gate. Rollback: purely additive; a revert is a revert. Irreversible steps:
none — no delete, no rename, no history rewrite, no Jira transition beyond the standard `start`.

### Findings

| # | Where | Severity | Failure scenario | Disposition |
|---|---|---|---|---|
| F1 | SOP §10 table | important | `chore/SCC-118-*` is 2 commits ahead with a clean tree and **adds two rows to the very table this plan adds a row to**; it also edits `parallel_check.py` and this lane's own close-out command. Both lanes editing one file is fine; both *unaware* of it is the failure — and a conflict discovered at merge time lands on `main`. | **recorded + ordered** — SCC-118 is further along and should land first. Either way this lane **absorbs `origin/main` before its review**, not at merge time, and re-applies the table row against the moved text. |
| F2 | plan §Verification | important | A hardcoded `18/18` becomes false the moment either lane lands, and a total that must lie or break is a check nobody trusts. | **applied** — `N/N`; the suite's own printed total is the authority. |
| F3 | plan §D2 | important | `@/` defaulted to a repo-root `src/`; AGY's config is at `frontend/tsconfig.json` with `"@/*": ["./src/*"]`, so every aliased frontend import would resolve to nothing and `IMPORTED BY` would read `none` — **the exact silently-empty defect this subtask exists to fix**, reintroduced by the fix. | **applied** — alias roots resolve relative to the declaring config's own directory; configs are discovered by the bounded walk. |
| F4 | plan §D3–D4 | important | Three cap-override flags traced to no acceptance item — "for flexibility", which the gate names a red flag. | **applied — cut.** Caps are constants; SCC-126 adds what it needs. |
| F5 | plan §Acceptance 10 | suggestion | `--pack` over zero files correctly prints nothing and exits 0, so an exit-code-only assertion scores green against a script that does nothing — the SCC-122 failure in script form. | **applied** — every check asserts on content; counter-examples are inverted output, never an absent file. |
| F6 | `smh-close-task-merge-tree.md` | nitpick | SCC-118 edits this lane's own close-out command; running it from memory would run last week's steps. | **recorded** — re-read the command body at close-out time. |

### Four gates

- **Verification strategy present?** Yes — every acceptance item names the command or inspection that
  proves it, and item 10 governs how the proofs themselves are proven.
- **Anything irreversible?** No. Additive only; no delete, rename, force-push or `main` merge here.
- **Any step vague enough that the builder guesses?** One was — the alias root — and F3 pinned it to a
  measured file rather than a convention.
- **Convention fit?** Anchored: stdlib-only ASCII scripts, one test file per script, `INDEX.md` row,
  SOP §10 row, artifacts in `_artifacts/_main/<date>_<slug>/`, `chore/<KEY>-<slug>` off `main`.

```
Audit verdict: GO
```

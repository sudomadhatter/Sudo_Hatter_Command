# Memory index

<!-- One line per memory: link + a short hook. Detail lives in the file. Keep under ~140 lines.
     Related memories share a line rather than getting one each — every file stays linked. -->

## ⛔ Read first
- [TWO machines: Mac AND PC](two-machines-mac-and-pc.md) — every shared doc is read on both; `python3` vs `python`; `core.hooksPath` is per-machine → gates silently OFF on a fresh clone.

## Project stores
<!-- Paths stay BACKTICKED, never markdown links: check_store() resolves every markdown link to a
     .md file by BASENAME against THIS store, so linking a project index would read as a dead link
     to a file that plainly exists. Do not write the literal link form here either - this comment
     is scanned too, and the first draft of it tripped the check it was written to warn about. -->
Settled project-only facts are relocated OUT of this index into the project's own store (SCC-73) —
this section is the signpost. Working in one? Read its store too; it is not loaded for you.
- **AGY_AVIATIONCHAT** → `Projects/AGY_AVIATIONCHAT/_artifacts/_memory/` — the entitlement claim + fail-closed authz, sprint/epic state, Cloud Run + ops surfaces, the test-harness and machine gates, Firestore write hazards.
- **NEXgen-VR-Director** → `Projects/NEXgen-VR-Director/_artifacts/_memory/` — no memories yet.

## Jira & tickets
- [Jira is LIVE (SCC + AVCH)](jira-integration-live.md) — `acli`, already authed; every branch/commit carries a key; gate ARMED, wrong-project key rejected.
- [Cross-repo work = a ticket PER REPO](cross-repo-work-needs-a-ticket-per-repo.md) — widening a project's `jira.conf` is ruled out in writing; and the key comes from the `epic/*` branch, never from the BMAD epic number.
- [`To Do Next` IS the queue](to-do-next-is-the-queue.md) — lead every "what's next" with it; `todo_list.md` is RETIRED as an agent source; the doc's `Blocked` doesn't exist (it's `Blocking`).
- [VS Code hides hook output](vscode-hides-git-hook-output.md) — a warn-only hook looks like clean success; ship hooks ARMED.

## ⛔ AGY data safety — AGY-scoped, kept HERE on purpose
<!-- Ruled 2026-08-11 (SCC-88): AGY-only by subject, so a later sweep reads these as unfinished
     business. They are not. They guard real production data — do not "finish" the move. -->
- [Corpus IS the asset](agy-corpus-is-the-asset.md) — real-user data is a revenue line; demo data is placeholder by design.
- [Archive, never delete](agy-archive-never-delete-ruling.md) — no delete affordance ever ships; removal = archive + `revoked` in one call. ⚠ Its price: BY-ID→BY-FIELD lookups make every superseded doc a live duplicate.
- [Real NDA-signed users](agy-has-real-nda-users.md) — production `users/` is NOT test data; delete only from an allow-list.

## Sprint, stories & close-out
- **Reading the board** — [it recommends stale work](sprint-dependency-map-recommends-stale-work.md) (lags the YAML; check status first) · [⛔ scrum board RETIRED 08-07](sudo-update-scrum-board-five-zones.md) (SCC-13; recovery ref + the SCC-56 spec are inside).
- [`parallel-ok` is a SET property](parallel-ok-is-a-set-property.md) — ① can't rule it (siblings don't exist yet); moved OUT of ① to on-request SCC-56 `/sudo-parallel-check`. `quick-dev` + `blocked` stay.
- **Multi-lane landing** — [lanes fix one finding](parallel-lanes-fix-the-same-finding.md) (re-diff the epic branch; the SET rule binds on file OVERLAP) · [close-out shape](multi-lane-closeout-board-merge-shape.md) (flip from the STORY FILE) · [landing ≠ close-out](landing-is-not-closeout.md) (check git BEFORE closing out).
- [⭐⛔ Operator acts in WORDS; agent does EVERY board write](review-status-means-needs-operator.md) — ALL lanes: `approved` / "its done" / a command trigger a ceremony and the agent types every status inside it; `review` = blocked-on-operator ONLY; a flow leaving the operator a manual Jira edit is BROKEN by definition.
- [Status-flip contract](story-status-flip-contract.md) — BMAD/AVCH stories; read as WHEN never WHO: `done` only inside the operator-invoked close-out, typed by the agent running it — the rule bans self-certification, not agent typing.
- [Follow-ons are NOT a new story](followon-fixes-are-not-a-new-story.md) — no worktree/board key; fix on the epic branch (or `chore/*` off main).
- [Close-out is the sign-off](close-out-command-is-daniels-signoff.md) — an operator-invoked sudo-* command IS the sign-off; never punt back.
- [active-context budget](active-context-pointer-budget.md) — ≤20 KB ≈ 5k tokens; entries born as ≤3-line pointers; stale text DELETED.
- **Scoping discipline** — [settled decisions are not gaps](settled-decisions-are-not-gaps.md) (never file a ruled-on decision under "limitations") · [recon reframes scope](recon-reframes-story-scope.md) (the feature already existed ×3; ground-truth by BEHAVIOR) · [test-debt = characterization](test-debt-stories-are-characterization.md) (retrofit tests pass green-first).
- [TEA retrofit (CLOSED)](tea-retrofit-active-initiative.md) — hub node only; lessons live in the linked memories.

## Git, machines & worktrees
- [git merge wedges Next dev](git-merge-wedges-next-dev-tailwind.md) — a merge under `npm run dev` wedges Tailwind.
- **Per-machine, never travels** — [env migration kit](env-migration-kit.md) (clone first, restore second) · [secrets layout is operator-owned](secrets-bundle-layout-is-operator-owned.md) (never reorganize; use his copy) · [`.zshrc` invisible to automation](zshrc-is-invisible-to-automation.md) (shared env → `~/.zshenv`) · [gitconfig didn't travel](gitconfig-never-migrated-to-the-mac.md) (`autoSetupRemote` can't retro-fix old branches).
- [Commit and push are ONE action](commit-and-push-are-one-action.md) — never end a step unpushed or dirty; verify `0 0` + clean per repo.
- [⛔ Backticks in `-m "…"` EXECUTE](commit-message-backticks-execute.md) — a message quoting a git command RUNS it; it created a branch mid-commit. Use `-F <file>`.
- [⭐ Git branch model + the main gate](git-branch-model-standard.md) — the prefix names the WORK; `main` is the only destination and the epic branch is OPTIONAL scaffolding. TWO doors reach main (`/cicd-push-e2e`, `/smh-close-task-merge-tree`) — `/cicd-update-sprint-memory` is NOT one. Gated mechanically since SCC-77 by `.githooks/pre-push` + a single-use token.
- [⛔ Nothing guards the merge TARGET](nothing-guards-the-merge-target.md) — every gate checks what you merge FROM; a bare `git merge` after a `cd` landed production work on a sibling lane and reported success. `-C` on every call; recovery is `--ff-only`, never reset.
- [⛔ One invocation = ONE merge](one-shot-permission-persists-in-context.md) — the close-out's body stays in context and reads like standing permission; 6 merges rode 1 sign-off. Merge-ready → STOP and hand back.
- [⭐ Main merge needs the operator's VERBATIM words](main-merge-needs-operator-verbatim-approval.md) — since SCC-37 (08-14) the minter refuses without `--operator-approval '<their exact words, this turn>'`; stage everything, CI green, then PARK — ⛔ never SOLICIT the words, the operator initiates; one landing = one quote.
- [⭐ Blocking gates need a QUOTED ruling](blocking-gates-need-a-quoted-ruling.md) — a new gate that can block a shipping path is new LAW: its own plan heading + the operator's words; a derived corollary is a proposal, never law.
- [Hook `ask` = DENY in auto mode](hook-ask-becomes-autodeny-in-auto-mode.md) — gates main only; reads pass, mutations die; retry once, then hand over the rule.
- [Pruned worktree blocks re-add](pruned-worktree-leaves-a-blocking-shell.md) — the empty dir blocks `worktree add`; only PowerShell deletes it.
- [Worktrees skip gitignored assets](worktrees-do-not-inherit-gitignored-assets.md) — copy auth_keys/ + .env; junction node_modules; `npm ci` for E2E.
- [GitHub 408 on satellite wifi](github-408-on-satellite-uplink.md) — operator flies; push dies mid-upload while reads pass; never a hook/gate/limit — chunk via scratch-ref commits or wait for landing.

## Testing
- **A green or a red can lie** — [a red can die pre-assertion](red-test-can-die-before-its-assertion.md) (a failure in SEEDING looks identical; read WHICH line raised) · [stubbed children = vacuous green](stubbed-children-make-green-vacuous.md) (mocking its panels proves NAVIGATION, only) · [a piped gate hides its exit code](piping-a-gate-hides-its-exit-code.md) (`| tail` → `$?` is TAIL's; run gates bare) · [zsh doesn't word-split gate args](zsh-does-not-word-split-gate-args.md) (`--paths $VAR` = ONE arg → false exit 0; `${PIPESTATUS[0]}` is bash-only; `grep -E` reads `\|` literally) · [`echo` truncates at `\c`](echo-truncates-at-backslash-c.md) (`.claude\commands` has one; use `printf`).
- **Source-grep guards are blind THREE ways** — [comments invert them](comment-literals-invert-source-grep-tests.md) (a comment with the pinned literal matches FIRST) · [they can't see ORDER](source-grep-guards-cannot-see-order.md) (a guard moved after the write it protects still passes) · [prose-pinning is vacuous](prose-pinning-guards-are-vacuous.md) (SCC-125: guards pinned the DESCRIPTION, the opposite-meaning file scored 323/323; pin the WIRING and fail the mutants FIRST — same-context authoring confirms, never falsifies).
- **Toolchain pins** — [rules tests need Java](firestore-rules-tests-need-java.md) (brew `openjdk@17`; JAVA_HOME in `~/.zshenv`) · [Node 26 breaks vitest jsdom storage](node-26-breaks-vitest-jsdom-storage.md) (run Node 22 LTS).
- **BDD** — [Vision Lock right-sized](bdd-vision-lock-rightsized.md) (lock conversation mandatory, standalone pytest-bdd opt-in) · [sync step needs asyncio.run](bdd-sync-step-needs-asyncio-run.md) (a skip-guarded RED masks it).
- [coverage `source` ignores paths](coverage-source-silently-ignores-file-paths.md) — use `source_pkgs`, never file paths.
- **Risk + certification** — [priorities matrix](test-priorities-matrix.md) (P0 100 / P1 80 / P2 50 / P3 20%; P0+P1 need E2E) · [certification at shipping SHA](test-certification-at-shipping-sha.md) (②→③ `certification-<story>.json`).
- **Secrets in tests** — [live-guard needs @live](test-live-guard-needs-live-marker.md) (or the guard is swallowed) · lesson from the closed Gemini-key leak: **`setdefault` is the wrong idiom for seeding a secret** — it defers to an exported real key; assign unconditionally in every conftest.
- [full-suite contention](vitest-full-suite-contends-across-lanes.md) — locks per-STACK; bg shells die on chat close.
- **Spec + fixture conventions** — [eval negative controls](eval-harness-negative-control-convention.md) (`_negative_control:true` + `NC_` id) · [E2E gate fiction](e2e-gate-fiction-test-guardrails.md) (report-only gate hid a fiction spec) · [ATDD mocks match the contract](atdd-mock-shape-must-match-backend-contract.md) · [red-file hosts expansions](red-file-hosts-expansion-tests.md) (ONE per tier; extend, never fork) · [domain-gated fixtures](domain-gated-fixtures-web-verify.md) (verify against PRIMARY sources).
- [Windows-authored code hides POSIX bugs](windows-authored-code-hides-posix-bugs.md) — chmod, `C:/` paths, `;` PATH joins, `robocopy`, bare `python`; 3 of 7 printed SUCCESS.
- [JWT last-char tamper is a no-op](jwt-tamper-last-char-is-a-noop.md) — that char carries 4 bits; mutate leading chars instead.

## Code-change hazards
- [New read regresses siblings](new-read-on-shared-endpoint-regresses-siblings.md) — run the whole endpoint suite, not just your test.
- [Shared registration entangles](shared-registration-file-entangles-stories.md) — registry.py carries sibling hunks; staged imports need staged modules.
- [Relocating drops mount guards](relocating-drops-mount-guards.md) — moving a conditional into a render guard drops mount preconditions.
- [Destructive re-verify reads FRESH](destructive-reverify-must-read-fresh.md) — a cached re-check no-ops the delete, and it looks like success.

## GitNexus
- **The index is a stale cache** — [machine-local](gitnexus-index-not-actually-live.md) (doesn't travel via git; every call MUST pass `repo:`) · [verify after pull](gitnexus-verify-index-fresh-after-pull.md) (`indexed_commit == HEAD` or fail-safe to the full suite) · [impact() misses attr-dispatch](gitnexus-impact-misses-attribute-dispatch.md) (0/LOW for `self.<attr>.<method>()`; grep-verify LOW).
- **Search blind spots** — [grep skips gitignored projects](grep-skips-gitignored-projects.md) (blind to `Projects/` from the lobby root) · [relocated links are mis-pathed](relocated-doc-links-are-mispathed-not-dead.md) (a broken link in a copied doc = the target moved).

## Toolkit & sync
- **Where law lives** — [center owns workflow law](thin-projects-center-owns-workflow-law.md) (no vendored toolkit; binding a project MEANS reading its `.agents/INDEX.md`, or STOP) · [repo-local enforcement never centralizes](repo-local-enforcement-never-centralizes.md) (hooks + `jira.conf` + BMAD tomls stay in the repo they gate) · [`platforms: []` = NOWHERE](platforms-empty-list-means-nowhere.md) (omit the key = all four).
- **The non-Claude platforms** — [Codex is the 4th](codex-is-fourth-platform.md) (reads AGENTS.md + skills natively) · [Antigravity uses workflows](antigravity-uses-workflows-not-commands.md) (12k limit SOLVED via auto-emitted launchers; never byte-golf).
- **Sync scope since 08-07** — [covers .agents not docs](toolkit-sync-covers-agents-not-docs.md) (LOBBY + caches only) · [maintained-projects is a LINT worklist](maintained-projects-allowlist.md) (sync no longer reads it).
- [Installed ≠ maintained](toolkit-installed-but-deliberately-unmaintained.md) — B-L-WorldWide + BRKN_Tattoos frozen on purpose; not gaps.
- **Map/graph tooling is a CACHE** — [map-drift recorder](map-drift-recorder.md) (a post-commit hook journals drift; not truth) · [doc-graph UNC hang](doc-graph-unc-hang-and-scope.md) (rebuild bare, never widen `--root`) · [check_maps falsely STALEs AGY](check-maps-all-false-stale-agy.md) (the fan-out omits AGY's ignore list) · [⛔ AUTO-STALE is ALWAYS false in a worktree](check-maps-stale-is-false-in-worktrees.md) (the label is the CWD basename; its printed remedy ships the lane name to main).
- **The command surface** — [center → child skills](command-center-sudo-skills.md) (`/sudo-*` are skill-launchers) · [BMAD wrappers are opencode-only](bmad-wrappers-are-opencode-only-bridges.md) · [_AP twins drift](sudo-commands-have-ap-twins-that-drift.md) (fix one, diff the twin) · [/team-onboarding is built-in](team-onboarding-is-claude-builtin.md) (a CLI built-in).
- [⭐ ONE door per platform per command](one-door-per-platform-per-command.md) — command = brain, a GENERATED launcher skill = the door for Claude AND Codex; `.claude/commands` + `~/.codex/prompts` RETIRED; hand-authored skills always win; gated 13/13.
- **Doc + board law** — [SOP currency gate](sop-doc-currency-gate.md) (ARMED: a usage-surface change without `sudo_workflows_testing.md` is REJECTED; `[sop-ok]` opts out) · [rules read in place](rule-org-single-source-audit.md) (the center's `.agents/rules/`) · [board narrative → history/](board-narrative-lives-in-history.md) (bare state; a note on a finished row is a lint ERROR) · [enforcement scripts](workflow-enforcement-scripts.md) (`tests/run_all.py` is the gate).
- [⭐ Preflight resolves the repo from CWD](preflight-resolves-repo-from-cwd.md) — it printed `clear to close out and merge` about ANOTHER lane's branch; pass `--repo` AND `--branch`, echo from `rev-parse`, never from belief. **Now mechanical** → [the close-out is a machine contract](closeout-target-is-a-machine-contract.md) (`--expect-key` REQUIRED, `task.yaml` manifest, `--toolkit-only`).
- [⭐ Memory is EVERY platform's, on every machine](memory-store-is-read-by-every-platform.md) — AGENTS.md §7 routes all four to `_artifacts/_memory/MEMORY.md`; READ-ONLY outside the write flows; the gate raises `MEMORY AUDIT DUE` at 90% and you must ASK → /memory-audit.
- **Local plumbing** — [hooks live in .githooks](git-hooks-live-in-githooks-not-git-hooks.md) (`.git/hooks` silently does nothing → [[two-machines-mac-and-pc]]) · [memory lives in the repo](portable-memory-store-dot-slug-trap.md) (`_artifacts/_memory/` + a junction; the slug turns `.` into `-`) · [PS console fakes mojibake](powershell-console-fakes-mojibake.md) (check BYTES, never the terminal) · [PS `,@()` unrolls ONCE](powershell-comma-array-wrapper-unrolls-once.md) (bare assignment only; `@(f())` nearly deleted 32 skill dirs).
- [Claude notifications: Mac + phone](claude-notifications-mac-and-phone.md) — string-form hooks are silently IGNORED (array schema required); a Focus mode swallows banners while exit 0 lies; phone = ntfy topic `mac-sudo-command`.

## Autopilot
- **Engines** — [lanes are not engines](autopilot-has-three-drifting-engines.md) (claude + opencode .ps1; a fix lands in BOTH) · [project-local](autopilot-engine-is-project-local.md) (FOUR diverged copies under `Projects/`; lobby holds only the spec — re-count, the old numbers rotted).
- [glm hybrid lane](autopilot-glm-hybrid-lane.md) — Dev on GLM via Z.ai, QA stays Claude; AGY-only, propagation owed.
- [Takeover: check liveness](autopilot-manual-takeover-check-liveness.md) — a "crashed" autopilot can resume and overwrite run files.

## Working style
- [Own it plainly](own-it-plainly-dont-make-excuses.md) — own it in one line, then ACT.
- [Writes for a big-picture operator](writes-for-big-picture-operator.md) — consequence before mechanism; explain every term; never dumb it down.
- [Daniel sells Hormozi-style](daniel-sells-hormozi-style.md) — direct, prove-it, give-value-first; default for marketing/copy/offers.
- [Operator chairs the board](operator-chairs-the-board.md) — multi-voice boards advance ONLY on the operator's word; voices ASK.
- [Caucus-card contract](adviser-board-caucus-card-contract.md) — silent caucuses → one-speaker Team Cards with originator credit.
- **Story artifacts** — [two-doc close](story-artifacts-two-doc-close.md) (audit → PLAN, review → WALKTHROUGH; `Verdict: … @ <sha>` is the flip gate) · [they live in the tree](story-artifacts-live-in-the-tree.md) (absence = the step never ran) · [limits relocate, never truncate](limits-relocate-content-never-truncate.md) (the 8/10 KB caps are GONE — SCC-51; a limit is legit only when going over means content is in the wrong file).
- **How the flows stop** — [wrappers collapse nested menus](wrapper-flows-collapse-nested-menus.md) (auto-continue BMAD menus; stop at real decisions) · [model-switch stops](dev-flow-model-switch-stops.md) (`continue`=audit here, `changed`=audit then STOP AGAIN) · [dev-story gate is conditional](dev-story-gate-is-conditional.md) (Step 2.5 stops ONLY on real questions).
- **Writing directives** — [restate Always-On obligations](restate-alwayson-obligations-in-command-bodies.md) (agents follow the literal step list; bake them in as steps) · [no personal name](no-personal-name-in-directives.md) (no "Daniel" in `.agents/` bodies; generic referent).
- [Plan reviews ride md-feedback memos](plan-reviews-ride-md-feedback-memos.md) — list_annotations FIRST (reflow hides the real memo); edit directly; respond in-thread.

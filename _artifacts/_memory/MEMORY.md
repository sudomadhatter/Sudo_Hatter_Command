# Memory index

<!-- One line per memory: link + a short hook. Detail lives in the file. Keep under ~140 lines.
     Related memories share a line rather than getting one each — every file stays linked. -->

## ⛔ Read first
- [TWO machines: Mac AND PC](two-machines-mac-and-pc.md) — shared docs read on both; python3 vs python; core.hooksPath is per-machine.

## Project stores
<!-- Paths stay BACKTICKED, never markdown links: check_store() resolves every markdown link to a
     .md file by BASENAME against THIS store, so linking a project index would read as a dead link
     to a file that plainly exists. Do not write the literal link form here either - this comment
     is scanned too, and the first draft of it tripped the check it was written to warn about. -->
Settled project-only facts are relocated OUT of this index into the project's own store (SCC-73) —
this section is the signpost. Working in one? Read its store too; it is not loaded for you.
- **AGY_AVIATIONCHAT** → `Projects/AGY_AVIATIONCHAT/_artifacts/_memory/` — authz claims, sprint state, Cloud Run ops, test harness, Firestore rules/hazards.
- **NEXgen-VR-Director** → `Projects/NEXgen-VR-Director/_artifacts/_memory/` — no memories yet.

## Jira & tickets
- [Jira is LIVE (SCC + AVCH)](jira-integration-live.md) — acli authed; branch/commit carries key; wrong-project key rejected.
- [⛔ acli CANNOT re-parent a subtask](acli-cannot-reparent-a-subtask.md) — create takes --parent, edit has no such flag; partial landing keeps parent open.
- [⛔ acli CANNOT attach a file](jira-attachments-need-the-rest-token.md) — upload is REST + the token in keychain `sudo-jira`; storing it corrupts silently two ways.
- [Cross-repo work = a ticket PER REPO](cross-repo-work-needs-a-ticket-per-repo.md) — ticket per repo required; key from epic/* branch, not BMAD number.
- [`To Do Next` IS the queue](to-do-next-is-the-queue.md) — lead every "what's next" with it; todo_list.md retired as agent source; use Blocking.
- [VS Code hides hook output](vscode-hides-git-hook-output.md) — warn-only hooks look like clean success; ship hooks ARMED.

## ⛔ AGY data safety — AGY-scoped, kept HERE on purpose
<!-- Ruled 2026-08-11 (SCC-88): AGY-only by subject, so a later sweep reads these as unfinished
     business. They are not. They guard real production data — do not "finish" the move. -->
- [Corpus IS the asset](agy-corpus-is-the-asset.md) — real-user data is revenue; demo data is placeholder by design.
- [Archive, never delete](agy-archive-never-delete-ruling.md) — no delete affordance; removal = archive + revoked in one call.
- [Real NDA-signed users](agy-has-real-nda-users.md) — production users/ is not test data; delete only from allow-list.

## Sprint, stories & close-out
- **Reading the board** — [it recommends stale work](sprint-dependency-map-recommends-stale-work.md) (check status first) · [⛔ scrum board RETIRED 08-07](sudo-update-scrum-board-five-zones.md) (SCC-13; parallel logic in /cicd-label-tasks).
- [`parallel-ok` is a SET property](parallel-ok-is-a-set-property.md) — property of a set at a moment; stamped via /cicd-label-tasks and /smh-label-tasks (SCC-155).
- **Multi-lane landing** — [⭐ collision is GATES, not files](lane-collision-is-gates-not-files.md) (zero file overlap still breaks; run each lane's gates on the other's blobs) · [lanes fix one finding](parallel-lanes-fix-the-same-finding.md) (re-diff epic branch on file overlap) · [close-out shape](multi-lane-closeout-board-merge-shape.md) (flip from story file) · [landing ≠ close-out](landing-is-not-closeout.md) (verify git before closing out).
- [⭐⛔ Operator acts in WORDS; agent does EVERY board write](review-status-means-needs-operator.md) — operator speaks words, agent writes Jira statuses; review = blocked-on-operator only.
- [Status-flip contract](story-status-flip-contract.md) — read as WHEN never WHO: done only inside operator-invoked close-out; bans self-certification.
- [Follow-ons are NOT a new story](followon-fixes-are-not-a-new-story.md) — no new worktree/key; fix on epic branch or chore/* off main.
- [Close-out is the sign-off](close-out-command-is-daniels-signoff.md) — operator-invoked command IS the sign-off; never punt back.
- [active-context budget](active-context-pointer-budget.md) — ≤20 KB budget; entries born as ≤3-line pointers; stale text deleted.
- **Scoping discipline** — [recon reframes scope](recon-reframes-story-scope.md) (ground-truth by behavior) · [test-debt = characterization](test-debt-stories-are-characterization.md) (retrofit tests pass green-first) · [⭐ review findings are not a work queue](review-findings-are-not-a-work-queue.md) (fix in thread, don't mint tickets) · [⭐⛔ discovered work = lettered subtask](discovered-work-becomes-a-lettered-part.md) (subtask under owning parent on one branch). · [⛔ a defer needs a STRUCTURAL blocker](a-defer-needs-a-structural-blocker.md) (no blocker on editing files; find the third door).
- [TEA retrofit (CLOSED)](tea-retrofit-active-initiative.md) — hub node only; lessons live in linked memories.

## Git, machines & worktrees
- [git merge wedges Next dev](git-merge-wedges-next-dev-tailwind.md) — merge under npm run dev wedges Tailwind.
- **Per-machine, never travels** — [env migration kit](env-migration-kit.md) (clone first, restore second) · [`.zshrc` invisible to automation](zshrc-is-invisible-to-automation.md) (shared env in ~/.zshenv) · [gitconfig didn't travel](gitconfig-never-migrated-to-the-mac.md) (set autoSetupRemote).
- [Commit and push are ONE action](commit-and-push-are-one-action.md) — never end step unpushed; verify 0 0 + clean per repo.
- [⛔ Backticks in `-m "…"` EXECUTE](commit-message-backticks-execute.md) — message quoting git commands runs them; use -F <file>.
- [⭐ Git branch model + the main gate](git-branch-model-standard.md) — prefix names work; main reached only via /cicd-push-e2e or /smh-close-task-merge-tree with single-use token.
- [⛔ Bash cwd resets to the MAIN checkout](bash-cwd-resets-to-main-checkout.md) — cd outside workspace resets cwd to main; relative paths read wrong tree.
- [⛔ Nothing guards the merge TARGET](nothing-guards-the-merge-target.md) — gates check merge source not target; pin cd <abs> && git in ONE line (SCC-351).
- [⛔ A revert reads from a REF](revert-target-must-be-a-ref.md) — checkout origin/main -- <p> is safe; checkout <sha> can delete sibling fixes.
- [⛔ One invocation = ONE merge](one-shot-permission-persists-in-context.md) — command stays in context; merge-ready -> STOP and hand back.
- [⭐⛔ The LANDING is the block, not the gates](landing-ceremony-is-the-block-not-the-gates.md) — permission layer blocks bare shared merges; PR door works via /smh-close-task-merge-tree.
- [⭐ Main merge needs the operator's VERBATIM words](main-merge-needs-operator-verbatim-approval.md) — minter requires verbatim approval quote; stage, CI green, then park.
- [Hook `ask` = DENY in auto mode](hook-ask-becomes-autodeny-in-auto-mode.md) — gates main only; reads pass, mutations die in non-interactive shells.
- [Pruned worktree blocks re-add](pruned-worktree-leaves-a-blocking-shell.md) — empty dir shell blocks worktree add; delete before re-adding.
- [⛔ Lens worktrees collide ACROSS reviews](lens-worktrees-collide-across-reviews.md) — stale lens-* trees are a different repo at a different sha; key the name, run the SCC-313 probe.
- [⛔ Pruning a story worktree can ORPHAN ①](story-worktree-prune-can-orphan-step1.md) — ①'s commit survives only as dangling; git fsck + cherry-pick, never re-run ① blind.
- [Worktrees skip gitignored assets](worktrees-do-not-inherit-gitignored-assets.md) — link auth_keys, .env, and node_modules into new worktree.
- [GitHub 408 on satellite wifi](github-408-on-satellite-uplink.md) — push times out mid-upload; chunk via scratch refs or wait for stable link.

## Testing
- **A green or a red can lie** — [⭐⛔ a red FILE may have run NOTHING](suite-red-file-may-have-run-nothing.md) (file count hides 0 cases; read the per-file tally) · [red can die pre-assertion](red-test-can-die-before-its-assertion.md) (setup failure masks bug) · [stubbed children = vacuous green](stubbed-children-make-green-vacuous.md) (mocks test nav only) · [piped gate hides exit code](piping-a-gate-hides-its-exit-code.md) (run gates bare) · [zsh doesn't word-split gate args](zsh-does-not-word-split-gate-args.md) (quote carefully) · [`echo` truncates at `\c`](echo-truncates-at-backslash-c.md) (use printf). · [⛔ the Mac's `grep` is ugrep](grep-on-the-mac-is-ugrep.md) (`grep -qv` exit code is INVERTED; count with `-vc`).
- **Source-grep guards are blind THREE ways** — [comments invert them](comment-literals-invert-source-grep-tests.md) (comment matches first) · [cannot see order](source-grep-guards-cannot-see-order.md) (moved guard passes) · [prose-pinning is vacuous](prose-pinning-guards-are-vacuous.md) (pin wiring, fail mutants first).
- **Toolchain pins** — [rules tests need Java](firestore-rules-tests-need-java.md) (brew openjdk@17; JAVA_HOME in ~/.zshenv) · [Node 26 breaks vitest jsdom storage](node-26-breaks-vitest-jsdom-storage.md) (run Node 22 LTS).
- **BDD** — [Vision Lock right-sized](bdd-vision-lock-rightsized.md) (vision lock mandatory, standalone .feature opt-in) · [sync step needs asyncio.run](bdd-sync-step-needs-asyncio-run.md) (skip-guarded red masks it).
- [coverage `source` ignores paths](coverage-source-silently-ignores-file-paths.md) — use source_pkgs, never file paths.
- **Risk + certification** — [priorities matrix](test-priorities-matrix.md) (P0 100% / P1 80% / P2 50% / P3 20%; P0+P1 need E2E) · [certification at shipping SHA](test-certification-at-shipping-sha.md) (②→③ certification-<story>.json).
- **Secrets in tests** — lesson from closed Gemini-key leak: **`setdefault` is wrong idiom for secrets** — assign unconditionally in conftest.
- [full-suite contention](vitest-full-suite-contends-across-lanes.md) — locks per-stack; bg shells die on chat close.
- **Spec + fixture conventions** — [eval negative controls](eval-harness-negative-control-convention.md) (_negative_control:true + NC_ id) · [E2E gate fiction](e2e-gate-fiction-test-guardrails.md) (report-only gate hid fiction spec) · [ATDD mocks match contract](atdd-mock-shape-must-match-backend-contract.md) · [domain-gated fixtures](domain-gated-fixtures-web-verify.md) (verify against primary sources).
- **Portability runs BOTH ways** — [Windows-authored code hides POSIX bugs](windows-authored-code-hides-posix-bugs.md) (chmod, C:/ paths, ;, robocopy, bare python, TRACKED exec bit -> inert hooks) · [⭐ Mac-authored code hides WINDOWS bugs](mac-authored-code-hides-windows-bugs.md) (CRLF at two seams, PATHEXT, `d / "C:"` IS `d`, SIGTERM undeliverable; fork behaviour, converge data).
- [JWT last-char tamper is a no-op](jwt-tamper-last-char-is-a-noop.md) — last base64 char carries 4 bits; mutate leading chars.

## Code-change hazards
- [New read regresses siblings](new-read-on-shared-endpoint-regresses-siblings.md) — run whole endpoint suite, not just local test.
- [Relocating drops mount guards](relocating-drops-mount-guards.md) — conditional inside render guard drops mount preconditions.
- [Destructive re-verify reads FRESH](destructive-reverify-must-read-fresh.md) — cached re-check no-ops delete and looks green.

## Code graph (GitNexus is RETIRED)
- [⛔ GitNexus is GONE — code-review-graph replaced it, PROJECTS-ONLY](gitnexus-index-not-actually-live.md) — SCC-272..288; never call impact()/context(); the lobby having no code graph is CORRECT (SCC-288). Leftover ~1.1 GB of `.gitnexus/` caches deleted 2026-08-25. Kept lesson: index and MCP registration are two per-machine problems, and registration fails silently.
- [⛔ do not re-evaluate `base`](base-is-not-a-gitnexus-replacement.md) — RESOLVED, the swap it recommended was executed; same NC license as GitNexus, no MCP, no transitive impact.
- **Search blind spots** — [grep skips gitignored projects](grep-skips-gitignored-projects.md) (blind to Projects/ from lobby) · [⭐ grep reads parked branch](grep-reads-the-branch-you-are-parked-on.md) (stale checkout fakes scope) · [relocated links are mis-pathed](relocated-doc-links-are-mispathed-not-dead.md) (target moved).

## Toolkit & sync
- [⭐ Zoo Code replaces Roo; VS Code replaces Antigravity](zoo-code-replaces-roo-code.md) — .roo/* paths kept; zoo-code.* settings namespace; NOT in sync-agents yet (SCC-349).
- [Zoo team: Wonderland roster](zoo-team-wonderland-roster.md) — March Hare = lead/orchestrator; emoji + name + ALL-CAPS role; 6 seats (Queen of Hearts = TESTER & QA, debug; The Gnat = LIBRARIAN, ask, read-only); review is the operator's model-switch gate — no seat writes a Verdict; SCC-350/360.
- [⭐⛔ Cheap models rationalize past PROSE](cheap-models-rationalize-past-prose.md) — every Zoo violation lived where a rule asked for judgment; fix with mechanism (mode groups, commit gates), never wording.
- [⭐ NAG the agent; don't rewrite the rule](nag-the-agent-dont-rewrite-the-rule.md) — restating law in a 5th place changes nothing; PostToolUse additionalContext reaches the model (allow+reason does NOT), cites the rule, ~36ms, never for destructive commands.
- [⛔ Zoo approvals live in globalState, not settings.json](zoo-approvals-decision-store.md) — file seeds ONCE, denies never; edit lists -> run zoo_permissions_apply.py --apply per machine (VS Code closed); git -C auto-denied, pin with cd && git.
- **Where law lives** — [center owns workflow law](thin-projects-center-owns-workflow-law.md) (thin projects; read .agents/INDEX.md) · [repo-local enforcement never centralizes](repo-local-enforcement-never-centralizes.md) (hooks and configs stay in gated repo) · [`platforms: []` = NOWHERE](platforms-empty-list-means-nowhere.md) (omit key = all four).
- **The non-Claude platforms** — [Codex is the 4th](codex-is-fourth-platform.md) (reads AGENTS.md + skills natively) · [⭐ Antigravity: EVERY door is a thin launcher](antigravity-uses-workflows-not-commands.md) (no size rule to re-derive; SCC-370).
- **Sync scope since 08-07** — [covers .agents not docs](toolkit-sync-covers-agents-not-docs.md) (lobby + caches only) · [maintained-projects is a LINT worklist](maintained-projects-allowlist.md) (sync no longer reads it).
- [Installed ≠ maintained](toolkit-installed-but-deliberately-unmaintained.md) — B-L-WorldWide and BRKN_Tattoos frozen on purpose.
- **Map/graph tooling is a CACHE** — [map-drift recorder](map-drift-recorder.md) (post-commit hook journals drift) · [doc-graph UNC hang](doc-graph-unc-hang-and-scope.md) (rebuild bare, don't widen --root) · [check_maps falsely STALEs AGY](check-maps-all-false-stale-agy.md) (fan-out omits AGY ignore list) · [⛔ AUTO-STALE is ALWAYS false in a worktree](check-maps-stale-is-false-in-worktrees.md) (label uses CWD basename).
- **The command surface** — [center → child skills](command-center-sudo-skills.md) (/sudo-* are skill launchers) · [BMAD wrappers are opencode-only](bmad-wrappers-are-opencode-only-bridges.md) · [twins drift: cicd/smh](sudo-commands-have-ap-twins-that-drift.md) (⭐ cicd IS the dev system, for real project work; smh = same system turned inward on the command centre; fix one, diff twin; ⛔ _AP twins ABANDONED) · [/team-onboarding is built-in](team-onboarding-is-claude-builtin.md) (CLI built-in).
- [⭐ ONE door per platform per command](one-door-per-platform-per-command.md) — command is brain, generated launcher skill is door; .claude/commands and ~/.codex/prompts retired.
- **Doc + board law** — [SOP currency gate](sop-doc-currency-gate.md) (usage changes require workflows_testing_SOP.md staged) · [rules read in place](rule-org-single-source-audit.md) (read center's .agents/rules/) · [board narrative → history/](board-narrative-lives-in-history.md) (notes on done rows fail lint) · [enforcement scripts](workflow-enforcement-scripts.md) (run_all.py is the gate).
- [⭐ Preflight resolves repo from CWD](preflight-resolves-repo-from-cwd.md) — pass --repo and --branch explicitly · [close-out is machine contract](closeout-target-is-a-machine-contract.md) (--expect-key required, task.yaml manifest).
- [Dev Record forks on `--story` slug](devrecord-story-slug-forks-the-record.md) — different slug creates duplicate record; check existing title.
- [⭐ Memory is EVERY platform's, on every machine](memory-store-is-read-by-every-platform.md) — AGENTS.md §7 routes all models; memory audit due at 90%.
- **Local plumbing** — [⛔ ARMED ≠ gated](hooks-armed-measures-pointer-not-payload.md) (hooks_armed checks core.hooksPath, never the directory; NEXgen read ARMED with zero gates) · [hooks live in .githooks](git-hooks-live-in-githooks-not-git-hooks.md) (.git/hooks silently inert) · [memory lives in repo](portable-memory-store-dot-slug-trap.md) (_artifacts/_memory/ + junction) · [PS console fakes mojibake](powershell-console-fakes-mojibake.md) (check bytes) · [PS `,@()` unrolls ONCE](powershell-comma-array-wrapper-unrolls-once.md) (bare assignment only).
- [⛔ Sandbox denies `.claude/hooks` + `.claude/skills`](sandbox-denies-writes-under-dot-claude-hooks-skills.md) — breaks `git merge`/`checkout` for every lane and blocks `/smh-sync-agents` in-session (SCC-300).
- [Claude notifications: Mac + phone](claude-notifications-mac-and-phone.md) — array schema required for hooks; phone notifications via ntfy mac-sudo-command.
- [Antigravity SCM repo list](antigravity-scm-repo-list-collapses.md) — git.path shim unstacks; a click collapses the multi-repo view (cmd+alt+r restores).

## Autopilot
- [Autopilot engines are project-local](autopilot-engine-is-project-local.md) — 4 diverged copies in Projects/ (Claude + Opencode .ps1); lobby holds spec only.
- [glm hybrid lane](autopilot-glm-hybrid-lane.md) — Dev on GLM via Z.ai, QA stays Claude.

## Working style
- [⭐ Exercise the REAL cicd doors when testing the system](exercise-the-real-cicd-doors.md) — run /cicd-* via Skill one story at a time, epic-branch worktrees; file every command defect as an SCC-244 subtask with an anchor.
- [⭐⛔ Audit findings need a FILE anchor](audit-findings-need-a-file-anchor.md) — fan-outs manufacture findings; no anchor = delete; never build an audit-of-the-audit (SCC-225).
- [⭐ Lightweight lane for specific, can't-break work](lightweight-lane-for-specific-no-break-work.md) — doc-only / operator-directed ask is ticket -> edit -> push (SCC-162).
- [⭐⛔ Close the loop; don't hand back decisions](close-the-loop-dont-hand-back-decisions.md) — no new-concern tails, no menus; pick the default, say it, keep going (SCC-201).
- [⛔ A script plus an instruction is NOT delivery](a-script-plus-an-instruction-is-not-delivery.md) — needs a live process? ship the installer, prove it with launchctl + its log (SCC-355).
- [Machine-read walkthrough lines must be UNFENCED](walkthrough-machine-read-lines-must-be-unfenced.md) — a fenced roster or Verdict stamp reads as absent; preflight blames task.yaml instead.
- [⛔ `## Your Actions` must be CHECKBOX rows](your-actions-must-be-checkbox-rows.md) — a table is invisible to reconcile-actions and finish; finish then writes Done over open work.
- [⛔ Quick-level roster is REFUSED under fan-out](quick-level-roster-refused-under-fanout.md) — walkthrough_roster --gate rejects the n/a lenses the SCC-232 quick level mandates; run --gate at review time; neutralize superseded Verdict stamps.
- [Own it plainly](own-it-plainly-dont-make-excuses.md) — own issues in one line, then act.
- [Writes for a big-picture operator](writes-for-big-picture-operator.md) — consequence before mechanism; explain terms clearly.
- [Daniel sells Hormozi-style](daniel-sells-hormozi-style.md) — direct, prove-it, value-first copy.
- [Operator chairs the board](operator-chairs-the-board.md) — multi-voice boards advance on operator word; voices ask.
- [Caucus-card contract](adviser-board-caucus-card-contract.md) — silent caucuses -> one-speaker Team Cards with originator credit.
- [⛔ Board roster is PRODUCT-shaped](adviser-board-roster-is-product-shaped.md) — personal topic = seat 2-3 lenses, not 5; apply "when NOT to seat" before the gate.
- **Story artifacts** — [two-doc close](story-artifacts-two-doc-close.md) (audit -> plan, review -> walkthrough) · [artifacts live in tree](story-artifacts-live-in-the-tree.md) (absence = step never ran) · [limits relocate, never truncate](limits-relocate-content-never-truncate.md) (caps removed under SCC-51).
- **How the flows stop** — [model-switch stops](dev-flow-model-switch-stops.md) (continue = audit, changed = audit and stop) · [dev-story gate conditional](dev-story-gate-is-conditional.md) (stops only on real questions).
- **Writing directives** — [no personal name](no-personal-name-in-directives.md) (generic referents in .agents/).
- [Plan reviews ride md-feedback memos](plan-reviews-ride-md-feedback-memos.md) — list_annotations first; edit directly and respond in-thread.
- [Budget is a live constraint — announce spend](budget-is-a-live-constraint-announce-spend.md) — say what spawns BEFORE it spawns; after a budget complaint, nothing spawns without his word; sleeping Mac ≠ working agent.
- [⛔ `worktree remove --force` eats UNTRACKED memories](worktree-remove-force-eats-untracked-memories.md) — write session memories on the lane and commit before the prune; re-create and verify if written post-merge.

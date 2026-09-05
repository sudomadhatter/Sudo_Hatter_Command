# Memory index

<!-- One line per memory: link + a short hook. Detail lives in the file. Keep under ~140 lines.
     Related memories share a line rather than getting one each — every file stays linked. -->

## ⛔ Read first
- [ONE PC: Windows host, Ubuntu in WSL2](one-pc-windows-and-wsl.md) — not two machines, no Mac; which side runs what; three checkouts, only WSL `Ubuntu` is live; why the Windows clone is kept.

## Project stores
<!-- Paths stay BACKTICKED, never markdown links: check_store() resolves every markdown link to a
     .md file by BASENAME against THIS store, so a project-index link would read as dead. -->
Settled project-only facts live in the project's own store (SCC-73). Working in one? Read its store too.
- **AGY_AVIATIONCHAT** → `Projects/AGY_AVIATIONCHAT/_artifacts/_memory/` — authz, sprint state, Cloud Run, test harness, Firestore.
- **NEXgen-VR-Director** → `Projects/NEXgen-VR-Director/_artifacts/_memory/` — no memories yet.

## Jira & tickets
- [Jira is LIVE (SCC + AVCH)](jira-integration-live.md) — acli authed; branch/commit carries key.
- [⛔ acli CANNOT re-parent a subtask](acli-cannot-reparent-a-subtask.md) — create takes --parent, edit doesn't.
- [⛔ acli CANNOT attach a file](jira-attachments-need-the-rest-token.md) — REST + keychain `sudo-jira` token.
- [Cross-repo work = a ticket PER REPO](cross-repo-work-needs-a-ticket-per-repo.md) — key from epic/* branch, not BMAD number.
- [`To Do Next` IS the queue](to-do-next-is-the-queue.md) — lead "what's next" with it; todo_list.md retired.
- [VS Code hides hook output](vscode-hides-git-hook-output.md) — warn-only hooks look clean; ship hooks ARMED.

## ⛔ AGY data safety — AGY-scoped, kept HERE on purpose
<!-- Ruled 2026-08-11 (SCC-88): guards real production data — do not "finish" the move. -->
- [Corpus IS the asset](agy-corpus-is-the-asset.md) — real-user data is revenue; demo data is placeholder.
- [Archive, never delete](agy-archive-never-delete-ruling.md) — removal = archive + revoked in one call.
- [Real NDA-signed users](agy-has-real-nda-users.md) — production users/ is not test data; delete only from allow-list.

## Sprint, stories & close-out
- **Reading the board** — [it recommends stale work](sprint-dependency-map-recommends-stale-work.md) (check status first).
- [`parallel-ok` is a SET property](parallel-ok-is-a-set-property.md) — of a set at a moment; stamped via label-tasks (SCC-155).
- **Multi-lane landing** — [⭐ collision is GATES, not files](lane-collision-is-gates-not-files.md) (run each lane's gates on the other's blobs) · [lanes fix one finding](parallel-lanes-fix-the-same-finding.md) · [close-out shape](multi-lane-closeout-board-merge-shape.md) · [landing ≠ close-out](landing-is-not-closeout.md) (verify git first).
- [⭐⛔ Operator acts in WORDS; agent does EVERY board write](review-status-means-needs-operator.md) — review = blocked-on-operator.
- [Status-flip contract](story-status-flip-contract.md) — WHEN never WHO: done only inside operator-invoked close-out.
- [Follow-ons are NOT a new story](followon-fixes-are-not-a-new-story.md) — no new worktree/key; epic branch or chore/*.
- [Close-out is the sign-off](close-out-command-is-daniels-signoff.md) — operator-invoked command IS the sign-off.
- [active-context budget](active-context-pointer-budget.md) — ≤20 KB; entries born ≤3-line; stale text deleted.
- **⛔ Close-out reads THREE machine contracts — a finished story blocks on any one** — [review is NARRATED until the block is in the walkthrough](review-is-narrated-until-the-block-is-in-the-walkthrough.md) (no `Verdict:` = "review has not run"; recover the roster from the lens log, never invent) · [receipts file under the BOARD-key slug](gate-receipts-file-under-the-board-key-slug.md) (`--story avch-109` reads as NO RECEIPT; re-run, never rename) · [File List paths are REPO-ROOT relative](file-list-paths-are-repo-root-relative.md) (stack-relative = all ABSENT; a backticked example in a comment is a 31st claim).
- **Scoping discipline** — [recon reframes scope](recon-reframes-story-scope.md) · [test-debt = characterization](test-debt-stories-are-characterization.md) · [⭐ review findings are not a work queue](review-findings-are-not-a-work-queue.md) (fix in thread) · [⭐⛔ discovered work = lettered subtask](discovered-work-becomes-a-lettered-part.md) · [⛔ a defer needs a STRUCTURAL blocker](a-defer-needs-a-structural-blocker.md).

## Git, machines & worktrees
- [git merge wedges Next dev](git-merge-wedges-next-dev-tailwind.md) — merge under npm run dev wedges Tailwind.
- **Per-machine, never travels** — [env migration kit](env-migration-kit.md) (clone first) · [`.zshrc` invisible to automation](zshrc-is-invisible-to-automation.md) (use ~/.zshenv).
- [Commit and push are ONE action](commit-and-push-are-one-action.md) — verify 0 0 + clean per repo.
- [⛔ Backticks in `-m "…"` EXECUTE](commit-message-backticks-execute.md) — use -F <file>.
- [⭐ Git branch model + the main gate](git-branch-model-standard.md) — main only via /cicd-push-e2e or /smh-close-task-merge-tree token.
- [⛔ Bash cwd resets to the MAIN checkout](bash-cwd-resets-to-main-checkout.md) — relative paths read wrong tree.
- [⛔ Nothing guards the merge TARGET](nothing-guards-the-merge-target.md) — pin cd <abs> && git in ONE line (SCC-351).
- [⛔ A revert reads from a REF](revert-target-must-be-a-ref.md) — checkout origin/main -- <p>; a <sha> can delete sibling fixes.
- [⛔ One invocation = ONE merge](one-shot-permission-persists-in-context.md) — merge-ready -> STOP and hand back.
- [⭐⛔ The LANDING is the block, not the gates](landing-ceremony-is-the-block-not-the-gates.md) — PR door via /smh-close-task-merge-tree.
- [⭐ Main merge needs the operator's VERBATIM words](main-merge-needs-operator-verbatim-approval.md) — stage, CI green, park.
- [Hook `ask` = DENY in auto mode](hook-ask-becomes-autodeny-in-auto-mode.md) — mutations die in non-interactive shells.
- [Pruned worktree blocks re-add](pruned-worktree-leaves-a-blocking-shell.md) — delete the empty shell first.
- [⛔ Lens worktrees collide ACROSS reviews](lens-worktrees-collide-across-reviews.md) — key the name; run the SCC-313 probe.
- [⛔ Pruning a story worktree can ORPHAN ①](story-worktree-prune-can-orphan-step1.md) — git fsck + cherry-pick, never re-run ① blind.
- [Worktrees skip gitignored assets](worktrees-do-not-inherit-gitignored-assets.md) — link auth_keys, .env, node_modules.
- [GitHub 408 on satellite wifi](github-408-on-satellite-uplink.md) — chunk via scratch refs or wait.

## Testing
- **A green or a red can lie** — [⭐⛔ a red FILE may have run NOTHING](suite-red-file-may-have-run-nothing.md) (per-file tally) · [red can die pre-assertion](red-test-can-die-before-its-assertion.md) · [stubbed children = vacuous green](stubbed-children-make-green-vacuous.md) · [piped gate hides exit code](piping-a-gate-hides-its-exit-code.md) (run bare) · [zsh doesn't word-split gate args](zsh-does-not-word-split-gate-args.md) · [`echo` truncates at `\c`](echo-truncates-at-backslash-c.md) · [⛔ the Mac's `grep` may be ugrep](grep-on-the-mac-is-ugrep.md) (launch-context dependent; `-qv` INVERTED on ugrep — count, never `-q`).
- [⭐⛔ Per-function tests miss REQUEST-ORDER defects](per-function-tests-miss-request-order-defects.md) — green suite, dead feature; buy a seam test that drives the real doors in order.
- **Source-grep guards are blind FOUR ways** — [comments invert them](comment-literals-invert-source-grep-tests.md) · [cannot see order](source-grep-guards-cannot-see-order.md) · [prose-pinning is vacuous](prose-pinning-guards-are-vacuous.md) (fail mutants first) · [⛔ a result-filter doesn't protect the WALK](rglob-sweeps-must-prune-the-walk.md) (rglob still walks .venv; Windows dies on torch's long paths — prune with os.walk).
- **Toolchain pins** — [rules tests need Java](firestore-rules-tests-need-java.md) (JAVA_HOME in ~/.zshenv) · [Node 26 breaks vitest jsdom storage](node-26-breaks-vitest-jsdom-storage.md) (run Node 22 LTS).
- **BDD** — [Vision Lock right-sized](bdd-vision-lock-rightsized.md) (standalone .feature opt-in) · [sync step needs asyncio.run](bdd-sync-step-needs-asyncio-run.md).
- [coverage `source` ignores paths](coverage-source-silently-ignores-file-paths.md) — use source_pkgs.
- **Risk + certification** — [priorities matrix](test-priorities-matrix.md) (P0 100%/P1 80%/P2 50%/P3 20%; P0+P1 need E2E) · [certification at shipping SHA](test-certification-at-shipping-sha.md) (②→③ certification-<story>.json).
- **Secrets in tests** — **`setdefault` is wrong idiom for secrets** — assign unconditionally in conftest.
- [full-suite contention](vitest-full-suite-contends-across-lanes.md) — locks per-stack; bg shells die on chat close.
- **Spec + fixture conventions** — [eval negative controls](eval-harness-negative-control-convention.md) · [E2E gate fiction](e2e-gate-fiction-test-guardrails.md) · [ATDD mocks match contract](atdd-mock-shape-must-match-backend-contract.md) · [domain-gated fixtures](domain-gated-fixtures-web-verify.md).
- **Portability runs BOTH ways** — [Windows-authored code hides POSIX bugs](windows-authored-code-hides-posix-bugs.md) (chmod, C:/, ;, robocopy, bare python, exec bit) · [⭐ Mac-authored code hides WINDOWS bugs](mac-authored-code-hides-windows-bugs.md) (CRLF, PATHEXT, SIGTERM; converge data).
- [JWT last-char tamper is a no-op](jwt-tamper-last-char-is-a-noop.md) — mutate leading chars.

## Code-change hazards
- [New read regresses siblings](new-read-on-shared-endpoint-regresses-siblings.md) — run the whole endpoint suite.
- [Relocating drops mount guards](relocating-drops-mount-guards.md) — render-guard move drops mount preconditions.
- [Destructive re-verify reads FRESH](destructive-reverify-must-read-fresh.md) — cached re-check no-ops the delete.

## Code graph (GitNexus is RETIRED)
- [⛔ GitNexus is GONE — code-review-graph replaced it, PROJECTS-ONLY](gitnexus-index-not-actually-live.md) — never call impact(); no lobby graph is CORRECT; MCP registration is per-machine and fails silently.
- **Search blind spots** — [grep skips gitignored projects](grep-skips-gitignored-projects.md) (blind to Projects/ from lobby) · [⭐ grep reads parked branch](grep-reads-the-branch-you-are-parked-on.md) (stale checkout fakes scope) · [relocated links are mis-pathed](relocated-doc-links-are-mispathed-not-dead.md).

## Toolkit & sync
- [⭐ Zoo Code replaces Roo; Antigravity lives on as the extension](zoo-code-replaces-roo-code.md) — .roo/* paths kept; Zoo is sync-agents platform 5 (SCC-349); Zoo, Claude and Antigravity fences render from ONE source (SCC-378).
- [Zoo team: Wonderland roster](zoo-team-wonderland-roster.md) — March Hare = lead; 6 seats; no seat writes a Verdict.
- [⭐⛔ Cheap models rationalize past PROSE](cheap-models-rationalize-past-prose.md) — fix with mechanism, never wording.
- [⭐ NAG the agent; don't rewrite the rule](nag-the-agent-dont-rewrite-the-rule.md) — PostToolUse additionalContext reaches the model; cites the rule; never for destructive commands.
- [⛔ Zoo approvals live in globalState, not settings.json](zoo-approvals-decision-store.md) — edit lists -> zoo_permissions_apply.py --apply per machine; git -C auto-denied.
- **Where law lives** — [center owns workflow law](thin-projects-center-owns-workflow-law.md) (read .agents/INDEX.md) · [repo-local enforcement never centralizes](repo-local-enforcement-never-centralizes.md) · [`platforms: []` = NOWHERE](platforms-empty-list-means-nowhere.md) (omit key = all four).
- **The non-Claude platforms** — [Codex is the 4th](codex-is-fourth-platform.md) (reads AGENTS.md natively) · [⭐ Antigravity's `/` menu is `.agents/skills/`](antigravity-uses-workflows-not-commands.md) — the same launcher Claude and Codex read; workflows retire 2026-11-01 (SCC-394).
- **Sync scope since 08-07** — [covers .agents not docs](toolkit-sync-covers-agents-not-docs.md) · [maintained-projects is a LINT worklist](maintained-projects-allowlist.md).
- [Installed ≠ maintained](toolkit-installed-but-deliberately-unmaintained.md) — B-L-WorldWide and BRKN_Tattoos frozen on purpose.
- **Map/graph tooling is a CACHE** — [map-drift recorder](map-drift-recorder.md) · [doc-graph UNC hang](doc-graph-unc-hang-and-scope.md) · [check_maps falsely STALEs AGY](check-maps-all-false-stale-agy.md) · [⛔ AUTO-STALE is ALWAYS false in a worktree](check-maps-stale-is-false-in-worktrees.md).
- **The command surface** — [center → child skills](command-center-sudo-skills.md) · [BMAD wrappers are opencode-only](bmad-wrappers-are-opencode-only-bridges.md) · [twins drift: cicd/smh](sudo-commands-have-ap-twins-that-drift.md) (⭐ cicd = project work; smh = centre-inward; fix one, diff twin) · [/team-onboarding is built-in](team-onboarding-is-claude-builtin.md).
- [⭐ ONE door per platform per command](one-door-per-platform-per-command.md) — command is brain, launcher skill is door.
- **Doc + board law** — [SOP currency gate](sop-doc-currency-gate.md) (usage changes stage the SOP) · [rules read in place](rule-org-single-source-audit.md) · [board narrative → history/](board-narrative-lives-in-history.md) · [enforcement scripts](workflow-enforcement-scripts.md) (run_all.py).
- [⭐ Preflight resolves repo from CWD](preflight-resolves-repo-from-cwd.md) — pass --repo/--branch · [close-out is machine contract](closeout-target-is-a-machine-contract.md) (--expect-key, task.yaml) · [⛔ gate_receipt --cwd needs an ABSOLUTE executable](gate-receipt-cwd-needs-absolute-executable.md) (relative venv python resolves against the LOBBY → exit 127).
- [Dev Record forks on `--story` slug](devrecord-story-slug-forks-the-record.md) — check existing title first.
- [⭐ Memory is EVERY platform's, on every machine](memory-store-is-read-by-every-platform.md) — AGENTS.md §7; memory audit due at 90%.
- **Local plumbing** — [⛔ ARMED ≠ gated](hooks-armed-measures-pointer-not-payload.md) (checks core.hooksPath, not the payload) · [hooks live in .githooks](git-hooks-live-in-githooks-not-git-hooks.md) · [memory lives in repo](portable-memory-store-dot-slug-trap.md) (_artifacts/_memory/ + junction) · [PS console fakes mojibake](powershell-console-fakes-mojibake.md) (check bytes) · [PS `,@()` unrolls ONCE](powershell-comma-array-wrapper-unrolls-once.md).
- [⛔ Sandbox denies `.claude/hooks` + `.claude/skills`](sandbox-denies-writes-under-dot-claude-hooks-skills.md) — breaks merge/checkout; blocks /smh-sync-agents in-session.
- [Claude notifications: Mac + phone](claude-notifications-mac-and-phone.md) — array schema; ntfy mac-sudo-command.
- [⛔ Hook background work gets SIGTERM ~15 ms after the hook exits](hook-background-work-gets-sigterm.md) — `curl &` dies; use `( trap '' TERM; … ) &` (SCC-376).

## Autopilot
- [Autopilot engines are project-local](autopilot-engine-is-project-local.md) — 4 diverged copies; lobby holds spec only.
- [glm hybrid lane](autopilot-glm-hybrid-lane.md) — Dev on GLM via Z.ai, QA stays Claude.

## Working style
- [⭐ Exercise the REAL cicd doors when testing the system](exercise-the-real-cicd-doors.md) — one story at a time; command defects → SCC-244 subtasks.
- [⭐⛔ Audit findings need a FILE anchor](audit-findings-need-a-file-anchor.md) — no anchor = delete; no audit-of-the-audit (SCC-225).
- [⭐ Lightweight lane for specific, can't-break work](lightweight-lane-for-specific-no-break-work.md) — ticket -> edit -> push (SCC-162).
- [⭐⛔ Close the loop; don't hand back decisions](close-the-loop-dont-hand-back-decisions.md) — no new-concern tails, no menus (SCC-201).
- [⛔ A script plus an instruction is NOT delivery](a-script-plus-an-instruction-is-not-delivery.md) — ship the installer, prove the live process (SCC-355).
- [Machine-read walkthrough lines must be UNFENCED](walkthrough-machine-read-lines-must-be-unfenced.md) — fenced roster/Verdict reads as absent.
- [⛔ `## Your Actions` must be CHECKBOX rows](your-actions-must-be-checkbox-rows.md) — a table is invisible to reconcile-actions.
- [⛔ Quick-level roster is REFUSED under fan-out](quick-level-roster-refused-under-fanout.md) — run --gate at review time; neutralize superseded Verdicts.
- [Own it plainly](own-it-plainly-dont-make-excuses.md) — one line, then act.
- [Writes for a big-picture operator](writes-for-big-picture-operator.md) — consequence before mechanism.
- [Daniel sells Hormozi-style](daniel-sells-hormozi-style.md) — direct, prove-it, value-first copy.
- [Operator chairs the board](operator-chairs-the-board.md) — boards advance on operator word.
- [Caucus-card contract](adviser-board-caucus-card-contract.md) — one-speaker Team Cards with originator credit.
- [⛔ Board roster is PRODUCT-shaped](adviser-board-roster-is-product-shaped.md) — personal topic = 2-3 lenses, not 5.
- **Story artifacts** — [two-doc close](story-artifacts-two-doc-close.md) (audit->plan, review->walkthrough) · [artifacts live in tree](story-artifacts-live-in-the-tree.md) (absence = never ran) · [limits relocate, never truncate](limits-relocate-content-never-truncate.md).
- **How the flows stop** — [model-switch stops](dev-flow-model-switch-stops.md) (continue = audit) · [dev-story gate conditional](dev-story-gate-is-conditional.md) (stops only on real questions).
- **Writing directives** — [no personal name](no-personal-name-in-directives.md) (generic referents in .agents/).
- [Plan reviews ride md-feedback memos](plan-reviews-ride-md-feedback-memos.md) — list_annotations first; respond in-thread.
- [Budget is a live constraint — announce spend](budget-is-a-live-constraint-announce-spend.md) — say what spawns BEFORE it spawns.
- [⛔ `worktree remove --force` eats UNTRACKED memories](worktree-remove-force-eats-untracked-memories.md) — write + commit lane memories before the prune.

# Memory index

<!-- One line per memory: link + a short hook. Detail lives in the file. Keep under ~140 lines.
     Related memories share a line rather than getting one each — every file stays linked. -->

## ⛔ Read first
- [TWO machines: Mac AND PC](two-machines-mac-and-pc.md) — every shared doc is read on both; `python3` vs `python`, and `core.hooksPath` is per-machine so gates are silently OFF on a fresh clone.

## Jira & tickets
- [Jira is LIVE (SCC + AVCH)](jira-integration-live.md) — every branch/commit carries a key; gate ARMED, wrong-project key rejected.
- [Cross-repo work = a ticket PER REPO](cross-repo-work-needs-a-ticket-per-repo.md) — widening a project's `jira.conf` is ruled out in writing; and the key comes from the `epic/*` branch, never from the BMAD epic number.
- [VS Code hides hook output](vscode-hides-git-hook-output.md) — a warn-only hook looks like clean success; ship hooks ARMED.

## AGY access & data
- [Corpus IS the asset](agy-corpus-is-the-asset.md) — real-user data is a revenue line; demo data is placeholder by design.
- [Archive, never delete](agy-archive-never-delete-ruling.md) — no delete affordance ever ships; roster removal = archive + `revoked` in one call.
- **The entitlement claim** — [no provenance](agy-entitled-claim-has-no-provenance.md) (one shared boolean; a billing revoke kills school access) · [claim-primary authz](agy-authz-claim-primary-ruling.md) (never a Firestore read on the gate; rulings live in DOCSTRINGS) · [two redemption doors](agy-redemption-has-two-doors.md) (REST endpoint AND the HR tool — change both).
- [/hanger-talk IS the free tier](agy-hanger-talk-is-the-free-tier.md) — no paywall, free ACCOUNT by design; don't re-file 4.27 as unbuilt.
- [AviationChat is ALWAYS .org](agy-domain-is-always-org.md) — every `@aviationchat.com` was a TYPO; demo keys off `schools/ACDEMO`.
- [Real NDA-signed users](agy-has-real-nda-users.md) — production `users/` is NOT test data; delete only from an allow-list.
- [Single-writer gate needs literals](single-writer-gate-needs-literal-payloads.md) — the AST gate flags variable/spread payloads on `users/{uid}` writes.
- **Fail closed, both of them** — [admin role](agy-admin-role-fail-closed.md) (roleless/invalid creds → DENY, never a defaulted super_admin; 2 latent sites) · [seat cap](agy-school-seat-cap-fails-closed.md) (no `max_seats` → cap 0 → every redemption REDEEM_FULL; check for None).
- [Voice-router entitlement vs cost](voice-router-entitlement-vs-cost-cap.md) — 4030 gate is PAID-only; free routers ungated but 4029 cost-capped.
- [Error envelope shapes](agy-error-envelope-shapes.md) — HTTPException → `body.detail.error.message`; app handlers → top-level `body.error`.
- **Closed but keep the lesson** — [admin creds drift](admin-credentials-drift-from-doc.md) (RESOLVED 07-25; bcrypt-check first, then suspect a wedged uvicorn) · [ghost-doc window](agy-school-identity-ghost-doc-window.md) (FIXED; never-delete + BY-ID→BY-FIELD lookup surfaced superseded records).

## AGY sprint & stories
- [Epic 19 deferred](agy-epic-19-deferred-pin-cascade.md) — adk 2.5.0 is a 4-family bump; never run ② on 19.x.
- **Reading the board** — [it recommends stale work](sprint-dependency-map-recommends-stale-work.md) (lags the YAML, mis-lanes rows; check status first) · [five zones](sudo-update-scrum-board-five-zones.md) (🧵 shows the ANSWER not the math; NO background model ever writes it).
- **State rots independently** — [epic keys rot silently](agy-epic-keys-rot-silently.md) (a stale REASON keeps a row alive; umbrellas can't self-close; 12.3 still open) · [epics.md + YAML check each other](agy-epics-md-is-partial.md) (YAML wins on state, epics.md for the why) · [deferred EPIC, never deferred-v3](agy-deferred-epic-not-deferred-v3.md) (parked rows under a finished epic hold it open forever).
- [Story files canonical dir](agy-story-files-canonical-dir.md) — `_bmad/bmm/stories/`; grep dot AND dash forms; next ID from sprint-status.yaml.
- [Status-flip contract](story-status-flip-contract.md) — dev sets `review`; only human close-out sets `done`. Fix the rule, not BMAD.
- [Follow-ons are NOT a new story](followon-fixes-are-not-a-new-story.md) — no worktree/board key; fix on the epic branch (or chore/* off main), explicit paths.
- [Close-out is the sign-off](close-out-command-is-daniels-signoff.md) — an operator-invoked sudo-* command IS the sign-off; never punt back.
- **Multi-lane landing** — [lanes fix one finding](parallel-lanes-fix-the-same-finding.md) (re-diff the epic branch first; the SET rule binds on file OVERLAP) · [close-out shape](multi-lane-closeout-board-merge-shape.md) (story lines conflict each merge; flip from the STORY FILE) · [landing ≠ close-out](landing-is-not-closeout.md) (code can merge while the board reads `review`; check git BEFORE closing out).
- [active-context budget](active-context-pointer-budget.md) — ≤20 KB ≈ 5k tokens; entries born as ≤3-line pointers; stale text is DELETED.
- [Settled decisions are not gaps](settled-decisions-are-not-gaps.md) — never file a ruled-on decision under "limitations"; it gets re-proposed.
- [Recon reframes story scope](recon-reframes-story-scope.md) — recon found the feature already existed ×3; ground-truth by BEHAVIOR.
- [Test-debt = characterization](test-debt-stories-are-characterization.md) — retrofit tests pass green-first; don't fake a red.
- [TEA retrofit (CLOSED)](tea-retrofit-active-initiative.md) — hub node only; lessons live in the linked memories.

## AGY infra & ops
- **A wedged process fans out** — [wedged backend](wedged-backend-fans-out-three-symptoms.md) (serves /health fast while hanging every Firestore route — restart FIRST) · [git merge wedges Next dev](git-merge-wedges-next-dev-tailwind.md) (a merge under `npm run dev` wedges Tailwind, 500-ing every route).
- **Cloud Run** — [deploys backend/ only](agy-cloud-run-deploys-backend-only.md) (the Dockerfile COPYs `backend/`; docs/toolkit in git cost $0) · [stale revision fakes an incident](stale-cloud-run-revision-fakes-prod-incident.md) (only `release` reveals a 0%-traffic revision) · [FAH secrets need viewer too](fah-secret-needs-viewer-role.md) (secretAccessor AND secretmanager.viewer; the raw build log has it).
- [Overseer jobs paused by design](overseer-jobs-paused-by-design.md) — both PAUSED 07-17; resume overseer-nightly only.
- [Sentry API access](sentry-api-access-aviationchat.md) — token in backend/.env; control vs region host split; the loop-guard filter is sacred.
- [Incident pipeline 16.2](incident-pipeline-16-2-operations.md) — agent lane PRIMARY; fire endpoint is the fallback pager.
- [Commit and push are ONE action](commit-and-push-are-one-action.md) — never end a step unpushed or dirty; verify `0 0` + clean per repo.
- [Git branch model](git-branch-model-standard.md) — main is the ONLY long-lived branch; epics on short-lived epic/* merged via /sudo-push-e2e; retired main_debug 2026-08-07; branches now carry a Jira key.
- [Hook `ask` = DENY in auto mode](hook-ask-becomes-autodeny-in-auto-mode.md) — the hook gates main only; reads pass while mutations die; retry once, then hand over the rule.
- [Pruned worktree blocks re-add](pruned-worktree-leaves-a-blocking-shell.md) — the empty dir blocks `worktree add`; only PowerShell can delete it.
- [Worktrees skip gitignored assets](worktrees-do-not-inherit-gitignored-assets.md) — copy auth_keys/ + .env; junction node_modules; `npm ci` for E2E.
- **Per-machine setup, never travels** — [env migration kit](env-migration-kit.md) (`_my_resources/migrations/`: master.env + new_machine guide; clone first, restore second) · [secrets layout is operator-owned](secrets-bundle-layout-is-operator-owned.md) (never reorganize the bundle; point scripts at his copy).
- **Shell + git config are per-box** — [`.zshrc` is invisible to automation](zshrc-is-invisible-to-automation.md) (interactive-only; shared env belongs in `~/.zshenv`) · [global gitconfig doesn't travel](gitconfig-never-migrated-to-the-mac.md) (Windows-only until applied on the Mac 08-07; `autoSetupRemote` can't retro-fix older branches).

## Testing
- [Typecheck: BE gated, FE not](agy-typecheck-is-enforced-nowhere.md) — pyrefly changed-files hard gate live 07-31; frontend `tsc` ungated but clean.
- **Source-grep guards are blind two ways** — [comments invert them](comment-literals-invert-source-grep-tests.md) (a comment with the pinned literal matches FIRST) · [they can't see ORDER](source-grep-guards-cannot-see-order.md) (a guard relocated after the write it protects passes identically).
- [ruff changed-files is a hard gate](agy-ruff-changed-files-is-a-hard-gate.md) — lints WHOLE changed files; re-run the suite after `--fix`.
- [Importing backend.database inits](agy-database-import-is-an-init-step.md) — module-scope `get_db()` needs `initialize_app()` ABOVE it. Smoke-run.
- **A green or a red can lie** — [a red can die pre-assertion](red-test-can-die-before-its-assertion.md) (one failing in SEEDING fails identically; read WHICH line raised) · [stubbed children = vacuous green](stubbed-children-make-green-vacuous.md) (mocking its panels proves NAVIGATION, not the panels).
- [Certification at shipping SHA](test-certification-at-shipping-sha.md) — ②→③ handoff is `certification-<story>.json`; suite 278 s, floor 2 runs.
- [Test priorities matrix](test-priorities-matrix.md) — P0 100% / P1 80% / P2 50% / P3 20%; P0+P1 need E2E.
- [True-P0 surface](agy-true-p0-surface.md) — Orchestrator + RAG/Librarian + Sully override + admin auth + PII scrub.
- **The two E2E tiers** — [learner harness](agy-learner-e2e-harness.md) (TEA-16 emulator harness is the ONE e2e suite; 3 silent breakers) · [backend emulator tier](agy-backend-emulator-e2e-tier.md) (sibling conftests global-mock the tree; verify FULL-TREE via `-m emulator`).
- [Frontend vitest harness](agy-frontend-vitest-harness.md) — jsdom rAF stub, zustand fresh-object resets; `vi.mock` can't close over a spy.
- **Toolchain pins** — [venv is Python 3.11](agy-canonical-test-venv.md) (`backend/.venv`; flags in the requirements runner-note) · [rules tests need Java](firestore-rules-tests-need-java.md) (Temurin on Win, brew `openjdk@17` on Mac; JAVA_HOME in `~/.zshenv`) · [Node 26 breaks vitest jsdom storage](node-26-breaks-vitest-jsdom-storage.md) (run Node 22 LTS; check `node --version` first).
- [✅ Gemini key leak (FIXED)](real-gemini-key-leaks-into-pytest-env.md) — `setdefault` is wrong for a secret; conftests assign. Rotation owed.
- [Live-guard needs @live](test-live-guard-needs-live-marker.md) — real-key tests need `@pytest.mark.live` or the guard is swallowed.
- [Windows-authored code hides POSIX bugs](windows-authored-code-hides-posix-bugs.md) — chmod, `C:/` paths, `;` PATH joins, `USERPROFILE`, `robocopy`, and bare `python` in ~20 doc lines; 7 found, 3 printed SUCCESS first.
- [Full-suite contention](vitest-full-suite-contends-across-lanes.md) — locks are per-STACK; long runs → persistent log; bg shells die on chat close.
- [⛔ "jsdom OOM" was a mock bug](sudo-admin-jsdom-oom-machine-bound.md) — an unstable `useRouter()` mock drove an infinite render loop.
- [coverage `source` ignores paths](coverage-source-silently-ignores-file-paths.md) — a .py path in `source` measures NOTHING; use `source_pkgs`.
- [Governance gate scans venv](governance-gate-scans-venv.md) — CLOSED; this WAS the xdist tail-hang. Prune is BY NAME.
- [Eval negative controls](eval-harness-negative-control-convention.md) — must-FAIL controls need `_negative_control:true` + `NC_` id.
- [E2E gate fiction test](e2e-gate-fiction-test-guardrails.md) — a report-only gate hid a fiction spec + wrong playwright config.
- [ATDD mocks match the contract](atdd-mock-shape-must-match-backend-contract.md) — mocks must use values the backend actually emits.
- [Red-file hosts expansions](red-file-hosts-expansion-tests.md) — a story's tests live in its ONE red file per tier; extend, never fork.
- [JWT last-char tamper is a no-op](jwt-tamper-last-char-is-a-noop.md) — that char carries 4 bits; mutate leading chars instead.
- **BDD** — [Vision Lock right-sized](bdd-vision-lock-rightsized.md) (lock conversation mandatory, standalone pytest-bdd opt-in) · [sync step needs asyncio.run](bdd-sync-step-needs-asyncio-run.md) (sync steps driving async need it; a skip-guarded RED masks it).
- [Domain-gated fixtures](domain-gated-fixtures-web-verify.md) — discharge domain-fixture gates against PRIMARY sources, never memory.

## Code-change hazards
- [New read regresses siblings](new-read-on-shared-endpoint-regresses-siblings.md) — run the whole endpoint suite, not just your test.
- [Shared registration entangles](shared-registration-file-entangles-stories.md) — registry.py carries sibling hunks; staged imports need staged modules.
- [Relocating drops mount guards](relocating-drops-mount-guards.md) — moving a conditional into a render guard drops mount preconditions.
- [Async routers must not block](agy-async-routers-must-not-block-the-loop.md) — sync Firestore in `async def` freezes every concurrent SSE stream.
- [Destructive re-verify reads FRESH](destructive-reverify-must-read-fresh.md) — a cached re-check no-ops the delete, and it looks like success.

## GitNexus
- [Index is machine-local](gitnexus-index-not-actually-live.md) — it doesn't travel via git; every MCP call MUST pass `repo:`.
- [Verify index after pull](gitnexus-verify-index-fresh-after-pull.md) — check `indexed_commit == HEAD` or fail-safe to the full suite.
- [impact() misses attr-dispatch](gitnexus-impact-misses-attribute-dispatch.md) — returns 0/LOW for `self.<attr>.<method>()`; grep-verify LOW.
- [Grep skips gitignored projects](grep-skips-gitignored-projects.md) — blind to `Projects/` from the lobby root; point path one level down.
- [Relocated links are mis-pathed](relocated-doc-links-are-mispathed-not-dead.md) — a broken link in a copied doc means the target moved.

## Toolkit & sync
- [Thin projects — center owns workflow law](thin-projects-center-owns-workflow-law.md) — no vendored toolkit anywhere; binding a project MEANS reading its `.agents/INDEX.md` or STOP.
- [Repo-local enforcement never centralizes](repo-local-enforcement-never-centralizes.md) — hooks + `jira.conf` + BMAD tomls stay in the repo they gate; stripping them deletes enforcement, not duplication.
- [`platforms: []` means NOWHERE](platforms-empty-list-means-nowhere.md) — syncs to ZERO platforms (omitting the key = all four) while looking installed.
- **The non-Claude platforms** — [Codex is the 4th](codex-is-fourth-platform.md) (reads AGENTS.md + skills natively; sync pushes only ~/.codex/prompts + skills) · [Antigravity uses workflows](antigravity-uses-workflows-not-commands.md) (the 12k limit is SOLVED via auto-emitted launchers; never byte-golf).
- [Command center → child skills](command-center-sudo-skills.md) — lobby `/sudo-*` are skill-launchers targeting the active project.
- [BMAD wrappers are opencode-only](bmad-wrappers-are-opencode-only-bridges.md) — testarch/persona stubs = [opencode]; sudo-* keep both.
- [Sync ghost-purge is FIXED](sync-leaves-local-command-ghosts.md) — `.sync-manifest.json` retires renamed/deleted commands everywhere.
- **Sync scope since 08-07** — [covers .agents not docs](toolkit-sync-covers-agents-not-docs.md) (targets the LOBBY + machine caches only; projects read from the center) · [maintained-projects is a LINT worklist](maintained-projects-allowlist.md) (sync no longer reads it; Fresh de-listed).
- **Deliberately frozen, not gaps** — [installed ≠ maintained](toolkit-installed-but-deliberately-unmaintained.md) (B-L-WorldWide + BRKN_Tattoos frozen on purpose) · [Fresh RETIRED 08-07](fresh-workspace-living-template.md) (no template exists now; cut new projects from the lobby master).
- [Rules read in place](rule-org-single-source-audit.md) — one home since 08-07: the center's `.agents/rules/`; the project vendor it describes is gone.
- [SOP doc currency gate](sop-doc-currency-gate.md) — ARMED 08-08: a usage-surface change without `sudo_workflows_testing.md` is REJECTED; `[sop-ok]` opts out.
- [Command restructure 07-14](command-surface-restructure-2026-07-14.md) — the rename map + /sudo-e2e gate + -SkipAP.
- [sudo commands have _AP twins](sudo-commands-have-ap-twins-that-drift.md) — when fixing one, diff the twin.
- [/team-onboarding is built-in](team-onboarding-is-claude-builtin.md) — a CLI built-in, NOT a toolkit file; don't re-hunt it.
- [check_maps falsely STALEs AGY](check-maps-all-false-stale-agy.md) — the fan-out omits AGY's ignore list; re-lint before trusting it.
- **Map/graph tooling is a CACHE** — [map-drift recorder](map-drift-recorder.md) (a post-commit hook journals drift; not truth; lobby-only) · [doc-graph UNC hang](doc-graph-unc-hang-and-scope.md) (rebuild bare, never widen --root).
- [Workflow-enforcement scripts](workflow-enforcement-scripts.md) — checklist prose as runnable checks; `tests/run_all.py` is the gate.
- [Board narrative lives in history/ since 08-03](board-narrative-lives-in-history.md) — AGY board is bare state (~62 KB); a note on a finished row is a lint ERROR; close-outs append to history/CHANGELOG.md.
- [PS console fakes mojibake](powershell-console-fakes-mojibake.md) — shows valid UTF-8 as `â€"`; check BYTES, never the terminal.
- [Hooks live in .githooks](git-hooks-live-in-githooks-not-git-hooks.md) — `core.hooksPath` set in 3 of 4 repos; `.git/hooks` silently does nothing. Fix machine-wide → [[two-machines-mac-and-pc]].
- [Memory lives in the repo now](portable-memory-store-dot-slug-trap.md) — `_artifacts/_memory/` + a junction; slug turns `.` into `-` too, and missing that strands everything.

## Autopilot
- **Engines** — [two, and they drift](autopilot-has-three-drifting-engines.md) (claude + opencode .ps1; a fix must land in BOTH) · [⛔ mobile RETIRED 08-07](autopilot-mobile-mirrors-claude.md) (Remote Control runs the desktop engines; don't re-create it).
- [Engine is project-local](autopilot-engine-is-project-local.md) — the .ps1 lives per-project (diverged); lobby holds only the spec.
- [glm hybrid lane](autopilot-glm-hybrid-lane.md) — Dev on GLM via Z.ai, QA stays Claude; AGY-only, propagation owed.
- [Takeover: check liveness](autopilot-manual-takeover-check-liveness.md) — a "crashed" autopilot can resume and overwrite run files.

## Working style
- [Own it plainly](own-it-plainly-dont-make-excuses.md) — own it in one line, then ACT.
- [Two-doc story close](story-artifacts-two-doc-close.md) — audit appends to the PLAN, review to the WALKTHROUGH; `Verdict: … @ <sha>` is the flip gate.
- [Limits relocate, never truncate](limits-relocate-content-never-truncate.md) — the 8/10 KB artifact caps are GONE (SCC-51); a limit is only legit when going over means content is in the wrong file.
- [Story artifacts live in the tree](story-artifacts-live-in-the-tree.md) — absence in THE tree = the step never ran; RUN the command.
- [Operator chairs the board](operator-chairs-the-board.md) — multi-voice boards advance ONLY on the operator's word; voices ASK.
- [Caucus-card contract](adviser-board-caucus-card-contract.md) — silent caucuses → one-speaker Team Cards with originator credit.
- [Daniel sells Hormozi-style](daniel-sells-hormozi-style.md) — direct, prove-it, give-value-first; default for marketing/copy/offers.
- [Writes for a big-picture operator](writes-for-big-picture-operator.md) — Sudo Hatter gets the vision, not the plumbing: consequence before mechanism, explain every term, never dumb down the system.
- [Wrappers collapse nested menus](wrapper-flows-collapse-nested-menus.md) — sudo-* auto-continue BMAD step-menus; stop only at real decisions.
- [Dev-flow model-switch stops](dev-flow-model-switch-stops.md) — `continue`=audit here, `changed`=audit then STOP AGAIN; never offer model changes.
- [Dev-story gate is conditional](dev-story-gate-is-conditional.md) — Step 2.5 stops ONLY on real questions, else proceeds.
- [Restate Always-On obligations](restate-alwayson-obligations-in-command-bodies.md) — agents follow the literal step list; bake them in as steps.
- [No personal name in directives](no-personal-name-in-directives.md) — no "Daniel" in `.agents/` directive bodies; generic referent.
- [Plan reviews ride md-feedback memos](plan-reviews-ride-md-feedback-memos.md) — list_annotations FIRST (editor reflow hides the one real memo); edit directly (apply is fix-only), respond in-thread; he closes in VS Code; one-item-per-line lists.

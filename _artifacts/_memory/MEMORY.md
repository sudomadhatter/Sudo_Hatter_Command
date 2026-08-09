# Memory index

<!-- One line per memory: link + a short hook. Detail lives in the file. Keep under ~140 lines.
     Related memories share a line rather than getting one each — every file stays linked. -->

## ⛔ Read first
- [TWO machines: Mac AND PC](two-machines-mac-and-pc.md) — every shared doc is read on both; `python3` vs `python`; `core.hooksPath` is per-machine → gates silently OFF on a fresh clone.

## Jira & tickets
- [Jira is LIVE (SCC + AVCH)](jira-integration-live.md) — `acli`, already authed; every branch/commit carries a key; gate ARMED, wrong-project key rejected.
- [Cross-repo work = a ticket PER REPO](cross-repo-work-needs-a-ticket-per-repo.md) — widening a project's `jira.conf` is ruled out in writing; and the key comes from the `epic/*` branch, never from the BMAD epic number.
- [`To Do Next` IS the queue](to-do-next-is-the-queue.md) — lead every "what's next" with it; `todo_list.md` is RETIRED as an agent source; the doc's `Blocked` doesn't exist (it's `Blocking`).
- [VS Code hides hook output](vscode-hides-git-hook-output.md) — a warn-only hook looks like clean success; ship hooks ARMED.

## AGY access & data
- [Corpus IS the asset](agy-corpus-is-the-asset.md) — real-user data is a revenue line; demo data is placeholder by design.
- [Archive, never delete](agy-archive-never-delete-ruling.md) — no delete affordance ever ships; removal = archive + `revoked` in one call.
- [Real NDA-signed users](agy-has-real-nda-users.md) — production `users/` is NOT test data; delete only from an allow-list.
- **The entitlement claim** — [no provenance](agy-entitled-claim-has-no-provenance.md) (one shared boolean; a billing revoke kills school access) · [claim-primary authz](agy-authz-claim-primary-ruling.md) (never a Firestore read on the gate) · [two redemption doors](agy-redemption-has-two-doors.md) (REST endpoint AND the HR tool).
- **Fail closed, both of them** — [admin role](agy-admin-role-fail-closed.md) (roleless/invalid → DENY, never a defaulted super_admin) · [seat cap](agy-school-seat-cap-fails-closed.md) (no `max_seats` → cap 0 → every redemption REDEEM_FULL; check for None).
- [Single-writer gate needs literals](single-writer-gate-needs-literal-payloads.md) — the AST gate flags variable/spread payloads on `users/{uid}` writes.
- **Product truths that get re-litigated** — [/hanger-talk IS the free tier](agy-hanger-talk-is-the-free-tier.md) (free ACCOUNT by design; don't re-file 4.27 as unbuilt) · [always .org](agy-domain-is-always-org.md) (every `@aviationchat.com` was a TYPO; demo = `schools/ACDEMO`) · [voice-router entitlement vs cost](voice-router-entitlement-vs-cost-cap.md) (4030 is PAID-only; free routers ungated but 4029 cost-capped).
- [Error envelope shapes](agy-error-envelope-shapes.md) — HTTPException → `body.detail.error.message`; app handlers → top-level `body.error`.
- **Closed, keep the lesson** — [admin creds drift](admin-credentials-drift-from-doc.md) (bcrypt-check first, then suspect a wedged uvicorn) · [ghost-doc window](agy-school-identity-ghost-doc-window.md) (never-delete + BY-ID→BY-FIELD lookup surfaced superseded records).

## AGY sprint & stories
- [Epic 19 REOPENED 08-08](agy-epic-19-deferred-pin-cascade.md) — AVCH-18 on `epic/AVCH-18-adk-2x-runtime`; adk 2.6.3 4-family bump; start at 19.5; don't merge to main early.
- **Reading the board** — [it recommends stale work](sprint-dependency-map-recommends-stale-work.md) (lags the YAML; check status first) · [⛔ scrum board RETIRED 08-07](sudo-update-scrum-board-five-zones.md) (SCC-13; recover via `git show 8144518^:...` — the operator went looking and couldn't find it; its Step 2.5 is SCC-56's spec).
- [`parallel-ok` is a SET property](parallel-ok-is-a-set-property.md) — ① can't rule it (siblings don't exist yet); moved OUT of ① to on-request SCC-56 `/sudo-parallel-check`. `quick-dev` + `blocked` stay.
- **State rots independently** — [epic keys rot silently](agy-epic-keys-rot-silently.md) (a stale REASON keeps a row alive) · [epics.md + YAML check each other](agy-epics-md-is-partial.md) (YAML wins on state, epics.md for the why) · [deferred EPIC, never deferred-v3](agy-deferred-epic-not-deferred-v3.md) (parked rows hold a finished epic open forever).
- **Multi-lane landing** — [lanes fix one finding](parallel-lanes-fix-the-same-finding.md) (re-diff the epic branch; the SET rule binds on file OVERLAP) · [close-out shape](multi-lane-closeout-board-merge-shape.md) (flip from the STORY FILE) · [landing ≠ close-out](landing-is-not-closeout.md) (check git BEFORE closing out).
- [Story files canonical dir](agy-story-files-canonical-dir.md) — `_bmad/bmm/stories/`; grep dot AND dash forms; next ID from sprint-status.yaml.
- [Status-flip contract](story-status-flip-contract.md) — dev sets `review`; only human close-out sets `done`.
- [Follow-ons are NOT a new story](followon-fixes-are-not-a-new-story.md) — no worktree/board key; fix on the epic branch (or `chore/*` off main).
- [Close-out is the sign-off](close-out-command-is-daniels-signoff.md) — an operator-invoked sudo-* command IS the sign-off; never punt back.
- [active-context budget](active-context-pointer-budget.md) — ≤20 KB ≈ 5k tokens; entries born as ≤3-line pointers; stale text DELETED.
- **Scoping discipline** — [settled decisions are not gaps](settled-decisions-are-not-gaps.md) (never file a ruled-on decision under "limitations") · [recon reframes scope](recon-reframes-story-scope.md) (the feature already existed ×3; ground-truth by BEHAVIOR) · [test-debt = characterization](test-debt-stories-are-characterization.md) (retrofit tests pass green-first).
- [TEA retrofit (CLOSED)](tea-retrofit-active-initiative.md) — hub node only; lessons live in the linked memories.

## AGY infra & ops
- **A wedged process fans out** — [wedged backend](wedged-backend-fans-out-three-symptoms.md) (serves /health fast while hanging every Firestore route — restart FIRST) · [git merge wedges Next dev](git-merge-wedges-next-dev-tailwind.md) (a merge under `npm run dev` wedges Tailwind).
- **Cloud Run** — [deploys backend/ only](agy-cloud-run-deploys-backend-only.md) (docs in git cost $0) · [stale revision fakes an incident](stale-cloud-run-revision-fakes-prod-incident.md) (only `release` reveals a 0%-traffic revision) · [FAH secrets need viewer too](fah-secret-needs-viewer-role.md) (accessor AND viewer).
- **Per-machine, never travels** — [env migration kit](env-migration-kit.md) (clone first, restore second) · [secrets layout is operator-owned](secrets-bundle-layout-is-operator-owned.md) (never reorganize; use his copy) · [`.zshrc` invisible to automation](zshrc-is-invisible-to-automation.md) (shared env → `~/.zshenv`) · [gitconfig didn't travel](gitconfig-never-migrated-to-the-mac.md) (`autoSetupRemote` can't retro-fix old branches).
- [Commit and push are ONE action](commit-and-push-are-one-action.md) — never end a step unpushed or dirty; verify `0 0` + clean per repo.
- [Git branch model](git-branch-model-standard.md) — main is the ONLY long-lived branch; `epic/*` merges via /sudo-push-e2e; branches carry a Jira key.
- [Hook `ask` = DENY in auto mode](hook-ask-becomes-autodeny-in-auto-mode.md) — gates main only; reads pass, mutations die; retry once, then hand over the rule.
- [Pruned worktree blocks re-add](pruned-worktree-leaves-a-blocking-shell.md) — the empty dir blocks `worktree add`; only PowerShell deletes it.
- [Worktrees skip gitignored assets](worktrees-do-not-inherit-gitignored-assets.md) — copy auth_keys/ + .env; junction node_modules; `npm ci` for E2E.
- **Ops surfaces** — [overseer jobs paused by design](overseer-jobs-paused-by-design.md) (both PAUSED 07-17; resume overseer-nightly only) · [Sentry API](sentry-api-access-aviationchat.md) (token in backend/.env; control vs region host split; loop-guard filter is sacred) · [incident pipeline 16.2](incident-pipeline-16-2-operations.md) (agent lane PRIMARY; fire endpoint is the fallback).

## Testing
- **A green or a red can lie** — [a red can die pre-assertion](red-test-can-die-before-its-assertion.md) (a failure in SEEDING looks identical; read WHICH line raised) · [stubbed children = vacuous green](stubbed-children-make-green-vacuous.md) (mocking its panels proves NAVIGATION, only) · [a piped gate hides its exit code](piping-a-gate-hides-its-exit-code.md) (`| tail` → `$?` is TAIL's; run gates bare).
- **Source-grep guards are blind two ways** — [comments invert them](comment-literals-invert-source-grep-tests.md) (a comment with the pinned literal matches FIRST) · [they can't see ORDER](source-grep-guards-cannot-see-order.md) (a guard moved after the write it protects still passes).
- **The two E2E tiers** — [learner harness](agy-learner-e2e-harness.md) (TEA-16 emulator harness is the ONE e2e suite) · [backend emulator tier](agy-backend-emulator-e2e-tier.md) (sibling conftests global-mock the tree; verify via `-m emulator`).
- **Toolchain pins** — [venv is Python 3.11](agy-canonical-test-venv.md) (`backend/.venv`) · [rules tests need Java](firestore-rules-tests-need-java.md) (brew `openjdk@17`; JAVA_HOME in `~/.zshenv`) · [Node 26 breaks vitest jsdom storage](node-26-breaks-vitest-jsdom-storage.md) (run Node 22 LTS).
- **BDD** — [Vision Lock right-sized](bdd-vision-lock-rightsized.md) (lock conversation mandatory, standalone pytest-bdd opt-in) · [sync step needs asyncio.run](bdd-sync-step-needs-asyncio-run.md) (a skip-guarded RED masks it).
- **Machine gates** — [typecheck: BE gated, FE not](agy-typecheck-is-enforced-nowhere.md) (pyrefly changed-files; frontend `tsc` ungated) · [ruff changed-files](agy-ruff-changed-files-is-a-hard-gate.md) (lints WHOLE files; re-run after `--fix`) · [coverage `source` ignores paths](coverage-source-silently-ignores-file-paths.md) (use `source_pkgs`) · [governance gate scans venv](governance-gate-scans-venv.md) (CLOSED — WAS the xdist tail-hang; prune BY NAME).
- **Risk + certification** — [priorities matrix](test-priorities-matrix.md) (P0 100 / P1 80 / P2 50 / P3 20%; P0+P1 need E2E) · [true-P0 surface](agy-true-p0-surface.md) (Orchestrator, RAG, Sully override, admin auth, PII scrub) · [certification at shipping SHA](test-certification-at-shipping-sha.md) (②→③ `certification-<story>.json`).
- **Secrets in tests** — [✅ Gemini key leak (FIXED)](real-gemini-key-leaks-into-pytest-env.md) (`setdefault` is wrong for a secret; rotation owed) · [live-guard needs @live](test-live-guard-needs-live-marker.md) (or the guard is swallowed).
- **Harness quirks** — [frontend vitest](agy-frontend-vitest-harness.md) (jsdom rAF stub, zustand fresh-object resets; `vi.mock` can't close over a spy) · [⛔ "jsdom OOM" was a mock bug](sudo-admin-jsdom-oom-machine-bound.md) (unstable `useRouter()` → render loop) · [full-suite contention](vitest-full-suite-contends-across-lanes.md) (locks per-STACK; bg shells die on chat close).
- **Spec + fixture conventions** — [eval negative controls](eval-harness-negative-control-convention.md) (`_negative_control:true` + `NC_` id) · [E2E gate fiction](e2e-gate-fiction-test-guardrails.md) (report-only gate hid a fiction spec) · [ATDD mocks match the contract](atdd-mock-shape-must-match-backend-contract.md) · [red-file hosts expansions](red-file-hosts-expansion-tests.md) (ONE per tier; extend, never fork) · [domain-gated fixtures](domain-gated-fixtures-web-verify.md) (verify against PRIMARY sources).
- [Importing backend.database inits](agy-database-import-is-an-init-step.md) — module-scope `get_db()` needs `initialize_app()` ABOVE it. Smoke-run.
- [Windows-authored code hides POSIX bugs](windows-authored-code-hides-posix-bugs.md) — chmod, `C:/` paths, `;` PATH joins, `robocopy`, bare `python`; 3 of 7 printed SUCCESS.
- [JWT last-char tamper is a no-op](jwt-tamper-last-char-is-a-noop.md) — that char carries 4 bits; mutate leading chars instead.

## Code-change hazards
- [New read regresses siblings](new-read-on-shared-endpoint-regresses-siblings.md) — run the whole endpoint suite, not just your test.
- [Shared registration entangles](shared-registration-file-entangles-stories.md) — registry.py carries sibling hunks; staged imports need staged modules.
- [Relocating drops mount guards](relocating-drops-mount-guards.md) — moving a conditional into a render guard drops mount preconditions.
- [Async routers must not block](agy-async-routers-must-not-block-the-loop.md) — sync Firestore in `async def` freezes every concurrent SSE stream.
- [Destructive re-verify reads FRESH](destructive-reverify-must-read-fresh.md) — a cached re-check no-ops the delete, and it looks like success.

## GitNexus
- **The index is a stale cache** — [machine-local](gitnexus-index-not-actually-live.md) (doesn't travel via git; every call MUST pass `repo:`) · [verify after pull](gitnexus-verify-index-fresh-after-pull.md) (`indexed_commit == HEAD` or fail-safe to the full suite) · [impact() misses attr-dispatch](gitnexus-impact-misses-attribute-dispatch.md) (0/LOW for `self.<attr>.<method>()`; grep-verify LOW).
- **Search blind spots** — [grep skips gitignored projects](grep-skips-gitignored-projects.md) (blind to `Projects/` from the lobby root) · [relocated links are mis-pathed](relocated-doc-links-are-mispathed-not-dead.md) (a broken link in a copied doc = the target moved).

## Toolkit & sync
- **Where law lives** — [center owns workflow law](thin-projects-center-owns-workflow-law.md) (no vendored toolkit; binding a project MEANS reading its `.agents/INDEX.md`, or STOP) · [repo-local enforcement never centralizes](repo-local-enforcement-never-centralizes.md) (hooks + `jira.conf` + BMAD tomls stay in the repo they gate) · [`platforms: []` = NOWHERE](platforms-empty-list-means-nowhere.md) (omit the key = all four).
- **The non-Claude platforms** — [Codex is the 4th](codex-is-fourth-platform.md) (reads AGENTS.md + skills natively) · [Antigravity uses workflows](antigravity-uses-workflows-not-commands.md) (12k limit SOLVED via auto-emitted launchers; never byte-golf).
- **Sync scope since 08-07** — [covers .agents not docs](toolkit-sync-covers-agents-not-docs.md) (LOBBY + caches only) · [maintained-projects is a LINT worklist](maintained-projects-allowlist.md) (sync no longer reads it) · [ghost-purge FIXED](sync-leaves-local-command-ghosts.md) (`.sync-manifest.json` retires dead commands).
- **Deliberately frozen, not gaps** — [installed ≠ maintained](toolkit-installed-but-deliberately-unmaintained.md) (B-L-WorldWide + BRKN_Tattoos frozen on purpose) · [Fresh RETIRED 08-07](fresh-workspace-living-template.md) (cut new projects from the lobby master).
- **Map/graph tooling is a CACHE** — [map-drift recorder](map-drift-recorder.md) (a post-commit hook journals drift; not truth) · [doc-graph UNC hang](doc-graph-unc-hang-and-scope.md) (rebuild bare, never widen `--root`) · [check_maps falsely STALEs AGY](check-maps-all-false-stale-agy.md) (the fan-out omits AGY's ignore list).
- **The command surface** — [center → child skills](command-center-sudo-skills.md) (`/sudo-*` are skill-launchers) · [BMAD wrappers are opencode-only](bmad-wrappers-are-opencode-only-bridges.md) · [_AP twins drift](sudo-commands-have-ap-twins-that-drift.md) (fix one, diff the twin) · [restructure 07-14](command-surface-restructure-2026-07-14.md) (rename map + /sudo-e2e gate) · [/team-onboarding is built-in](team-onboarding-is-claude-builtin.md) (a CLI built-in).
- **Doc + board law** — [SOP currency gate](sop-doc-currency-gate.md) (ARMED: a usage-surface change without `sudo_workflows_testing.md` is REJECTED; `[sop-ok]` opts out) · [rules read in place](rule-org-single-source-audit.md) (the center's `.agents/rules/`) · [board narrative → history/](board-narrative-lives-in-history.md) (bare state; a note on a finished row is a lint ERROR) · [enforcement scripts](workflow-enforcement-scripts.md) (`tests/run_all.py` is the gate).
- [⭐ Preflight resolves the repo from CWD](preflight-resolves-repo-from-cwd.md) — it printed `clear to close out and merge` about ANOTHER lane's branch; pass `--repo` AND `--branch`, echo from `rev-parse`, never from belief.
- **Local plumbing** — [hooks live in .githooks](git-hooks-live-in-githooks-not-git-hooks.md) (`.git/hooks` silently does nothing → [[two-machines-mac-and-pc]]) · [memory lives in the repo](portable-memory-store-dot-slug-trap.md) (`_artifacts/_memory/` + a junction; the slug turns `.` into `-`) · [PS console fakes mojibake](powershell-console-fakes-mojibake.md) (check BYTES, never the terminal).

## Autopilot
- **Engines** — [two, and they drift](autopilot-has-three-drifting-engines.md) (claude + opencode .ps1; a fix must land in BOTH) · [⛔ mobile RETIRED 08-07](autopilot-mobile-mirrors-claude.md) (Remote Control runs the desktop engines).
- [Engine is project-local](autopilot-engine-is-project-local.md) — the .ps1 lives per-project (diverged); lobby holds only the spec.
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

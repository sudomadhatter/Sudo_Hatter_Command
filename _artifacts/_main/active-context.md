# ACTIVE CONTEXT — _main  (you own this, not a vendor)

## 1. PRIME STATE
Current workspace: `_main` (lobby; bucket renamed from `_home` on 2026-06-26)   |   Last session: 2026-09-09
**2026-09-09 (latest): SCC-436 SHIPPED AND CLOSED — full Poimandres 3D toolset, component catalog and recipes.**
Merged to `main` at `1c541916` (PR #203). Equipped Caterpillar and `.agents/skills/visual-fx-3d/` with the complete
Poimandres (`pmndrs`) 3D creative suite (`pmndrs/react-three-fiber`, `pmndrs/drei`, `pmndrs/postprocessing`,
`pmndrs/react-three-rapier`, `pmndrs/gltfjsx`, `pmndrs/leva`). Authored `CATALOG.md` detailing 100+ components across
8 domains with exact imports and props. Authored `RECIPES.md` with 8 copy-pasteable production component examples.
Updated `/smh-designer`, `frontend_UI_design_guide.md`, and `workflows_testing_SOP.md` with direct repo links.
All 83 test suites passed. Dev Record filed, ticket transitioned to Done, worktree pruned.
Record: `_artifacts/_main/2026-09-09_scc-436-r3f-repo-link/walkthrough.md`.

**2026-09-09: SCC-435 SHIPPED AND CLOSED — full React Three Fiber and Drei 3D suite in /smh-designer.**
Merged to `main` at `f4700885` (PR #201). Subbed out synthetic SVG displacement filter (`liquid-glass-js`) for
`pmndrs/react-three-fiber` + `@react-three/drei`'s `MeshTransmissionMaterial` (authentic Apple VisionOS physical optical
glass refraction with chromatic edge dispersion). Added tactile 3D Spring Tilt Cards (`PresentationControls`), `gltfjsx`
model compilation workflow, and DOM-in-3D pinning (`<Html>`). Capped `dpr={[1, 1.5]}` and `frameloop="demand"`
invariants enforced. All test suites green (343/343 command surfaces, 102/102 parity, 28/28 allowlist, check_maps green).
Worktree pruned, Dev Record filed, ticket Done. Record: `_artifacts/_main/2026-09-09_scc-435-r3f-drei-suite/walkthrough.md`.

**2026-09-07 (late night): /smh-llm-approvals (SCC-434) — MERGED and CLOSED (PR #197 @ 3db331d1).**
5 new approval families harvested across platforms into `families.json` (`allow-gh-api`, `allow-gh-run` rerun, `allow-gcloud-run-describe`, `allow-npx-next`, `allow-npx-tsc`). Uncovered stops dropped from 14 to 7 (~1.5h wait saved). Antigravity store updated (`allow=275, deny=500`, keeping 148 store-only clicks); Claude user scope apply command printed for operator; PR #197 merged, ticket SCC-434 Done. Worktree pruned.

**2026-09-07 (night): AUTOPILOT v3 — Task SCC-429 with both lanes PLANNED, AUDITED (GO) and PUSHED, waiting on ONE approval. Nothing built.**
`/smh-plan-task SCC-429` ran end to end: SCC-430 (Claude, wave 1, `chore/SCC-430-autopilot-claude`, PR #192 draft) and
SCC-431 (Zoo, wave 2, locked after SCC-430, `chore/SCC-431-zoo-remote`, PR #193 draft), each with
`implementation_plan.md` + `task.yaml` + its fast-read outline committed and its plan ATTACHED to its ticket; both
`Audit verdict: GO` after a three-lens self-audit that found and RESOLVED 3 blockers on the Claude plan (the
`sandbox.excludedCommands` edit does not exist as a mechanism — `claude_permissions_apply.py` refuses that key by
design and by test, so S0 now MEASURES reachability; deleting the 5 old doors breaks `test_review_engine.py`,
`test_twin_parity.py`, `test_settings_allowlist.py` + 2 code-review-engine docs, now declared; the port rule fired on
the teaching-edition mirror, ruled out of scope with evidence) and 1 blocker + 4 behaviour-changing findings on the Zoo
plan (no `_artifacts` INDEX row → close-out gate; the PC service must run INSIDE WSL or it cannot reach the Unix
socket; keyway has NO readable verb so `keyway run -e` is the launcher and the token never touches a service file;
`code tunnel` has no binary in WSL). The design record rides the SCC-430 branch. **The one stop: his approval of the
two plans.** Then `/smh-quick-dev` in the SCC-430 lane; SCC-431 after it lands; SCC-429 closes LAST.
Rulings still owed: 1 (the charter rows), 3 (the five deletions), 5 (the Zoo approve path).
SCC-208 (the Idea ticket) deleted by the operator; its history is snapshotted in the design folder and attached to SCC-429.
The record is [`2026-09-07_autopilot-v3-design/implementation_plan.md`](2026-09-07_autopilot-v3-design/implementation_plan.md)
(summary posted as a round-3 comment on SCC-208). Shape: one interactive lead session (March Hare, Remote Control on)
dispatches each step through a deterministic runner (`autopilot_run.py`, not built) to a fresh headless `claude -p`
child started as one Wonderland seat (rendered AT LAUNCH as `--agents` JSON from the same `smh-team-*.md` masters that
make the Zoo modes, `skills:` preloaded — the on-disk `.claude/agents/<seat>.md` idea was withdrawn in round 3d), running the EXISTING door; every step is a Jira comment (`jira_feed.py step`,
not built); ③ is a fresh Fable child with no seat identity. Rulings owed: (1) the charter table §2.5 row by row,
(2) Telegram deferred in favour of tap chip + ticket, (3) delete the three `-AP` twins and the opencode launcher, banner
the six `.ps1` engines. Prerequisites before any spike: CLI upgrade to ≥2.1.259 (Ask First) and two settings rows
putting the runner on `sandbox.excludedCommands`. Operator direction mid-session: Claude first, then a Zoo variant
(§2.6: March Hare + `new_task` + `zoo_notify.py`, which already pushes to the phone), AND a **Zoo remote is its own
subtask by his word** (§2.6.1: the inbound half is the gap — `zoo_inbox.py` on a secret ntfy reply topic posting his
reply onto the ticket for the March Hare's poll; Jira-app reply is the zero-build path; Remote Tunnel for raw asks;
Telegram is the swap if he wants chat UX). **Round 3b (same evening) answered his cost question** — §9 of the record:
children must NOT each re-research; five layers (byte-identical prefix with `--exclude-dynamic-system-prompt-sections`
mandatory, a per-story `context-pack.md` written once by a cheap Gnat child, the build child as a `--resume --fork-session`
of the plan child so the Cat runs ② end to end on one seat, fresh sessions only for audit and review, lead holds summaries).
Vendor pages read: prompt-caching / sessions / workflows; community: Anthropic 4×/15× numbers, HumanLayer, Ralph loop,
Roo Boomerang, Cline bank, Deriv/mer.vin measurements. One risk to measure in S0: a custom system prompt (`--agent`?) may get
ZERO cache reads; fallback is `--append-system-prompt-file` + `--system-prompt-snapshot on`. Dynamic workflows weighed and
deferred. **Round 3c (same evening) — the Zoo remote, §10:** Zoo KEPT Roo's programmable surface (measured on the
installed 3.83.100457 bundle + Zoo's source): an IPC Unix socket via env `ROO_CODE_IPC_SOCKET_PATH` (StartNewTask /
ResumeTask / SendMessage in, every task event out — `TaskInteractive` = needs you) and an in-process API with
`approveCurrentAsk` / `pressPrimaryButton`. A text `SendMessage` ANSWERS a pending `followup` ask but is "denied with
feedback" on a tool ask, so approvals need a ~50-line companion extension. Roomote Control is dead with Roo. Claude side
already done: Remote Control forwards permission prompts to the phone (vendor page), and first-party Telegram/Discord/
iMessage CHANNELS exist with Allow/Deny relay buttons. Recommendation: ONE app, Telegram (bot bridge for Zoo with chat-id
allow-list; channel plugin for Claude optional); events replace the thread-store poller; `code tunnel` inside WSL as the
fallback. Zoo also ships a headless `roo` CLI = Zoo's `claude -p` (lever for the S8 variant). All three rounds are comments
on SCC-208; six rulings listed in §7. **Round 3d (same evening) — his rulings + the drift check, §11:** RULED in his words:
"Claude already has remote, we don't need anything more than that. Zoo is the one I am interested in making work remote
and we would have to build that. I also have an iOS phone." → rulings 2 and 6 closed (Claude lead stays on Remote Control,
no Telegram channel), ruling 4 closed (iOS → Telegram bot for Zoo; the ntfy iOS app cannot type a reply); the phone carries
TWO apps (Claude app + Telegram). Drift requirement ("scale on top of the workflow we use, not stand-alone; edits to the
/ commands and rules auto-update") answered YES by construction: `.claude/commands` is a RETIRED door — Claude enters a /
command through a generated launcher skill that is a POINTER to the `.agents/commands/` master, `.roo/commands/` is the same
pointer, `.roomodes` roleDefinitions are pointers to the seat masters (`test_zoo_team.py` compares generated vs master);
rules arrive live via CLAUDE.md `@` imports + `.claude/rules/` + the `rule-trigger.py` UserPromptSubmit hook; skills preload
full content at launch. So: the Claude seat is rendered at LAUNCH as `--agents` JSON (session-only, never on disk; S2 amended),
the runner passes door NAMES never text and holds NO list of doors (the retired `.ps1` engines' exact failure), `--bare` is
forbidden on children (skips the hooks that carry the law), and an S1 grep test refuses any door/rule text inside the runner.
One new S0 measurement: `--agent` resolving an `--agents`-defined seat on one launch line (fallback `--append-system-prompt-file`).
The four rounds were comments on SCC-208, snapshotted to `2026-09-07_autopilot-v3-design/tickets/brainstorm-history-scc-208.md`
before he deleted it. **Minted (his go, 2026-09-07 night):** SCC-429 Task under the CI/CD grouping epic SCC-33 (placement his to
move), plan + history ATTACHED, fast-read outlines `tickets/SCC-429.md` / `SCC-430.md` (Claude, S0–S6) / `SCC-431.md` (Zoo, S7 remote
then S8 variant), all bare, all To Do. Design folder renamed key-free to `2026-09-07_autopilot-v3-design/` (was untracked, links repointed).
Next: rulings 1, 3, 5 on SCC-429, then `/smh-plan-task SCC-429` grounds the two lanes (`chore/SCC-430-…`, `chore/SCC-431-…`) — nothing is cut yet.

**2026-09-07 (earlier today): `/about` INVESTOR SURFACE — reviewed, FAILED, hotfixed, LIVE. Next up is AVCH-140.**
AVCH-133 (quick-fix-1.3, the `/about` rebuild) had merged at `660f7794` self-rated CONCERNS "because no
independent review ran". The operator asked for `/cicd-code-review` to move it to PASS. **It moved to FAIL**:
five clean-room lenses (each in its own project worktree at the reviewed sha) found 7 real defects live on
aviationchat.org — all 14 nav controls dead, `Escape` scrolling past the whole Spindle, `<img src="">` on both
Try cards, `border-white/12` emitting no CSS, raw `#E000FF`/`#24FF00` in 21 places against the "blue and white
only" ruling, `lenis` installed unapproved, and a byte budget measuring ZERO `/about` assets (no Storage
emulator — proven by browser probe). Every gate was green the whole time. Operator ordering: hotfix first.
**AVCH-139 (quick-fix-1.4) shipped the live-breaking seven** via PR #92, merged `0b1d2979`, all 8 checks green,
773 unit / 86 journey certified, mutation sweep 5/5 — and the sweep caught MY new guard being vacuous three
times before it was real (record: `_artifacts/quick_fixes/quick-fix-1.4-about-review-fallout/mutation-table.md`).
CI also surfaced a pre-existing race in `admin.student-archive.red.test.tsx` (hardened once 2026-09-06, assertion
left behind) — fixed in-lane, proved non-vacuous, not re-run-until-green. Both tickets Done, Dev Records filed,
worktree + 4 lens checkouts pruned (7 symlinks unlinked first, targets verified), both branches gone local+remote.
**PHONE QA CAME BACK (2026-09-07 23:51, operator screenshot): "glitchy, nothing moves, not mobile first."**
Diagnosed from code, not guessed: the phone gets a STATIC page BY THE APPROVED PLAN'S OWN WORDS — plan §Spindle
"Mobile: no pin at all" (`Spindle.tsx:67` gates the pin on `min-width: 640px`), the ray fan's sway is
`animation: none` under 640px (`HeroBackdrop.tsx` base rule; only a 21–35s opacity pulse survives, invisible),
and the plan's one promise for phones — "retaining entrance choreography" on the stack — was never built
(`Spindle.tsx:167` base branch has zero motion). MY gap, not the device's; review lenses judged against the plan.
Plus a rendering bug: the deck GlassPanel shows a straight line above its rounded top-left corner — the known
WebKit `backdrop-filter` + `border-radius` + `overflow:hidden` square-region bug; fix is a `-webkit-mask-image`
radial-gradient on the rounded element (unverified on iOS from here — operator confirms after). The magenta
"PERSONAL AVIATION TUTOR" in the header is the site-wide brand PNG `AvCh_Full_Logo_2.0.png`, NOT `/about` code;
blue/white there needs a new logo asset — product call, raised once.
**LANDSCAPE PHONE (second screenshot, 23:5x): "scrolling doesn't do anything."** REPRODUCED the review's
`overscroll-contain` finding on a real device: sideways the phone is >640px wide so it gets the PIN, but the
viewport is ~390px tall, so the pinned card (`Spindle.tsx:271` `max-h-full overflow-y-auto overscroll-contain`)
becomes its own scroll container and `overscroll-contain` swallows every swipe — the page never advances, the
Spindle never releases. Desktop never sees it because the card fits. Also `h-screen`=`100vh` at `:226` misjudges
iOS's toolbar viewport → use `100dvh`. Fix belongs in AVCH-140 (0).
**AND THE PALETTE MISS IS MINE:** the `SYS.ROULETTE` eyebrow in his screenshot is PINK — `#C766D6` (orchid),
which MY hotfix d12cc943 put in as the replacement for `#E000FF` (page.tsx:60,86; TryAgentCards.tsx:76-77;
SlideDeckViewer.tsx ×5). Still purple under a "blue and white only" ruling. AVCH-140 (0) swaps every `#C766D6`
to the house cyan `#00C2FF` / white and the P1 guard test gains `#C766D6` as a third forbidden hex.
**LOCKED VISION for the Spindle (operator, 2026-09-07 ~00:00, his words):** "a turning drive train. Like a
vertical turn table. The images rotate in as it scrolls down. They slide into view as you go down and back out
when you go up." Read back and confirmed: a DRUM on a horizontal axle, viewer faces its front; scroll is the
crank — SCROLL-LINKED (angle = scroll position), never scroll-triggered, so reversing is free. Next card rises
from the bottom edge tilted back (rotateX), flattens at eye level, tilts forward and exits over the top; scroll
up reverses it exactly. Dot rail turns with it like the chain. PHONES GET THE DRUM TOO — and moving cards
DROP backdrop-blur (glass look via gradient; only the flat reading card keeps real blur) because 3D rotation +
blur compounds on a mobile GPU. `prefers-reduced-motion` keeps the plain stack. Plan §2 quotes this verbatim.
**AVCH-140 / quick-fix-1.5 — `/about` REBUILT MOBILE FIRST. SHIPPED, merged `5765710a` (PR #93), ticket Done.**
Certified at `de02ded5`: frontend unit 778 passed/1 skipped (111 files), journey pack 105 passed, `next build
--webpack` green, tsc only the 7 pre-existing Epic 23 errors, eslint 0 errors on changed files, mutation sweep
**11/11 killed**. Record: `Projects/AGY_AVIATIONCHAT/_artifacts/quick_fixes/quick-fix-1.5-about-mobile-first-drum/walkthrough.md`
(+ 11 screenshots at three viewports beside it). ⛔ THE PLANNING TEXT BELOW THIS BLOCK IS SUPERSEDED — it
describes AVCH-140 as unstarted.

WHAT LANDED: **the DRUM** — cards in normal page flow, no pin at any width, each turning around a vertical
shaft as a pure function of its position; scroll-LINKED, so the strongest row (D1) returns to a remembered
scroll offset and demands a byte-identical transform matrix, which no keyframe can pass. **The AURORA** —
vertical curtains that run on a phone, set and indifferent to scroll. **`.inv-lit`** replaces every
`backdrop-filter` on the surface (a blur over a moving field can never be cached — that was the stutter, and it
took the WebKit corner artifact with it). Blue and white asserted as a rule in HSL. An honest weight gate: it
had been measuring ZERO bytes while the live page shipped 27.76MB. The landscape NDA gate went from a 10.3%
reading window with the buttons past the fold to 44.9% with them on screen.

SEVEN RIDERS the operator ruled in mid-lane rather than mint separately (work-consolidation working as
designed): the app-wide bug-report chrome (closed now means ABSENT, not transparent); the Try cards showing the
agents the PRODUCT shows; `.inv-hologram` so they move on a phone; **six utilities that emitted NO css at all**;
the header at 50%; the green-screen Igor plate; and D9.

⭐ THE TWO WORTH REMEMBERING, both mine, both found by RUNNING rather than reading. (1) The full unit suite had
not been run since T2 and hid a `ResizeObserver` that threw before any assertion in every `/about` spec, plus
six utilities emitting nothing: Tailwind's opacity scale is multiples of five, so `bg-black/92` and four
arbitrary-hex `/97` were silently dropped, leaving the sticky header, nav dropdown, mobile drawer, NDA card and
two scrims with NO background over an animated field. The guard for exactly this only inspected `-white/N` and
`-black/N`; widened. (2) A record SCREENSHOT found the Try cards cut off mid-sentence on a phone — `DrumWrap`
takes its angle from the scroll progress of what it wraps and I had wrapped the GRID. D6 stayed green
throughout and correctly so: it asks whether the PAGE scrolls sideways, and `overflow-x: clip` guarantees it
does not, by slicing anything that sticks out. **Clipping is the opposite of overflowing.** D9 now measures
whether the thing being read is inside the window.

Also fixed a LIVE product defect found while sourcing art: `igor_dpe.png` was the raw green-screen plate, and
the dashboard rendered it raw on the branch every iPhone takes. The keyed frame had sat beside it unreferenced
under a misspelled stem; it now owns the name.

FOLLOW-ON — **AVCH-141** (To Do, under AVCH-132), carrying three: (A) Sully and Igor actually animate on iOS —
their alpha is VP9 WebM, which WebKit does not render, so every iPhone gets a frozen still; the fix is an
HEVC-with-alpha encode (`hvc1`, Safari since iOS 13) which needs VideoToolbox on the operator's Mac, and that
asset BLOCKS the lane. (B) A failed OAuth sign-in leaves the page spinning — `authLoading` never clears; two
candidate causes needing different fixes, and the ticket says do not fix until the console evidence names
which. Sign-in also CANNOT be tested in device emulation: the popup-vs-redirect choice reads the user agent and
Chrome's device toolbar rewrites it. (C) The dashboard drawer moves to the left, desktop and the mobile tab.
**AVCH-140 IS NOW MOBILE-FIRST, not "the a11y tail":** (0) pin the Spindle on phones too (touch-tuned,
`100dvh` not `100vh`), rays that MOVE on phones (fewer layers, but moving), entrance choreography for the card
stack, the Safari corner mask — plan for his tap-approval BEFORE any edit; then the original order:
**Original AVCH-140 order, now after (0):** (1) make the weight gate honest —
route Storage at the local byte-identical copies + a positive control, so W1/W2/W3 can actually fail;
(2) `next/image` + `images.remotePatterns` for the Storage host — **operator APPROVED 2026-09-06**, drops
`Igor.png` 4.52MB → tens of KB, closes the `no-img-element` warnings; (3) `prefers-reduced-motion` coverage
(zero at any tier; the vitest guard is unfalsifiable by mutation); (4) browser-verify then fix three layout
findings — `overscroll-contain` dead-scroll on the pinned card (the operator's own anti-trap criterion), the
14-segment rail ~0.15px/target at 375px, the NDA gate on a landscape phone (330px card); (5) a11y tail —
`aria-hidden` cards with focusable buttons, duplicate `inv-glass-refract` id, arrow keys double-bound.
Findings table with file:line for all of it: `quick-fix-1.3-about-investor-surface/walkthrough.md`
`## Code Review (2026-09-06)`. Open on the operator: live QA of `/about` on his phone (nav, Try cards, no magenta).
Tooling learned: Playwright browsers are at `/tmp/ms-playwright` (memory written; SCC-425).
**2026-09-06: EPIC 24 PHASE 1 IS SHIPPED AND LIVE, and AviationChat now runs TRUNK MODE — no epic branch.**
Merged to `main` at `77f0cfaa` (PR #87) on the operator's direction to ship now and build the rest from `main`.
Gate on the shipped tree: backend 3569P/46S/0F (cov 67.50%) · frontend build clean · **E2E GREEN 44/44** ·
main-write-gate pass (146 keyed commits) · enforcement 5/5. **Deploy VERIFIED, not assumed:** Cloud Run
revision `aviationchat-backend-00082-joc` deployed with no traffic, smoke-tested at its private
`sha-77f0cfa` tagged URL (200 — the gate that permits promotion), promoted to 100%, old revisions untagged;
confirmed afterwards by direct probe — backend `/health` 200 and `https://aviationchat.org` 200. No downtime.
Epic branch and both lanes pruned local + remote. **AVCH-100 stays In Progress on purpose:** 24.8 and 24.9
are unwritten by the 2026-08-27 ruling until the operator's TESTPILOT run, and they are now built FROM `main`.
Three gate lessons landed on the way, all recorded: the epic→main PR is the FIRST thing that ever lints most
of an epic (99 changed files at once); **editing a file is what pulls it into that gate**, so one type fix
dragged in a file carrying 6 ruff + 29 pyrefly errors and was reverted in favour of a call-site fix; and a
vitest mock keyed on a call counter failed only under CI load (de-flaked, revert-proved).
Record: `Projects/AGY_AVIATIONCHAT/_artifacts/epic_24/epic-24-ship-to-main/walkthrough.md`.

**2026-09-06: TRUNK MODE IS LIVE (SCC-423, merged `41fb27a1`; record fix `10ecf899`) — a third epic mode.**
An epic is now *extension of main*, *quick-dev*, or **trunk: no epic branch at all** — story lanes cut from
`origin/main`, landing on `main` by a PR the operator merges, so **every merge is a deploy**. The switch is a
git query, never prose: `git for-each-ref 'refs/remotes/origin/epic/*'` empty = trunk. Additive — the two
older modes are byte-untouched. ⛔ Two things deliberately did NOT change: `merge-target-guard.sh` still
refuses a LOCAL `main:story` merge (a trunk landing happens on GitHub, where no local hook runs), and the
never-branch-a-story-from-`main` hard stop still binds wherever a live epic exists. Assert-first:
`test_trunk_mode.py` RED 12/22 → 22/22, `run_all.py` 81/81. Two gates caught ME restating the sign-off rule
backwards ("the click is the sign-off" — the DECISION is). Session:
`_artifacts/_main/2026-09-06_trunk-mode-no-epic-branch/`.
**Open, operator-owned:** AVCH-136 — `www.aviationchat.org` returns NXDOMAIN (measured on two independent
resolvers, and still absent after 15 min of polling). Not caused by AVCH-128, which only ran
`firebase hosting:disable`; a cached permanent redirect is why it still appears to work in his browser.
Also filed: SCC-424 — `test_repo_template.py` intermittently dies on a `FileNotFoundError` under the CI runner.

**2026-09-05: INCIDENT — Epic 24 work reached live prod mid-epic through a chore lane; the guard now exists (SCC-416, PR #176 merged @ `604a12b0`).**
`chore/AVCH-80-rolling-bugs` (cut off `main`) shared three runtime files with the live `epic/AVCH-100`; both
preflights judged it by its own diff and `/cicd-push-e2e` shipped it (PR #72 → `4afaa667` → Cloud Run 00076).
The operator's ruling forbidding it lives on the epic branch, unreadable from `main`. SCC-416 adds
`task_preflight.epic_freeze()` — a live-epic product-file overlap check both doors run BEFORE their surface
decision — and the operator's design: the epic's mode (extension of main / quick-dev) is decided at kickoff
and carried in the branch name (`-quickdev` suffix); the story door lands by PR or direct push accordingly.
`run_all.py` 79/79 @ `5d5d7f41`. **AviationChat is untouched and owed its own tickets**: the revert
decision on `4afaa667`, re-landing AVCH-80 on the epic, ruleset `exclude` for `*-quickdev`,
`pr-check-skip.yml` to `main`, the enforce-on-create probe, and AVCH-80's ticket/worktree cleanup.
Session: `_artifacts/_main/2026-09-05_scc-416-in-flight-epic-freezes-main/`.
**Record closed 2026-09-05 (second PR, same lane name):** `finish` had held SCC-416 at `Review Required` on one
`## Your Actions` row that handed over AviationChat work; it is now a prose section in the walkthrough (content on
AVCH-80, comment 10437). Once that PR merges, `/smh-close-task-merge-tree --after-merge SCC-416` closes the ticket.
**SCC-417 (subtask of SCC-411) closes that gap — built, reviewed PASS @ `e0027c49`, PR #178 ready for the operator's merge.**
The banned-row gate now catches ticket(s) × "your call" in either order and the plural, a row filing work as another
board's tickets ("its own AVCH tickets"), and both through inline markup (`banned_action_rows` flattens the markdown the
patterns see). Ten mutants 10/10; 0 new corpus hits over 194 walkthroughs; suite 79/79. Session:
`_artifacts/_main/2026-09-05_scc-417-banned-row-plural-order/`. Next: `/smh-close-task-merge-tree` (the sign-off; it
stamps the preflight receipt the `main-write-gate` PR check reads), the merge, then `--after-merge SCC-417`.
**2026-08-23: Command Center + AviationChat maps and indexes reconciled; NEXgen excluded.**
Lobby map lint is clean; `_artifacts/INDEX.md` again carries exactly the newest 50 sessions and 110
displaced/new-overflow rows were added to the verbatim archive (168 archived total). Current artifact,
skills, commands, and workflow indexes now name the live command surfaces and measured inventory.
AviationChat is thin-project conformant, has a current repo-map and Epic 23 ledger, and passes its targeted
map gate with its code graph current. Session: `_artifacts/_main/2026-08-23_update-maps-indexes/`.
**2026-08-11: Windows-PC → Mac Antigravity IDE extension migration guide added.**
Exports portable extension IDs on Windows, transfers them by Git or direct upload, compares against the Mac, and installs only missing IDs. Guide: `docs/migrations/install_guides/antigravity-ide-extension-migration.md`; session: `_artifacts/_main/2026-08-11_antigravity-extension-migration-guide/`.
**2026-08-08 (latest): the operator's SOP page is now gate-enforced, and the system is TWO machines.**
An armed commit-msg gate (`sop_currency.py`) rejects any usage-surface change that leaves
`docs/_scc_sops_prds/workflows_testing_SOP.md` behind — `[sop-ok]` is the logged opt-out.
⚠️ **Mac AND PC:** `python3` vs `python` differ, and `core.hooksPath` is LOCAL config, so a fresh clone
has **no gates at all** — `git config --global core.hooksPath .githooks` arms every repo per machine.
Walkthrough: `_artifacts/_main/2026-08-07_toolkit-centralization/walkthrough-sop-currency.md`.
**2026-08-08: toolkit centralization SHIPPED — the thin model is live on every main.**
Epic SCC-31 + AVCH-23: ~1M lines of vendored toolkit removed; every project now carries only tier-2 law
(rules · skills · INDEX router) + the repo-local enforcement carve-out. Self-audit GO. Merged: lobby
`5e9f1ed` · VR `04bf376` · RAG `68cf6fd` · skeleton `6b96deb`; AGY = operator push of `epic/AVCH-23-thin-toolkit`
(ff, deploy-safe). Session: `_artifacts/_main/2026-08-07_toolkit-centralization/`.
**2026-08-04: rule load class has ONE source of truth, and the protocol tier now loads on a BINDING trigger.**
Audit of `.agents/rules/` found the set already clean on the things people check (all 21 have frontmatter,
`name:` matches filename everywhere, INDEX covers all 21, no ghosts). The rot was elsewhere: **load class
had three sources of truth that disagreed** — `AGENTS.md` §3, the INDEX `Load` column, and a frontmatter
`activation:` field on **12 of 21 rules written in Cursor's vocabulary** ("Always On", "Model Decision")
that **nothing reads** (grep-verified across `.agents/`, `docs/`, `.claude/`, `.opencode/`).
`000-PLAN-FIRST-GATE` — the priority-zero kill-chain — had **three sources giving three different answers**
about when it loads; `powershell-encoding-safety` claimed `Always On`. `activation:` deleted from all 12;
`AGENTS.md` §3 now states the INDEX's three tiers. **Token win:** `artifacts-always-first` (21 KB) stops
loading in conversation-only turns. **⚠️ THE LESSON — Daniel caught it, I didn't:** making the protocol tier
conditional without making the condition **binding** is a regression, not an optimization. §3 said "load the
moment a session may touch files" — descriptive; an agent can read that and never load the plan gate. Now
imperative: **load BEFORE the first tool call that creates, edits, or deletes a file — if you are about to
write and they aren't loaded, stop and load them first.** Plus a standing **anchor invariant**: the four
protocol rules are conditional but **their LAW is not** — every gate they carry is also stated inline in
`AGENTS.md` AND the floor `constitution.md`, so the stop binds even in a session that never opens the rule.
*A protocol rule whose law is not anchored in both is a defect — fix the anchor, never promote the rule to
floor.* The invariant **failed its own first test** and exposed `000-PLAN-FIRST-GATE` with zero references
in `constitution.md` (pre-existing; C2 made it load-bearing) — now fixed. Also: 2 de-dupes landed, **the 3rd
deliberately dropped** (stripping the sign-off summary from floor `constitution` would leave floor deferring
to protocol `git-policy`, which may not be loaded — the exact hole just closed); INDEX regrouped by load
class, proven lossless by sorted-line diff; **EOL integrity check added mid-run** (unplanned — a scripted
frontmatter strip is the `powershell-encoding-safety` bug class; all files 100% CRLF, 0 bare LF).
**Propagated:** `project-template` + AGY §4 + Fresh §4 by hand — `/sync-agents` vendors `.agents/` but
**never writes a project's root `AGENTS.md`** (`sync-agents.ps1:525-532`), so root files are always manual.
**OPEN (corrected — Daniel caught my misread):** `NEXgen-VR-Director` is a **healthy Fresh clone on GitHub**
(`sudomadhatter/NEXgen-VR-Director`, private, `main`+`main_debug`, full skeleton, pushed 2026-08-04 04:41) —
but **this desktop never cloned it**; `Projects/NEXgen-VR-Director/` was an empty 2026-07-30 placeholder and
the sync vendored 3 toolkit dirs into it, which now block a clean clone. Fix: clear placeholder → clone →
hand-apply §4 → re-sync. `RAG_Pipeline_AC` has an AGENTS.md but is NOT maintained, so its vendored rules never refresh.
**UNCOMMITTED ×3** (lobby + AGY + Fresh) and **`/sync-agents` owed first.**
Session: `_artifacts/_main/2026-08-04_rules-folder-optimization/`.

**2026-08-04 (latest): `reproduce-before-you-fix` — the house debug loop is now a rule.**
Debug guidance existed as five scattered one-liners (`karpathy-guidelines:20`, `collaborative-debug-first`,
`sudo-quick-dev:40`, `sudo-mobile-error-team` §4, `sudo-live-testing-team:46`) — but `grep -ri reproduc`
over **every rule and every command** returned **one hit**, a disk path in `sudo-close-workingtree`.
**Reproduction had zero coverage**, and nothing anywhere put a stop condition on the guess-loop. New
on-demand rule with **five gates**: G1 reproduce (a *citable* artifact — command, URL+click path, Sentry id,
or a failing test; "I can see it in the code" is a hypothesis) → G1.5 minimize → G2 pin a test **SEEN red**
and commit it → G3 falsify one hypothesis at a time under stop conditions (**10 min / 3 falsified / 2
no-evidence edits**, house-set and labeled tunable) → G4 minimal fix at the mechanism → **G5 revert the fix
hunk, watch the test go red, restore**. G5 is the gate nobody runs and the only cheap proof a pinning test
isn't passing coincidentally. Two legitimate *endings* keep agents from faking a repro: can't-observe →
`collaborative-debug-first`; genuinely non-reproducible → add observability and stop. **Dispatch matters
more than the rule** — an on-demand rule only fires if something reaches for it, so the pointer went into
`karpathy-guidelines` §1, which is floor. It **references, never restates** (`tests-must-gate-for-real` #1
for right-reason reds, its #4 for revert-don't-delete), so there is no duplicated prose to drift. Also
wired into `/sudo-quick-dev` (pinning test seen red BEFORE the fix) and `/sudo-mobile-error-team` (§4's
"fails on broken code" must be **observed**). Sources: MIT 6.031, Verraes, delta debugging, Google SRE.
**UNCOMMITTED**, and **`/sync-agents` owed** (2 command files + shared rules). Deferred by agreement:
`sudo-live-testing-team` (diagnoses only) and `sudo-dev-story-tests:103` (suite failures, not reported bugs).
Session: `_artifacts/_main/2026-08-04_debug-protocol-rule/`.

**2026-08-04 (latest): Auto-memory is now junctioned into the repo — tooling shipped, NOT yet applied.**
Claude memory lives under a slug **derived from the workspace's absolute path**, so it never leaves the
machine and a rename orphans it. **15 files were already dead** (13 + 2 under two stale slugs from past
renames) because `rename-fix.ps1` repairs `.claude\settings.json` but never knew `projects/<slug>/memory/`
existed. Canonical store is now `_artifacts/_memory/`, linked by `.agents/scripts/link-memory.ps1` /
`link-memory.sh` — **twins by contract**, dry-run by default, and they **never merge or delete**: seed if
canonical is empty, otherwise back the local set aside to `memory.local-backup-<ts>` and report.
**⛔ NOTHING WAS APPLIED ON THIS DESKTOP — deliberate.** This box holds the OLDEST memories; the laptop has
the current ones. **The first machine to link SEEDS the shared store**, so the laptop must go first or
stale memory propagates everywhere. Sequence: (1) commit+push the tooling from here, (2) laptop pulls →
`link-memory.ps1 -All` dry run → `-Apply` → commit `_artifacts/_memory/` → push, (3) desktop pulls + runs
it (its 25 stale files get backed up, not lost), (4) MacBook — **run `ls ~/.claude/projects/` and report
before `--apply`**; the macOS slug shape is inferred from Windows paths and the script refuses rather than
guessing. Also tightened `artifacts-always-first.md`: plans must be pasted **FULLY inline** (link-only = a
gate violation) — found via one of the *stranded* memories, which is a neat proof of what stranding costs.
Still open from earlier today: 3 project repos hold **staged, uncommitted** `adk-prompting` deletions, and
**B-L-WorldWide is on `main`** (owner-only).
Session: `_artifacts/_main/2026-08-04_portable-memory-store/`.

**2026-08-04 (latest): INDEX-depth exceptions are a named list; `.agents/` is now linted.**
`check_maps.py` had `_artifacts` hardcoded as the sole depth exception at 3 call sites. It is now two named
sets — `DEPTH3_DIRS` (index deeper) and `DOT_CONTENT_DIRS` (dot-dirs that are content, not tool cache) — so
adding a folder is a one-line edit. Answering "should `.agents/` index deeper": **no.** Six of its ten
subfolders are flat, `skills/` self-describes through `SKILL.md` frontmatter, `bmad/` is regenerated, and
`templates/project-template/` is a scaffold. It already carried `AGENTS.md`, `INDEX.md`, both adapters, and
an `INDEX.md` in all ten subfolders — the gap was that **check 2.5's dot-dir skip (written for `.ruff_cache`)
made the whole master toolkit invisible to the linter**. It is now scanned, and its four Tier-1 law files are
asserted in check 6. Retired the `adk-prompting` skill (4 dirs + sync-manifest entry): an Antigravity guide
misfiled as ADK, unloadable in its richer copy, whose content `v3-prompt-architecture` already covers and
partly corrects; its one unique idea lives on as v3 #21. `check_maps.py --all` shows **zero new drift** — all
three conformant workspaces clean on both changed checks. **UNCOMMITTED:** run `/sync-agents` first (the
`v3-prompt-architecture` mirror is one section stale by design), then the single commit in the walkthrough.
**Open, needs Daniel:** (1) `5_adk_skills/` nesting hides `adk-agent-development` + `adk-testing-patterns`
from the harness entirely — both genuine and matching the pinned `google-adk==1.26.0`; flattening touches the
sync manifest + 4 caches + 3 vendored copies. (2) ~~vendored copies~~ **DONE** — all 12 deleted via `git rm -r`
(explicit paths) across AGY / Fresh / B-L-WorldWide; 16 dirs gone total incl. the lobby's 4, both real ADK
skills intact everywhere. Deletions are **staged, uncommitted** in all 3 repos; ⚠️ B-L-WorldWide is on
`main` = OWNER-ONLY. **Standing lesson from it:** deletion propagation is *surface-specific* —
`/sync-agents` purges `.claude/skills/` (manifest-tracked per skill folder; a retired skill dir is a command
ghost) but NEVER `Projects/<name>/.agents/skills/`, whose vendor is additive by design because the vendored
`.agents` is a hybrid holding project-owned rules/skills a blanket purge would destroy. Retiring a skill
therefore always needs the manual vendored delete too.
**Retracted from this session:** the two "orphan `.claude/skills/` mirrors" were false positives from a scan
that only compared `.agents/skills/` to `.claude/skills/`. `sudo-merge-epic-workingtrees` is generated from
its master COMMAND `.agents/commands/sudo-merge-epic-workingtrees.md`; `gitnexus` is a 6-sub-skill bundle
mastered at `.agents/.claude/skills/gitnexus/`. Both correct — nothing to delete.
**Do not hand-edit `.sync-manifest.json`** — it is the record of what the last sync wrote, and removing an
entry disables the purge that propagates a deletion (learned the hard way this session; edit reverted).
Session: `_artifacts/_main/2026-08-04_index-depth-exception-list/`.

**2026-07-30 (latest): Artifact ownership rule corrected and histories consolidated.**
Every directory under `Projects/` now owns its artifact history project-locally by default, regardless of
cwd or tool. The complete Sudo-managed exception registry contains only `Fresh_Workspace_BMAD` and
`OpenChat-Openrouter`. Canonical rule/skill/checker/standard copies hash-match across AviationChat, Fresh
Workspace, and NEXgen VR. Migrated the former Sudo buckets for AviationChat (18 files / 146677 bytes) and
NEXgen VR (9 files / 57266 bytes), verified SHA-256 manifests, then removed only those two source folders.
The Sudo `_artifacts/` root now contains `_main`, Fresh Workspace, and OpenChat. No git delivery occurred.
Session: `_artifacts/_main/2026/07/2026-07-30_project-first-artifact-locality/`.

**2026-07-23 (latest): Fan-out map and INDEX reconciliation complete.**
Regenerated the lobby, AGY AviationChat, and Fresh Workspace AUTO map blocks in their declared modes and repaired all deterministic INDEX drift (including the AGY `frontend/test-results/` index). `python .agents/scripts/check_maps.py --all` now reports that all maps and indexes agree with disk. Still informational: lobby GitNexus is stale and needs a post-commit `node .gitnexus/run.cjs analyze`; AGY's active context is 391 lines with no dated session blocks, so it needs a human decision rather than a mechanical prune. Project git discovery required a per-command safe-directory override because the sandbox user differs from the worktree owner. No commits or map anchors were created.
Session: `_artifacts/_main/2026/07/2026-07-23_update-maps-indexes/`.

**2026-07-14 (latest): GitNexus graphs updated & dev tooling excluded. Sync guide created.**
Refined product GitNexus index scope to exclude development/testing tooling (`load/`, `scripts/`, `_test_scripts/`, `auth_keys/`, `scratch/`, and root scripts) from indexing. Documented the new scope in `Projects/AGY_AVIATIONCHAT/docs/gitnexus.md`. Wrote a guide on the index files being machine-local and how to re-index other machines — **that guide was never tracked and is LOST**: it was authored in an Antigravity scratch dir on the PC (`docs/gitnexus-sync.md`, 0 commits in git history, absent from disk), and the link here was a Windows absolute `file:///c:/...` path that resolved on no machine. De-linked 2026-08-12 rather than repaired: there is nothing to point at. The fact it recorded survives in `.agents/rules/` and the GitNexus memories. Executed GitNexus analysis on lobby (`Sudo_Hatter_Command`) and product project (`AGY_AVIATIONCHAT`), successfully updating local indexes. Regenerated content-mode AUTO blocks for both repo-maps, and resolved a missing debug index row drift for `password-reset-fix`. Verify maps checks clean (`exit 0`).
Session: `_artifacts/_main/2026/07/2026-07-14_update-gitnexus-graphs/`.

## 5. PICK UP  (read-only brief)
- 5.1 Doing: map/index maintenance is complete; no process is running.
- 5.2 Changed this session: regenerated three declared-mode AUTO map blocks; added the missing lobby and AGY artifact-ledger rows; created the AGY `frontend/test-results/INDEX.md` and `epic_debug_2/INDEX.md` inventories; verified fan-out lint clean.
- 5.3 Remaining: after the relevant commits, re-anchor with `python .agents/scripts/check_maps.py --set-anchor --all`; re-index lobby GitNexus; decide whether and how to compact AGY's undated 391-line continuity brief.
- 5.4 Git: do not mass-stage the lobby—it already contained unrelated uncommitted changes before this reconciliation.
- 5.5 Historical hand-off from 2026-07-14 follows.
- 5.1 Doing: maintaining GitNexus indexing and map/index health.
- 5.2 Changed this session:
  - Excluded development, testing, and credential tools from the `AGY_AVIATIONCHAT` GitNexus indexing in `.gitnexusignore`.
  - Created a synchronization guide at `docs/gitnexus-sync.md` explaining that the compiled index is machine-local.
  - Linked the sync guide in the `docs/gitnexus.md` files of both workspaces.
  - Updated GitNexus index graphs locally for Sudo_Hatter_Command (lobby) and AGY_AVIATIONCHAT.
  - Regenerated content-mode AUTO blocks for both repository maps.
  - Added the missing index row in `Projects/AGY_AVIATIONCHAT/_artifacts/debugging/INDEX.md` for `2026-07-14_password-reset-fix/`.
  - Verified maps and indexes are clean (`exit 0`).
- 5.3 Git status:
  - Lobby: Modified `_artifacts/INDEX.md`, `_artifacts/_main/INDEX.md`, `docs/gitnexus.md`, `docs/repo-map.md`. Untracked `docs/gitnexus-sync.md`, `_artifacts/_main/2026/07/2026-07-14_update-gitnexus-graphs/`.
  - Product (`AGY_AVIATIONCHAT`): Modified `.gitnexusignore`, `docs/gitnexus.md`, `docs/repo-map.md`, `_artifacts/debugging/INDEX.md`, and local gitnexus skills.
- 5.4 Best next move: Daniel commits changes in both repositories and runs `python .agents/scripts/check_maps.py --set-anchor --all` to baseline map diffs.

## 6. HAND OFF  (verified state at this checkpoint)
- 6.1 Completed: the fan-out map/index reconciliation; all deterministic linter checks pass.
- 6.2 In progress: nothing.
- 6.3 Open: lobby GitNexus re-index after commit; AGY continuity-brief compaction needs an authoring decision; map anchors await commits.
- 6.4 Session: `_artifacts/_main/2026/07/2026-07-23_update-maps-indexes/`.
- 6.5 Historical hand-off from 2026-07-14 follows.
- 6.1 Completed: Refined indexing scopes, synchronized GitNexus graphs, added machine-local index sync documentation, regenerated AUTO blocks, and verified zero drift.
- 6.2 In progress: Nothing executing.
- 6.3 Open tasks / trade-offs: Indexes are machine-local; other machines must re-run analyze after pulling.
- 6.4 Related links: `docs/gitnexus-sync.md`, `_artifacts/_main/2026/07/2026-07-14_update-gitnexus-graphs/` (plan + walkthrough).
- 6.5 Git: Uncommitted lobby and product files ready for Daniel to commit (commands in walkthrough).

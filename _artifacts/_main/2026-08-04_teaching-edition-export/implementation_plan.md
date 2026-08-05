---
IsArtifact: true
ArtifactMetadata:
  title: Teaching Edition — generated shareable pair (command center + skeleton)
  type: implementation_plan
  date: 2026-08-04
---

# Teaching Edition — Implementation Plan

**Branch:** `claude/teaching-edition` (off `main_debug` @ `b9e6a80`, clean tree)

**Goal:** a shareable **pair** — teaching command center + teaching project skeleton — a stranger can
clone, key up, and learn from without touching Daniel's personal layer.

**Operator decisions:** separate repos · full 6-stop tour incl. a live story · source = lobby +
`Fresh_Workspace_BMAD` · the skeleton is what you clone per project · training toggles off at will ·
every answer is a teaching answer.

## Core design: export, don't fork

A hand-maintained fork goes stale silently — the failure already recorded for the per-project
autopilot engines. So: **export script + two manifests**. Improve the live repo, re-run, push. The
manifest **is** the privacy audit — reviewed once, not re-decided per push.

## Phase 1 — the export engine

`.agents/scripts/export-teaching-edition.ps1` — reads a manifest, copies the include-list to a
target, applies transforms, reports every excluded path. `-WhatIf` supported. Manifests:
`teaching-edition/lobby.manifest.json` + `skeleton.manifest.json`.

**Excluded (both):** `_my_resources/` · `_artifacts/` · `_bmad-output/` · `.env` · `.venv/` ·
`scratch/` · `.gitnexus/` · `.git/` · `check_maps_output.txt` · `Projects/`

**Excluded (lobby) — AviationChat-domain skills:** voice-ai · sse-streaming · adk · dual-store-rag ·
agent-handoff · hr-agent-schema · rag-implementation · regulatory-verification · specialist-agents ·
gemini-live · gcp-cloud-run · deploy-backend · troubleshoot-cloudrun · `security_team_aviationchat`

**Transforms:**

| Source | Transform / why |
|---|---|
| [`operator-profile.md`](../../../.agents/rules/operator-profile.md) | → generic "learn your operator". **Most important**: floor-tier and hard-codes Daniel as chair, so unchanged, a stranger's agent thinks it is talking to him. |
| [`maintained-projects.txt`](../../../.agents/maintained-projects.txt) | → emptied to header (names AGY / Fresh / NEXgen) |
| [`router.md`](../../../router.md) | → exception registry dropped (names Daniel's projects) |
| [`AGENTS.md`](../../../AGENTS.md) | → §3 gains training-mode; AGY refs out of §4/§5 |
| Skeleton `README.md` | → `_my_resources/` becomes "the owner's personal area" |

## Phase 2 — the `.env` pair

- **New** lobby `.env.example` — **system** keys: `GITHUB_PAT_CLASSIC`, `ANTHROPIC_API_KEY`,
  `OPENROUTER_API_KEY` (deepseek lane), `TELEGRAM_BOT_TOKEN`/`CHAT_ID`, `SENTRY_AUTH_TOKEN`. Tiered
  required/optional, each with a one-line "where you get this". Confirmed **not** gitignored.
- **Extend** [skeleton `.env.example`](../../../Projects/Fresh_Workspace_BMAD/.env.example) — keeps
  its **app** keys (Gemini/GCP/Firebase/Vertex), gains the same tiering + source links.
- **New** `export-env-example.ps1` — regenerates the lobby example from the real `.env`, **names
  only, values stripped**. Cannot leak, cannot drift.

## Phase 3 — the training rule + toggle

**New** `.agents/rules/training-mode.md`, floor-tier when active, overriding `operator-profile`.
Toggle = a **`.training-mode` sentinel file** at repo root (not an env var) — identical across all
four surfaces, visible, greppable. `/training on|off|status`. Ships **present**.

**Every answer is a teaching answer** (operator) — governs *any* question at *any* time, not just
tour steps and commands:

- Answer first, then the *why*. The reasoning is the product; the answer alone is trivia.
- Cite the rule or file it came from as a **clickable link**, so they learn where truth lives and can
  eventually stop asking.
- Define jargon on first use each session — ①②③, TEA, ATDD, worktree, `main_debug`, floor-tier, gate.
- Never "as you know" / "obviously" / "just". They do not know yet; that is the premise.
- If the honest answer is "the system does not do that", say so. **Never invent a command** — a
  newcomer cannot tell a real one from a plausible one, and one hallucinated command discredits the
  whole system.

Around commands: explain before executing · afterwards say what happened and what is next · treat
the first `approved` gate as the thesis, not friction.

**Turning it off is first-class, not a graduation** (operator, raised twice):

- Available at **any** moment, not only stop 5. `/training off` mid-tour is legal — the tour keeps
  working, it just stops explaining itself.
- **Reversible**: `on` restores it, no state lost — the sentinel is the whole mechanism.
- **Honest about latency**: floor rules load at session start, so `off` fully lands next session. The
  command says so and offers the half-measure ("dropping the tutor voice now, rule unloads next
  session") instead of silently under-delivering.
- Nothing is gated behind training mode; nothing breaks when it leaves. Deleting the sentinel by hand
  is equally valid — what remains is the real system, not a crippled one.

## Phase 4 — `/sudo-tour`

**New** `.agents/commands/sudo-tour.md` + `.agents/skills/sudo-tour/SKILL.md`.

| Stop | Covers |
|---|---|
| 0 | What this system is + the two rules above every command |
| 1 | Keys in and verified (both `.env.example` files) |
| 2 | Clone the skeleton → `gh repo create` → first push → on `main_debug`, **why `main` is a trap** |
| 3 | Idea → backlog: brainstorm → brief → PRD → architecture → epics/stories → sprint + risk scoring |
| 4 | **Run ①②③ live** on a seeded tiny story (health-check endpoint) whose red phase is honestly red |
| 5 | The safety net that was running underneath + the ship gate. Autopilot gets a *mention*, not a stop — the engines have no canonical master and drift per project. |

Each stop ends at a checkpoint. **Resumable the autopilot way** — finished stops detected by their
marks, not a counter.

## Phase 5 — the front doors

- **New** lobby `README.md` (none today) — what this is in five sentences, then clone → `.env` →
  `/sudo-tour`.
- **New** `docs/quick-reference.md` — [`sudo_workflows_testing.md`](../../../_my_resources/_quick_reference/sudo_workflows_testing.md)
  moved out of the personal area, its "In this workspace" block rewritten for someone with no
  projects yet; everything below already ports untouched.
- Skeleton README gains what it lacks: ①②③, TEA gates, worktrees, `main` vs `main_debug`.

### 5b — "the skeleton is a template, not a workshop" (operator)

Trap: a newcomer builds **in** the template — first project tangled with template history, second
project has no clean template left. Said in four places: skeleton `README.md` first block · tour stop
2 (clone walked live) · lobby `README.md` · **skeleton `AGENTS.md`, as an agent rule**.

That last one is what holds. A README does not stop an agent: session inside the template, say "let's
build my app", and it cheerfully builds — in the template.

**Resolves the two-doors conflict.** `/new-project` scaffolds a *thin* workspace (pointers,
`AGENTS.md`, vendored `.agents/`, artifacts, git repo) with **no BMAD, no test bench, no
backend/frontend scaffold, no TEA gate**. Ruling: **clone the skeleton for a real project;
`/new-project` only for a utility workspace that needs no BMAD.**

**Two cuttable additions:** (1) publish the skeleton as a **GitHub template repository** — "Use this
template" becomes a button with clean history, replacing the `clone` → `rm .git` → `git init` dance;
(2) **`init-project.ps1 -ProjectName MyApp`** — one-command rename, versus today's hand-replacement
of `{{PROJECT_NAME}}` across three files plus re-pointing `AGENTS.md` §9, the SessionStart hook, and
`pyrefly.toml`/`pyrightconfig.json`. They will miss one and **the failure is silent** — memory
resolves to a missing path, the hook points at nothing.

## Phase 6 — verification (the real gate)

1. `-WhatIf` both manifests; read the exclusion report.
2. Export to scratch, then **leak-grep** for `Daniel`, `dlohneiss`, `AviationChat`, `AGY`, `NEXgen`,
   `sudomadhatter`, and every key **value** from the live `.env`. **Any hit = FAIL.**
3. `python .agents/scripts/tests/run_all.py` still green (94 checks) — export must not disturb the
   live tree.
4. Cold-read the exported lobby for references to paths absent from the export.
5. Dry-run `/sudo-tour` stops 0–2 against the exported pair.

## Decisions (operator, 2026-08-04)

1. ✅ Repo names: **`sudo-command-center`** + **`sudo-project-skeleton`**.
2. ✅ Visibility: **private, invite-only.** Flip to public later only if wanted — private→public is
   one click; public→private un-leaks nothing.
3. ✅ Keep the `.env` split — skeleton → `auth_keys/.env`, lobby → `.env`. It is what the code reads.

Still unaddressed: the two cuttable 5b additions (template-repo button, `init-project.ps1`).
Default is **include** unless cut.

## Not a fork — a generated repo

No git relationship to the live repos: no fork, no submodule, no remote link. The **script** is the
only connection. Improve the live repo → re-run the export → commit + push the teaching repo. Updates
flow **one way only** (live → teaching); nothing ever flows back.

Why not a real fork: a fork shares **history**. `git log` on it would expose every past commit that
touched `_my_resources/`, `.env`, or AviationChat — clean current files do not clean a dirty past.
The export's first commit is its whole history.

**The discipline this demands:** the teaching repos are **generated, never hand-edited** — a re-export
overwrites. A wanted change goes into the source repo or the manifest. Hand-edit the output and the
next export silently destroys it (the exact drift failure already recorded for the autopilot engines).

## Execution order

1 → 6. Engine first: every later phase is verified by running it. Nothing pushed to a new remote
until Phase 6 is clean.

## Self-Audit (2026-08-04)

**Right-size: FULL.** It touches a floor-tier rule that overrides another floor-tier rule, a paired
contract (two manifests against one engine), and shared config. **Target deviation:**
`/sudo-self-audit` Step 0 binds a child project and says never operate on the lobby; this plan spans
the lobby *and* `Fresh_Workspace_BMAD`, so both were bound. Operator-authorised.

- **Phase 0 — scope/traceability:** every phase maps to an operator decision; no orphan steps. Phases
  A and 1 already built and committed (`b99f9cd`, `a314d31`, `8739a89`) — audited as shipped, not planned.
- **Phase 1 — blast radius:** traced the toggle against `AGENTS.md` §3 rule-loading, `mobile-mode` (the
  only existing conditional-floor precedent), Fresh's `.claude/settings.json` SessionStart hook, and
  Fresh's vendored rule/skill inventory. Grep-based; this repo is not GitNexus-indexed for these paths.
- **Phase 2 — over-engineering:** two tripwires fired, both survive justification (below).
- **Phase 3 — pre-mortem:** the silent-failure walk is what produced F1, F3 and F4 — each ships
  something that *looks* correct and fails without an error.

### Findings

| # | Where | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| F1 | `AGENTS.md:26-28` vs plan Phase 3 | **HIGH** | Plan edits only §3 to load the training rule. But §3 states `.agents/rules/INDEX.md` is the per-rule router carrying the same classification, and **"if the two ever disagree, they are both wrong until reconciled."** Editing one ships a rule that is floor-tier in one place and unclassified in the other — the tutor silently never loads. | FIX — edit both |
| F2 | plan Phase 3 | MED | Plan rejects an env var for a sentinel file, but the house's only conditional-floor rule (`mobile-mode`) triggers on env `CLAUDE_CODE_REMOTE` and **owns its own trigger**. Deviation unjustified. | KEEP the file (an env var is not committed, so a cloner would get training OFF — the opposite of intent) + state the why, and follow mobile-mode's structure: the rule owns the trigger, `AGENTS.md` points at it |
| F3 | `living-template-sync` | **HIGH** | Part A added `why:`/`since:` to the 21 lobby rules. Fresh vendors **30** rules and got none. `living-template-sync` requires home-base rule changes to land in Fresh. The teaching skeleton would ship 30 provenance-less rules next to a teaching lobby that has it — and the ratchet test only guards the lobby. | FIX before B6 |
| F4 | plan Phase 2 | **HIGH** | Plan claims `export-env-example.ps1` "cannot leak" because values are stripped. **Key NAMES are not stripped** — an `AGY_*` or `AVIATIONCHAT_*` variable name ships intact. | FIX — route the generated file through substitution + the leak scan |
| F5 | plan Phase 4 stop 4 | **HIGH** | Stop 4 runs ①②③ live. Those bind a child project via `.agents/active-project.txt`, open a **git worktree**, and need a BMAD board + `sprint-status.yaml` + a story file. Plan says "seeded story" without specifying the seed contains them → hard failure at the tour's climax. | FIX — specify the seed |
| F6 | plan Phase 4 | MED | Stop 4 needs a runnable bench; stop 2 covers GitHub, not venv/`pip install`. A red phase cannot be honestly red if pytest will not start. | FIX — dependency setup moves into stop 2 |
| F7 | plan Phase 5 | MED | "moved out of the personal area" implies editing `_my_resources/`, which is protected — and it is excluded from export, so a move is the only way it ships. | FIX — ship it as a `replacements/` file; never touch `_my_resources/` |
| F8 | plan Phase 6 | LOW | "94 checks" is unverified — the harness reports 6 files with per-file counts. | FIX — measure or drop the number |
| F9 | skeleton manifest | MED | Fresh vendors **15** domain skills, two more than the lobby (`gemini-live-api-dev`, `google-adk-python`). Reusing the lobby's exclusion list ships both. | FIX — derive the list from Fresh |

### Over-engineering gate

Two tripwires fired. **`/training status`** — a verb no requirement asked for; kept, because it is
three lines and it is how a user answers "is the tutor on?" without reading the rule. **`init-project.ps1`
+ the GitHub template button** — generalising beyond "teach them"; kept, because F-class silent failure
is exactly what they prevent, and both are already flagged cuttable at the operator's word.

### Gates

**Verification strategy:** present and executable (Phase 6, leak-grep is the real gate). **Irreversible/
destructive:** none — the export writes to a fresh tree and nothing pushes until Phase 6 is clean; the
one destructive property (re-export overwrites hand edits) is documented in the engine header.
**Vague steps:** F5 and F7 were exactly this and are now tightened. **Quality fit:** the engine follows
the existing `.agents/scripts/` conventions and the new test follows `_harness.py`.

**Audit verdict: NO-GO** until F1, F3, F4, F5 are fixed — each ships something that looks correct and
fails silently. F2, F6, F7, F8, F9 fixed in the same pass.

<!-- CHECKPOINT id="ckpt_msfgxg5t_6hbfvu" time="2026-08-05T02:29:02.609Z" note="auto" fixes=0 questions=0 highlights=0 sections="" -->

<!-- CHECKPOINT id="ckpt_msfim33l_ii3jou" time="2026-08-05T03:16:11.697Z" note="auto" fixes=0 questions=0 highlights=0 sections="" -->

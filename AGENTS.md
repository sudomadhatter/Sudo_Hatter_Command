# ROOT LAW — Sudo_Hatter_Command Operating System

Prime mission: Sudo_Hatter_Command is Daniel's **home base**. From here, an agent (Claude, opencode, or
Antigravity/Gemini) routes into the right workspace, loads **only what the task needs**, does the
work, and persists everything to the shared `_artifacts/` memory. The folder is the app; markdown is
the program; you **become** the agent the workspace describes.

## 1. START HERE  (read this — not the whole tree)
1. You are in the LOBBY. Do NOT read the whole tree; that burns tokens. Least-context loading is the whole game.
2. A routing / "what should I work on" / ownership question → read `router.md`.
3. Working inside a project → read THAT project's `AGENTS.md` (its workspace map), not this file.
4. Before any risky/irreversible action → see §6 GATES.
5. Continuity ("pick up" / "hand off") → see §7 PERSISTENCE.
6. Before editing any file outside `_artifacts/` → an approved `implementation_plan.md` is required (see §3 gate).
7. **Entering any folder: if it carries an `AGENTS.md`, read that FIRST** (the local law — how to act
   there); read its `INDEX.md`/`README.md` only when you need the inventory. Tier model (which folders
   get one) → `docs/workspace-standard.md` Part 1.

## 2. MAP / MISSION / SUPPORT  (answer these for every task — then you're never lost)
- **MAP** — where am I, where can I go?   → `router.md` (lobby) → a workspace `AGENTS.md` (floor)
- **MISSION** — what is the work here?     → the target workspace's `AGENTS.md` routing table
- **SUPPORT** — what tools/skills/context? → `.agents/skills/`, `.agents/commands/`, pulled per the table

## 3. ALWAYS-LOAD  (small by design)

Three tiers — only the first is actually always-on. **`.agents/rules/INDEX.md` is the per-rule router**
and its `Load` column states this same classification; if the two ever disagree, they are both wrong
until reconciled. A rule's own frontmatter does **not** declare its load class.

**FLOOR — load now, every session:** `.agents/rules/operator-profile.md` (**who you're talking to** —
Daniel is the visionary/chair, you are the engineer; the eight speaking obligations that govern every
reply), `.agents/rules/constitution.md` (hard stops + gates), and `.agents/rules/karpathy-guidelines.md`
(how to work).

**PROTOCOL — load BEFORE the first tool call that creates, edits, or deletes a file.** Not "eventually",
not "if it seems relevant": if you are about to write and these are not loaded, **stop and load them
first.** `.agents/rules/artifacts-always-first.md` (the plan-first gate) · `.agents/rules/000-PLAN-FIRST-GATE.md`
(its priority-zero kill-chain) · `.agents/rules/git-policy.md` (the branch model + write gate) ·
`.agents/rules/worktree-per-story.md`. Together ~44 KB — which is why they are conditional rather than
floor, and why the trigger has to be a rule you follow rather than a hope.

> **These four are conditional, but their LAW is not.** Every gate they carry is also stated inline in
> this file — the ⛔ ARTIFACTS block at the end of this section, plus the WORKTREE and GIT WRITE gates in
> §6 — and again in the always-loaded `constitution.md` Hard Stops. So the gate binds even in a session
> that never opens the rule. The rule files carry the *mechanics*; `AGENTS.md` and `constitution.md`
> carry the *stop*. If you ever find a protocol rule whose law is NOT anchored in both, that is a defect —
> fix the anchor, don't promote the rule to floor.

**ON-DEMAND — everything else in `.agents/rules/`**, pulled when its trigger fires (the `Trigger` column
in the INDEX). Do not preload. The full rule set is the shared toolkit, not a startup payload. How a
workspace is shaped + kept healthy → `docs/workspace-standard.md`.

> **One on-demand rule is named HERE because its trigger hides in plain sight: the Jira board.** Any
> sprint/backlog/ticket question — **"what's next?" / "what should I work on?"**, "what's In Progress?",
> "move/mint this ticket" — is answered from the **live board** via the authenticated `acli` CLI — load
> `.agents/rules/jira.md` (cheat-sheet + queue order + flag traps + guardrails) and run the query. Never
> answer "I have no Jira integration": every shell-capable agent on this machine has one. The local
> `sprint-status.yaml` remains the machine state; Jira is the human view — the rule carries the join.
> **"What's next" has a defined answer, not a judgment call:** `In Progress` → **`To Do Next`** (the
> operator's hand-picked queue) → `To Do`, first non-empty rank wins; `Blocking` is an impediment, never
> a candidate. Full rule → `.agents/rules/jira.md` §The queue.

> **A second on-demand rule is named HERE for the same reason — its trigger is invisible from inside the
> edit: `sop-currency.md`.** Editing a `/` command, a rule, a safety-net script, a commit gate, or this
> file **changes how the operator uses the system**, so
> `docs/_scc_sops_prds/workflows_testing_SOP.md` — the operator's PRD, the one page that
> answers "what do I type" — must be updated **in the same commit**. An armed commit-msg gate rejects the
> commit otherwise; `[sop-ok]` in the message is the logged opt-out for changes that genuinely alter no
> usage. Load the rule before you touch any of those surfaces.

> **Web/mobile session?** When env **`CLAUDE_CODE_REMOTE=true`** (Claude Code on the web or phone), also
> load `.agents/rules/mobile-mode.md` — the web/mobile lane: it adapts git, the approval gate, artifacts,
> and verification for a device with no terminal. On a desktop IDE session the var is unset → ignore it and
> use the desktop defaults. `mobile-mode.md` owns the trigger (single source for the lane boundary).

> **⛔ ARTIFACTS — MANDATORY FIRST ACTION.** Before modifying ANY file outside `_artifacts/`, write an
> `implementation_plan.md` into the artifact store owned by the target workspace (§5) and **STOP until Daniel says "approved."** Track
> work with a live TodoWrite list; close with one `walkthrough.md`. **This applies at the lobby
> too — not only inside projects.** Full protocol → `.agents/rules/artifacts-always-first.md`; the
> priority-zero kill-chain that enforces it (and the `_bmad/custom/` guard tomls that load it into every
> dev-story / quick-dev run) → `.agents/rules/000-PLAN-FIRST-GATE.md`. (Skip only for
> read-only/investigatory asks, trivial one-liners, `/cicd-quick-dev`, and **the lightweight lane
> `/smh-quick-fix`** — that exemption list lives in `artifacts-always-first.md` § "When to Skip" and
> nowhere else.)
>
> **⭐ The lightweight lane, because its trigger is a sentence rather than a file (SCC-162, operator
> ruling 2026-08-15).** *"Not everything is a full quick dev. sometimes I just want an agent to do
> something specific… this does not touch anything that can break."* Command-centre work only —
> *"only for the smh / commands, not normal cicd work"* — and the test is his own sentence: **things
> that do not affect our development system.** Writing a guide, fixing a reference, tidying a messy
> source-control state. Invoking **`/smh-quick-fix`** IS the "skip the plan" instruction, and so is
> saying *"skip the plan, just do it"*. ⛔ **Do not ask whether to mint a ticket or open a lane** —
> asking is the over-engineering the ruling names. **Qualification is a script, never a judgement:**
> `python3 .agents/scripts/lane_qualify.py --paths <paths>` — `LIGHT`/`LIGHT-VCS` qualify, and **no
> paths at all is `TASK`**, because silence is unknown scope. The lane still takes a Jira key, a
> `chore/*` worktree, the gates, a lean walkthrough, and `/smh-close-task-merge-tree` — there is no
> lighter door to `main`.

## 4. WHAT LIVES WHERE  (home-base infrastructure)
| Area | Path | Purpose |
|---|---|---|
| Master toolkit | `.agents/` | rules · commands · skills · workflows · bmad · scripts · templates (single source of authorship) |
| Home-base memory | `_artifacts/` | home-base/cross-project history plus explicitly registered Sudo-managed exceptions |
| Docs | `docs/` | home-base documentation (master implementation plan, workspace standard) |
| Navigation index | `docs/repo-map.md` | the lobby's repo-map (curated header + auto body); drift-checked at SessionStart |
| Routing canary | `_routing-canary/` | model-agnostic proof the routing works (Claude/opencode/Antigravity) |
| System builder | `docs/system-builder.md` | how to add/maintain workspaces (`/smh-new-project`, `/smh-sync-agents`) |
| New-machine setup | `docs/migrations/` | secrets export/restore + rename-day tooling; start at its `INDEX.md`. Not day-to-day infra, but standing reference — run when pointed at, never deleted (moved out of `_my_resources/` under SCC-89) |
| Lobby tool dirs | `.claude/`, `.opencode/` | synced copies of the master. **One door per platform per command (SCC-66):** Claude + Codex enter through a **launcher skill** (generated per eligible command into `.agents/skills/`, tree-copied to `.claude/skills/`; hand-authored `SKILL.md` wins); opencode through `.opencode/commands/`; Antigravity through `.agents/workflows/`. `.claude/commands/` and `~/.codex/prompts` are **retired** doors; `platforms:` frontmatter limits a command's reach |
| SOPs & PRDs | `docs/_scc_sops_prds/` | **every procedural doc** — what the *operator* does and types, as opposed to `.agents/`, which describes the system to an *agent*. Start at its `INDEX.md`; `workflows_testing_SOP.md` is THE quick reference and is gated by `sop-currency.md`. Consolidated here by SCC-74 |
| Thinking space | `_my_resources/` | Daniel's brainstorming + personal notes. **⛔ IGNORE unless he links a specific document** (ruling 2026-08-10). Not authoritative, deliberately un-scanned, staleness fine by design. Standing exception: `open_tasks/todo_list.md` (the `## Open Tasks` list only). The `migrations/` exception is **retired** — SCC-89 moved that kit to `docs/migrations/`, so it is now scanned documentation like everything else under `docs/`. Local law → `_my_resources/AGENTS.md` |
| BMAD (lobby) | `_bmad/` · `_bmad-output/` | BMAD module (regenerated — never hand-edit) + its state/output |
| Projects | `Projects/<name>/` | project-owned workspaces, each with its own repo and `_artifacts/`, except the explicit Sudo-managed exceptions in `router.md` |

> **⚠️ SEARCHING FROM THE LOBBY:** root-level Grep/Glob are **blind to `Projects/`** (ripgrep honors the
> lobby `.gitignore`) — a "clean" root search proves nothing about the project repos. Point Grep at
> `Projects/<name>`, or sweep all projects with Bash `find`. Full mechanics → `.agents/rules/lobby-search.md`.

## 5. NAMING & ARTIFACT PLACEMENT  (this replaces a database)
Artifacts go **with their owning workspace, regardless of cwd or tool**. Every directory under `Projects/`
owns its history in `Projects/<name>/_artifacts/` unless it appears in the explicit Sudo-managed exception
registry in `router.md`. The only current exceptions are `Fresh_Workspace_BMAD` and
`OpenChat-Openrouter`; their operational history stays in the matching home-base `_artifacts/<name>/`
bucket. Home-base and cross-project system work uses `_artifacts/_main/`.

The full bucket rules (story `<epic>/<story>/`, local `_main/`, debugging, file naming, continuity) live in
the protocol-tier **`.agents/rules/artifacts-always-first.md`** (§2 — loaded whenever a session may write
files, per §3); full model →
`docs/workspace-standard.md`.

## 6. GATES  (consult before acting)
- **ROUTING GATE**: confirm the target workspace via `router.md` before touching files in it.
- **PROJECT-LAW GATE — binding a project = loading its law.** The moment a target project is bound
  (`/cicd-*` Step 0 §BIND, or any work under `Projects/<name>/`), read `PROJECT_ROOT/.agents/INDEX.md`
  and honor its `Load` column — a converted (thin) project's INDEX routes its own rules + skills; a
  converted project missing it → STOP. Two-tier contract → `.agents/rules/project-law.md`.
- **SEARCH GATE** — a root-level Grep is blind to `Projects/` (ripgrep honors the lobby `.gitignore`) and
  reads as a false "clean"; point Grep at `Projects/<name>` or use Bash. **Full mechanics →
  `.agents/rules/lobby-search.md`.**
- **RISK GATE**: never delete / overwrite / publish without explicit go-ahead.
- **WORKTREE GATE — one lane, one worktree.** **Any lane that will produce commits** opens its own git
  worktree **before the first project file is edited** — automatic, don't ask, and **don't first work
  out what kind of work this is** (SCC-62, 2026-08-09: the trigger is **concurrency, not work type** — a
  chore lane beside a story lane collides exactly as hard). What differs by lane is the **branch and its
  base, never whether you isolate**: a story lane takes `claude/<KEY>-<slug>` off **the story's epic
  branch** (`epic/<KEY>-<slug>`, never `main`), ad-hoc/Task work takes `chore/<KEY>-<slug>` off `main`.
  Each is pruned by its own close-out — `/cicd-close-workingtree` for a story, `/smh-close-task-merge-tree`
  Step 5 for a Task. Commits stay explicit-path (`git add -A`/`.`/`-u` banned). Read-only sessions and a
  single trivial edit the operator is watching are exempt. A fresh tree does not inherit gitignored
  assets (`.env`, `auth_keys/`, `.venv`, `node_modules`) — run `.agents/scripts/link-worktree-assets.py`,
  and `--unlink` **before** any tree is removed. **⛔ Your tree is your world** — never sweep, revert,
  commit, or **file as a finding** another lane's in-flight work.
  **Parallel teams are the NORM — up to four lanes (sometimes more) run at once:** expect other lanes'
  dirty files in the shared checkout (never sweep, revert, or "fix" work you didn't do) and expect the
  epic branch to move mid-session; several lanes
  landing together go through `/cicd-merge-epic-workingtrees`, never one-by-one. Full lifecycle →
  `.agents/rules/worktree-per-story.md`.
- **GIT WRITE APPROVAL — the gate is WHERE a write lands.** FREE: your own `claude/*` or `chore/*`
  branch — commits **and** pushes. SIGN-OFF (per-action, never carries): landing on **the epic branch** —
  Daniel's in-the-moment "approved", or invoking `/cicd-update-sprint-memory` (its Step 7 does the
  landing; invoking it IS the sign-off). OWNER-ONLY: **`main`** — only via `/cicd-push-e2e` (epic merge,
  full gate) or Daniel's direct ask. Full branch model + enforcement → `.agents/rules/git-policy.md`
  (web/mobile → `mobile-mode.md`).
- Full hard stops + "ask first" list → `.agents/rules/constitution.md`.

## 7. PERSISTENCE  (you own this — not a vendor)
- **Location follows ownership** — a non-exempt project's history is always project-local, even when the chat
  starts in the lobby. Sudo-managed exceptions use their named home-base buckets; home-base/cross-project
  work uses `_artifacts/_main/`. Full model → `.agents/rules/artifacts-always-first.md` ·
  `docs/workspace-standard.md`.
- **"pick up"** → read-only continuity brief from the right `active-context.md`, then surface open work
  **from the live Jira board** — `In Progress` → `To Do Next` → `To Do`, first non-empty rank wins
  (`.agents/rules/jira.md` §The queue; trigger also → `router.md`). ⛔ **NOT from
  `_my_resources/open_tasks/todo_list.md`** — retired as an agent source (ruling 2026-08-09): it is the
  operator's personal notes, it is stale, and it duplicates tickets that already exist. Never quote it as
  "what's next". **"hand off"** → write state back, append the matching `INDEX.md` row, read it back to
  verify.
- **Memory — every platform reads it, every machine has it (SCC-65).** The persistent memory store is
  **`_artifacts/_memory/`** — the repo path is canonical: it travels via git, so it is identical on both
  machines and readable by every model. **At session start read `_artifacts/_memory/MEMORY.md`** (the
  index — one line per memory, ≤25 KB) and open the full files relevant to your task. Recalled facts
  reflect when they were written — verify against the live repo before acting on one.
  **The store is READ-ONLY except through the sanctioned flows** (the Claude harness auto-memory and
  `/cicd-update-sprint-memory`'s learning-routing step): never edit, delete, reorganize, sweep, or
  commit `_artifacts/_memory/` files otherwise — a dirty memory file in your tree that you did not
  write is another session's work in flight. Write law, for the writers: one index line per memory;
  update the existing file, never fork a duplicate; wrong → **delete** (git is the undo);
  closed-but-instructive → compress to a one-line lesson. (Claude's `~/.claude/...` harness path is a
  per-machine symlink into this store — a convenience, never the mechanism; fresh machine →
  migrations kit §1 step 8.)
  **That read-only rule governs memory CONTENT.** A **structural** change is a different act —
  and "structural" means exactly three things, by enumeration, because an undefined word here is a
  self-authorizing exemption to the one rule protecting memory: (1) the index's **section layout**,
  (2) the **`## Project stores` pointers**, (3) **relocating** a memory file between tiers. Anything
  touching what a memory *says* is content and stays read-only. ⛔ **All three still require the
  operator's explicit approval** — the same per-item yes relocation already needs; a ticket whose
  title you wrote is not authorization. Editing someone's memory in passing is what the rule
  forbids; rebuilding the shelf, on a branch that says so and with a yes in hand, is not (SCC-73).
- **The store is TWO-TIER — lobby = inbox + cross-project, project = settled project history (SCC-73).**
  The lobby store `_artifacts/_memory/` is where **every** platform writes, always: Claude's harness
  bakes an absolute per-workspace path into its own memory instruction, and no repo law can redirect
  it — so a rule saying "write project facts over there" would be unenforceable for the writer that
  produces most of them. **Do not change where you write.** What settles into project-only truth is
  **relocated** to that project's own `Projects/<name>/_artifacts/_memory/` by `/smh-memory-audit`, per
  item, on the operator's word — its fourth disposition beside retire / merge / compress, and its first
  lever, since SCC-69 measured compaction spent (145 memories, 633 bytes freed). ⛔ **Never relocate a
  memory on your own judgment, and never outside that command.** Two obligations follow, and
  `test_memory_store.py` treats them **differently on purpose — one blocks, one only reports**: the
  lobby index must carry a **`## Project stores`** section signposting every maintained project (a
  memory moved out with no pointer left behind is indistinguishable from a deletion) — that is a
  **hard failure**, because this repo owns it. Each project index must carry the **mirror line back**
  to the lobby (a lane launched inside a project reads only that repo's store, so workflow law and
  cross-cutting hazards would otherwise be invisible to it) — that is a **`[SIGNAL]`, never a
  failure**, because it lives in a repo whose armed hook rejects this repo's ticket keys, and a gate
  that reds for a defect nobody standing here may fix blocks every unrelated lane instead. Cross-project law, operator rulings and the ⛔ hazards **stay in the
  lobby** — they are not any one project's.
- **⚠ The memory-audit trigger — a standing obligation for every platform (SCC-68).** Upkeep is gated:
  `tests/test_memory_store.py` (in `run_all`) enforces the 25 KB index cap + link↔file integrity, and at
  **90 % of the cap** it prints a `MEMORY AUDIT DUE` block — below the cap, while the run still passes,
  so the trigger prevents the red instead of being it. **If you see that block, STOP and ask the
  operator whether to run `/smh-memory-audit` now.** It is a script: it can print, it cannot ask. You are the
  half that asks — do not silently note it, do not defer it to a later command, and do not decide for
  them. ⛔ And do not act on it yourself: **never compact, merge, or retire a memory on your own
  judgment, and never raise the cap.** Compaction is `/smh-memory-audit`'s work, applied per item on the
  operator's word — a model summarizing away a hard-won pitfall is silent, permanent loss of exactly
  the recall this store exists for.

## 8. PORTABILITY
`AGENTS.md` is the universal contract; `CLAUDE.md` / `GEMINI.md` are one-line adapters pointing here (nothing
model-specific in shared files). **Codex** reads `AGENTS.md` **and** the Agent Skills in `.agents/skills/`
natively — it needs no adapter file. One command set (`.agents/commands/`) reaches **all four** LLM surfaces
via `/smh-sync-agents`, with **one door per platform per command (SCC-66)**: Claude and Codex invoke the
**launcher skill** (generated per claude/codex-eligible command; the skill's whole body is "read the command
file, follow it end to end", so the command stays the single brain); opencode invokes its command mirror;
Antigravity its workflow mirror (12k-cap thin launchers included). `platforms:` frontmatter limits reach;
default = everywhere. The retired doors — `.claude/commands/` and Codex custom prompts (`~/.codex/prompts`,
`/prompts:<name>`) — double-doored commands beside their skills and are purged by the sync. BMAD's skills —
which install to `.claude/skills`, outside Codex's search path — are mirrored to `~/.codex/skills` so BMAD is
reachable there too. Full model → `docs/workspace-standard.md`.

**⭐ Command naming law (SCC-63, 2026-08-09).** A command's prefix declares what it IS, and the prefix
is load-bearing — it decides what the command is allowed to touch:

| Family | What it is | Target |
|---|---|---|
| **`cicd-*`** | the BMAD-paired story/epic dev loop and its logistics (write → dev → review → close, boards, worktrees, autopilot, shipping) | binds `smh-target-resolution.md` — **exactly ONE project, never the lobby** |
| **`smh-*`** | workflows run ON the command centre + everyday operator tasks (sync, maps, memory, Task close-out, ideation) | allowed to act on the repo you are standing in |
| **`sentry-*`** | the Sentry incident system — a separate system from the dev loop | reserved family; one member today |

Rules: **hyphens only, never underscores.** An autopilot twin appends **`-AP`**. Vendor BMAD bridges
(`dev`, `pm`, `qa`, `sm`, `tea`, `analyst`, `architect`, `testarch-*`, …) keep their upstream names and
take **no** prefix. **Skills take no prefix** — a prefix marks a command; a generated launcher inherits
its command's name, a hand-authored skill is named for what it knows. ⛔ The `sudo-` prefix is
**RETIRED**: any `/sudo-` reference anywhere in this system is stale by definition. Enforced
mechanically by `workflow_lint.py --toolkit-only`.

> **GitNexus** — code-intelligence (impact · detect_changes · query · context) for this repo →
> `docs/gitnexus.md`. (Lobby index is routing-surface only; product work uses `repo: "AGY_AVIATIONCHAT"`.)

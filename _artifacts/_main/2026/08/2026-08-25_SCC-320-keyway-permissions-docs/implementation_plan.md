# Implementation plan — Keyway: the missing migration-kit step, permissions, and the `run` trap

**Date:** 2026-08-25
**Workspace:** `_main` (lobby / home base)
**Origin:** SCC-157 (Set Up Keyway) — found while setting Keyway up on the PC
**Epic:** SCC-75 (Security · Auth · Testing)

---

## 0. ⛔ THE ROOT ISSUE — the migration kit has no Keyway step (operator ruling 2026-08-25)

*"there is a document missing, all the documents in migrations are what we are doing now. and that
needs these instruction as well as the sharing permission instruction. so there is nothing to do
until this issue is fixed"*

**This is correct, and it reframes the whole ticket.** Today's session WAS a machine migration —
`docs/migrations/` is the kit that governs it — and Keyway is absent from the one place a fresh
machine actually follows.

**What is missing, precisely:**

| Where | State |
|---|---|
| `INDEX.md` §1 — "New machine, the ordered path", **11 numbered steps** | ⛔ **No Keyway step exists.** Step 6 covers per-machine logins (gcloud, gh, firebase, Java, Node); 6b covers `acli`. Keyway appears in neither |
| `install_guides/` — 8 guides | ⛔ **No `keyway-setup.md`.** Every other per-machine concern that can silently half-succeed has its own guide: `jira-api-token-setup.md`, `python_vytest-…`, `scratchpad-allow-hook-per-machine.md` |
| `machine_setup_card.md` §3 | ⚠️ One dense line inside a table cell: install per platform, `keyway login`, `keyway init`, and a pointer to the sharing guide. Correct as far as it goes, and **too buried to act as the procedure** |
| Any verification step | ⛔ **Nothing states the success canary.** This is not cosmetic — see below |

**The missing verification is what actually cost us.** `keyway doctor` on a correctly set-up machine
in this repo reads **`5 passed, 1 warning`** — never 6/6, because the `.gitignore` warning is a
permanent false positive. Before login it reads `4 passed, 2 warnings`. Nothing wrote that down, so
there was no way to tell a finished setup from an unfinished one — and **SCC-150 ("Install and verify
Keyway CLI on Main PC") was marked `Done` while this machine had never run `keyway login`.** The
install half happened, the login half did not, and with no canary the ticket closed on half the work.
A verification step is what turns "I ran the command" into "the machine is set up."

**Second, smaller staleness found in the same file:** `INDEX.md`'s first-live-execution table records
`.agents/scripts/link-memory.ps1` as **"⚠️ dry run only"**, with the note that this machine's memories
were stale so seeding from here would push stale memory everywhere, and *"the machine holding the
NEWEST memories must link first."* That ordering has now played out exactly as written — the Mac
seeded, so the PC could link safely — and `-Apply` **has now been run for real on the PC**
(2026-08-25): all three workspaces junctioned, 26 stale local memories backed aside, nothing deleted.
That row now understates what has been verified.
**Lane:** `TASK` — decided by script, not judgment:

```
python .agents/scripts/lane_qualify.py --paths docs/_scc_sops_prds/sharing_keys_secrets_secure.md .agents/skills/keyway-secrets/SKILL.md
TASK
toolkit path(s): .agents/skills/keyway-secrets/SKILL.md - this changes the development
system, so it takes the full lane (plan, audit, RED, review)
```

The operator doc alone qualifies `LIGHT`, but the skill is a toolkit path, and the two pages are
twins by contract (the skill's §7 names the doc as "the human-facing version of this page"). Fixing
only the `LIGHT` half would ship drift between them, so both move together on the full lane.

---

## 1. The defect

`keyway run` with no `-e` flag does **not** default to `development`. It opens an interactive
arrow-key picker and blocks until a human chooses:

```
┃ Environment:
┃ > development
┃   staging
┃   production
```

Measured 2026-08-25, PC, Keyway 0.5.3. `keyway run -- node probe.js` timed out at 90 s with that
picker on stderr. The same call with `-e development` returned `✓ Injected 37 secrets` immediately.

**Why it matters:** both pages print the bare form as *the daily loop* — the single most-copied
command in either document. An agent, a CI job, or any non-interactive shell that follows the
documented instruction deadlocks and burns its whole timeout with no error message.

**Why it is a real omission rather than a nitpick:** both pages *already* document this exact failure
mode for a sibling command — "with no provider argument it prompts interactively — so a bare
`keyway sync` blocks forever in a headless or agent context." The hazard is understood and written
down; it was simply never carried across to `run`. The docs also promise `pull` "defaults to
development", which is true of the *value* and false of the *prompting*.

## 2. Scope — two files, no code

### A. `docs/_scc_sops_prds/sharing_keys_secrets_secure.md`

| § | Edit |
|---|---|
| §5 "The daily loop" | Add `-e development` to the two bare `keyway run` examples; add a short warning that the bare form prompts and hangs headless. |
| §7 "The dangerous flags" | New table row: bare `run` / `pull` with no `-e` → interactive picker, blocks forever in agent/CI context. Sits directly beside the existing `keyway sync` row that describes the same hazard. |
| §11 "Quick reference" | Update the `keyway run -- npm run dev` line to carry `-e development`. |
| §9 troubleshooting table | New symptom row: "command hangs forever, no output" → cause: no `-e`, picker waiting → fix: name `-e`. |

### B. `.agents/skills/keyway-secrets/SKILL.md`

| § | Edit |
|---|---|
| §3 "Pulling Secrets" | `keyway pull` bare example gains `-e development`. |
| §4A "Zero-Disk In-Memory Execution" | Both bare `keyway run` examples gain `-e development`; add the warning note. |
| §4F destructive-flags table | New row for the bare `run` / `pull` prompt-hang, matching the doc's §7 row. |

### C. New: how to change and share permissions (operator request, 2026-08-25)

*"I do want you to update the documentation on using keyway to explain how to change and share the
permissions."*

The guide today says **that** access is granted on GitHub (§6.1) and **that** offboarding is three
steps (§6.4), but it never shows the operator *how to actually do either*. There is not one
`gh` command, one dashboard click-path, or one way to answer "who can read this vault right now?"
It states policy without procedure.

New material, into the guide as §6.8 "Doing it — the actual commands" and mirrored into the skill
as a §5 subsection:

| Question the operator has | What the docs must show |
|---|---|
| Who can read this vault **right now**? | `gh api repos/<owner>/<repo>/collaborators` + the pending-invitation check, because an invite that has not been accepted does not appear in the collaborator list |
| How do I **add** someone? | `gh api --method PUT .../collaborators/<user> -f permission=push`, or the Settings → Collaborators path; then they run `keyway login` and it just works |
| How do I **change** what they reach? | Two separate levers — GitHub role changes *whether they are in at all*; the Keyway dashboard's per-environment RBAC changes *which environments*. Name both and say which to use for what |
| How do I **remove** someone? | The existing three-step §6.4, now with the commands attached, including `gh api --method DELETE` |
| How do I check the **blast radius** before I rotate? | `keyway diff <env> <env> --keys-only` to enumerate exactly what a departing person could have pulled |

**Grounding — measured on the live board 2026-08-25, so the examples are real rather than invented:**

| Repo | Visibility | Who |
|---|---|---|
| `Sudo_Hatter_Command` | **public** | `sudomadhatter` (admin) only |
| `AGY_AVIATIONCHAT` | private | `sudomadhatter` (admin), **`sir-cooper` (write)** |
| `sudo-command-center` | private | `sudomadhatter` (admin), `sir-cooper` (write) |
| `sudo-project-skeleton` | private | `sudomadhatter` (admin), `sir-cooper` (write) |
| the other five | private | `sudomadhatter` (admin) only |

No pending invitations anywhere; `sudomadhatter` is a personal account in no organizations. So the
team is exactly two people, and `sir-cooper` reaches three repos.

⛔ **One open question the docs must NOT guess at.** `Sudo_Hatter_Command` is **public**, and the
guide's one-line model is *"if you can push to the repo, you can read its secrets."* Push and read
are the same thing on a private repo and wildly different on a public one. The page must state the
rule it can actually verify and flag the public-repo case as needing confirmation with the vendor,
rather than asserting a bound nobody here has tested.

## 3. Writing constraints (from `sop-currency.md`)

- **Timeless present tense.** State the rule as though it had always been so — no "⭐ new", no dates,
  no "since SCC-x", no before/after narration in the page body.
- **Every printed command must run on both machines.** These are `keyway` invocations, identical on
  Mac and PC, and each one gets pasted into a shell before it is written down.
- **Retire, don't accrete** — the bare forms are corrected in place, not left beside a corrected twin.

## 4. Gate expectations

- `sop-currency` should **not** fire: its trigger list is `.agents/commands/`, `.agents/rules/`,
  `.agents/scripts/*.py|.ps1`, the git hooks, and root `AGENTS.md`. `skills/` is on its explicit
  *"not a usage change"* list, and `docs/_scc_sops_prds/sharing_keys_secrets_secure.md` is not
  `workflows_testing_SOP.md`. If it fires anyway, that is a finding about the gate — report it,
  do not reach for `[sop-ok]` reflexively.
- `python .agents/scripts/tests/run_all.py` must stay green.

## 5. Steps

0. Mint an SCC Task ("Document the `keyway run` headless-hang trap"), linked to SCC-157.
1. Open worktree `chore/SCC-<key>-keyway-run-env-flag` off `main` (WORKTREE GATE — one lane, one tree).
2. Run `.agents/scripts/link-worktree-assets.py`.
3. Apply the §2 edits to both files.
4. **Verify by execution, not by reading**: run each corrected command form and confirm it returns.
5. `run_all.py` green.
6. Commit explicit paths; close via `/smh-close-task-merge-tree`.

## 6. Explicitly out of scope

- **The vault-hygiene finding** (37 secrets in `development`, 0 in `production`, including
  `GITHUB_PAT_CLASSIC` and `ANTHROPIC_API_KEY`). That is a secrets-handling decision with real
  blast radius and it is the operator's call. It keeps SCC-157 open on its own merits.
- **The memory-store junction on this PC** (`~/.claude/projects/<slug>/memory` is a plain directory,
  not a junction; 27 memories are local-only). `portable-memory-store-dot-slug-trap.md` states "a
  human reconciles" — dry-run shown, `-Apply` withheld.
- **SCC-150** ("Install and verify Keyway CLI on Main PC") is marked **Done**, but this machine was
  never logged in until today — install was done, `keyway login` was not, and `keyway doctor` read
  *"Not logged in"*. Worth reopening or noting; not this ticket's work.

---

## ⛔ Awaiting approval

Per the ARTIFACTS gate this plan stops here until Daniel says **approved**.

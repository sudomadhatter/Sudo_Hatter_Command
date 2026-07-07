# AGENTS.md — `.agents/` (master toolkit · Tier-1 floor)

## 1. ROOT LAW (what this folder is)
This is **THE master toolkit** — the single source of authorship for every tool the agents have: rules,
commands, skills, workflows, the BMAD install, scripts, templates, hooks. Everything the whole system runs
on originates **here**; the copies elsewhere are **downstream mirrors, never sources**:
- `.claude/` · `.opencode/` (the lobby + each project) + the machine-global caches = synced command/skill copies.
- each `Projects/<name>/.agents/` = an additive vendored copy of this whole folder.

**Never edit a mirror. Edit here, then run `/sync-agents`** to propagate. Rules are read **in place** from
`rules/` via the `CLAUDE.md`/`GEMINI.md`→`AGENTS.md` chain — they are NOT copied into `.claude/rules`.

## 2. START HERE (don't read the whole toolkit)
Least-context still applies: use the routing table (§3) to jump to the ONE subfolder a task needs, then scan
that subfolder's `INDEX.md` to dispatch — never read every rule/command/skill. Full inventory of this folder
→ `INDEX.md`. Not toolkit authorship? **Go back up** → `../AGENTS.md` (lobby law) or `../router.md` (routing).

## 3. ROUTING TABLE (task → subfolder → its index)
| Task | Go to | Dispatch via |
|---|---|---|
| Behavioral law / a rule (how to act) | `rules/` | `rules/INDEX.md` |
| A slash command (`/sudo-*`, `/autopilot_*`, `/sync-agents`, `/new-project`, …) | `commands/` | `commands/INDEX.md` |
| A skill (a capability the model invokes) | `skills/` | `skills/INDEX.md` |
| An Antigravity workflow / in-repo reference doc | `workflows/` | `workflows/INDEX.md` |
| The BMAD method install | `bmad/` | **BMAD-owned — regenerated on BMAD update, NEVER hand-edit** |
| A maintenance script | `scripts/` | `check_maps.py` · `generate_repo_map.py` · `record_map_changes.py` · `generate_doc_graph.py` · `sync-agents.ps1` · `new-project.ps1` |
| Scaffold a new project | `templates/project-template/` | consumed by `/new-project` |
| The git write-approval hook | `hooks/` | `require-push-approval.py` (deployed to every `.claude/hooks/` by `/sync-agents`) |
| opencode agent definitions | `opencode-agents/` | — |

## 4. THE LAW (authorship + sync)
- **Single source of authorship.** Author here; `/sync-agents` mirrors `commands/` + `skills/` to all three
  platforms (Claude, opencode, the Antigravity workflow mirror) + the machine-global caches, and additively
  vendors this whole `.agents/` into each `Projects/<name>/`.
- **`platforms:` frontmatter** on a command limits its reach (absent = everywhere).
- **After ANY edit here, run `/sync-agents`** (or the project-scoped variant) so the mirrors don't drift.

## 5. GATES / GO BACK UP
- Full hard stops + gates → `rules/constitution.md`; the plan-first artifact gate → `rules/artifacts-always-first.md`.
- Entering a subfolder: if it carries an `INDEX.md`, scan that to dispatch (an `AGENTS.md` first, if one exists).
- Not toolkit work? → `../AGENTS.md` (lobby) or `../router.md` (routing).

<!-- No GitNexus block by design: this toolkit is markdown, navigated by these indexes (and the doc-graph),
     not the code-graph. If graph intel is ever wanted here, put it in a separate file + a one-line pointer —
     never inline in this floor law. -->

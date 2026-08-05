---
IsArtifact: true
ArtifactMetadata:
  title: Rules folder optimization pass
  type: walkthrough
  date: 2026-08-04
---

# Walkthrough — `.agents/rules/` optimization + three-tier load model

- **Date:** 2026-08-04 · **Workspace:** home base, propagated to AGY + Fresh
- **Plan + Self-Audit:** [`implementation_plan.md`](implementation_plan.md) — verdict **GO**

---

## 1. What this was

"Clean up all the rules files to optimize them a little — we never did that." Audit first, then act.

**Already clean:** all 21 rules carry frontmatter, `name:` matches filename in every case, every rule has
a `description:`, and the INDEX has a row for all 21 with no ghosts. Nothing to fix there.

**The real finding:** load class had **three sources of truth and they disagreed.** Root `AGENTS.md` §3,
`rules/INDEX.md`'s `Load` column, and a frontmatter `activation:` field on 12 of 21 rules that **nothing
reads** (grep-verified across `.agents/`, `docs/`, `.claude/`, `.opencode/` — rules load through the
`CLAUDE.md`→`AGENTS.md` chain). Its vocabulary was **Cursor's** ("Always On", "Model Decision"), not the
house's.

`000-PLAN-FIRST-GATE` — the priority-zero kill-chain — had **three sources giving three different
answers** about when it loads. `powershell-encoding-safety` claimed `Always On`, a Windows encoding rule
in every session forever if an agent believed the file over the router.

## 2. What changed

- **C1** — `activation:` deleted from all 12. Load class now has exactly two live statements.
- **C2** — `AGENTS.md` §3 reconciled to the INDEX's three tiers. §3 had only two, so the protocol set got
  flattened: `artifacts-always-first` promoted into always-load (21 KB in *every* session), and
  `git-policy`, `worktree-per-story`, `000-PLAN-FIRST-GATE` swept into on-demand by §3's "everything else"
  sentence. **The token win:** a 21 KB rule no longer loads in conversation-only turns.
- **C3** — two duplicated passages collapsed to owner + pointer (the "`git status` becomes a soup"
  rationale → `worktree-per-story`; the plan-gate **When to Skip** exemption list →
  `artifacts-always-first`). Two copies of a gate's exemptions was the dangerous one.
- **C4** — INDEX rows grouped by their own `Load` column.
- **C5 (added mid-flight)** — see §3.

## 3. The correction that mattered — Daniel caught it

C2 as approved made the protocol tier conditional **without making the condition binding.** §3 said "load
the moment a session may touch files" — descriptive, not imperative. An agent could read that and never
load the plan-first gate. Naming is not triggering.

Three fixes:

1. **§3's PROTOCOL is now imperative** — *"load BEFORE the first tool call that creates, edits, or deletes
   a file. Not 'eventually', not 'if it seems relevant': if you are about to write and these are not
   loaded, stop and load them first."*
2. **The anchor invariant** — the four protocol rules are conditional, but **their law is not.** Every gate
   they carry is *also* stated inline in `AGENTS.md` (the ⛔ ARTIFACTS block, §6's WORKTREE + GIT WRITE
   gates) **and** in the always-loaded `constitution.md` Hard Stops. The rules carry the *mechanics*;
   `AGENTS.md` and `constitution.md` carry the *stop*. Written down as a standing invariant: *a protocol
   rule whose law is not anchored in both is a defect — fix the anchor, don't promote the rule to floor.*
3. **The invariant immediately failed its own first test.** `000-PLAN-FIRST-GATE` had **zero** references
   in `constitution.md`. It pre-dated this session — §3 never named it either, which is precisely how it
   got swept into on-demand — but C2 is what made it load-bearing. Now anchored; all four verify OK.

## 4. Task Checklist

- [x] Audited all 21 rules: frontmatter, INDEX coverage, size ladder, duplication (8-word runs over all 210 pairs)
- [x] C1 — `activation:` stripped from 12 rules
- [x] C2 — `AGENTS.md` §3 three tiers + `docs/workspace-standard.md` §4 (which was already wrong — omitted `operator-profile`)
- [x] C3 — 2 of 3 de-dupes; the third **dropped with reason** (see below)
- [x] C4 — INDEX regrouped, proven lossless by sorted-line diff
- [x] C5 — binding trigger + anchor invariant + `000-PLAN-FIRST-GATE` into constitution Hard Stops
- [x] Self-Audit appended to the plan (8 findings, verdict GO), plan trimmed to 8147 B under the hard 8 KB budget
- [x] Propagated: `project-template` + AGY §4 + Fresh §4 (both on `main_debug`, ad-hoc → no worktree)

## 5. Evidence

```
V1 frontmatter      all 21: name matches filename, description present
V2 activation:      0 files still carry it
V3 INDEX rows       21
V4 anchor invariant artifacts-always-first OK · git-policy OK · worktree-per-story OK · 000-PLAN-FIRST-GATE OK
V5 de-dupes         soup rationale: worktree=1 git-policy=0 (pointer x3)
                    When-to-Skip:   artifacts=1 000-GATE=0 (pointer x2)
V6 check_maps       folder coverage / INDEX paths / level-2 / structure  ALL [ok] clean
V7 EOL integrity    12 rules + 3 AGENTS.md: 100% CRLF, 0 bare LF, 1-line diffs

per-project anchor check (AGY + Fresh):  all four protocol rules OK in both
per-project EOL:  template 54/54 · AGY 153/153 · Fresh 125/125 CRLF
```

**V7 was not in the plan.** A scripted frontmatter strip is exactly the bug class
`powershell-encoding-safety` exists for; a plan that edits by script without checking EOLs is
under-verified. Added during execution and recorded as a gap in the plan as written.

**Precision on V4's last row:** the check greps the literal string `000-PLAN-FIRST-GATE`, so it proves the
*pointer* exists. Its actual *law* — no file modified before an approved plan — is anchored by §5 ARTIFACTS
PROTOCOL, which the `artifacts-always-first` row verifies. The invariant holds; the row measures the pointer.

**Pre-existing, not from this work:** `check_maps` still reports a stale AUTO block (NEXgen brief folders)
and a dead `_my_resources/migrations/_secrets/master.env` path in `repo-map.md` from the `_system/`
rename. Both are `/update-maps-indexes`' job.

## 6. Decisions that went against the plan

**De-dupe 3 dropped.** The plan said to strip the sign-off definition from `constitution.md` and point at
`git-policy.md`. Reading it properly, `constitution:18` is a Hard Stops one-liner that already ends "Full
policy → the `git-policy` rule." Constitution is **floor**; git-policy is now explicitly **protocol**.
Stripping the floor summary would leave a floor rule deferring to a file that hasn't loaded — the exact
hole C5 closed. It stays.

**Heading rename reverted.** I renamed §3 `ALWAYS-LOAD` → `WHAT LOADS, AND WHEN` — unapproved, and it
broke three references keyed on that exact name (`workspace-standard.md:52`, the project template, a
`_my_resources/` guide). Reverted; updated the standard's description instead.

## 7. Open — flagged, not actioned

- **`NEXgen-VR-Director` — CORRECTED (Daniel caught it):** the project is a healthy Fresh clone on GitHub
  (`sudomadhatter/NEXgen-VR-Director`, private, `main`+`main_debug`, full skeleton incl. `AGENTS.md`,
  pushed 2026-08-04 04:41). **This desktop simply never cloned it** — `Projects/NEXgen-VR-Director/` was
  an empty placeholder from 2026-07-30. The earlier "no root AGENTS.md / not a git repo" claims described
  the placeholder, not the project. Remaining work: clone it here, then hand-apply the §4 three-tier edit
  (the sync never writes root `AGENTS.md`).
- **`RAG_Pipeline_AC`** has a `## 4. ALWAYS-LOAD` but is **not** in `maintained-projects.txt`, so
  `/sync-agents` will never keep its vendored rules current. Left alone by decision.
- **`_my_resources/diagrams_guides/system/…:79`** still describes §3 as constitution + karpathy +
  artifacts-always-first. Protected personal area — reported, not edited.

## 8. Your Actions

**`/sync-agents -Maintained` is DONE** (run by the agent at Daniel's direction, dry-run first): all 4
targets clean. Post-sync verification: `reproduce-before-you-fix` present in all 3 projects, `activation:`
gone from every master-owned vendored rule (0/12 ×3), all 6 spot-checked project-owned rules intact,
`bmad/` untouched (AGY `project_name` intact), every `AGENTS.md` rule reference resolves. **NEXgen-VR-Director caveat:** the sync vendored into what
turned out to be an **empty placeholder** — the real repo lives on GitHub, never cloned to this desktop
(see §7). The vendored dirs must be cleared before a clean clone can land in that path.

Three commits remain — lobby, AGY, Fresh (both projects on `main_debug`, sign-off needed to land):

```powershell
# lobby
git add AGENTS.md docs/workspace-standard.md .agents/rules .agents/templates/project-template/AGENTS.md _artifacts/_main/2026-08-04_rules-folder-optimization _artifacts/_main/INDEX.md _artifacts/INDEX.md _artifacts/_main/active-context.md
git commit -m "refactor(rules): one source of truth for load class + binding protocol trigger

activation: frontmatter on 12 of 21 rules was dead metadata in Cursor's
vocabulary that NOTHING reads, and it contradicted both AGENTS.md and the
INDEX - 000-PLAN-FIRST-GATE had three sources giving three answers. Deleted.
AGENTS.md now states three tiers matching the INDEX, and the protocol tier
loads on a binding trigger (before the first file-writing tool call) rather
than a description. New anchor invariant: a protocol rule's law must ALSO be
inline in AGENTS.md and the floor constitution - which immediately caught
000-PLAN-FIRST-GATE missing from constitution Hard Stops."
```

AGY and Fresh each need `git add AGENTS.md` plus their own commit inside
`Projects/<name>` — same reasoning, one-file change.

⚠️ Still outstanding from earlier sessions: the [debug-protocol rule](../2026-08-04_debug-protocol-rule/walkthrough.md#6-your-actions)
and [portable-memory](../2026-08-04_portable-memory-store/walkthrough.md#6-your-actions) commits, the
staged `adk-prompting` deletions in three project repos, and **B-L-WorldWide is on `main`** (owner-only).

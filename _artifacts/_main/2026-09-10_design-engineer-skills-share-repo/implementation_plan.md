# Share `/smh-designer` as a standalone public repo — `sudomadhatter/design-engineer-skills`

**Lane:** command-centre TASK · **Branch:** current (`chore/SCC-437-llm-approvals`) is NOT the lane — cut `chore/<KEY>-designer-share` before any write
**Operator decisions (2026-09-10):** repo name `design-engineer-skills` · **public** · Phase 2 **stops at the plan**

## Why

Mr. Hatter wants to hand someone a git URL and have their agent stand up the whole `/smh-designer`
workflow. Today that is impossible: the workflow is 10 files across 8 skills plus one doc, wired
together with seven hardcoded `file:///home/dlohn/Sudo_Hatter_Command/…` links, and its Phase 2
hands off to four commands that exist only here.

## The measured edge set (what actually has to travel)

| # | Source | Files | Notes |
|---|---|---|---|
| 1 | `.agents/commands/smh-designer.md` | 1 | The brain. Everything else is reached from here. |
| 2 | `.agents/skills/smh-designer/SKILL.md` | 1 | Generated thin launcher; points at the command. |
| 3 | `.agents/skills/ui-ux-pro-max/` | SKILL.md + 24 CSV + 3 `.py` | Scripts are **stdlib-only, no abs paths** — verified. |
| 4 | `.agents/skills/emil-design-eng/` | SKILL.md, RECIPES.md | |
| 5 | `.agents/skills/vgpu/` | SKILL.md | |
| 6 | `.agents/skills/visual-fx-3d/` | SKILL.md, CATALOG.md, RECIPES.md | |
| 7 | `.agents/skills/webm-alpha-video/` | SKILL.md | |
| 8 | `.agents/skills/animate-expo/` | SKILL.md, RECIPES.md | **Invisible from the command file** — see Gap A. |
| 9 | `.agents/skills/write-swift/` | SKILL.md | **Invisible from the command file** — see Gap A. |
| 10 | `docs/_scc_sops_prds/frontend_UI_design_guide.md` | 1 | The procedural manual; owns the 5-pillar map. |

Total ≈ 864K. `__pycache__/*.pyc` (2 files) is the only junk and does not ship.

### Gap A — the 4-vs-5 pillar split (the real find)

`smh-designer.md` enumerates **four** pillars. `frontend_UI_design_guide.md` enumerates **five**, and
the fifth ("Rich Media & Platform Specialists") is the only place `animate-expo` and `write-swift` are
named. Anyone packaging from the command file alone ships a set with two missing limbs. Fixed at the
source: the command file's pillar list gains pillar 5.

### Gap B — Phase 2 leaves the repo

Phase 2 mints Jira via `acli jira workitem create` and hands off to `/smh-quick-dev`,
`/smh-quick-fix`, `/cicd-dev-story-tests`, `/cicd-quick-dev`. None exist for a recipient.
**Decision: Phase 2 ends by writing `implementation_plan.md` and stopping.** The Jira + dev-lane
hand-off moves to a documented "Adapting to your own lane" section, described as optional.

### Gap C — operator identity

"Mr. Hatter" appears 9× in the command file (lines 33, 37, 38, 73, 74, 110, 118, 121). Becomes
"the operator" / "you".

### Gap D — attribution

`emil-design-eng` encodes Emil Kowalski's philosophy (already credits him + animations.dev);
`vgpu` wraps `vercel-labs/vgpu`; `visual-fx-3d` wraps the Poimandres suite. A public repo needs
`LICENSE` (MIT, covering our own composition only) + `CREDITS.md` naming all three upstreams.

## Repo shape

```
design-engineer-skills/
├── README.md              # the "give an agent this URL" install contract
├── LICENSE                # MIT
├── CREDITS.md             # Emil Kowalski · pmndrs · vercel-labs/vgpu
├── .gitignore             # __pycache__/, *.pyc
├── commands/
│   └── smh-designer.md
├── skills/
│   ├── smh-designer/      ├── ui-ux-pro-max/   (data/ + scripts/)
│   ├── emil-design-eng/   ├── vgpu/
│   ├── visual-fx-3d/      ├── webm-alpha-video/
│   ├── animate-expo/      └── write-swift/
└── docs/
    └── frontend_UI_design_guide.md
```

Flat `commands/` + `skills/` (not `.agents/`) so the tree is legible on GitHub's file browser; the
README tells the installing agent where to copy each half for its own harness.

## Transformations (exhaustive)

1. **7 absolute `file:///home/dlohn/…` links** in `smh-designer.md` → repo-relative
   (`../skills/<name>/SKILL.md`, `../docs/frontend_UI_design_guide.md`).
2. **10 `](../../.agents/…)` links** in the design guide → `../skills/…` / `../commands/…`.
3. **Command file pillar list** gains pillar 5 (`animate-expo`, `write-swift`) — closes Gap A.
4. **Phase 2** rewritten to stop at `implementation_plan.md`; Jira/dev-lane → optional section.
5. **9 × "Mr. Hatter"** → operator-neutral.
6. **Drop** `scripts/__pycache__/`.
7. **`smh-designer/SKILL.md`** launcher path `.agents/commands/smh-designer.md` → `commands/smh-designer.md`.
8. **README** authored: what it is, the 8 skills, install for Claude Code / Codex / Cursor / opencode,
   and an explicit agent-executable "Setup" block so the URL alone is enough.

## What "done" looks like — acceptance rows

- **A.** `grep -rn 'file:///' .` over the new repo returns **0 rows**.
- **B.** `grep -rn '/home/dlohn\|Sudo_Hatter_Command\|Mr\. Hatter' .` returns **0 rows**.
- **C.** Every relative Markdown link in the repo resolves to a file that exists (link checker script,
  run in-repo).
- **D.** `python3 -m py_compile` passes on all 3 scripts, AND `python3 scripts/search.py <query>`
  returns real rows from a clean clone — proving `ui-ux-pro-max` works standalone.
- **E.** `grep -rn '/smh-quick-dev\|/cicd-' commands/ skills/` returns rows ONLY inside the documented
  "Adapting to your own lane" section — no live dangling hand-off.
- **F.** All 9 skills present with their full file counts (manifest check against the table above).
- **G.** Repo exists at `github.com/sudomadhatter/design-engineer-skills`, public, README renders.

## Verification plan

A single `verify.py` in the repo root runs A–F and prints a pass/fail table; it ships as part of the
repo so a recipient can prove their clone is intact. G is verified with `gh repo view`.

## Out of scope (named, not silently dropped)

- Porting `/smh-quick-dev` / `/smh-quick-fix` (operator chose "stop at the plan").
- Any change to the command centre's own copies of these files — this lane **reads** them only.
  Gap A's pillar-5 fix lands in the shared repo; back-porting it here is a separate one-line follow-up.

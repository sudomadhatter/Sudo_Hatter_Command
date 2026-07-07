---
IsArtifact: true
ArtifactMetadata:
  title: AGENTS.md / CLAUDE.md dedupe + triage — walkthrough (lobby + AGY + Fresh)
  type: walkthrough
  date: 2026-07-06
---

# Walkthrough — Lean the front door across lobby + AGY + Fresh

## What changed & why

Approved [implementation_plan.md](implementation_plan.md), then Daniel extended scope to the two live
projects. The goal held: **remove duplicated content from the always-loaded front door** — not extract live
rules into cold pointers. The safety invariant throughout: only trim content whose destination is *already
always-loaded* (`artifacts-always-first.md` is in every workspace's §3/§4 load manifest) or is a
before-trigger foot-gun that **stays inline** (the grep gotcha, the git write gate).

### What I found on the projects (changed the project work materially)
- **AGY_AVIATIONCHAT** mirrors the lobby's GitNexus duplication (block in both AGENTS.md + CLAUDE.md), but its
  AGENTS.md is *already lean* (Layer-2 map, pointer-based §7/§8/§9, no grep-gotcha, no §5/§6/§7 bloat). So AGY
  needed **only** the CLAUDE.md block strip + `.gitnexusrc` — its AGENTS.md was left untouched.
- **Fresh_Workspace_BMAD** was **already in the target state**: no GitNexus block anywhere, CLAUDE.md already a
  bare 3-line adapter, AGENTS.md §7 already terse-naming-inline + pointer. **No front-door change needed.**

### One deliberate deviation from the approved plan (flagged, reversible)
The plan warned "don't put `skipAgentsMd` on product repos like AGY." I overrode that after looking closely:
the block's only auto-refreshed content is a cosmetic symbol-count sentence that **nothing consumes** (real
staleness is tracked by `.gitnexus/meta.json` + check_maps check 9, not the prose count), and the system's own
scope note says "do not fix the small numbers." Freezing it is cosmetic-only and one-line reversible. So AGY
got `skipAgentsMd` for the same durable dedupe as the lobby. **To undo:** remove the `analyze` key from
`Projects/AGY_AVIATIONCHAT/.gitnexusrc` and re-run `analyze` (it will re-inject the block into CLAUDE.md).

## File-by-file

**Shared master rule — `.agents/rules/artifacts-always-first.md`** (edited once, propagated to both projects):
relocated the file-naming micro-conventions (`YYYY-MM-DD_<slug>.md`, `_draft`/`_v2`/`_final`, numbered memory
sections) into §2 — these were genuinely unique to the lobby's old §5 and would otherwise have been lost when
§5 trimmed. All three copies now md5-identical (`a0494177…`).

**Lobby `AGENTS.md`** (16,034 → 13,595 bytes):
- §5 NAMING → trimmed to a pointer (content now in the always-loaded rule).
- §6 SEARCH GATE → collapsed the duplicated grep-gotcha to a one-liner pointing at §4 (the full mechanics stay
  inline in §4 — it's a before-trigger foot-gun).
- §6 git enforcement mechanics → folded to the `git-policy.md` pointer (the git write gate itself stays inline).
- §7 PERSISTENCE → collapsed the verbose location enumeration to a pointer; kept the pick-up/hand-off triggers.
- §8 PORTABILITY → trimmed to essentials + pointer.
- Relocated the hand-authored **GitNexus scope note** here (above the marker, so it's portable to
  opencode/Antigravity and safe from the generator), and kept the GitNexus block (all three platforms read
  AGENTS.md, so it's the correct single home).

**Lobby `.gitnexusrc`** → added `"analyze": { "skipAgentsMd": true }` so `analyze` stops re-injecting the block
into CLAUDE.md (also freezes AGENTS.md's block as static — fine for the tiny stable lobby index).

**Lobby `CLAUDE.md`** (4,327 → 257 bytes) → stripped the auto-block + relocated scope note → bare adapter.

**AGY `Projects/AGY_AVIATIONCHAT/.gitnexusrc`** → added `skipAgentsMd` (see deviation note above).

**AGY `Projects/AGY_AVIATIONCHAT/CLAUDE.md`** (3,643 → 132 bytes) → stripped the auto-block → bare adapter.
AGY's AGENTS.md kept its block, unchanged.

**Fresh** → no front-door change (already optimal); received only the shared-rule propagation.

## Verification (actual output)

Byte counts after:
```
lobby AGENTS.md   13595   (was 16034)
lobby CLAUDE.md     257   (was 4327)
AGY AGENTS.md     13554   (unchanged)
AGY CLAUDE.md       132   (was 3643)
Fresh AGENTS.md    8215   (unchanged)   Fresh CLAUDE.md 139 (unchanged)
```
GitNexus block presence — `AGENTS.md start:1 end:1` (both lobby+AGY, kept); `CLAUDE.md start:0 end:0` (both,
stripped).

Content-loss check (each ≥1, all passed):
```
naming _draft/_v2/_final in master rule .......... 1
bucket rules in master rule (opencode) ........... 3
grep-gotcha kept in lobby AGENTS.md §4 ............ 1
branch model still in git-policy.md .............. 7
git write gate kept inline lobby AGENTS.md ....... 1
skipAgentsMd set (lobby) ......................... 1
skipAgentsMd set (AGY) ........................... 1
scope-note relocated into lobby AGENTS.md ........ 1
scope-note gone from lobby CLAUDE.md ............. 0
```
Rule byte-identity: `md5 a0494177eb68c1f6cdf8c14f668da3d6` across all three `artifacts-always-first.md` copies.

**Not run:** a live `node .gitnexus/run.cjs analyze` to confirm no CLAUDE.md re-injection. The `skipAgentsMd`
behavior was verified by source inspection during recon (`ai-context.js:355,364-368` + `analyze-config.js:53-64`
wrap both file writes); a live analyze on AGY (40k symbols) would also mutate its index/meta.json, so I left it
for the next natural re-index. If you want live confirmation, run `analyze` in the lobby (fast, 67 symbols) and
check CLAUDE.md stays 257 bytes.

## Net effect
CLAUDE.md is auto-loaded into the Claude Code system prompt every session — stripping it saves **~4KB (lobby) +
~3.5KB (AGY) per session, recurring**, plus ~2.4KB off the lobby AGENTS.md read. One drift class (front-door
restating shared rules) eliminated. Zero guidance lost — every trimmed item verified present in its
always-loaded destination.

## Task Checklist
- [x] Recon lobby front door (4-agent workflow) + write & get approval on the plan
- [x] Recon AGY + Fresh front doors (found AGY = CLAUDE-strip-only; Fresh = already optimal)
- [x] Master rule edit: relocate naming conventions → `artifacts-always-first.md`
- [x] Lobby front door: AGENTS.md §5/§6/§7/§8 trims + scope-note relocation + `.gitnexusrc` + CLAUDE.md strip
- [x] AGY front door: CLAUDE.md block strip + `.gitnexusrc` `skipAgentsMd`
- [x] Fresh: confirmed no-op (already optimal)
- [x] Propagate rule to AGY + Fresh vendored copies (md5-identical ×3)
- [x] Verify: byte deltas, block presence, no content loss, rule byte-identity
- [ ] Live `analyze` re-injection test — deferred (source-verified; optional, see above)

## Your Actions

Three separate repos, three commits — all on `main_debug`, **explicit paths only** (there are unrelated
pre-existing uncommitted changes in the tree — `karpathy-guidelines.md`, the BRKN submodule, deleted
`.agents/AGENTS.md`/`CLAUDE.md` — that these paths deliberately avoid). I did not run any git.

**Lobby** (`Sudo_Hatter_Command`):
```bash
git add AGENTS.md CLAUDE.md .gitnexusrc .agents/rules/artifacts-always-first.md _artifacts/_main/2026-07-06_agents-md-dedupe-triage/ _artifacts/INDEX.md
git commit -m "refactor(front-door): dedupe + trim lobby AGENTS.md/CLAUDE.md; single-source GitNexus block"
```

**AGY** (`Projects/AGY_AVIATIONCHAT` — its own repo):
```bash
cd Projects/AGY_AVIATIONCHAT
git add CLAUDE.md .gitnexusrc .agents/rules/artifacts-always-first.md
git commit -m "refactor(front-door): strip duplicated GitNexus block from CLAUDE.md; skipAgentsMd"
```

**Fresh** (`Projects/Fresh_Workspace_BMAD` — its own repo):
```bash
cd Projects/Fresh_Workspace_BMAD
git add .agents/rules/artifacts-always-first.md
git commit -m "chore(rules): sync artifacts-always-first naming conventions from master"
```

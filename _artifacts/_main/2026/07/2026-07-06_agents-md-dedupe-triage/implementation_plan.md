---
IsArtifact: true
ArtifactMetadata:
  title: AGENTS.md / CLAUDE.md dedupe + triage — lean the lobby front door
  type: implementation_plan
  date: 2026-07-06
---

# Implementation Plan — Lean the lobby front door (AGENTS.md / CLAUDE.md dedupe + triage)

## Goal

Shrink the always-loaded lobby front door by removing **duplicated** content — not by extracting
live rules into cold pointers. Every section that summarizes a rule already covered by an
**always-loaded** rule file collapses to a pointer; genuine before-trigger foot-guns stay inline; the
GitNexus tool-usage block is single-sourced. Net effect: fewer tokens on every session, one drift
class eliminated, zero loss of guidance.

**Scope: the LOBBY only** (`Sudo_Hatter_Command/` root `AGENTS.md`, `CLAUDE.md`, `.gitnexusrc`, and the
shared `.agents/rules/artifacts-always-first.md`). Propagating the convention to `Projects/*` front
doors is a **separate, out-of-scope follow-up** (see §7).

## Honest correction to my earlier pitch

My first message argued a headline reason was "AGENTS.md (16KB) exceeds Antigravity's ~12k front-door
ceiling, so it's being truncated." **That was wrong.** Recon proved the 12,000-char limit is a guard on
Antigravity **workflow/slash files** (live guard: `.agents/scripts/sync-agents.ps1:170-171`), **not** a
cap on reading `AGENTS.md` as context. Root `AGENTS.md` is 16,034 bytes and functions fine as the
Antigravity front door — no truncation. The change is still worth doing, but on **token-economy +
anti-drift** grounds, not a truncation fix.

## Why it's still worth doing (grounded)

- **Recurring token cost.** `CLAUDE.md`'s GitNexus block (~3.9 KB) is **auto-loaded into the Claude Code
  system prompt every session** (it's in the project-instructions payload right now). Stripping it is a
  guaranteed every-session saving. Trimming `AGENTS.md` (~4.5 KB) saves whenever the agent reads it
  (most sessions). Rough total: **~8 KB / ~2k tokens off a typical session**, recurring.
- **Kills a drift class.** §5/§6/§7 restate `artifacts-always-first.md`, `git-policy.md`, and
  `constitution.md`. Two copies drift; `git-policy.md:24` literally says "per-workspace AGENTS.md GATES
  sections point here rather than restating it" — the current §6 is exactly the drift that line exists
  to prevent.
- **Consistency.** Matches the model already built in `.agents/rules/INDEX.md` (router → pull the one
  rule you need) and the §8 portability principle ("CLAUDE.md/GEMINI.md are one-line adapters").

## The safety invariant (what makes every trim safe)

**We only trim content whose destination is *already always-loaded* or is a before-trigger foot-gun
that *stays inline*.** Nothing critical gets demoted to a cold on-demand read.

- `artifacts-always-first.md` and `constitution.md` are in AGENTS.md §3's always-load manifest → §5
  (naming/placement) and §7 (persistence) collapse to them **without leaving context**.
- `git-policy.md` owns the branch model; the **one-line git write gate stays inline** (it's a
  before-router foot-gun) — only the restated mechanics collapse to the pointer.
- The grep-is-blind foot-gun **stays inline** (§4); only its second copy (§6) collapses.

This is the direct application of the memory lesson `restate-alwayson-obligations` — we are NOT hiding
standing obligations behind pointers agents skip; we're deleting duplicates of content that is present
in-context anyway.

---

## Ground-truth findings (from 4-agent recon — all citations verified)

### A. GitNexus block generator (the tricky edge case)
- Written by the **globally-installed `gitnexus` CLI** (`dist/cli/ai-context.js →
  upsertGitNexusSection()`), on `node .gitnexus/run.cjs analyze`. **Not** a hook — the gitnexus
  PostToolUse hook only *nags* to re-run analyze; it never writes the block itself.
- **Target file set `{AGENTS.md, CLAUDE.md}` is HARDCODED** (`ai-context.js:357,361`). `GEMINI.md` is
  never a target (that's why it's a clean 271-byte adapter).
- **No per-file toggle exists.** The only switch is `skipAgentsMd` (aliases `skipContextFiles`;
  CLI `--skip-agents-md`) and it is **all-or-nothing** — suppresses the block in *both* files together.
- A bare hand-delete of CLAUDE.md's block **gets silently re-injected** on the next `analyze`
  (`upsertGitNexusSection` even re-creates the whole file if missing — `ai-context.js:183-187`). So the
  dedupe requires a **config change**, not just an edit.

### B. AGENTS.md triage — all 4 suspected duplications CONFIRMED
| § | Lines | Disposition | Why |
|---|---|---|---|
| header, §1, §2, §3-manifest, §3-artifacts-gate, §4-infra, §4-grep-gotcha, §6-routing-gate, §6-git-write-gate | 1–52, 54–69, 93, 102–114 | **KEEP inline** | routing framework / infra map / before-trigger foot-guns & gates |
| §5 NAMING | 71–90 | **TRIM to pointer** (+ relocate 2 unique lines) | 74–89 duplicate `artifacts-always-first.md` §2; line 89 already says "Full model → workspace-standard.md" |
| §6 SEARCH GATE | 94–101 | **DEDUPE** | verbatim 2nd copy of §4's grep gotcha; already self-refers "Full mechanics → §4" |
| §6 git enforcement note | 115–119 | **TRIM to pointer** | duplicates `git-policy.md:29-33` |
| §7 PERSISTENCE | 122–136 | **TRIM to pointer** | duplicates `artifacts-always-first.md`; already ends "Full protocol → …" |
| §8 PORTABILITY | 138–143 | **TRIM to 1–2 lines + pointer** | conceptual background; ends "Full model → workspace-standard.md" |
| GitNexus block | 145–189 | **KEEP in AGENTS.md** (strip the CLAUDE.md copy instead — see decision) | portability: opencode + Antigravity read AGENTS.md, not CLAUDE.md |

**No section needs a NEW rule file** — every demotable chunk already lives in an existing
always-loaded rule/doc. The move is trim-to-pointer, not extraction.

### C. The one genuine content MOVE
`artifacts-always-first.md` covers the artifact **bucket/placement** model in full, but a grep confirms
the **file-naming micro-conventions are absent** there and in `workspace-standard.md`:
- `YYYY-MM-DD_<slug>.md` (dated *file*), and `<slug>_draft.md → _v2.md → _final.md` (versioned drafts).

These are unique to AGENTS.md §5 lines 72–73 → **must be appended to `artifacts-always-first.md`** before
§5 is trimmed, or they're lost.

### D. Platform / blast radius
- Front-door files (`AGENTS.md`/`CLAUDE.md`/`GEMINI.md`) are **NOT synced** by `/sync-agents` — they're
  per-workspace hand-authored. So lobby edits are **lobby-only** (good — contained blast radius).
- The lobby is a **template** others hand-mirror, and coverage already drifts (only 4/8 projects have
  `AGENTS.md`; `BRKN_Tattoos/GEMINI.md` still carries a stale name). → Propagation is a deliberate,
  separate follow-up, never automatic.

---

## The change set (exact, per file)

### File 1 — `.agents/rules/artifacts-always-first.md`  (do this FIRST — prevents content loss)
Append the unique file-naming micro-conventions into §2, immediately after the folder-naming block
(current line 108, end of the "Random one-off" bullet). Proposed insertion:

> **File names within a folder:** dated output → `YYYY-MM-DD_<slug>.md`; versioned drafts →
> `<slug>_draft.md` → `<slug>_v2.md` → `<slug>_final.md`. Memory / active-context sections are
> **numbered** (e.g. `5.2`) so agents skip-to-N instead of reading the whole file.

(No `INDEX.md` row needed — appending to an existing always-loaded rule.)

### File 2 — `AGENTS.md` (lobby root)  — the trims/dedupes
1. **§5 (71–90) → collapse** to one line under the existing header, e.g.:
   `Naming & artifact placement (buckets, opencode namespace, story/system/random folders, dated +
   versioned file names) → \`.agents/rules/artifacts-always-first.md\` (always-loaded) · full model →
   \`docs/workspace-standard.md\`.`
2. **§6 SEARCH GATE (94–101) → one line:**
   `**SEARCH GATE** — a root-level Grep is blind to \`Projects/\` (ripgrep honors the lobby
   \`.gitignore\`); point Grep at \`Projects/<name>\` or use Bash. Full mechanics → §4.`
3. **§6 git enforcement (115–119) → fold** into the existing git-policy pointer; keep the top-line
   write gate (102–114, lightly tightened) and the constitution pointer (120) inline.
4. **§7 (122–136) → collapse** to the two pointers it already ends with (`artifacts-always-first.md`
   for the protocol; `router.md` for the open-tasks trigger), ~2 lines.
5. **§8 (138–143) → collapse** to 1–2 lines + the `workspace-standard.md` pointer.
6. **GitNexus block (145–189) → unchanged** (kept as the portable tool-index). Add a **hand-authored
   one-line scope note ABOVE the `<!-- gitnexus:start -->` marker** carrying the "lobby index is
   deliberately tiny; pass `repo:\"AGY_AVIATIONCHAT\"` for product work" note relocated from CLAUDE.md,
   so opencode/Antigravity see it too. (Safe: the generator only writes *between* the markers, and with
   File 3 it won't write at all.)

### File 3 — `.gitnexusrc` (lobby root)
Change `{"pdg":true}` → `{"pdg":true, "analyze":{"skipAgentsMd":true}}` (or top-level
`"skipContextFiles":true`). Then **hand-delete CLAUDE.md's block once** (File 4). This stops future
`analyze` from re-injecting into CLAUDE.md. **Trade-off:** AGENTS.md's block also stops auto-refreshing
its symbol counts — acceptable here (the lobby index is tiny/stable and CLAUDE.md's own note says "do
not fix the small numbers"). **⚠️ Do NOT propagate `skipAgentsMd` to product repos** (e.g. AGY, 37.7k
symbols) where counts change meaningfully.

### File 4 — `CLAUDE.md` (lobby root)
Delete the auto-generated GitNexus block (**lines 9–53**, the `<!-- gitnexus:start -->` …
`<!-- gitnexus:end -->` span). Relocate the substance of the hand-authored scope note (lines 7–8) into
AGENTS.md (File 2, step 6). Result: `CLAUDE.md` becomes a bare ~5-line adapter matching `GEMINI.md`.

---

## Open decision for Daniel (one real fork)

**Where does the single GitNexus block live?** My recommendation is baked into the change set above:
**keep it in `AGENTS.md`, strip the `CLAUDE.md` copy.** Rationale: opencode and Antigravity read
`AGENTS.md` (not `CLAUDE.md`), so keeping it there preserves the tool guidance for all three platforms
and honors the "adapters are bare" principle. The recon's triage agent floated the opposite (keep in
CLAUDE.md) but hadn't weighed opencode/Antigravity readership.

- **Alternative A (lighter touch):** don't touch `.gitnexusrc`; keep the block auto-managed in both
  files, add a post-`analyze` strip of CLAUDE.md folded into `/update-maps`. Keeps AGENTS.md
  auto-refresh, but adds a moving part and CLAUDE.md transiently re-bloats each analyze.
- **Alternative B (do nothing on GitNexus):** apply only the AGENTS.md §5–§8 trims, leave the GitNexus
  duplication as-is. Smallest change; forgoes the ~3.9 KB every-session CLAUDE.md win.

If you don't flag otherwise, I'll proceed with the recommended path (Option 1: `skipAgentsMd` + strip).

## Edge cases & risks
1. **Frozen AGENTS.md gitnexus stats** — accepted for the lobby (stable, "don't fix the numbers"). To
   regenerate on a gitnexus upgrade: temporarily unset the flag, run `analyze`, re-strip CLAUDE.md,
   re-set the flag.
2. **`skipAgentsMd` must not reach product repos** — lobby-only; called out in File 3.
3. **gitnexus PostToolUse hook may still nag** to run analyze after git ops — harmless (analyze becomes
   a no-op for these files).
4. **Pointer-skip risk** — mitigated by the safety invariant: every trim's destination is already
   always-loaded (or stays inline). No standing obligation moves behind a cold read.
5. **Lobby-only** — front doors aren't synced; project propagation is a separate opt-in follow-up.

## Verification plan (run after execution, before handoff)
1. **No-content-loss grep** — for each trimmed item, confirm the content survives in its destination:
   bucket rules in `artifacts-always-first.md §2`; grep gotcha in AGENTS.md §4; branch model in
   `git-policy.md`; persistence in `artifacts-always-first.md`; the `_draft/_v2/_final` + dated-file
   patterns newly present in `artifacts-always-first.md`.
2. **Byte-count delta** — record AGENTS.md and CLAUDE.md before/after (expect AGENTS.md ≈16 KB→~11.5 KB;
   CLAUDE.md ≈4.3 KB→~0.4 KB).
3. **Re-injection check** — run `node .gitnexus/run.cjs analyze` and confirm CLAUDE.md is **not**
   re-injected (block stays gone) with `skipAgentsMd` set.
4. **Fresh-agent read-through** — trace AGENTS.md as each platform would: confirm every gate/rule is
   still reachable via a pointer and every kept foot-gun is still inline.

## Rollback
All five files are git-tracked on `main_debug`; revert is `git checkout -- <files>` (or revert the
commit). No data migration, no destructive ops.

## Out of scope (follow-ups, not this plan)
- Mirroring the leaner front-door convention into `Projects/*` (and fixing the stale
  `BRKN_Tattoos/GEMINI.md` name, the missing AGENTS.md in 4/8 projects).
- Any change to product-repo `.gitnexusrc` files.
- Reconsidering whether the GitNexus block should be a skill rather than an always-loaded block at all.

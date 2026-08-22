# Implementation Plan — Make the sudo `/` flow work in Antigravity (and unify the command/workflow surfaces)

**Status:** EXECUTED 2026-06-28 (plan approved). D1/D2/D3 all resolved + done; verified on disk. **PENDING: Daniel reloads the Antigravity IDE to confirm `/sudo-*` shows in the `/` menu.**
- **D1 → kept `.agents/` (plural)** — it's the current standard; no rename.
- **D2 → per-project `.agents/workflows/`** is the surface (clone-safe). The old global cache (`~/.gemini/antigravity/global_workflows/`) is left as harmless legacy — the IDE wasn't reading it (it had the sudo *commands* since 13:20 today and they never showed). If a duplicate `/` entry appears after reload, the fix is to stop the sync writing that global cache.
- **D3 → done:** self-audit unified into one source `commands/sudo-self-audit.md` (full content, no proxy); `1_self-audit-stress-test.md` deleted + all ghosts purged; 3 dependents repointed.
- **Mechanism shipped:** `sync-agents.ps1` now mirrors the 6 antigravity-eligible `sudo-*` commands → `.agents/workflows/` verbatim (function `Sync-AntigravityWorkflowMirror`). One source (`commands/`), generated mirror for Antigravity. Re-run `/sync-agents` after editing any sudo command.
**Author:** Claude (Opus 4.8). I got Antigravity's model wrong twice today; this plan is built on web-researched facts, not guesses (sources at bottom).

---

## 1. The problem, stated plainly
Antigravity (Gemini) has **no concept of "commands."** Its `/` menu is built from:
- **workflows** → markdown files in `.agents/workflows/` (invoked `/name`)
- **skills** → `.agents/skills/` (auto-activated by the agent, *not* `/`-invoked) — this is why the BMAD personas (`bmad-agent-dev`, `sm`, etc.) are skills.

The `sudo-*` flow was authored **only** in `.agents/commands/` — a **Claude/opencode-only** folder Antigravity never reads. That is the entire reason it's invisible in Gemini. It was never deleted and the sync never purged it; it was simply put in the wrong bucket for Antigravity. "commands" is a Claude thing you got when you added Claude Code.

**Did the sync break anything?** No. Your 39 source files in `.agents/commands/`, the Claude/opencode copies, and `~/.gemini/antigravity/global_workflows/` are all intact. The only harm today was my "fully restart Antigravity" advice, which flushed its cached `/` menu — that's why even the BMAD entries disappeared from view (they're still on disk).

---

## 2. What I already changed today (correct regardless of the Antigravity fix — keep)
- **`sudo-update-sprint-memory.md`** — removed the "ask Daniel / leave it at review" punt. Now: running it = your sign-off → it closes the story (review→done) + updates the sprint by default; the ONLY block is objectively-red tests (a `/sudo-code-review` FAIL). *Verified + synced.*
- **`sudo-code-review.md`** — added Step 5: update the story `walkthrough.md` (port of the autopilot twin's step). *Verified + synced.*
- Synced lobby + AGY + Fresh; saved 2 memories (sign-off principle; manual-vs-`_AP` twin drift).

These stand on their own — they are not part of the Antigravity bug.

---

## 3. Research findings (verified — see sources)
- **Workflow location:** `.agents/workflows/` (plural — current default) **or** `.agent/workflows/` (singular — legacy, still back-compat supported). One community source quotes Antigravity's system prompt as "Workflows must be in `.agent/workflows/`; files anywhere else are ignored," so the exact behavior is **version-dependent and must be verified on your install.**
- **Global workflows:** `~/.gemini/antigravity/global_workflows/` (the path the sync already targets) — **BUT see the IDE caveat below; this may be the wrong install's folder.**
- **You are on the Antigravity *IDE*, not the CLI — and that almost certainly explains "global doesn't work."** On disk you have THREE separate stores: `~/.gemini/antigravity/` (older install — Jun-4 protobuf `.pb` conversations), `~/.gemini/antigravity-ide/` (your ACTIVE IDE — today's sqlite `.db` conversations), and shared `~/.gemini/`. The sync writes the global cache to the **old** `~/.gemini/antigravity/global_workflows/` — a folder your current IDE likely does **not** read. The IDE probably reads from an IDE-specific path (e.g. under `~/.gemini/antigravity-ide/…`) and/or the shared `~/.gemini/…`, and possibly its own AppData (`%APPDATA%\Antigravity*`). This is the leading hypothesis for why nothing global shows. **Must be confirmed empirically before changing the sync.**
- **12,000-character limit per workflow file.** `sudo-update-sprint-memory.md` is ~11.3k — dangerously close; must check every file we sync as a workflow.
- **Known bug:** Antigravity **v1.20.5** — `/` does not trigger workflows at all (they only appear under the "…" dropdown); fixed by rolling back to **1.19.6**. So "global doesn't work" may partly be this bug, not our setup. **Check your installed version.**
- **Skills ≠ workflows:** skills auto-activate; you don't `/`-invoke them. BMAD personas are skills, so they're a separate mechanism we don't need to touch.
- **Artifacts (confirmed by Daniel):** Antigravity does NOT write to the repo's `_artifacts/` folder — it keeps its own working artifacts in its `brain/` store, and that is fine/expected. The repo `_artifacts/<epic>/<story>/walkthrough.md` convention is the durable record that any tool writes when explicitly told to (e.g. `sudo-code-review` Step 5). The two coexist; no reconciliation needed, and the walkthrough-update step does not depend on Antigravity's internal store.

---

## 4. The design target: kill the proxy, one source fans out
Today `sudo-self-audit` (a Claude command) is a **proxy** pointing at `1_self-audit-stress-test` (the workflow). There is no good reason for it — the sync generates copies from one source, so "drift" can't happen. Decision (Daniel, confirmed in chat): **drop the proxy.**

**Target architecture:** one **source file per capability**, one **consistent `sudo-*` name**, and the sync copies the **full content** into each platform's folder:
- `.agents/workflows/` → Antigravity
- `.claude/commands/` → Claude
- `.opencode/commands/` → opencode

You author once; the sync fans it out; the name is identical on every platform; nothing is hand-duplicated.

---

## 5. Open decisions for Daniel (answer these tomorrow → then I execute)

**D1 — `.agents` (plural) vs `.agent` (singular)? → RESOLVED: keep `.agents` (plural). No action.**
Confirmed via current docs + multiple community sources: Antigravity's CURRENT default is **`.agents/` (plural)** for `rules/`, `skills/`, and `workflows/`. The singular `.agent/` is only **legacy backward-compat** (the form the workspace used back in May). So `.agents` is correct — Daniel did NOT make the folder wrong. Renaming to singular would go backward and risks disturbing the working BMAD skills (which load from `.agents/skills/`). One outlier community repo still documents `.agent/workflows/` singular, but it's against the weight of current docs. (Sources at bottom of this plan.)

**D2 — One Antigravity surface (this is what prevents "two of everything")?**
Duplicates happen only if the same workflow name is registered from **two** places Antigravity reads at once. So pick one:
- **(a) Per-project `.agents/workflows/`** — clone-safe, travels with the repo, reliable. Cost: a sync-generated copy per project (you don't maintain it). **← my recommendation**
- **(b) Global only** — one machine-wide copy, your stated preference. Caveats: we must FIRST find the **IDE's** real global path (step 6.2) because the sync currently writes the *old install's* `~/.gemini/antigravity/global_workflows/`, which is the likely reason "global doesn't work"; plus it's exposed to the v1.20.5 bug and isn't clone-safe.
If we choose (a), the sync must **stop** writing the global copy (or we get double entries). If (b), we stop writing per-project.

**D3 — Self-audit rename?** Rename `.agents/workflows/1_self-audit-stress-test.md` → `sudo-self-audit.md` and delete the proxy command. **Recommend:** yes (consistent naming). Old references in stories/_artifacts are throwaway provenance.

---

## 6. Execution steps (once D1–D3 are answered)
1. **Verify reality on your machine first** (no guessing):
   - 6.1 Check Antigravity **IDE** version (is it the buggy 1.20.5?).
   - 6.2 **Find where the IDE actually reads global workflows** — it's the IDE, so confirm whether it's `~/.gemini/antigravity-ide/…`, shared `~/.gemini/…`, or AppData (`%APPDATA%\Antigravity*`), NOT necessarily the old `~/.gemini/antigravity/global_workflows/` the sync writes today. Easiest: in the IDE, create one global workflow via the "…" → Workflows → **+ Global** button, then find which file appeared on disk — that reveals the true global path.
   - 6.3 Drop ONE throwaway test file in `Projects/AGY_AVIATIONCHAT/.agents/workflows/zz-test.md`, reload, confirm `/zz-test` appears + triggers. Repeat in `.agent/` (singular) only if plural fails. This settles D1 + D2(a) empirically.
2. **Update `sync-agents.ps1`:** add a step that mirrors the invocable `sudo-*` set (full content) into `.agents/workflows/` for each project, **merged** with the existing real workflows (do not clobber `1_update-maps`, `autopilot_bmad_dev_loop`, etc.). Reuse the script's existing "is-a-master-command vs is-a-master-workflow" logic.
3. **Resolve global per D2:** stop writing `global_workflows` if we go per-project (prevents dupes), or make it the sole surface if we go global.
4. **Self-audit (D3):** rename the workflow, delete the proxy command, fix references.
5. **12k guard:** assert every file synced as a workflow is < 12,000 chars; split any that exceed (watch `sudo-update-sprint-memory`).
6. **Re-sync** lobby + all projects; **verify in Antigravity** that `/sudo-write-story-tests`, `/sudo-dev-story-tests`, `/sudo-code-review`, `/sudo-update-sprint-memory`, `/sudo-self-audit`, `/sudo-boot-sprint-memory` all appear AND trigger.
7. Update `.agents/workflows/INDEX.md` + `.agents/commands/INDEX.md` + memories to record the unified model.

---

## 7. Risks / watch-outs
- **Don't rename `.agents`→`.agent` blindly** — it could break the working BMAD skills. Verify first (D1 + step 6.2).
- **Double-registration** (global + workspace) → duplicate `/` entries. Pick one surface (D2).
- **12,000-char limit** may silently drop big workflows.
- **v1.20.5 slash bug** can make a correct setup look broken — confirm version before concluding anything.
- The `_AP` autopilot twins are Claude-only (`platforms: [claude]`) — they should NOT be synced to the Antigravity workflow surface.

---

## Sources
- Antigravity workflows / `.agent` vs `.agents` folder convention: https://github.com/harikrishna8121999/antigravity-workflows
- Rules & workflows on disk (paths, global location): https://atamel.dev/posts/2025/11-25_customize_antigravity_rules_workflows/
- Slash-command-doesn't-trigger bug (v1.20.5 → roll back to 1.19.6): https://discuss.ai.google.dev/t/the-slash-command-workflows-doesnt-trigger/116253
- Official docs (JS-rendered, for your manual reference): https://antigravity.google/docs/rules-workflows · https://antigravity.google/docs/ide-workflows
- Skills directory caveats: https://medium.com/google-cloud/configuring-mcp-servers-and-skills-for-antigravity-cli-and-ide-a938c7eebb78

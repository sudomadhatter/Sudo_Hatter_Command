# PROPAGATE: autopilot GLM hybrid lane → a project's local `autopilot-dev-story.ps1`

> **Agent: this is a task for you.** The autopilot engine (`scripts/autopilot-dev-story.ps1`) is
> **project-local** — every project under `Projects/` has its own copy and they are NOT synced. The GLM
> hybrid lane (`/autopilot_glm`) was built and proven in **AGY_AVIATIONCHAT**. Your job is to bring the
> SAME change into the target project's local engine + drop in the `/autopilot_glm` command, then verify.
> The canonical source of truth is AGY's engine; the exact change is captured in
> [`autopilot-glm-hybrid.patch`](../scripts/autopilot-glm-hybrid.patch) (this folder).

**What the change does:** adds opt-in flags (`-DevBaseUrl` / `-DevModel` / `-DevAuthToken` + the `-Glm`
sugar switch) that route the **Dev lane (Stage 1 Plan + Stage 3 Implement)** through an
Anthropic-compatible endpoint (Z.ai's GLM 5.2) so that token-heavy code-writing spends **zero Claude
subscription tokens**. The QA lane (Stages 2 + 4) stays on Claude. Empty flags = byte-identical to the
existing all-Claude engine, so this is purely additive and cannot change `/cicd-autopilot-claude`.

---

## 0. Resolve the target

Let `ENG = <target-project>/scripts/autopilot-dev-story.ps1`. Run this whole runbook against ONE project.
(From the command center, `<target-project>` = `Projects/<name>`; from inside a project, it's `.`.)

## 1. Idempotency precheck — is it already applied?

```
grep -c "DevBaseUrl" "$ENG"
```
If **> 0**, the GLM lane is already in this engine — **STOP, nothing to do** (verify with §5 if unsure).
If **0**, continue.

## 2. Divergence check — pick the path

Compare the target against AGY's PRE-GLM baseline (Fresh_Workspace's copy was byte-identical to it):
```
git diff --no-index Projects/Fresh_Workspace_BMAD/scripts/autopilot-dev-story.ps1 "$ENG"
```
- **No differences** (or only trivial ones) → the copy has NOT diverged → **Path A (fast copy)** is safe.
- **Real differences** (this project hand-tuned its engine) → **Path B (surgical)** — do NOT clobber the local tweaks.

## Path A — fast whole-file copy (un-diverged targets)

Copy AGY's engine (which already has the GLM lane) over the target:
```
cp Projects/AGY_AVIATIONCHAT/scripts/autopilot-dev-story.ps1 "$ENG"
```
Then go to §4.

## Path B — surgical patch (diverged targets)

Apply [`autopilot-glm-hybrid.patch`](../scripts/autopilot-glm-hybrid.patch). Try the patch tool first:
```
git apply --3way docs/migrations/scripts/autopilot-glm-hybrid.patch   # adjust -p / path if needed
```
If the hunks don't land cleanly (because of divergence), apply these **9 idempotent edits by hand** —
each anchors on stable, unchanged lines. (The patch file is the exact reference for each block's text.)

1. **New params** — after the `[string]$TestScope = 'auto',` param, before `[switch]$DryRun`: add the
   `$DevBaseUrl`, `$DevAuthToken`, and `[switch]$Glm` params (patch hunk @@ ~149).
2. **Normalization block** — right after `$OutputEncoding = [System.Text.Encoding]::UTF8`: add the
   `-Glm` default-fill + auth-token resolution + the two misconfig guards (patch hunk @@ ~161). Token
   precedence: explicit `-DevAuthToken` > process env (`Z_AI_API_KEY`/`GLM_API_KEY`/`ANTHROPIC_AUTH_TOKEN`)
   > a gitignored **`.env`** found by walking up from the project root to the command center (so one
   lobby-level `.env` serves every child project, immune to the Windows "new User env var not seen by an
   already-open shell" gap). **Note:** the missing-key guard must include `-and -not $DryRun` so a
   `-DryRun` preview works without a key.
3. **DryRun readout** — after the `qa  = $qaShow` line: add the `if ($DevBaseUrl) { ... HYBRID ... }`
   readout line (patch hunk @@ ~446).
4. **Startup banner** — after the `Start    : Stage $startStage ...` line: add the two `HYBRID` banner
   lines gated on `$DevBaseUrl` (patch hunk @@ ~490).
5. **Invoke-Stage params** — after `[string]$SessionName`: add `[string]$BaseUrl = ""` and
   `[string]$AuthToken = ""` (patch hunk @@ ~503).
6. **Env scope (open)** — after `Push-Location $RepoRoot` / before `$cargs = @(`: add the `$envKeys` /
   `$envSaved` capture + the `if ($BaseUrl) { set ANTHROPIC_BASE_URL/AUTH_TOKEN + the 3 model slots }`
   block (patch hunk @@ ~515).
7. **Env scope (restore)** — in the `finally` after the `& $Claude @cargs` call: restore/remove the
   `$envKeys` before `Pop-Location` (patch hunk @@ ~538).
8. **Model-mismatch tolerance** — where `$served` is compared to `$Model`: normalize a trailing
   `[..]` tag + case (`$normReq` / `$servedNorm`) so `glm-5.2[1m]` doesn't false-fire (patch hunk @@ ~564).
9. **Wire the Dev-lane calls** — append ` -BaseUrl $DevBaseUrl -AuthToken $DevAuthToken` to the
   Stage 1 (`-Name "Plan"`) AND Stage 3 (`-Name "Implement"`) `Invoke-Stage` calls (hunks @@ 1102, 1158).

Stages 2 + 4 are left untouched (no `-BaseUrl` → native Anthropic).

## 4. Drop in the `/autopilot_glm` command

Copy AGY's command into the target project's command dirs (create the wrapper if the target is a
different surface):
```
cp Projects/AGY_AVIATIONCHAT/.claude/commands/autopilot_glm.md "<target-project>/.claude/commands/autopilot_glm.md"
cp Projects/AGY_AVIATIONCHAT/.agents/commands/autopilot_glm.md "<target-project>/.agents/commands/autopilot_glm.md"
```
It's a thin wrapper (only the `-Glm` delta + key prereq); it defers all reporting mechanics to
`/cicd-autopilot-claude`, so it needs no per-project edits.

## 5. Verify (do all three — none spend money)

```
# a) parses clean
powershell -NoProfile -Command "$e=$null; [System.Management.Automation.Language.Parser]::ParseFile('<ENG>',[ref]$null,[ref]$e)|Out-Null; if($e){$e|%{ 'ERR L'+$_.Extent.StartLineNumber+': '+$_.Message }}else{'OK'}"

# b) $0 dry run resolves the GLM endpoint + model (pick any ready-for-dev story in the project)
powershell -NoProfile -File "<ENG>" -Story <id> -Glm -DryRun
#   → expect a "Dev lane : HYBRID -> https://api.z.ai/api/anthropic [model glm-5.2 ...]" line

# c) keyless REAL run must fail fast at $0 (before any stage), NOT proceed
#   (with $env:Z_AI_API_KEY unset)
powershell -NoProfile -File "<ENG>" -Story <id> -Glm
#   → expect: "Dev-lane endpoint -DevBaseUrl is set ... but no auth token was found ..." + exit 1
```

## Done criteria

- `grep -c DevBaseUrl "$ENG"` ≥ 1, parses clean, dry-run shows the HYBRID line, keyless run fails fast.
- `/autopilot_glm` exists in the project's command dir(s).
- `/cicd-autopilot-claude` is **unchanged in behavior** (the flags are opt-in; default path is byte-identical).

## Do NOT

- Do not touch `/cicd-autopilot-claude`'s defaults or the QA lane (Stages 2 + 4 must stay on Anthropic).
- Do not put the Z.ai key on the command line or in a committed file — it comes from `$env:Z_AI_API_KEY`.
- Do not port to `/autopilot_mobile` as part of this task — that's a separate Workflow-engine mirror
  decision (see the `autopilot-glm-hybrid-lane` / `autopilot-mobile-mirrors-claude` memory).

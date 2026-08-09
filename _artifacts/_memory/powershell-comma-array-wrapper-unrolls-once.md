---
name: powershell-comma-array-wrapper-unrolls-once
description: "A PowerShell function returning `,@(...)` must be captured by BARE assignment. `@(f())` and `f() | Where-Object` both hand you the inner array as ONE object — which turned a manifest purge into 'delete all 32 skill dirs'."
metadata:
  type: reference
---

The `return ,@($items)` idiom exists so an empty or 1-element array survives PowerShell's automatic
unrolling. It only works if the caller lets the pipeline unroll the wrapper **exactly once**:

```powershell
$x = Get-SkillDirSet $dir            # ✅ the real array
$x = @(Get-SkillDirSet $dir)         # ⛔ 1-element array whose item IS the array
Get-SkillDirSet $dir | Where-Object {...}   # ⛔ Where-Object sees ONE object
```

Verified 2026-08-09 (SCC-66): `@(...)` around the call printed `count=1 first=System.Object[]`.

**Why it matters:** the wrong form is silent and *type-plausible* — code keeps running with a list
that matches nothing. In `sync-agents.ps1` it made the manifest's "what we still own" set match no
name, so `Invoke-ManifestPurgeDir` proposed deleting **all 32 `.claude/skills` dirs, hand-authored
ones included**. Both wrong forms were written and both got caught by `-WhatIf` before disk was
touched.

**How to apply:** capture with a bare assignment, then filter the variable. And run
`sync-agents.ps1 -WhatIf` before any real sync after editing it — the dry run is what turns this
class of bug into a footnote. Related: [[one-door-per-platform-per-command]].

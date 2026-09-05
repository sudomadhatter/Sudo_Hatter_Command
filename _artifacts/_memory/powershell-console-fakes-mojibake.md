---
name: powershell-console-fakes-mojibake
description: PS 5.1 Get-Content renders perfectly good UTF-8 as mojibake — never diagnose encoding from terminal output
metadata: 
  probe: "test -e .agents/scripts/workflow_lint.py"
  node_type: memory
  type: feedback
  originSessionId: d9adc5bc-e814-4396-b913-62eac264ecce
  modified: 2026-08-03T18:39:57.125Z
---

Windows PowerShell 5.1 `Get-Content` / `Select-String` decode files as the system ANSI
codepage, so a valid UTF-8 em dash (`E2 80 94`) prints as `â€"`. Terminal output is
therefore **worthless as evidence of file corruption** — on 2026-08-03 this faked mojibake
in `sprint-status.yaml`, `sudo-self-audit_AP.md`, and `scripts/INDEX.md`; all three were
strict-valid UTF-8.

**Why:** the lie runs one way only — it invents corruption that isn't there, so you "fix"
clean files and churn the tree. (It can also hide the reverse: real corruption inside a
code span that a naive scan flags, or a BOM that makes `startswith("---")` false so
frontmatter looks absent.)

**How to apply:** diagnose encoding at the byte level, never by eye:
```powershell
$b=[System.IO.File]::ReadAllBytes($f)
try { [System.Text.UTF8Encoding]::new($false,$true).GetString($b)|Out-Null; 'OK' } catch { 'BROKEN' }
```
Or just run `.agents/scripts/workflow_lint.py`, which does this: U+FFFD ⇒ ERROR (undecodable
bytes), `â€`-class digraphs in **prose** ⇒ WARN, and the same digraphs inside backticks or
fences ⇒ silent, because docs that teach the bad pattern quote it verbatim
([[comment-literals-invert-source-grep-tests]] is the same shape).

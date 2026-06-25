---
name: powershell-encoding-safety
description: "Prevents UTF-16LE/BOM file corruption when restoring or creating source files on Windows. Activates whenever file content is written via shell commands."
activation: Always On
---

# PowerShell Encoding Safety (Windows)

## The Problem

PowerShell's `>` and `>>` redirect operators write files as **UTF-16LE with BOM** by default.
This is invisible locally (Node, Python, and VS Code handle it fine on Windows), but **breaks
production builds** in Linux-based CI/CD containers (Cloud Build, Docker) where tools like
Turbopack expect strict UTF-8.

**Real incident (May 2026):** `git show <sha>:file > file.tsx` produced a UTF-16LE file that
built locally but failed in Cloud Build with: `invalid utf-8 sequence of 1 bytes from index 0`.

## Rules

| Scenario | ✅ Do This | ❌ Never Do This |
|---|---|---|
| **Restore a deleted file** | `git checkout <sha> -- <path>` | `git show <sha>:<path> > <file>` |
| **Restore from stash** | `git restore --source=stash@{0} -- <path>` | Redirect stash content via `>` |
| **Write file content** | Use the `write_to_file` / `replace_file_content` tool | `echo "content" > file.ext` |
| **Copy a file** | `Copy-Item <src> <dst>` | `Get-Content <src> > <dst>` |

## Quick Encoding Check

If you suspect a file has bad encoding, verify the first bytes:

```powershell
[byte[]]$b = [System.IO.File]::ReadAllBytes("path/to/file"); "$($b[0]) $($b[1])"
```

- `255 254` = **UTF-16LE BOM (BROKEN)** — re-checkout from git
- `239 187 191` = **UTF-8 BOM** — usually OK but strip if possible
- Any printable ASCII (e.g., `34 117` = `"u`) = **Clean UTF-8 (CORRECT)**

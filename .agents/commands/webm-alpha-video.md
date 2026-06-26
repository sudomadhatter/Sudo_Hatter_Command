---
description: Convert green-screen MP4 videos to WebM with true alpha transparency for floating UI elements
---

# /webm-alpha-video — Transparent WebM Generator

Execute the workflow defined in @.agents/workflows/webm-alpha-video.md.

**opencode execution notes:**
- This workflow shells out to ffmpeg. If ffmpeg is not on PATH, ask Don to install it (`winget install Gyan.FFmpeg` or via chocolatey) — do not attempt the install yourself (constitution: ask before installing dependencies).
- Input/output paths come from $ARGUMENTS or by asking Don.
- Output should land in `webapp_images/` or wherever the workflow specifies — do NOT write to the project root.
- Per the constitution's "Clean Workspace Protocol" (Rule 6), never leave ad-hoc files in the project root.

Optional additional input (input MP4 path, output WebM path, color-key tweaks): $ARGUMENTS

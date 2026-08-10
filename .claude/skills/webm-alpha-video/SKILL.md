---
name: webm-alpha-video
description: Convert green-screen MP4 videos to WebM with true alpha transparency for floating UI elements
---

# webm-alpha-video — Transparent WebM Generator

Hand-authored knowledge skill, not a launcher — there is no `/webm-alpha-video` command (retired
SCC-63; this file used to point at a command body that only pointed back at this file). Load it
when the operator asks to convert a green-screen video, or says "webm alpha video" / "transparent
video asset".

**Goal:** process a raw green-screen `.mp4` into a web-optimized `.webm` with a native alpha channel
using FFmpeg, for "floating" UI elements (e.g. an avatar) that need to sit on top of complex
backgrounds (glassmorphism, etc.) without a bounding box. MP4 codecs carry no alpha channel; this
workflow bypasses that limit.

## Prerequisites

FFmpeg must be on PATH. Verify with `ffmpeg -version`. If missing, ASK before installing — never
install a dependency unprompted:
- macOS: `brew install ffmpeg`
- Windows: `winget install --id Gyan.FFmpeg -e --source winget`

## Required inputs

Get all three before running anything:
1. **Input file path** — the source `.mp4`.
2. **Output file path** — ask the caller where the `.webm` should land; it is project-specific
   (e.g. `frontend/public/assets/`, `webapp_images/`). Never write to a repo root.
3. **Exact hex color** of the green screen (e.g. `#27BB36`).

## Step 1 — Run the FFmpeg chromakey conversion

**Parameters:**
- `chromakey=0x[HEX]:0.15:0.02` — first number is the similarity threshold (how aggressive the cut
  is; `0.15` is tight). Second is blend/feathering (`0.02` is slightly soft). If the subject is
  getting erased, lower similarity to `0.10`.
- `format=yuva420p` — adds the alpha-channel structure; this is what makes transparency stick.
- `-c:v libvpx-vp9` — required codec for transparent WebM to render in Chrome/Safari.

macOS / Linux (bash):
```bash
input_file="/path/to/input.mp4"
output_file="/path/to/output.webm"
hex="HEX_CODE"   # no leading #

ffmpeg -i "$input_file" -vf "chromakey=0x${hex}:0.15:0.02,format=yuva420p" \
  -c:v libvpx-vp9 -auto-alt-ref 0 -b:v 0 -crf 28 -y "$output_file" 2>&1 | tail -n 10
```

Windows (PowerShell):
```powershell
$input_file = "path\to\input.mp4"
$output_file = "path\to\output.webm"
$hex = "HEX_CODE"   # no leading #

ffmpeg -i $input_file -vf "chromakey=0x${hex}:0.15:0.02,format=yuva420p" -c:v libvpx-vp9 -auto-alt-ref 0 -b:v 0 -crf 28 -y $output_file 2>&1 | Select-Object -Last 10
```

> **Exit-code note:** the VP9 encoder often reports `Exit code: 1` when the muxer closes the file,
> even on a fully successful conversion. Trust the output file, not the exit code — verify size
> instead (Step 2).

## Step 2 — Verify the output

Confirm the file exists and is a plausible size (> 500KB usually means it worked):
```bash
ls -la "$output_file"          # macOS/Linux
```
```powershell
Get-Item -Path $output_file | Select-Object Name, Length   # Windows
```

## Step 3 — Wire it into the frontend

When adding the `<video>` element in React/Next.js, this shape is required for silent, automatic,
looping playback with no user interaction:

```tsx
<video
    src="/assets/[your_file].webm"
    poster="/assets/[your_fallback_image].png"
    autoPlay
    muted
    loop
    playsInline
    className="opacity-80 object-contain drop-shadow-2xl"
/>
```

**Rules:**
- `muted` and `playsInline` are strictly required — modern browsers block `autoPlay` without both.
- Always provide a `poster` (a static PNG fallback) so the UI doesn't look broken while the asset
  loads.
- Tune `opacity` to the background so the asset reads as part of the page, not pasted on.

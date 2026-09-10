---
name: hevc-alpha-encode-recipe
description: "Transparent video for Safari/iOS is HEVC-alpha and only the MAC can make it. premultiply=inplace=1 is REQUIRED (omitting it ships a green background on iPhone), and alpha_quality — whose error message is a lie — is the free-bytes dial, not resolution."
metadata: 
  node_type: memory
  type: reference
  originSessionId: d0818319-a66a-4b19-b118-dc55584e5558
  modified: 2026-09-08T14:21:20.167Z
---

Alpha video that plays on an iPhone is **HEVC-with-alpha, tagged `hvc1`**. WebKit decodes VP9 but
refuses to render a WebM alpha channel, so a WebM alone means every iPhone sees a still.

**Only the Mac can encode it.** `hevc_videotoolbox` is macOS-only; x265 does not support the
`yuva420p` alpha format ffmpeg would need, and the WSL box has no ffmpeg at all. Homebrew's ffmpeg
carries the encoder but **not** `libwebp` — use `cwebp` for WebP.

The recipe, corrected on 2026-09-08 by a real iPhone (AVCH-141) after 33 measured encodes
(AVCH-143) had concluded the opposite:

```
ffmpeg -c:v libvpx-vp9 -i in.webm -vf "scale=N:N,premultiply=inplace=1" \
       -c:v hevc_videotoolbox -require_sw 1 -pix_fmt bgra \
       -alpha_quality 0.3 -q:v 50 -tag:v hvc1 -movflags +faststart out.mov
```

⭐ **`premultiply=inplace=1` IS REQUIRED — omit it and iOS paints a solid GREEN background.**
`hevc_videotoolbox` tags its alpha *premultiplied*. Feed it straight alpha and Safari
un-premultiplies data that never was, painting whatever RGB is stored where alpha is zero — which in
a chroma-keyed source is the un-keyed plate (measured RGB 35,185,53). `premultiply` forces those
pixels to exactly (0,0,0), so a decoder that ignores alpha paints black instead of green.

⛔ **THE VERIFICATION TRAP THAT CAUSED THE WRONG ANSWER, and it will catch you again.** An SSIM
comparison of ffmpeg's own decode is **structurally incapable** of seeing this: ffmpeg APPLIES alpha
correctly, so it only ever compares correctly-composited output. That is how "premultiply makes it
worse" got measured over 33 encodes and shipped a green iPhone. The question is never *"which
variant scores higher when composited?"* — it is **"what colour is stored where alpha is ZERO?"**

⛔ **`alpha_quality` is the dial; resolution is not.** At fixed `-q:v`, taking it 0.9 → 0.3 saves
~38% of the bytes for 0.001 SSIM; dropping `-q:v` costs 4× that quality for half the saving. Its
`Error setting alpha quality: -12902` is **spurious — the setting takes** (byte counts track the
value monotonically). Its **default is 0**, which silently mushes the mask, so never omit the flag.

⛔ **Serve it as `.mov` / `video/quicktime`, never `.mp4`,** and list it BEFORE the WebM. Safari
picks the WebM if offered first and paints a black box; Chrome (which has decoded HEVC since 2023)
may accept an `.mp4` and render it opaque, but declines the QuickTime container and falls through.

**Verify on Apple's stack, not ffmpeg's** — `AVAssetReader` in `kCVPixelFormatType_32BGRA`, and check
the **mean RGB UNDER fully-transparent pixels is BLACK**, not merely that
`kCMFormatDescriptionExtension_ContainsAlphaChannel` is set. A file can declare alpha, decode with
real feathering, and still carry the green plate underneath. Working guard, which FAILS on the
broken files and passes on the fixed ones: `AGY_AVIATIONCHAT/frontend/scripts/verify-hologram-alpha.swift`
(`npm run verify:holograms`). macOS-only — CI is Linux and cannot run it, so this class of defect is
caught on the Mac seat or not at all.

Related: [[one-pc-windows-and-wsl]] (why this is a Mac-seat job).

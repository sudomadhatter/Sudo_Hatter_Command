---
IsArtifact: true
ArtifactMetadata:
  title: Fix Hero Video Autoplay on iOS
  type: implementation_plan
  date: 2026-07-17
---

# Fix Hero Video Autoplay on iOS

This plan fixes the issue where the hero video does not autoplay or loop on mobile devices (specifically iPhone) in the `B-L-WorldWide` project.

## User Review Required

> [!IMPORTANT]
> The fix includes programmatically forcing `muted = true` and `defaultMuted = true` and invoking `.play()` on mount, which is already present on the `claude/hero-video-autoplay-f7zbcy` branch. We are adding programmatic `loop = true` to guarantee looping on Safari/iOS.
> 
> Once approved, we will merge this branch into `main` and push to origin as explicitly requested by Daniel.

## Proposed Changes

### website

#### [MODIFY] [HeroVideo.jsx](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/Projects/B-L-WorldWide/website/src/components/HeroVideo/HeroVideo.jsx)
- Set `video.loop = true;` inside the programmatic initialization loop in `useEffect`.

## Verification Plan

### Automated Tests
- Run `npm run build` in the `website` directory to verify there are no compilation or packaging errors.

### Manual Verification
- Verify the video elements render properly with correct HTML attributes.

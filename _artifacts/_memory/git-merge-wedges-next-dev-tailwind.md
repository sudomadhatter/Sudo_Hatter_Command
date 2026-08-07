---
name: git-merge-wedges-next-dev-tailwind
description: "A git merge/checkout under a running Next dev server wedges Tailwind's JIT with a stale ENOENT stat, 500-ing EVERY route; the symptom is \"my UI change didn't take effect\" and the fix is a dev-server restart, not CSS."
metadata: 
  node_type: memory
  type: project
  originSessionId: 27c1ed6c-690d-4f25-91b4-b537755e900d
  modified: 2026-07-26T02:52:26.593Z
---

A `git merge`/`checkout` that rewrites files while `npm run dev` is running can permanently
wedge Tailwind's JIT content watcher. It `statSync`s a file in the instant git has it
unlinked, throws `ENOENT`, and **never recovers** — even after the file is back on disk.

Observed 2026-07-25 (AGY, story-21.6 merge):

```
Error: ENOENT ... frontend/src/app/admin/__tests__/admin-login-hardening.red.test.tsx
  at resolveChangedFiles (tailwindcss/lib/lib/content.js:236)
  Import trace: ./src/app/globals.css → ./src/app/layout.tsx
```

`globals.css` fails → `layout.tsx` fails → **every route 500s**, because they all import the
layout. A `.test.tsx` under `src/` is enough: the Tailwind `content` globs scan it.

**Why it fools you:** the browser tab open at the time keeps showing the last good render.
HMR is dead, so no edit can ever reach that tab. It reads exactly like "the fix didn't work"
or a browser cache — and you go hunting the CSS, which is fine. This burned a whole
debugging pass chasing a `md:flex-wrap` change that had never once been served.

**Tell:** if a UI change seems inert, `curl -I localhost:3000/<route>` or drive Playwright at
it BEFORE reading any CSS. A 500 on the main document settles it in one call.

**Fix:** restart the dev server. Nothing else. Prefer Ctrl+C in the operator's own terminal
so the process stays attached to their shell rather than being orphaned in an agent's — unless the
operator explicitly asks you to do it, which overrides this.

Two additions from 2026-07-25 (a second, separate instance):

- **It does not self-heal, and it does not stay small.** That server sat wedged for ~11 hours and rode
  through FOUR merges still 500-ing. Age is no evidence it recovered.
- **⚠️ The dev server serves the MAIN CHECKOUT, not your worktree.** Under this repo's
  worktree-per-story rule that means restarting it proves nothing about the branch you are on — it
  renders the shared checkout's branch (`main` today; `main_debug` at the time of this incident).
  Live-verify AFTER landing, or point a second dev server at the worktree. Not
  knowing this reads as "my fix didn't take", i.e. the exact same false signal as the wedge itself.
  (I also cleared `.next` during that restart, so plain-restart-alone was never isolated — the cache
  clear may well be unnecessary.)

Same shape as [[wedged-backend-fans-out-three-symptoms]] — one wedged long-running process
fanning out into symptoms that all look like application bugs. Check process health first.

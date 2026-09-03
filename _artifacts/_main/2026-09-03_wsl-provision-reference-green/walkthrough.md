# Walkthrough — WSL box brought to reference green (2026-09-03)

## Result

Documented command, run from the AGY root with `backend/.venv/bin/python`
(`-m pytest backend/tests -n auto --dist loadfile -q`):

```
3159 passed, 35 skipped, 895 warnings in 29.06s
```

Before this session the same command failed 40 (every one `403 PermissionDenied`); the emulator
detour earlier today got it to 19. Restoring the gitignored files did the rest — no emulator, no code
change. `35 skipped` matches the Desktop and Mac reference rows exactly.

## What was copied (all from `/mnt/c/Sudo_Hatter_Command`, mode 600 for anything secret)

- lobby `.env`; `docs/migrations/auth_keys/_secrets/master.env`; `.agents/bmad/custom/config.user.toml`; `.opencode/package*.json`
- AGY `auth_keys/{.env,.env.example,service-account.json,librarian-service-account.json}`,
  `frontend/.env.local`, `frontend/.vercel/`, `_bmad/custom/config.user.toml`, `.opencode/package*.json`
- AGY scratch: `_test_scripts/`, `backend/_test_scripts/`, `frontend/_test_scripts/`
- AGY media: `_my_resources/` (27 lesson audio/video, 4.5 GB), `_webapp_images/` (18 MB),
  `backend/__about_video_infographics/` (327 MB), `frontend/public/assets/about/` (101 MB)
- gcloud ADC → `~/.config/gcloud/application_default_credentials.json` (needed the sandbox lifted:
  `~/.config` is outside its write allowlist)

## One mistake, reverted in the same minute

`frontend/.env.production` is **tracked** in AGY (only `.env.production.local` is ignored). I copied
the Windows copy over it on the strength of the bundle carrying a block for it; `git status` showed
` M`, `git checkout -- frontend/.env.production` restored it. Tree clean. The bundle carrying a
tracked file is itself a small defect in `env_master.py`'s discovery (`ENV_FILENAMES` includes
`.env.production`) — noted for the docs ticket.

## Deliberately not copied

`.claude/settings.local.json`, `.claude/scratchpad-root` (Windows paths); `.code-review-graph/graph.db`
(115 MB, rebuilt per machine); `.coverage`, `tsconfig.tsbuildinfo`, `next-env.d.ts`, `out.txt`,
`test-results/`, `*.pre-restore.bak`; `docs/.maps-journal*.jsonl` (per-checkout cache); both dead
Windows venvs (`.venv_stale`, `_venv-rollback-old314`).

## Noise, explained

The post-checkout hook reported a "MEMORY STORE REGRESSION" for two files in `_artifacts/_memory`.
Both live on the epic branch (commits AVCH-102 `4227c9f6`, AVCH-110 `87335d33`), not on `main`; the
baseline was recorded while a worktree had the epic checked out. Not a regression on `main`; it clears
when Epic 24 merges.

## Card finished — the four items that were still open, closed the same afternoon

1. **Python 3.11.** Operator ran the deadsnakes line; venv rebuilt per the companion guide's
   Linux block ([venv-rebuild.log](venv-rebuild.log), pip exit 0; xdist 3.8.0, ruff 0.16.0 pinned).
   Suite re-run on 3.11.15: **`3159 passed, 35 skipped, 927 warnings in 23.56s`**
   ([suite-py311.log](suite-py311.log)) — same totals as the 3.12 run, 5 s faster.
2. **gcloud CLI** 583.0.0 from Google's apt repo; the copied ADC file mints a token
   (`gcloud auth application-default print-access-token` → 257 bytes); project set to `aviationchat`.
   Both gcloud calls needed the unsandboxed retry — `~/.config/gcloud` is outside `allowWrite`.
3. **Keyway** 0.5.3 via `npm install -g @keywaysh/cli` (unsandboxed retry: npm cache is outside
   `allowWrite`), operator logged in; `keyway doctor` → **`5 passed, 1 warnings, 0 failed`**, the
   finished state INDEX step 6c names.
4. **The Linux column** — SCC-384, this lane: `docs/migrations/INDEX.md` gains a `Linux (WSL2 / Ubuntu)`
   column on all 15 rows; the new-machine guide §5 gets the one-block sudo list and the
   firebase-tools warning; the pytest companion gets the WSL row and a Linux line in its rebuild
   block; `terminal-permissions-guide.md` §3.6 records the four sandbox behaviors measured today.

5. **The bundle itself.** `env_master.py` now skips anything git tracks (regression test added, 27/27),
   and the bundle was re-exported on this box: **7 files**, `--verify-only` PASSED. It now carries the
   librarian service account and today's re-issued service account, and no longer carries the tracked
   `frontend/.env.production`. BRKN's `frontend/.env.local` was carried across from `/mnt/c` first so the
   new bundle is a superset of the Windows one. This is the file the Mac restores from.

## Was still open before that — kept for the record

1. `backend/.venv` is Python **3.12.3**; the guide pins **3.11**. Ubuntu 24.04 ships 3.12 only →
   `sudo apt install python3.11 python3.11-venv` (deadsnakes) is the operator's line, then rebuild per
   `python_vytest-updates-other-machines.md`.
2. `gcloud` CLI not installed (ADC file present, so the SDKs work). `sudo apt install google-cloud-cli`.
3. Keyway not installed / not logged in (INDEX step 6c). `npm install -g @keywaysh/cli` + `keyway login`.
4. Migration docs have no Linux/WSL column — the ticket this walkthrough feeds.

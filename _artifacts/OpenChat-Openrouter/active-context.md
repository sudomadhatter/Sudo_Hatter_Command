# active-context — OpenChat-Openrouter

## 1. PRIME

This continuity brief records the cross-machine NVIDIA NIM OpenCode configuration session, started from the home base on 2026-07-23.

## 5. PICK UP

- The approved plan is in `2026-07-23_add-nvidia-api-key/implementation_plan.md`.
- Global OpenCode was upgraded from `1.18.3` to `1.18.4`.
- The maintained repository has an isolated worktree at `Projects/OpenChat-Openrouter/.claude/worktrees/nvidia-nim-model` on `claude/nvidia-nim-model`.
- Commit `addde4e` adds the non-secret `nvidia-nim` provider and `nvidia/nemotron-3.5-nano-30b-a3b` to `opencode.json`. It is landed on `origin/main_debug` and `origin/main`.
- `NVIDIA_API_KEY` is stored in the Windows User environment and was format-validated; never print or commit it.
- The active global OpenCode directory is now a junction to the maintained repository; its former physical directory is preserved as a timestamped backup.
- `opencode models --refresh` completed and lists the custom `nvidia-nim` provider.

## 6. HAND OFF

**Awaiting corrective approval.** NVIDIA's authenticated model catalog does not contain `nvidia/nemotron-3.5-nano-30b-a3b`; it returns 404 both directly and through OpenCode. The endpoint and credential are proven by a 200 response from `nvidia/nemotron-3-super-120b-a12b`. Ultra is listed but currently returns NVIDIA capacity 503.

After Daniel says `approved`, reuse the existing `claude/nvidia-nim-model` worktree to replace the 3.5 Nano entry with the verified Super 120B entry, commit/push/land the one-file correction, fast-forward the primary checkout, and run the exact OpenCode neutral test. Do not run `opencode models --refresh`; Daniel already updated the catalog.

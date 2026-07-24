---
IsArtifact: true
ArtifactMetadata:
  title: Add NVIDIA API key to OpenCode
  type: implementation_plan
  date: 2026-07-23
---

# Enable a verified NVIDIA model in OpenCode

## Goal

Make the verified hosted **NVIDIA Nemotron 3 Super 120B A12B** model selectable and usable in this Windows user's OpenCode installation and in the maintained cross-machine OpenCode configuration. The supplied credential must never be stored in the repository, an artifact, or a configuration file.

## Evidence

- The global OpenCode CLI was upgraded from `1.18.3` to `1.18.4` under the approved plan.
- Even after an official catalog refresh, `opencode models nvidia` reports `Provider not found: nvidia`. This release exposes NVIDIA's catalog only through OpenRouter, not as a native provider.
- NVIDIA documents the new model as `nvidia/nemotron-3.5-nano-30b-a3b`, served through the OpenAI-compatible endpoint `https://integrate.api.nvidia.com/v1` and authenticated with `NVIDIA_API_KEY`.
- The active global config is [opencode.jsonc](/C:/Users/dlohn/.config/opencode/opencode.jsonc); it currently contains only the schema declaration, so adding one provider will not overwrite existing settings.
- The maintained [OpenCode configuration repository](../../../Projects/OpenChat-Openrouter/opencode.json) is clean on `main` and syncs other machines through its [setup script](../../../Projects/OpenChat-Openrouter/setup.ps1), but this machine is not currently linked to it.

## Root-cause findings

- The originally configured `nvidia/nemotron-3.5-nano-30b-a3b` model is absent from the authenticated NVIDIA `/v1/models` catalog. A direct neutral completion reproduces its `404` outside OpenCode, so the failure is not caused by OpenCode.
- The NVIDIA endpoint and credential are healthy: `nvidia/nemotron-3-super-120b-a12b` completed the same direct neutral test with HTTP `200`.
- `nvidia/nemotron-3-ultra-550b-a55b` is listed but NVIDIA currently returns HTTP `503` because its worker request limit is exhausted. It is not a reliable replacement today.

## Revised planned change

1. Store the supplied credential in the Windows **User** environment-variable store as `NVIDIA_API_KEY`.
2. Create an isolated `claude/nvidia-nim-model` worktree from the required `main_debug` integration baseline. Because this repository currently has only `main`, establish `main_debug` from the current clean `origin/main` first.
3. Add a non-secret `nvidia-nim` custom provider to the tracked [opencode.json](../../../Projects/OpenChat-Openrouter/opencode.json). It will use OpenCode's OpenAI-compatible provider adapter, NVIDIA's hosted endpoint, and the environment-variable reference—not the credential itself.
4. Replace the unavailable `nvidia/nemotron-3.5-nano-30b-a3b` entry with the verified `nvidia/nemotron-3-super-120b-a12b` model, retaining its documented 1M-token context window and 16,384-token output limit.
5. Commit only `opencode.json` in the worktree, push the `claude/*` branch, validate the GitHub repository's required secrets/variables, then land the one configuration commit on `main_debug` and `main` as requested for cross-machine sync.
6. Fast-forward the clean local repository to the landed `main`, then run [setup.ps1](../../../Projects/OpenChat-Openrouter/setup.ps1). It will move the existing minimal global OpenCode folder to a timestamped backup (not delete it), create the documented junction to this maintained repository, and install its declared dependencies.
7. Skip catalog refresh because Daniel has already updated OpenCode's models; verify the credential's format without exposing it, verify the configured `nvidia-nim` entry, and run a neutral one-word completion through that exact model.
8. On each other machine, pull the updated repository, run its setup script if it is not already linked, and set that machine's own `NVIDIA_API_KEY` User environment variable. The key cannot and will not be shared by Git.

## Verification

- `NVIDIA_API_KEY` exists at Windows User scope and matches the expected NVIDIA-key pattern, with no value printed.
- The committed GitHub `main` contains the provider configuration but no credential.
- This machine's global OpenCode directory is a junction to the maintained repository; its former folder is present as a timestamped backup.
- No OpenCode catalog refresh is run; Daniel has already completed that update.
- `opencode models nvidia-nim` lists the configured model.
- A neutral `READY` prompt sent through `nvidia-nim/nvidia/nemotron-3-super-120b-a12b` succeeds.
- Confirm the only intended tracked repository change is `opencode.json`, and that it contains no credential.

## Fresh approval required

The earlier approved foundation has completed: OpenCode is upgraded, the key is stored locally, the non-secret provider is committed as `addde4e` on GitHub `main` and `main_debug`, this machine is linked to the shared configuration, and the catalog has been refreshed. The only remaining corrective change is replacing the unavailable 3.5 Nano model entry with the live-tested Super 120B entry, committing and landing that one-file correction, then rerunning the exact OpenCode test. It needs fresh explicit approval before the shared configuration is changed again.

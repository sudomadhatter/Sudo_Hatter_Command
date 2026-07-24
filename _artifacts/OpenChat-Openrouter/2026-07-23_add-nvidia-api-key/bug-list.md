---
IsArtifact: true
ArtifactMetadata:
  title: NVIDIA NIM live-test findings
  type: bug_list
  date: 2026-07-23
---

# NVIDIA NIM live-test findings

## Reproduction

The shared OpenCode configuration selected `nvidia-nim/nvidia/nemotron-3.5-nano-30b-a3b` and sent the neutral prompt `Reply with exactly READY`.

## Findings

1. **Unavailable target model — confirmed root cause**
   - OpenCode returns HTTP 404 from NVIDIA's hosted chat-completions endpoint.
   - Direct NVIDIA checks reproduce the same 404, while `GET /v1/models` succeeds with HTTP 200.
   - The authenticated NVIDIA model catalog does not contain `nvidia/nemotron-3.5-nano-30b-a3b`.

2. **Credential and endpoint are healthy**
   - Direct `nvidia/nemotron-3-super-120b-a12b` neutral completion returned HTTP 200.
   - This proves the configuration path, key, endpoint, and API contract are functional.

3. **Ultra is temporarily saturated**
   - `nvidia/nemotron-3-ultra-550b-a55b` appears in the authenticated catalog.
   - A direct neutral completion returned HTTP 503: NVIDIA reports its worker request limit is exhausted.

## Corrective recommendation

Replace the unavailable 3.5 Nano config entry with the proven `nvidia/nemotron-3-super-120b-a12b` entry, then rerun the same OpenCode neutral completion.

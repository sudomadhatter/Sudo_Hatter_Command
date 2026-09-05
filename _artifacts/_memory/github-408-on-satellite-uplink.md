---
name: github-408-on-satellite-uplink
description: "Operator works from planes on satellite wifi — git push dies with HTTP 408 while reads work; diagnose by pack size, cure by chunked temp-ref pushes or waiting for landing."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 39e92bc8-43a2-4412-b261-42683501d3ef
  modified: 2026-08-10T15:02:24.045Z
---

The operator flies and works over satellite wifi (~750 ms RTT to github.com). On that link `git push`
fails repeatedly with `HTTP 408` / `curl 56` mid-upload while `ls-remote` and small pushes succeed —
GitHub's pack receiver hangs up after ~10 s of upload stall. It is NEVER a hook, gate, or GitHub limit
(2 GB/push): diagnose by comparing a small push vs the failing pack
(`git pack-objects --revs --stdout | wc -c`).

**Cure:** land on real internet (a 0.7 MB pack pushes in seconds), or grind it through: build
deterministic synthetic commits on a scratch ref (`git commit-tree` with FIXED `GIT_*_DATE` so reruns
resume free), each carrying ~6 files of the diff, force-push each with retries, then the real branch
push sends only the commit objects. A "failed" push may have LANDED server-side with the success reply
lost — force-push on the scratch ref makes retries converge instead of dying on non-fast-forward.
Script pattern: `chunk_grind.sh` in the SCC-63 session (2026-08-10). Delete the scratch ref after.

Related: [[one-pc-windows-and-wsl]] (the Mac has no SSH keys — HTTPS is the only transport).

---
name: sudo-tour
description: Guided first run of this system — six stops from an empty clone to a shipped story, doing real work on a real project. Resumable by detecting state, not by counting. Use when the user says "start the tour", "sudo tour", "walk me through this system", "how do I get started", or opens a freshly cloned teaching edition for the first time.
---

# /sudo-tour — command-center launcher

Entry point for the guided first run. It walks someone from a fresh clone to a story that actually
shipped, in six stops.

**Execute now:** read `.agents/commands/sudo-tour.md` (relative to the repo root) and follow it END TO
END. Pass `$ARGUMENTS` through verbatim — a bare number jumps to that stop, empty resumes.

Two things that command gets right and are easy to lose:

- **Resume by detecting state, never by counting.** Check the world — is there a `.env`, a project, a
  board, a done story — and announce where you are picking up and why. Nobody should have to remember
  which stop they were on.
- **A failure is a stop, not an interruption.** If a command fails mid-tour, debug it together. A
  tour that only survives the happy path teaches nothing about a system whose entire point is the
  gates that catch unhappy paths.

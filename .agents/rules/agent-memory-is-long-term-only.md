---
name: agent-memory-is-long-term-only
description: "Agent memory is for long-term facts only: operator preferences, recurring machine and tooling quirks, and standing rulings. Story-scoped findings go in the story file or artifacts; delete story-scoped memories on sight; narrate every write in chat in one line. Load when reading, writing, auditing, or pruning agent memory."
trigger: model_decision
triggers: [memory, remember, save to memory, note for later, MEMORY.md, auto-memory, memory audit]
---

# Agent Memory Is Long-Term Only

Memory holds only what must be remembered for a long time: how Mr. Hatter wants to be worked with,
machine and tooling quirks that recur across projects, and standing rulings. A finding tied to one
story or one fix belongs in that story's file or its `_artifacts/` walkthrough, where the next lane
reads it and where it retires with the story.

> **Operator ruling (2026-09-04, SCC-386):** *"Those should be in the story, not memory that will
> not be used after this story is done. Only keep things we need to remember for a long time — we
> have to clean up and delete memories."*

## The One Test

Before saving ANY memory — auto-memory, manual note, or close-out routing — ask:

> **"Will this still be true and still be useful after this story closes?"**

- **NO** → It is a **story fact**. Put it in the story file (`_bmad/bmm/stories/`), the session
  walkthrough (`walkthrough.md`), or the audit under `_artifacts/`. It stays in the project history,
  informs the immediate follow-ons, and retires cleanly when the story lands.
- **YES** → It is a candidate for memory. Author it concisely following the memory store rules.

## What Qualifies for Memory

Memory is an expensive shared context cost paid by every future session on every platform. Only three
categories earn a permanent home:

1. **Operator preferences and profile**: how Mr. Hatter thinks, directs work, reviews, and
   communicates (the Jobs/Woz division of labor; consequence before mechanism; directness).
2. **Machine and tooling quirks**: persistent toolchain behavior that recurs across stories and
   projects (Windows vs WSL/Ubuntu side differences, `acli` CLI syntax and flag traps, SDK bugs, shell
   quoting traps, permission quirks).
3. **Standing rulings**: durable architectural, testing, or workflow decisions that govern future
   lanes and projects.

## A Measurable Memory Carries Its Own Falsifier (`probe:`)

Long-term is not the same as **permanently true**. `two-machines-mac-and-pc.md` was confirmed by
Mr. Hatter on 2026-08-08, went false when SCC-376 moved the working environment into WSL2 on
2026-09-02, and stayed loaded and trusted for two more days while an agent used it to tell him four
wrong things in one afternoon. Nothing in the suite could tell a memory that is still true from one
that stopped being true — age and shape cannot separate them.

**The law.** A memory whose claim is *measurable* — it names an absolute or `~/` path, a binary, a
version, or a tool's behaviour — **must** carry a `probe:` line in its frontmatter:

```yaml
metadata:
  probe: 'grep -q microsoft-standard-WSL2 /proc/version'
```

**A memory may carry SEVERAL — repeat the key, one per checkable fact.** The runner numbers the
rows (`file.md [2/5]`), so a failure names which claim went false, not just which file.

⚠️ **Write it in SINGLE quotes.** The reader strips the outer quotes and does no YAML unescaping, so
a double-quoted value containing `\"` reaches the shell with its backslashes intact and fails for a
reason nothing in the output explains.

A plain shell command. **Exit 0 means the claim still holds.** No DSL: the probe IS the command you
would type to check by hand, which is the only form that stays honest — an author who cannot type it
cannot write it. `.agents/scripts/memory_probe.py` runs every probe, `test_memory_store.py` goes
**red and names the file** when one fails, and `/smh-memory-audit` lists path-naming memories with
no probe as candidates.

⛔ **AND THE PROBE MUST BE ABLE TO FAIL — this is the one that was got wrong first.** The first cut
of this mechanism shipped 59 probes and the review found **54 of them could not fail**: they were
`test -e <a path git tracks>`, which every checkout satisfies forever. Five unrelated memories shared
`test -e .agents/commands`; four shared `test -e _artifacts/_memory`, the very directory the runner
walks to reach them. The suite printed `59 probe(s) passed` and that number meant nothing — a green
tick on the same failure the mechanism was built to end. `memory_probe.weak_probes()` now refuses
both shapes, and the suite reds on either:

- **not a tracked path's existence** — git guarantees it. Probe what the memory *claims*: the content
  of a file, the identity of a binary, a per-machine artifact git does not carry.
- **anchored to the claim** — the probe must name something the memory's own body names. A falsifier
  wired to something else is a green light with no wire behind it.

**A probe you cannot write is a signal, not a problem.** Most memories are rulings, conventions and
behavioural lessons; those take no probe and must not be given a decorative one. Five of 145 carry a
probe today, and five true probes are worth more than fifty-nine that cannot fail.

Three further constraints, each of which has already cost something:

1. **A probe OBSERVES.** It runs inside the suite, on every machine. Mutating and network shapes
   (`rm`, `mv`, `curl`, `>`, `git push`, `sudo`, …) are refused outright and reported as failures.
   A probe that writes is a bug in the memory, not a test to skip.
2. **Probe what is STABLE, not what is true today.** A commit count, a file count or a timestamp
   changes on its own and would red the suite for a reason no author can fix — and a gate that cries
   wolf is one people learn to skip, which is the disease this exists to cure. Probe existence,
   identity and shape. (`one-pc-windows-and-wsl` deliberately does not probe its behind-counts.)
3. **Never echo a secret to prove it is set.** `${VAR:+SET}`, never `echo $VAR` — a bare echo puts
   the value in a transcript, a scrollback and a log, and it cannot be taken back out.

**A ruling or a preference needs no probe.** "Mr. Hatter chairs the board" is not measurable and
must not be forced into a shell command. The probe is for claims about the world, not about judgment.

## What Never Qualifies (Prohibited in Memory)

The following must **never** be saved to agent memory:

- **Measurements**: benchmark numbers, execution times, character counts, or byte savings from a run.
- **A bug's mechanism**: root-cause explanations of a defect being patched. The fix, its test, and
  the story record capture that permanently.
- **Gate mismatches & temporary failures**: CI mismatches, broken checks, or pipeline failures that a
  ticket is actively fixing (e.g. the Epic 24 CI scope mismatch that AVCH-119 resolves). Saving them
  creates stale noise the moment the fix lands.
- **Story tasks & intermediate notes**: task checklists, in-flight status, or temporary observations.

## The Delete-on-Sight Duty

Story-scoped notes rot into deceptive distractions that cause agents to fight ghost issues months
later.

Whenever you read, review, or audit a memory store (the lobby `_artifacts/_memory/`, local platform
stores like `~/.claude/projects/*/memory/` which symlink into the shared checkout, or project stores):
- If you find a note that is story-scoped, obsolete, or tied to a single resolved fix,
  **delete it on sight** (and remove its entry from `MEMORY.md` in the same commit to preserve
  link↔file integrity).
- Do not amend, soften, or archive temporary facts into permanent memory — remove them. Git history is
  the undo mechanism if anything historical is ever needed.
- ⛔ **Never delete another session's in-flight uncommitted memory** (`AGENTS.md` §7 authorship gate).
  If deleting on an active lane, perform the deletion in your worktree and commit it on the branch; never
  mutate the shared checkout directly.

## The Narrate-Every-Write Duty

Every time an agent writes, creates, or updates a memory file (including automatic memory captured by
platform harnesses), it must:
- **State in chat, in one line, exactly what was saved.**
- This keeps memory generation visible to Mr. Hatter in real time so invalid or story-scoped notes can
  be challenged and pruned immediately.

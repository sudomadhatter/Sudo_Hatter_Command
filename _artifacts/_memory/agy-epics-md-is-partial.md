---
name: agy-epics-md-is-partial
description: "AGY's epics.md and sprint-status.yaml check EACH OTHER — neither alone is sufficient. The YAML wins on status and is the more complete inventory."
metadata: 
  node_type: memory
  type: project
  originSessionId: b80fc075-1753-4842-9946-7a790b19dc98
  modified: 2026-08-02T18:48:21.428Z
---

**Both files must be read together.** Each catches a failure the other cannot:

- **`epics.md` catches work the YAML forgot.** Story `4.27`/FR41 was listed there with **no key in the
  YAML at all** — so no drift check ever fired and closing Epic 4 nearly buried a shipped FR.
- **`sprint-status.yaml` catches epics `epics.md` never described** — and it **wins on status**. It is
  also the more complete inventory: the 8.19–8.23 admin-data wave, the `debug-N` live-testing epics and
  the TEA retrofit exist **only** there.

✅ **Reconciled 2026-08-02** (was: 5 epics undocumented + a ghost section). `epics.md` now covers all 22
epics. Fixed then: sections reconstructed for **10, 13, 14, 15, 16** (created via
`sprint-change-proposal-*.md`, never written up); the **Epic 9 ghost** retired — it described *"Platform
Polish & Evolution"* (9.1 Voice A/B, 9.2 Tech Debt), a superseded plan **never built under that number**,
while the real Epic 9 is **Native-Grade PWA**. That content wasn't lost: **9.1 → absorbed into Story 8.2**,
**9.2 → dispersed into `deferred-work.md`**.

⚠️ **Still true, and the durable lesson:** individual `Status:` lines in `epics.md` rot independently of
the YAML — five were stale at the reconcile, one by **34 stories** (Epic 8 read "Stories 8.1–8.9
planned"). **Use `epics.md` for the *why*, the YAML for the *state*.** Never treat either file's silence
as evidence.

Related: [[agy-epic-keys-rot-silently]], [[recon-reframes-story-scope]], [[settled-decisions-are-not-gaps]].

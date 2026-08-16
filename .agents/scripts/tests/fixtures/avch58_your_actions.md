<!-- FIXTURE — the AVCH-58 `## Your Actions` section, VERBATIM, pre-correction.
     Provenance: Projects/AGY_AVIATIONCHAT @ 9674880d
       _artifacts/_main/2026-08-15_avch-58-migrations-refs/walkthrough.md:210-217

     ⛔ It is VENDORED, not fetched. The sha lives in a DIFFERENT REPOSITORY, so a test in this
     repo cannot `git show` it — a fixture that silently degrades to "the sha is unreachable, so
     nothing was checked" is the empty-input-reads-as-pass shape `tests-must-gate-for-real` bans.
     Copied bytes are the only form of this evidence that survives a fresh clone.

     This is the KNOWN-POSITIVE required by SCC-163 acceptance B1, and it is three rows doing
     three different things — which is exactly why it is worth keeping whole:

       row 1  the banned shape, by name — it asks the operator to CREATE or PLACE a ticket
              ("fold into AVCH-54, or mint its own AVCH key", "board placement is the
              operator's"). MUST be flagged.
       row 2  a settled decision already owned by a live ticket. A real defect — it is not an
              action — but a STATUS NOTE, which SCC-163 acceptance B5 rules out of scope for the
              automated check. MUST NOT be flagged.
       row 3  a status note about branch freshness, made stale by the close-out itself. Same
              ruling. MUST NOT be flagged.

     Zero of the three were operator calls, and `finish` held AVCH-58 on Review Required over all
     three. Corrected post-merge at 3988299c; row 1 became AVCH-61. -->

# Walkthrough — AVCH-58 (fixture excerpt)

## Your Actions

- [ ] Rule on the `.gitignore` symlink defect — fold the one-line fix into AVCH-54 (it hits that lane
      directly), or mint its own AVCH key. Not mine to place: board placement is the operator's.
- [ ] `backend/requirements.txt:59` remains AVCH-55's, still correctly deferred — it is the only other
      live dead reference and it sits on a deployable path.
- [ ] Your local `main` is behind `origin/main`; `epic/AVCH-18-adk-2x-runtime` is behind both. Absorb
      before building on either — a merge under `npm run dev` wedges Tailwind.

# Walkthrough — SCC-360: the Zoo fix (Cheshire Cat · The Gnat · the review gate · verdict receipts)

**Lane:** `chore/SCC-360-cheshire-cat-rename` (consolidated; riders SCC-361, SCC-362, SCC-363)
**Repo:** Sudo_Hatter_Command (lobby)

## What shipped, and why

The AVCH-101 / AVCH-106 audit found the Zoo team was not defying the rules — it was
**out-arguing the prose**. Every violation lived where a rule asked for judgment: the review level
was reasoned down to `quick`, the full suite was skipped by citing the operator's own
parallel-lane concern, ten test-adequacy findings died in one blanket dismissal, a fix was recorded
as applied that was never applied, and a self-run review stamped its own `Verdict: PASS` over a red
standing suite. A cheaper model does not break a refusal; it rationalizes through anything that is
not one. So every part of this lane replaces a sentence with a mechanism.

### Part 0 (SCC-360) — the ENGINEER seat is the Cheshire Cat

`Carpenter` → `😼🔨 Cheshire Cat — ENGINEER`, at every carrier: the seat master, the five sibling
masters that name it in their hand-off text, `zoo-team.md`, both INDEXes, the SOP page, the
twin-parity ledger key, `sync-agents.ps1`'s seat map, and the generated Zoo surfaces. The rename is
cosmetic; doing it across every carrier in one commit is not — a half-renamed seat is how a
generated surface silently resurrects a stock Zoo mode.

### SCC-361 — The Gnat claims the `ask` slug

`🦟🔍 The Gnat — LIBRARIAN`, groups exactly `[read]`. The stock Ask mode carried **no seat law at
all**, so any work routed through it was ungoverned by design — the leak the operator spotted first.
The seat is an unbiased lookup desk: it answers from project evidence and cites where it read, and
it **cannot** write a file or run a command, because the extension enforces mode groups. The
harmlessness is the mechanism, not the wording.

### SCC-362 — review left the seats and became the operator's model-switch gate

② runs to review-ready and stops. The operator switches the model and runs ③ himself
(`/cicd-code-review` / `/smh-code-review`), and ① (`/cicd-create-epic-sprint`,
`/cicd-write-story-tests`) runs on that same reviewing model. **No seat writes a `Verdict:` stamp
any more** — the refusal is in every master. The Queen of Hearts keeps the red phase and
review-readiness; she no longer judges her own team's finished work, which is the sentence that
authorized the self-stamped PASS.

### SCC-363 — a verdict needs a receipt

A new armed **commit-msg** gate (`verdict-receipt.sh` + `VERDICT-ENFORCE` + `verdict_receipt.py`).
A commit that adds `Verdict: PASS` or `Verdict: CONCERNS` to a walkthrough is **refused** unless the
lane carries a real `suite` receipt at the same tree. `FAIL` and `WAIVED` are never gated (recording
bad news must never be harder than recording good news); `[verdict-ok]` logs an auditable bypass;
deleting the flag drops it to warn-only. Registered in `hooks_armed.py` so an ARMED report cannot
omit it.

## Evidence

Suite, after absorbing origin/main (18 commits) into the lane:

```
python3 .agents/scripts/tests/run_all.py                       ->  68/68 files passed   (exit 0)
python3 .agents/scripts/workflow_lint.py --toolkit-only        ->  0 error(s), 0 warning(s) (exit 0)
python3 .agents/scripts/check_maps.py --depth3-only --strict   ->  exit 0
```

The generator agrees with the tree: `sync-agents.ps1 -GlobalsOnly` emitted **6 team seats** into
`.roomodes` and left the worktree **byte-clean**, proving the generated Zoo surfaces are what the
generator produces rather than hand-forged copies.

Conflict resolution on the absorb kept **both sides' facts** in the two ledger files
(`_artifacts/_main/INDEX.md` and the SOP changelog); `docs/doc-graph.md` is generated and was
regenerated rather than hand-picked.

## Your Actions

- [x] Approve the landing — given as the word `approved` (2026-08-31)

Verdict: PASS @ 90ebb15e

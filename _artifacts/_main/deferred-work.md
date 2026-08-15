# Deferred work — the center's judged ride-along ledger

This is the `DEFERRED_WORK` file the code-review engine's caller contract names, for toolkit
lanes (the center is its own caller). **Nothing in this file is owed** (operator ruling
2026-08-15): every entry already passed step-03's relevance gate, carries why it matters and the
lane class it rides, and gets picked up when that lane next opens — or deleted when its reason
dies. No close-out mints a ticket from this file as a pile.

Format per entry: `- <title> [<file>] — <why it matters> · rides <lane class> · from <review>`.

## SCC-160 first live run — re-triage of the SCC-156 + SCC-154 residues (2026-08-15)

- Ctrl-C drains the pool instead of stopping [.agents/scripts/tests/run_all.py] — an
  uninterruptible 88 s run; `cancel_futures=True` is the whole fix · rides the next `run_all`
  lane (folds into proposed Ticket A if minted) · from SCC-156 review #4.
- Zero-file suite prints `0/0` and exits 0 [.agents/scripts/tests/run_all.py] — a 0-file PASS
  receipt could authorize a gate SKIP; trigger exotic today (tests dir must vanish while all
  else works); 2-line floor guard · rides the next `run_all` lane (folds into proposed Ticket A
  if minted) · from SCC-156 review #7.
- `dirty_paths` readback: rename-row and quoted-path parses uncovered
  [.agents/scripts/gate_receipt.py tests] — receipts are cited evidence and the failure
  DIRECTION of a misparse is unverified; 3 cheap cases settle it · rides the next receipts lane
  · from SCC-154 review #7.

# Billing: line items and payments — the spec for THIS change

This is the `STORY_FILE` for one change to `codebase/` in the review engine's negative control
(SCC-129). It specifies line items, payments and totals, and nothing else. Refunds are a separate
change with its own spec (`spec-refunds.md`) — **a reviewer holding this document should not
expect refunds in the diff it is auditing, and vice versa.**

Keeping one spec per change is not bookkeeping: an auditor handed a spec covering work that is not
in front of it correctly reports every unimplemented section as a gap, which is a finding about
the pairing rather than about the code.

## 1. Line items

`load_line_items(raw)` returns the trimmed, non-empty entries of a comma-separated blob. It reuses
the existing `helpers.parse` helper rather than introducing a second parser.

`unit_price(total, quantity)` returns the per-unit price of a line item, rounded to two places. A
quantity of zero is a caller error and **must not** surface as a `ZeroDivisionError` out of the
billing layer.

## 2. Payments

`record_payment(ledger, amount)` adds `amount` to the ledger's running `paid` total and returns
the ledger.

⛔ **A negative `amount` is a caller error, and `record_payment` MUST raise ValueError.** It must
never be clamped, coerced to zero, or silently ignored. A clamped negative payment records a
transaction that did not happen, reconciles to the wrong number, and nothing downstream is looking
for it again — the caller's bug becomes the ledger's bug.

## 3. Totals

`invoice_total(subtotal)` returns what the customer owes with tax **INCLUDED** — the subtotal
plus the tax on it.

## 4. Tests

Every deterministic function added under this spec carries a fast unit test covering its guard
clauses, in the same change that adds it.

## 5. Conventions

Amounts are floats rounded to two places, matching the existing module. That is a stated fixture
convention, not an oversight, and a change here is not expected to migrate it.

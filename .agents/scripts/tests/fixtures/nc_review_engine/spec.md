# Billing: line items, payments and refunds — the spec for the fixture change

This is the `STORY_FILE` for the review engine's negative control (SCC-129). The two diffs beside
it are proposed changes to `codebase/`, and this document is what the engine's **Acceptance
Auditor** audits them against. It is fixture data: no real work is specified here.

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

## 3. Refunds

`refund(ledger, amount)` subtracts `amount` from the ledger's `paid` total. Both a negative amount
and a refund larger than the amount already paid are caller errors and **MUST raise ValueError**,
for the same reason as §2 — a silently absorbed bad refund is a wrong balance nobody notices.

## 4. Totals

`invoice_total(subtotal)` returns what the customer owes with tax **INCLUDED** — the subtotal
plus the tax on it.

## 5. Tests

Every deterministic function added under this spec carries a fast unit test covering its guard
clauses, in the same change that adds it.

## 6. Conventions

Amounts are floats rounded to two places, matching the existing module. That is a stated fixture
convention, not an oversight, and a change here is not expected to migrate it.

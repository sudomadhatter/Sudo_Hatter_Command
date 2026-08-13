# Billing: refunds — the spec for THIS change

This is the `STORY_FILE` for one change to `codebase/`. It specifies refunds, and nothing else.
Line items and payments are a separate change with its own spec (`spec.md`) — **a reviewer holding
this document should not expect them in the diff it is auditing, and vice versa.**

Keeping one spec per change is not bookkeeping: an auditor handed a spec covering work that is not
in front of it correctly reports every unimplemented section as a gap, which is a finding about
the pairing rather than about the code.

## 1. Refunds

`refund(ledger, amount)` subtracts `amount` from the ledger's running `paid` total and returns the
ledger.

⛔ Both a negative amount and a refund larger than the amount already paid are caller errors and
**MUST raise ValueError**. Neither may be clamped, coerced, or silently absorbed: a silently
absorbed bad refund is a wrong balance nobody notices, and nothing downstream is looking for it
again.

## 2. Tests

Every deterministic function added under this spec carries a fast unit test covering its guard
clauses, in the same change that adds it.

## 3. Conventions

Amounts are floats rounded to two places, matching the existing module. That is a stated fixture
convention, not an oversight, and a change here is not expected to migrate it.

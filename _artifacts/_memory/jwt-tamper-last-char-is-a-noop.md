---
name: jwt-tamper-last-char-is-a-noop
description: "Tampering the LAST base64url char of an HS256 signature is a 1-in-943 no-op (it carries only 4 significant bits) — a \"tampered token must 401\" test written that way is flaky; mutate leading chars instead"
metadata: 
  node_type: memory
  type: reference
  originSessionId: fd0be18a-da49-4433-b48f-a3bff6f02bf6
  modified: 2026-07-27T02:55:32.404Z
---

**2026-07-26 (story 21.5 ③, independent pass — the flake fired mid-review).**
`test_sudo_admin_endpoint_401s_tampered_token` built its tampered token as
`token[:-2] + ("aa" if not token.endswith("aa") else "bb")`. An HS256 signature is 32 bytes → **43
base64url chars**, and 43 × 6 = 258 bits, so the **43rd char carries only 4 significant bits** — 16
distinct chars decode to the same final byte. When the mutation lands on such a pair the "tampered"
token decodes to **identical signature bytes**, still verifies, the endpoint returns 200, and the
`assert resp.status_code == 401` fails with no code change involved.

Measured over 50,000 real HS256 tokens: **53 still-valid = 0.106%, about 1 run in 943.** Fix — mutate
the **first** two signature chars, which are fully significant: re-measured **0 / 50,000**.

```python
head, _, sig = token.rpartition(".")
tampered = f"{head}.{('aa' if not sig.startswith('aa') else 'bb')}{sig[2:]}"
```

**Why:** the payload carries `iat`/`exp`, so every run mints a different signature — this is a fresh
dice roll per run, not a stable pass or fail. It sat in the **authorization** gate suite, where a random
red gets blamed on whatever story happens to be in flight. That is exactly the failure
`tests-must-gate-for-real` exists to prevent, and it is invisible to "run it again, it passed."

**How to apply:**
- Never mutate the trailing char(s) of a base64/base64url blob to "corrupt" it. Trailing chars are
  partially padding. Mutate leading bytes, or flip a bit in the **decoded** bytes and re-encode.
- A test that fails once in hundreds of runs will be read as environmental. When a suite-wide run
  produces a failure that passes in isolation and per-file, **compute the failure probability** before
  filing it as flaky-and-unexplained or blaming your own diff — here the arithmetic named the cause and
  proved the story hadn't caused it (`routers/` also collects before `services/`, so the new tests
  couldn't have touched it).

Related: [[red-test-can-die-before-its-assertion]], [[e2e-gate-fiction-test-guardrails]],
[[vitest-full-suite-contends-across-lanes]], [[agy-backend-emulator-e2e-tier]].

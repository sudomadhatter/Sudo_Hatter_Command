---
name: voice-router-entitlement-vs-cost-cap
description: "AGY voice WS routers — the 4030 entitlement gate is PAID-only (igor + sully-spike); the free routers (igor-spike, sully-intro) are ungated but still universally 4029 cost-capped. Ungated ≠ uncapped."
metadata: 
  node_type: memory
  type: project
  originSessionId: aca12155-d5f5-4915-ac9b-e714de4901e5
---

AGY has 4 Gemini-Live voice WebSocket routers. Two entitlement/cost invariants that are
easy to get backwards (they reframed TEA-15 mid-flight and will reframe tea-16/tea-17):

- **Entitlement gate (4030, `reject_if_unentitled`, Story 8.19.9) is PAID-ROUTERS-ONLY** —
  wired into EXACTLY `igor_websocket` (/ws/igor) and `sully_spike_websocket` (/ws/sully-spike).
  The two FREE routers, `igor_spike_websocket` (/ws/igor-spike) and `sully_intro_websocket`
  (/ws/sully-intro), have NO 4030 gate by design — a signed-in but un-entitled user may use them.
  (grep + GitNexus both confirm only those 2 callers.) So there is no "4030 matrix" to extend
  onto the free routers — the meaningful test is the INVERSE: assert they stay free.
- **Cost cap (4029, `check_cost_cap`, Story 11.10) is UNIVERSAL** — fires in ALL 4 routers at
  handshake, pre-Live → zero spend if over cap. Free ≠ uncapped: free sessions also keep a
  mid-session cost-cap watchdog + a hard session-duration watchdog (igor-spike 5 min /
  sully-intro 3 min) + an idle timeout. Daniel's standing constraint: a free/un-entitled user
  must never be able to camp on a Live session and run up an unbounded bill — the 4029 brake
  is what guarantees that, independent of entitlement.

Router auth order: accept → first-message auth (4003, Story 11.16) → [entitlement 4030 — paid
only] → cost cap (4029) → concurrent-session (4001) → api-key guard → Live.

**Why:** the two gates protect different things (who's allowed in vs. how much they can spend)
and are wired to different router sets — conflating them produces tests that assert
non-existent behavior, or a false worry that free = unbounded cost.

**How to apply:** for any voice-router test/change, gate 4030 assertions to igor + sully-spike
ONLY; assert 4029 on all four. When patching in a test, note the import style: `reject_if_unentitled`
is a TOP-LEVEL import (patch in the router's namespace) but `check_cost_cap` is a FUNCTION-LOCAL
import (patch at `backend.services.cost_meter.check_cost_cap` — it re-resolves through the source
module each call). Related: [[test-live-guard-needs-live-marker]], [[tea-retrofit-active-initiative]].

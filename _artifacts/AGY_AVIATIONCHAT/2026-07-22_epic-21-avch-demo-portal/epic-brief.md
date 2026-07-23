# Epic 21 — AvCh Demo Portal (Sales Demo Mode)

**Status:** Brief / pre-story — **Phase 0 already shipped (see below)**
**Date:** 2026-07-22

---

## 0. ✅ Already done — 2026-07-22 (not stories; landed directly)

**Live infrastructure provisioned** (verified against project `aviationchat`):
- School `ACDEMO` "AvCh Demo" created, `max_seats=25`. `TESTPILOT` untouched. **Two schools now exist.**
- Auth accounts created with documented passwords: `demo@aviationchat.org` (`demo1215`), `schooltesting@aviationchat.org`, `solotesting@aviationchat.org` (both `testing1215`).
- `demo@aviationchat.org` registered as `school_admin` bound to `ACDEMO`, `is_owner=False`.

**🔴 Security hole closed.** `admin_credentials/demo@aviationchat.com` had **no `role` field**, so `admin_auth_service.py:118` (`data.get("role", ROLE_SUPER_ADMIN)`) resolved it to **`super_admin`** — and its password was printed on `/about` to every NDA'd visitor. An explicit `role: school_admin` + `school_code: ACDEMO` was stamped on it. It can no longer inherit super_admin.

**`/about` Mission Control CTA removed entirely** (operator decision: the admin panel is shown only in operator-led demos from TESTPILOT, which has real data). Removed the credentials block, the "Access Mission Control" link, both desktop and mobile nav entries, and the orphaned `Play`/`ExternalLink`/`ShieldCheck`/`Link` imports. Epic 21 story 21.9 reclaims that slot for the Sully/Igor cards.

**Stale credential sweep — 8 scripts deleted** (all zero-reference, all hardcoding stale production credentials, two actively dangerous): `backend/{update_demo,update_pass,make_admin,revert_admin,create_user,fix_all_admins,fix_admin_firestore}.py` and `scripts/add_demo_admin.py`. `make_admin.py` granted **super_admin to team@aviationchat.org**; `fix_admin_firestore.py` deleted and recreated the owner credential.

**Fixed rather than deleted:**
- `scripts/create_admin.py` — bootstrap now takes `ADMIN_BOOTSTRAP_PASSWORD` from env (no hardcoded credential), and creates the owner with explicit `is_owner=True, role="super_admin"`. It previously created the account with `1215admin` while *printing* a different password, and left `role` implicit — relying on the very default that caused the demo-account escalation.
- `backend/routers/bug_reports.py` — `_DEMO_ADMIN_EMAIL` → `_DEMO_ADMIN_EMAILS` frozenset covering both addresses (4 call sites).
- `frontend/src/app/admin/page.tsx` — `isDemoEmail()` helper replacing two inline `.com` comparisons.
- `backend/scripts/purge_and_repair_accounts.py` — **the three new accounts were not in the protected-from-deletion allowlist.** A purge run would have destroyed them. Added.

**Verification:** frontend typecheck clean for both edited files; admin suite 18/18; bug-reports suite 22/22 (the demo-denylist test now asserts *every* address in the frozenset, not one hardcoded string); full backend collection 2650 tests, 0 import errors.

**⚠️ Still open — the root cause is untouched:** `admin_auth_service.py:118` and `:300` still default a roleless doc to `super_admin`. All four current records have explicit roles, so nothing is exposed *today*, but any future roleless record silently becomes a full operator. This should fail **closed**. Needs its own story + test — it is an authz behaviour change and this shop is test-first.
**Source:** `/bmad-party-mode` brainstorm — Winston (architect), Amelia (dev), Sally (UX), Mary (analyst), chaired by Daniel
**Next step:** `/sudo-create-epic-sprint` to formalize stories + sprint board + P0–P3 risk scoring

---

## 1. Goal

Give Daniel a controlled way to put a prospective flight school **inside the real product** for ~2 minutes, so they experience three things in order and nothing else:

1. **Sully teaches** them (Voice CFI coach) — 3 questions
2. **Igor examines** them (Voice DPE / checkride) — 5 questions
3. **The Admin Agent grades it** and returns real feedback

Everything else about the platform Daniel explains verbally. The demo is not a product tour.

> **Operator's scope discipline (verbatim):** *"We are over designing this, we can't show all the features of the app. The goal is for them to see how Sully teaches, then feel what a checkride will be like and finish with the graded feedback from the admin. That is all the demo is — the rest I will be explaining to them, we don't need to demo it."*

### Non-goals
- No bespoke sales UI. **The demo mirrors the real product.** *"We are demoing what we already have… we are not creating a fake thing we don't have."*
- **No fabricated results.** The Admin Agent grades what actually happened. We choose hard questions so misses are plausible — if the prospect does well, that's fine too. *"We don't make up things."*
- The **admin panel is NOT demoed from the demo school** — it's demoed from **TESTPILOT**, which has real data.

---

## 2. The two demo modes

| | **Mode A — Master (live demo)** | **Mode B — Prospect (self-serve)** |
|---|---|---|
| Who logs in | Daniel, in the room | The prospect, after signing the NDA |
| Account | `demo@aviationchat.org` | Their own profile, created at `/about` |
| School | AvCh Demo (`ACDEMO`) | AvCh Demo (`ACDEMO`) |
| Limits | **None.** Fresh every time, nothing stored | **Capped + revocable** ($10/account) |
| Access granted by | N/A (it's Daniel's) | Daniel toggles them ON manually |
| Purpose | Live pitch | Link + school code sent to prospect; captures the NDA |

Daniel expects Mode B to be the common path: *"I will not use the master account that often — it will mostly be sending them the link and the school code so I have the NDA captured."*

---

## 3. Account & tenancy model (includes a cleanup)

| Account | Role | School | Purpose |
|---|---|---|---|
| `sudomadhatter@gmail.com` | `super_admin`, `is_owner` | — (global) | Operator. `/sudo_admin`. **Exists.** |
| `team@aviationchat.org` | `school_admin` | `TESTPILOT` | Real-data school portal — **this is what gets demoed** as "the admin panel". **Exists.** |
| `demo@aviationchat.org` | `school_admin` | `ACDEMO` | Daniel's live-demo login **and** his access-control panel. **Must never appear publicly.** *(net-new / migrate)* |
| `schooltesting@aviationchat.org` | student | `TESTPILOT` | Live student profile, **entitled** path. PW `testing1215`. *(net-new)* |
| `solotesting@aviationchat.org` | student | **none** | Live student profile, **un-entitled / solo** path — exercises the beta lock, `BetaLockPopup`, and WS `4030`. PW `testing1215`. *(net-new)* |

> **Both accounts are permanent, not scratch.** Operator, 2026-07-22: *"we need one for testing from a school perspective and one for testing from a solo perspective — they are different user experiences."* School and solo are two distinct product paths, not one path with a flag flipped, so each needs a standing live profile. They also happen to give both sides of the entitlement gate for free, letting the `4030`, default-OFF, and three-state tests in §9 run against real accounts instead of mocks.

**Password for the demo account: `demo1215`** (operator decision, 2026-07-22 — "we will keep it clean").

### ✅ RESOLVED — the demo account is `demo@aviationchat.org` / `demo1215`

Operator, 2026-07-22: *"no .com — we don't have that for the @aviationchat.org emails."* **Every account in this system is `@aviationchat.org`.** There is **one** demo account: it runs the live Sully/Igor demo *and* administers ACDEMO.

That makes the `.com` references **stale or non-existent mailboxes**, and one of them is shipped:

| Source | Stale value | Action |
|---|---|---|
| `/about` `#cta-section` (**shipped UI — on screen today**) | `demo@aviationchat.com` / `1215admin` | Must be corrected or removed (see below) |
| `login_testing_credentials.md` §3 | `demo@aviationchat.com` / `demo1215` | Domain typo — operator to correct (file is in the protected `_my_resources/` area) |
| Story 10.1 seeding + `scripts/add_demo_admin.py` | `demo@aviationchat.com`, PW `1215admin`, `is_owner:false` | Migrate to `.org`; retire `1215admin` and `demo2026!` |

**The shipped `/about` page is advertising a credential on a domain that may not exist.** Worth confirming whether that account is currently reachable at all — if prospects have been handed it, it may already be dead.

### 🚩 Two consequences that hang off it

1. **`/about` currently prints a live credential on screen.** That block *is* the existing "Try the Mission Control Admin" CTA. Since the admin panel is now demoed by Daniel from TESTPILOT, decide: **remove the credentials block entirely, or keep the CTA?** Printing the demo password contradicts "must never appear publicly."
2. **Can one identity be both `school_admin` and student?** `school_admin` lives in `admin_credentials` behind an admin JWT; the student experience needs a Firebase `users/{uid}` profile with progress and a school_code. The same email likely *can* hold both, but it is **unverified**. This is **not demo-specific** — the target buyer is an owner who is also a CFI, so every school sold will need admin-and-user in one identity.

### School
- **Name:** `AvCh Demo` — **Code:** `ACDEMO`
- Strictly separate from `TESTPILOT` (which holds real data we actually use).
- **No `max_seats`.** Control is via per-student access toggle + delete, not seat exhaustion.

---

## 4. What already exists (verified — reuse, don't rebuild)

This is the epic's biggest lever: **most of the "demo unlock" is already built**, because the closed-beta lock *is* a school-code system.

| Capability | Where | Note |
|---|---|---|
| Entitlement == redeemed school code | `backend/middleware/entitlements.py` | `is_entitled(claims)`; `reject_if_unentitled()` → WS close **4030** |
| Redeem endpoint | `backend/routers/entitlement.py` | `POST /redeem-school-code` mints the `entitled` claim |
| School CRUD + seats | `backend/services/schools_service.py` | `schools` collection `{name, code, created_at, max_seats}`; `create_school`, `seed_school`, `redeem_seat`, `get_school`, `normalize_code`. Fail-closed. |
| **Per-school admin portal** | `backend/services/admin_auth_service.py` | `ROLE_SUPER_ADMIN` / `ROLE_SCHOOL_ADMIN`; `school_code` stamped into the admin JWT **only** for a school_admin; codeless school_admin = DENY-ALL |
| Igor + Sully grading | `backend/agents/admin/agent.py` | Teaching agents never grade. `IgorCheckrideGradingResult`, `CHECKRIDE_EVALUATION_PROMPT`, `SullyGradingResult`, `GradingEventWriter` |
| Cost caps | `backend/middleware/usage_guard.py`, `backend/services/cost_meter.py` | `QUOTA_EXCEEDED` path exists |
| NDA signing | `backend/routers/nda.py` | `POST /api/v1/nda/sign` → `nda_signatures/{uid}` + `users/{uid}.nda_signed_at` |
| Deck unlock rule | `backend/routers/lessons.py:81` | `unlocked = state in ("rote_level","application","mastered")` — **seed lessons at rote_level+ and decks unlock naturally** |
| Agent cards | `frontend/src/components/dashboard/AgentCards.tsx` | `SullyLiveCard`, `DpeLiveCard`; `useEntitlement` → `shouldShowLock`; voice WS first-message auth |
| `/about` CTA pattern | `frontend/src/app/about/page.tsx` `#cta-section` | Existing card + `<Link href="/admin" target="_blank">` — the new cards are siblings |

**Consequence:** no bespoke "demo claim" is needed. **ACDEMO is just a school.** Winston retracted his own earlier proposal on this point — *"the demo isn't a different kind of user; it's a school with tighter dials."*

---

## 5. The critical security finding

> **A revoked user currently keeps working for up to an hour.**

`entitled` is a **Firebase custom claim baked into the ID token (~1hr TTL)**. `setCustomUserClaims()` + `revokeRefreshTokens()` do **not** invalidate an already-issued ID token. So "block this user now" is currently a coin flip up to 60 minutes.

**Fix (Winston and Amelia converged independently):** stop trusting the claim for authorization.
- Keep the claim as a cheap **UI hint** (fast paint).
- Make the gate read truth server-side per WS connect: `users/{uid}.school_code` → `schools/{code}` → require exists + `active` + member not revoked. Fail-closed on read error.
- Cost: ~2 Firestore reads **per connect**, not per audio frame. Negligible.
- Model membership as `schools/{code}/members/{uid}` docs with `status: active|revoked` — not an array field. Gives audit trail + `list_members()` for the admin UI for free.

Daniel confirmed this is **a real product security issue, not a demo concern**: *"this is a critical security issue for the actual app anyway — we will have different schools and they can not blend data from another school."*

Mid-session eviction of a *live* socket is **out of scope** — Daniel: *"as long as there is already a built in timer for the session… once the session ends then they can't log back in is ok."*

---

## 6. Story breakdown

### Phase 1 — School tenancy & access control *(real product capability; demo is its first customer)*

> This phase stands alone as product value. It could ship as its own epic if you want it decoupled from the demo.

- **21.1 — Per-student access toggle, default OFF.** New student redeeming a school code lands in `no access granted`; the school_admin must manually toggle them ON. *This is the primary anti-code-sharing gate* and applies to every school we sell.

  > 🔴 **This story introduces a THIRD user state the product does not have today.** School and solo are genuinely different user experiences (operator, 2026-07-22), and default-OFF splits the school path in two:
  >
  > | State | Has code? | Access | What they should see |
  > |---|---|---|---|
  > | **Solo pilot** | No | Premium agents locked | Existing `BetaLockPopup` → *"join the waitlist"* → `/earlyaccess`. Chuck + Mrs. Coleman stay open. |
  > | **School member, toggled OFF** | **Yes** | Premium agents locked | ⚠️ **NEW — no UX exists.** |
  > | **School member, toggled ON** | Yes | Full access | Normal product |
  >
  > Falling through to the waitlist popup for the middle state would be **wrong and confusing**: that student *has* their school's code — their instructor simply hasn't switched them on. Telling them to "join the waitlist" reads as a broken redemption and will generate support noise on day one of every school we onboard. This state needs its own copy, something like *"Your instructor hasn't granted you access yet."* **Scope this as part of 21.1, not an afterthought.**
- **21.2 — Immediate revoke.** Server-side membership check replaces claim-trust (§5). Acceptance test that must fail against today's code first: **valid `entitled` claim + revoked membership → DENY**.
- **21.3 — Delete a student profile/data.** Housekeeping so revoked names leave the list. **NDA record is unaffected and survives.**
- **21.4 — Change a school code.** Rotating the code auto-updates all currently-*active* students so they aren't locked out.
- **21.5 — NDA vault in `/sudo_admin`.** NDA records kept in their own store, findable and **downloadable by Daniel at any time** for his records. Independent of student deletion.

### Phase 2 — The demo tenant

- **21.6 — Stand up AvCh Demo + fix the account model.** Create `ACDEMO`; create `demo@aviationchat.org` as its `school_admin`; create `testing@aviationchat.org` (student, `TESTPILOT`); **resolve the `demo@aviationchat.com` two-identity conflict** and stop printing a real credential on `/about`.
- **21.7 — Demo profile seed (idempotent).** Lessons at `rote_level`+ so decks unlock; enough genuine progress that `igor_unlocked` opens **naturally — no bypass flag**. Believable to an expert CFI: a mid-training student, uneven strengths, not a finished account.
- **21.8 — Master demo mode.** The demo account runs unlimited, stores nothing, fresh every session.
- **21.8b — 🔴 Quarantine demo data from the self-learning pipeline.** *(Operator's stated "big threat" — highest-value story in the epic.)*

  Demo traffic must **never** reach the Evolution Engine or the `/sudo_admin` learning surfaces. Daniel: *"I don't want the messy broken data mixing in with the things we are trying to learn and develop the self-learning with. That is the big threat I want to avoid — I don't care how."*

  Contamination surface (verified to exist):
  `backend/services/evolution/nightly_overseer.py` (4 AM Trap Distillation + Golden RAG Discovery), `evolution/reward_service.py`, `evolution/affinity_service.py`, `evolution/dag_discovery_service.py`, `evolution/trap_distillation_prompt.py`, `backend/services/acs_ledger_service.py` (RKP Teaching Ledger), `backend/services/prebunk_service.py`, `backend/services/curriculum_graph_service.py`, and the grading-event writes in `backend/agents/admin/agent.py`.

  **Exclude at the WRITE boundary, not the read boundary** — stamp `school_code` on every evolution-feeding record and refuse to write them for a school flagged `demo: true`. Read-side filtering means every present and future consumer has to remember to filter; one forgotten query silently poisons the learning corpus. Structural, not conventional.

  Noise *inside* the ACDEMO school portal is explicitly acceptable ("if the noise doesn't break anything that is fine") — the requirement is only that it never crosses into global learning or `/sudo_admin`.

### Phase 3 — The demo experience

- **21.9 — `/about` "Try Sully" / "Try Igor" cards.** Siblings to the existing Mission Control CTA. Open a **new tab**; a popup asks for the **school code given by the AviationChat Team**. *No auto-login* (see §7).
- **21.10 — Demo question sets + agent wrap behavior.** 3 Sully / 5 Igor, **editable without a redeploy**. After the last question the agent stops offering interaction: Sully soft-closes; **Igor says the demo is complete and that it is being graded.** No forced socket close — the existing session timer tears down.
- **21.11 — Per-account hard cap: $10.** Wire to the existing `cost_meter` / `usage_guard`; a cap breach must surface gracefully, never as a raw `QUOTA_EXCEEDED` in front of a prospect.

---

## 7. Decisions locked

| # | Decision | Rationale |
|---|---|---|
| 1 | School = **"AvCh Demo"**, code **`ACDEMO`** | Operator |
| 2 | **No auto-login.** New tab + school-code popup | Daniel: *"it can be a new tab and we just tell them to use the school code given to them by the AviationChat Team."* Removes the whole `/api/demo/session` + nonce + custom-token path from scope, **and dodges the `signInWithCustomToken` landmine** (Firebase auth persistence is per-origin, not per-tab — auto-login in a new tab would have logged Daniel out of his own account mid-pitch) |
| 3 | **Revoke, not block.** Plus separate delete-for-housekeeping | Revoke kills API/code access; delete removes the profile from the list. NDA is preserved independently |
| 4 | **New students default to NO access** | The strongest gate against a shared school code |
| 5 | **3 Sully / 5 Igor** questions | Teaching is slower; the checkride needs more surface to grade |
| 6 | **Soft wrap**, not a hard cut | Agent announces the demo is complete; Igor adds that grading is running |
| 7 | **$10 per-account cap** | Session should never exceed ~10 min ⚠️ *see open item* |
| 8 | **No `max_seats` on ACDEMO** | Control via toggle + delete instead |
| 9 | **Real grading only** | *"We are not making up results… we'll just choose hard questions so they can miss some."* |
| 10 | Admin panel demoed from **TESTPILOT** | ACDEMO will never hold real data worth showing |
| 11 | v1 skips abuse hardening for the master path | Threat model is "Daniel's laptop." Mode B is gated by NDA + code + manual toggle + cap. **Write this boundary into the story so nobody over-hardens it.** |

---

## 8. Open items — status after operator review 2026-07-22

| # | Item | Status |
|---|---|---|
| 1 | **$10 per-account cap** | ✅ **Accepted.** Still un-measured against real `cost_meter` records; operator is comfortable. Worth a sanity read before the constant is frozen, not a blocker. |
| 2 | **Demo data polluting analytics / self-learning** | ✅ **Resolved into story 21.8b.** Noise inside the ACDEMO portal is acceptable; crossing into `/sudo_admin` or the Evolution Engine is not. |
| 3 | **Demo account domain (`.com` vs `.org`)** | ✅ **Resolved — `.org`.** All system emails are `@aviationchat.org`; `.com` does not exist. Demo account = `demo@aviationchat.org` / `demo1215`. All `.com` references are stale and must be migrated — including the one **currently shipped on `/about`**. |
| 3b | **One identity as both `school_admin` and student** | 🚩 **OPEN — unverified.** Not demo-specific; the owner-CFI buyer needs it too. |
| 3c | **Fate of the `/about` credentials block / Mission Control CTA** | 🚩 **OPEN.** Admin panel is now demoed from TESTPILOT; printing the demo password contradicts "never appear publicly." |
| 4 | **Sully's entry point** | ✅ **Resolved.** A single **demo lesson**, visible only when accessed from the demo school account, plainly labelled as a demo lesson. Operator: *"don't over engineer it."* |
| 5 | **Igor question clustering** | ✅ **Resolved — 2 sections.** |
| 6 | **Can the grader handle a short run?** | ✅ **Resolved — yes, verified. The earlier risk flag was wrong.** `IgorCheckrideGradingResult.per_rkp_assessments` is a `List[RKPAssessment]` with an empty default; verdict derives from `failed_areas` / `failed_lesson_ids`. **No section or question count is hardcoded anywhere in the grader** — it grades whatever RKPs it is handed. Frontend agrees: `CheckrideDebrief` `.map()`s over `section_results` and `summarizeSections` already handles the empty case. Nothing to design around. |

---

## 9. Test posture

Full ATDD — Daniel: *"We will build this story the full way with all testing and stories."*

Highest-value seams:
- **The money test:** valid `entitled` claim + revoked membership → **DENY**. Write it red against today's code.
- `reject_if_unentitled` → 4030 for: school missing, school inactive, member revoked, no `school_code`. One parametrize.
- Fail-closed: Firestore read raises → DENY.
- Default-OFF: newly redeemed student cannot open a voice WS until toggled ON.
- Cross-tenant: an `ACDEMO` school_admin can never read `TESTPILOT` students (and vice versa).
- Grading: a 5-question Igor transcript produces an `IgorCheckrideGradingResult` and `GradingEventWriter` writes — assert *that it graded*, not any particular score.
- E2E (`/sudo-e2e`, emulator-backed): `testing@aviationchat.org` → dashboard → Sully unlocked → WS accepted; then revoke → next connect → 4030.

> Run backend tests with `backend\.venv\Scripts\python.exe -m pytest`. Bare `python` is the drifted global 3.14 and produces false missing-dependency failures.

<!-- CHECKPOINT id="ckpt_mrwmksx6_lq0d3u" time="2026-07-22T21:59:32.970Z" note="auto" fixes=0 questions=0 highlights=0 sections="" -->

<!-- CHECKPOINT id="ckpt_mrwopyqf_4q2o4l" time="2026-07-22T22:59:33.015Z" note="auto" fixes=0 questions=0 highlights=0 sections="" -->

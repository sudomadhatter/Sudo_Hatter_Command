---
name: agy-hanger-talk-is-the-free-tier
description: "/hanger-talk is AGY's deliberate free-value surface — no paywall, free ACCOUNT required by design. It delivers FR41; don't re-file it as an unbuilt story."
metadata: 
  node_type: memory
  type: project
  originSessionId: b80fc075-1753-4842-9946-7a790b19dc98
  modified: 2026-08-02T18:38:07.729Z
---

`frontend/src/app/hanger-talk/page.tsx` **is** FR41 / Story 4.27 ("Free Learning Materials Page"),
delivered. Confirmed 2026-08-02 — it had no story key anywhere and looked unbuilt.

- Modules grouped by ACS Area (FR41-A); per-lesson audio + video download buttons (FR41-B).
- `handleDownload` (`components/dashboard/Library.tsx:110`) builds a **direct public Firebase Storage
  URL with no auth token** — so FR41-C ships *literally*.
- **No paywall on this surface:** no `entitled` claim, no 4030 gate. Deliberate free value — students
  get the full lesson audio/video library without paying, to earn confidence before any purchase.

**The one clause superseded:** FR41 says "no login required." The page requires a **free account**
(`useAuth` → redirect), because it reads `rkp_manifests` client-side and Firestore rules require an
authenticated read. **Operator ruling 2026-08-02:** *"you can't get into the main page of the app
without making an account, this is by design"* — **free means no PAYMENT, not no account.** Requiring
the free account also *serves* FR41-D (conversion funnel) better than anonymous access would.

**Do not re-open this as a gap.** Going anonymous would mean opening `rkp_manifests` to unauthenticated
Firestore reads — a real security-surface change, not polish, and not currently wanted. Ruling is
recorded under FR41 in `prd.md`. Note `/flight-briefings` is a *different*, auth-gated video page.

Related: [[settled-decisions-are-not-gaps]], [[recon-reframes-story-scope]], [[agy-entitled-claim-has-no-provenance]].

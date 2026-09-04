# Adviser Board Session — Oral Readiness Brownfield Direction

**Date:** 2026-07-21  
**Status:** Closed by Daniel  
**Scope:** AviationChat checkride-oral practice as the first vertical for a scalable self-learning assessment system.

## The direction selected

The product should begin as a permissionless, high-value learning loop:

> Short spoken diagnostic → clear private gap map → one targeted practice loop → retest → improved readiness brief → optional CFI/outcome confirmation.

The student is not promised a pass prediction. They receive credible, explainable evidence of what they have demonstrated aloud, what remains uncertain, and the next practice action.

The customer-facing artifact may be called the **Readiness Brief**. “Oral Fitness Record” remains a strong internal/product concept, but should be tested for student language.

## Ideas Daniel selected

1. **Admin Agent evidence scale**
   - Use the Admin Agent’s authoritative grading evidence to measure spoken preparedness.
   - Retain full / partial / none credit, articulation quality, failed/remediated status, recency, scope coverage, and source evidence.
   - Treat this as a read-only, versioned readiness projection—not as a second grade.

2. **Authority + competency graph + scenario generator + spoken assessment + evaluator + intervention policy + governed outcome experiment**
   - This is the macro business architecture for a scalable self-learning education system.
   - Aviation is the proving ground, not the limit of the company.
   - Do not build the complete generic platform first; extract and formalize the contracts through this narrow AviationChat vertical slice.

3. **Permissionless first-value exchange**
   - A new student can record one short oral answer without an instructor or school integration.
   - AviationChat immediately returns an understandable gap map and one next practice action.
   - The resulting private record gives the learner a reason to return, improve, and voluntarily share—not merely consume a novelty voice feature.

4. **Checkride countdown in the Flight Status drawer**
   - Add a display-only countdown from the existing validated checkride date.
   - Make it optional, editable, and non-shaming for missing or elapsed dates.
   - Once readiness evidence exists, pair the date with evidence freshness and a single next action rather than a fear-based score.

5. **Student-owned record and controlled CFI handoff**
   - Private by default.
   - The student can share a limited, expiring, revocable Readiness Brief with a named CFI.
   - Schools remain limited to their existing narrow advisory readiness state and allowlisted weak areas.

## What the product should say

The learner promise:

> Practice the oral, see what you can defend, and know the next useful step before your checkride.

Recommended front-door language:

> Practice the oral before it counts. Speak through a short scenario, get a clear next step, and begin your private readiness record.

Avoid: pass prediction, AI evaluation, adaptive engine, readiness score, or language that labels the learner as failing.

Use: “evidence still needed,” “building evidence,” “recent evidence,” and “bring these questions to your CFI.”

## Brownfield implementation sequence

1. **Countdown first**
   - Add it to the existing Flight Status drawer.
   - Use the existing profile checkride date.
   - No effect on progression, grading, or readiness.

2. **Readiness contract before code**
   - Define permitted source events, deterministic calculation rules, coverage and freshness policies, uncertainty states, model versioning, snapshot source pointers, and explicit non-goals.
   - The model cannot write grades, change progression, change checkride state, or widen school-readiness data.

3. **Read-only oral-readiness projection**
   - Compute from existing Admin Agent grading events and full Igor checkride state.
   - Initially use a narrow evidence set: RKP/area credit, articulation evidence, failed/remediated state, recency, completed-session coverage, and model version.
   - Return states such as: insufficient evidence, building evidence, current evidence with active gaps, and stale evidence—not an unqualified readiness percentage.

4. **Separate existing score from readiness**
   - The present “Assessed Readiness Score” is actually the learner’s best historical Igor performance.
   - Relabel it as **Best Igor Performance** (or equivalent) and show the new readiness projection beside it, with a plain-language explanation of the difference.

5. **Readiness Brief**
   - Private student view: demonstrated areas, thin/missing evidence, concise feedback, recency, prioritized next step, and source/date.
   - Share view: selected CFI sees only strengths, current focus areas, recency, questions to discuss, and selected next actions.
   - No raw transcripts, full behavioral notes, detailed score history, or private record by default.

6. **One bounded free spoken diagnostic**
   - Reuse the existing server-enforced entitlement pattern.
   - It is one complete short loop, not a free full checkride.
   - It cannot alter Igor state, mastery, eligibility, school visibility, or an exam-origin grade.
   - Use a realistic scenario, a meaningful follow-up, one corrective re-attempt if validated, immediate feedback, and one next action.

7. **Governed calibration experiment**
   - Measure baseline diagnostic → targeted practice → retest.
   - With separate consent, compare to blinded CFI mock-oral ratings and real outcomes.
   - Use results to calibrate the readiness model by cognitive-demand type before expanding scenario generation or claiming prediction.

## Non-negotiable safeguards

- Admin Agent remains sole authority for full Igor checkride grading.
- A readiness projection is derived, versioned, reproducible, and does not mutate append-only grading events.
- Sparse or stale evidence must fail closed to an honest uncertainty state.
- Voice diagnostics are formative; they cannot acquire hidden authority.
- Diagnostic audio, transcript, feedback, saved summaries, projections, and shared artifacts need separate retention/deletion rules.
- CFI sharing requires preview, named recipient, exact field scope, expiry, revocation, and access audit.
- Research contribution is an independent opt-in with no service penalty for refusal.
- Existing school readiness stays narrow; do not route raw oral evidence or private brief detail into it.
- Readiness must never be used as a CFI, school, growth, or intervention performance target.
- Countdowns must have a hide/disable path and be monitored for anxiety-driven, repetitive low-value practice.

## Measures that matter

- Time to first useful calibration.
- Diagnostic completion.
- Completion of the first recommended practice action.
- Seven-day return to spoken practice.
- Baseline-to-retest improvement by cognitive-demand type.
- Student confidence/clarity about the next step before and after the loop.
- Voluntary Readiness Brief shares.
- Calibration with consented CFI mock-oral judgments.
- Cost per useful diagnostic and abuse/cap signals.

Do not treat time-in-app, practice volume, shares, or a green-looking state as competence.

## Decisions still needed

1. Can the initial diagnostic include one corrective re-attempt so the learner leaves with demonstrated progress rather than only a deficiency?
2. May students share a Readiness Brief directly with a named CFI outside school membership, or must sharing follow school policy?
3. Which learner-facing term tests best: “Readiness Brief,” “Oral Fitness Record,” or another plain-language label?
4. What definitions make evidence “current,” “scope-wide,” and “sufficient” for the first readiness states?


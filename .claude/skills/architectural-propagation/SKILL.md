---
name: architectural-propagation
description: "Grep-audit checklist for propagating architectural invariant changes across documentation. Use when the user says 'run propagation audit' or after any story that modifies Firestore paths, agent I/O contracts, state fields, SSE events, or structured output schemas."
---

# Architectural Invariant Propagation Audit

> **When:** Any story or task modifies an architectural invariant — Firestore paths, agent inputs/outputs, state field names, UI trigger names, structured output schemas, or session lifecycle patterns.
>
> **Who:** The Dev Agent executing the change. This is NOT optional.

## The Problem This Solves

Architectural decisions are documented across many files: component specs, architecture decision tables, active-context pitfalls, frontend-sse pitfalls, implementation artifacts, and stories. When an invariant changes in ONE document, the old value becomes a "ghost" in the others. Future agents grep these files and hallucinate V1 patterns into V2 code.

## Required Propagation Audit

After implementing any architectural change, the Dev Agent MUST run a grep audit before closing the story:

### Step 1: Identify Changed Terms
List every term, path, field name, or pattern that changed. Example:
- `sessions/{session_id}/lesson_plan` → `users/{uid}/lesson_plan_cache/{lesson_id}`
- `current_attempt` → `attempt`
- `module_content` → `RKPManifest + InvestigationDossier`

### Step 2: Grep Audit
For EACH changed term, search across ALL documentation surfaces:

```
_bmad-output/component-specs/
_bmad-output/planning-artifacts/
_bmad-output/active-context/
_bmad-output/implementation-artifacts/
_bmad/bmm/stories/ (open stories ONLY — Done stories are historical)
```

### Step 3: Fix or Annotate
- **Component specs, architecture docs, active-context:** FIX the old term immediately.
- **Open/In-Progress stories:** FIX the old term immediately.
- **Done stories:** DO NOT EDIT the story body. If a Done story contains a stale term that future agents might grep, add a `> [!WARNING] SUPERSEDED` callout at the top of the story file noting which terms are now stale.

### Step 4: Pitfall Section Hygiene
When updating a "Known Pitfalls" section in any component spec:
- **REVISE existing pitfalls** if the underlying architecture has changed. Do not just append a contradicting new entry.
- **Date-tag updates** with `(Supersedes: YYYY-MM-DD)` so the revision trail is visible.
- **Delete pitfalls** that are no longer relevant.

## Verification Gate

The story's Dev Agent Record MUST include a `Propagation Audit` field:

```markdown
### Propagation Audit
- Searched terms: [`old_term_1`, `old_term_2`]
- Files updated: [list]
- Files skipped (historical): [list]
```

If this field is missing, the story does NOT satisfy the Definition of Done.

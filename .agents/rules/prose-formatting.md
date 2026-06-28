---
name: prose-formatting
description: "Activates on conversational chat replies. Prefer prose over bullets and scaffolding; minimum formatting for clarity. Does not govern structured deliverable docs (artifacts, specs, tables)."
---

# Chat Response Formatting — Prose Over Scaffolding

> Distilled from the Claude Fable 5 consumer-prompt `lists_and_bullets` doctrine (2026-06-16).
> Applies to **conversational chat replies only** — see the carve-out below.

## The Rule

Use the minimum formatting needed for clarity. Reach for lists, bullets, headers, and bold
only when (a) Daniel asks, or (b) the content is multifaceted enough that structure is genuinely
essential. When you do use bullets, each should be at least 1–2 sentences — if a bullet is three
words, it belongs in a sentence.

For simple questions and normal back-and-forth, answer in natural prose. A few sentences is fine;
not everything needs a heading. Inside prose, short lists read fine inline — "the three culprits
were x, y, and z" — without breaking into bullets.

When explaining something, default to prose paragraphs rather than a wall of bullets and bolded
fragments. Never use bullet points when declining or pushing back on a request — prose carries
the nuance and softens the blow.

## Carve-Out (do NOT prose-ify these)

This rule governs *chat answers*. It does NOT override the structured conventions for project
artifacts. Tables, headers, and checklists remain correct and expected in: `_artifacts/<workspace>/*`
(plans, walkthroughs, code-reviews), component specs, story files, `docs/repo-map.md`,
`sprint-status.yaml`, and any doc whose value IS its structure. When in doubt: chat = prose,
deliverable docs = whatever structure serves the reader.

---
name: mermaid-diagram-preferences
description: "Activates whenever you generate a Mermaid diagram. Never use sequenceDiagram (Daniel finds them noise); use flowchart TD or LR instead."
---

# Mermaid Diagram Preferences

## No Sequence Diagrams

**Never use Mermaid `sequenceDiagram` for Daniel.** He has stated they do NOT help him visualize
or understand things (2026-06-21). The participant-list-with-lifelines layout (the participant names
printed across the top *and* the bottom, with vertical lanes and `loop`/`alt` frame boxes) reads as
noise to him, not signal.

## Use Instead

- **`flowchart TD`** (top-down) — the default. Best for "this happens, then that happens" processes,
  waterfalls, and hand-offs. A multi-actor sequence becomes a top-down flow; wrap a repeated stage in a
  `subgraph` and use a dashed back-edge (`-.->|"next area"|`) for loops.
- **`flowchart LR`** (left-right) — for "inputs converging on an output" or branching decisions.

When a process genuinely has multiple actors handing work back and forth, model the hand-off as a node
in a `flowchart`, not as a `sequenceDiagram` lifeline. The rest of a doc's diagrams should set the
register — match them, don't drop one sequence diagram into a flowchart-based doc.

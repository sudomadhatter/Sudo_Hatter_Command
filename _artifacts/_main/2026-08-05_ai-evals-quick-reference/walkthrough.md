---
IsArtifact: true
ArtifactMetadata:
  title: AviationChat AI evaluations quick reference walkthrough
  type: walkthrough
  date: 2026-08-05
---

# Walkthrough — AviationChat AI Evaluations Quick Reference

Status: complete. Documentation-only session; no application code, dependencies, configurations, external services, or paid model evaluations were changed or run.

## Task Checklist

- [x] Assess AviationChat's current AI and voice evaluation layers.
- [x] Research current ADK, Gemini Live, Vertex judge-evaluation, and OpenEvals capabilities.
- [x] Create a plain-language quick reference with Mermaid diagrams.
- [x] Verify the document contains two Mermaid flowcharts and no unescaped ampersands.

## Evidence

| Requirement | Evidence |
|---|---|
| Explain the current testing posture | The guide documents L1 through L4, inactive ADK evalsets, the L3 harness, and the voice-session gap. |
| Explain how to start AI and voice evaluation | The guide provides an ordered setup backlog and a staging voice-replay flow. |
| Use helpful Mermaid diagrams | Two `flowchart TD` diagrams depict the evaluation layers and native-audio replay loop. |
| Place the document in quick reference | `_my_resources/_quick_reference/agy_aviationchat_ai_evaluations.md` was created. |

Static verification: passed — document exists, contains 2 Mermaid blocks, and contains 0 ampersands.

## Suite Ledger

| Scope | Command | Result | Why |
|---|---|---|---|
| Documentation validation | PowerShell static checks | PASS | Confirmed document existence, Mermaid block count, and Mermaid escaping rule. |

## Your Actions

- Read the [AI and voice evaluation guide](/C:/Sudo_Hatter_Command/_my_resources/_quick_reference/agy_aviationchat_ai_evaluations.md).
- When ready, direct the next setup story: activate the ADK golden evalsets and establish the current behavioral baseline.

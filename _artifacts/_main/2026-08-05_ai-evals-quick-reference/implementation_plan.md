---
IsArtifact: true
ArtifactMetadata:
  title: AviationChat AI evaluations quick reference
  type: implementation_plan
  date: 2026-08-05
---

# Implementation Plan — AviationChat AI Evaluations Quick Reference

## Goal

Create a concise, plain-language reference document for Daniel that explains AviationChat's current AI and voice testing posture, the recommended evaluation approach, and the practical first setup work.

## File to create

- `C:/Sudo_Hatter_Command/_my_resources/_quick_reference/agy_aviationchat_ai_evaluations.md` — new quick-reference guide. It will include verified current findings, links to official ADK, Gemini Live, Vertex AI, and OpenEvals sources, plus two Mermaid flowcharts.

## Execution

1. Explain what AviationChat already tests and distinguish deterministic L1 tests, inactive ADK L2 evals, advisory L3 judge evals, and human L4 review.
2. Explain why OpenEvals is a useful future reference but not the first dependency to install.
3. Show the recommended evaluation loop and a native-audio voice replay flow with Mermaid flowcharts.
4. Give an ordered, non-implementation setup backlog: activate ADK golden evalsets, rebaseline and calibrate the judge, then add a staging-only voice replay suite.
5. Verify all Mermaid syntax against the workspace standard and confirm the document contains no secrets or production changes.

## Verification

- Review the document for consistency with the observed repository state.
- Confirm the diagrams use `flowchart`, quoted complex labels, and no unescaped ampersands.
- This is documentation-only work; no application code, dependencies, configurations, tests, or external services will be changed or run.

## Open questions

None. The document will record the recommended path without committing the project to a new vendor or test framework.

---
description: >
  Comprehensive guide for testing ADK agents in AviationChat-AGY using the ADK 1.26.0 evaluation framework.
  Covers: adk web UI testing, built-in evaluation framework (.test.json, .evalset.json), evaluation criteria,
  User Simulation with Personas, pytest integration via AgentEvaluator, adk eval CLI, and prompt iteration workflows.
  Use when: testing agents, evaluating prompts, debugging tool calls, building eval sets, or running agent evaluations.
---

# ADK Testing & Evaluation Patterns (v1.26.0)

**Skill Type:** Development Workflow  
**Domain:** AviationChat-AGY  
**ADK Version:** 1.26.0  
**Use When:** Testing agents, evaluating prompts, debugging tool calls, building eval sets, or running CI/CD evaluations

---

## 1. Testing Architecture Overview

ADK 1.26.0 provides **three testing layers**:

| Layer | Tool | Best For |
|-------|------|----------|
| **Interactive** | `adk web` | Prompt iteration, debugging, building eval sets |
| **CI/CD** | `pytest` + `AgentEvaluator` | Automated regression tests |
| **Batch Eval** | `adk eval` CLI | Running evalsets from command line |

---

## 2. Interactive Testing: `adk web`

### Quick Start

```powershell
# 1. Edit backend/agent.py to select agent
# 2. Start the web UI
cd C:\Users\dlohn\.gemini\antigravity\scratch\Sudo_Hatter_Command\Projects\AGY_AVIATIONCHAT
backend\.venv\Scripts\adk.exe web --port 8001
```

Open `http://127.0.0.1:8001/dev-ui/`

### Agent Selection (`backend/agent.py`)

```python
# backend/agent.py — Root agent selector for adk web / adk run
from backend.agents.greeting.agent import greeting_agent
root_agent = greeting_agent

# Other options:
# from backend.agents.hr.agent import hr_agent
# from backend.agents.specialist.agent import specialist_agent
```

### Key UI Features

| Tab | Purpose |
|-----|---------|
| **Chat** | Interact with agent in real-time |
| **Events** | See tool calls, model requests/responses |
| **Trace** | Step-by-step execution flow |
| **Eval** | Create/run evaluation cases |

### Prompt Iteration Workflow

1. Chat with agent → test prompt change
2. Happy with result? → Click **"Add current session"** in Eval tab
3. This saves the conversation as an eval case
4. Run eval later to catch regressions

---

## 3. Evaluation Framework

### Two Evaluation Formats

| Format | File Suffix | Use Case |
|--------|-------------|----------|
| **Test File** | `.test.json` | Unit test: single session, fast |
| **Eval Set** | `.evalset.json` | Integration test: multiple sessions, multi-turn |

### Test File Structure (`.test.json`)

```json
{
  "eval_set_id": "greeting_agent_welcome",
  "name": "Greeting Agent Welcome",
  "description": "Tests Chuck's welcome flow",
  "eval_cases": [
    {
      "eval_id": "first_greeting",
      "conversation": [
        {
          "invocation_id": "turn-001",
          "user_content": {
            "parts": [{ "text": "Hi there!" }],
            "role": "user"
          },
          "final_response": {
            "parts": [{ "text": "Welcome to AviationChat!" }],
            "role": "model"
          },
          "intermediate_data": {
            "tool_uses": [],
            "intermediate_responses": []
          }
        }
      ],
      "session_input": {
        "app_name": "greeting_agent",
        "user_id": "test_user",
        "state": {}
      }
    }
  ]
}
```

### Evaluation Criteria (7 Built-in Metrics)

**Fast (CI/CD Safe):**
- `tool_trajectory_avg_score` — Exact match of tool call trajectory (default threshold: 1.0)
- `response_match_score` — ROUGE-1 text similarity (default threshold: 0.8)

**LLM-Judged (Deeper):**
- `final_response_match_v2` — Semantic equivalence to reference
- `rubric_based_final_response_quality_v1` — Custom quality rubrics
- `rubric_based_tool_use_quality_v1` — Tool usage correctness

**Safety:**
- `hallucinations_v1` — Groundedness against context
- `safety_v1` — Harmlessness check

### Criteria Config (`test_config.json`)

```json
{
  "criteria": {
    "tool_trajectory_avg_score": 1.0,
    "response_match_score": 0.7,
    "hallucinations_v1": 0.8
  }
}
```

### AviationChat Recommended Criteria

| Agent | Criteria | Rationale |
|-------|----------|-----------|
| **Greeting (Chuck)** | `response_match_score` + `safety_v1` | Conversational, semantic match sufficient |
| **Specialist** | `tool_trajectory_avg_score` + `hallucinations_v1` | Must call RAG tools AND ground answers |
| **Socratic Teacher** | `rubric_based_final_response_quality_v1` | Custom rubric: "must ask follow-up" |
| **Reasoner** | `tool_trajectory_avg_score` + `response_match_score` | Must call Librarian AND return correct action |

---

## 4. User Simulation (ADK 1.26.0+)

Instead of writing hardcoded user messages, describe a **ConversationScenario** and ADK generates realistic prompts dynamically via an LLM "user simulator."

### ConversationScenario

```json
{
  "starting_prompt": "I'm studying for my PPL written exam",
  "conversation_plan": "Ask about VOR navigation. Ask a follow-up about VOR vs GPS. Request a quiz.",
  "user_persona": "NOVICE"
}
```

### Pre-Built Personas

| Persona | Behavior |
|---------|----------|
| `NOVICE` | Simple language, follows instructions literally |
| `EXPERT` | Technical jargon, skips explanations, multi-step requests |

### Custom Persona Example

```json
{
  "starting_prompt": "Hey, I just started ground school",
  "conversation_plan": "Ask about airspace classifications. Get confused between Class B and Class C.",
  "user_persona": {
    "id": "STUDENT_PILOT",
    "description": "A new student pilot who mixes up similar aviation concepts",
    "behaviors": [
      {
        "name": "Confusion with similar terms",
        "description": "Frequently confuses related aviation concepts",
        "behavior_instructions": [
          "Occasionally mix up Class B and Class C airspace",
          "Ask clarifying questions when corrected"
        ],
        "violation_rubrics": [
          "The user never shows confusion about aviation concepts"
        ]
      }
    ]
  }
}
```

### User Simulator Config

```json
{
  "criteria": { "hallucinations_v1": 0.8, "safety_v1": 0.8 },
  "user_simulator_config": {
    "model": "gemini-2.5-flash",
    "max_allowed_invocations": 20
  }
}
```

> **Note:** User Simulation only supports `hallucinations_v1` and `safety_v1` criteria (no expected trajectory/response).

---

## 5. Running Evaluations

### A. Via `adk web` (Interactive)

1. Start: `backend\.venv\Scripts\adk.exe web --port 8001`
2. Chat with agent → test conversation
3. Go to **Eval** tab → Create eval set → Add current session
4. Click **Run Evaluation** → configure thresholds → Start
5. Inspect Pass/Fail results

### B. Via `pytest` (Automated)

```python
from google.adk.evaluation.agent_evaluator import AgentEvaluator
import pytest

@pytest.mark.asyncio
async def test_greeting_welcome():
    """Test Chuck's greeting flow."""
    await AgentEvaluator.evaluate(
        agent_module="backend.agents.greeting",
        eval_dataset_file_path_or_dir="backend/agents/greeting/evals/welcome.test.json",
    )
```

Run: `backend\.venv\Scripts\python -m pytest backend/tests/evals/ -v`

### C. Via `adk eval` CLI (Batch)

```powershell
backend\.venv\Scripts\adk.exe eval `
  backend/agents/greeting/ `
  backend/agents/greeting/evals/greeting_eval_set.evalset.json `
  --print_detailed_results
```

**Run specific evals only:**
```powershell
# Only run "first_greeting" and "returning_user" from the set
backend\.venv\Scripts\adk.exe eval `
  backend/agents/greeting/ `
  backend/agents/greeting/evals/greeting_eval_set.evalset.json:first_greeting,returning_user
```

---

## 6. Eval File Organization

```text
backend/agents/<agent_name>/
├── agent.py
├── prompts.py
└── evals/                            ← Eval data lives with the agent
    ├── welcome.test.json             ← Unit test (single session)
    ├── multi_turn.test.json          ← Unit test (multi-turn)
    ├── conversation_scenarios.json   ← User Simulation scenarios
    ├── <agent>_eval_set.evalset.json ← Integration test (multi-session)
    └── test_config.json              ← Scoring thresholds
```

---

## 7. Debugging Workflow

### Trace View (adk web)

The **Trace** tab shows every model request/response:
- **Event**: Raw event data
- **Request**: Exact prompt sent to model
- **Response**: Model's raw response
- **Graph**: Visual tool call flow

### Common Issues

| Symptom | Check | Fix |
|---------|-------|-----|
| Agent doesn't respond | Events tab for errors | Verify `GEMINI_API_KEY` |
| Tool call fails | Tool result in Events | Check tool implementation |
| Wrong routing | Trace tab for agent transfers | Check sub_agent descriptions |
| Slow response | Trace timing | Enable token compaction (auto in 1.26.0) |

---

## 8. Environment Variables

```powershell
# Required for all ADK testing
$env:GEMINI_API_KEY = "your_key"
$env:GCP_PROJECT_ID = "your-project-id"
$env:GOOGLE_APPLICATION_CREDENTIALS = "path\to\service-account.json"
```

---

## 9. Key 1.26.0 Features for Testing

| Feature | What It Does |
|---------|-------------|
| **Token Compaction** | Auto-compresses context before model calls (reduces cost) |
| **Custom Client Injection** | `Gemini(client=mock_client)` — inject mock for unit tests |
| **Session Rewind** | Revert session to a previous invocation for debugging |
| **Parallelized Tool Resolution** | Faster agent startup with many tools |
| **`load_skill_from_dir()`** | Load ADK Skills from a directory at runtime |

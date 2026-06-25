---
description: Comprehensive guide for building, structuring, and maintaining ADK Agents in AviationChat-AGY. Updated for ADK 1.26.0 — includes token compaction, custom Client injection, load_skill_from_dir, and eval framework integration.
---

# ADK Agent Development Skill

This skill consolidates the rules, patterns, and workflows for creating Google Agent Development Kit (ADK) agents within the AviationChat-AGY project.

## 1. Core Philosophy: Form vs. Function
We follow the "Steve Jobs Test" for agent design:
- **Simple**: Can a non-developer tweak the prompt without breaking code?
- **Obvious**: Is the file structure immediately clear?
- **Consistent**: Do all agents follow the exact same pattern?

To achieve this, we separate **Logic (`agent.py`)** from **Personality (`prompts.py`)**. 

---

## 2. Directory Structure & Organization

### A. Location
Agents are catigorized by **Visual Containment** (Parent/Sub-Agent), not arbitrary abstract catigories:
*   **Parent Agents** (`backend/agents/`): Top-level conversational managers routing from endpoints. (e.g., Greeting, HR, Specialist).
*   **Sub-Agents** (`backend/agents/.../sub_agents/`): Physically nested agents that support exactly one Parent Agent.
*   **Tools** (`backend/tools/`): Generic Python algorithmic scripts (like the Librarian RAG searcher) stripped of AI fluff.

### B. Agent Package Layout
Every agent MUST follow the strictly separated **Component Pattern**:
```text
backend/agents/my_parent_agent/
├── __init__.py          # Exports the agent object
├── agent.py             # MANDATORY: Logic, model init, tool routing
├── prompts.py           # MANDATORY: System instructions & prompts
└── sub_agents/          # Physically nested supporting agents
    └── my_sub_agent/
        ├── agent.py     
        └── prompts.py
```
*(Note: If a sub-agent relies on a global tool from `backend/tools/`, create a `_proxy.py` file to visually map the dependency).*

---

## 3. Coding Standards

### A. Imports
**CRITICAL**: ALWAYS use absolute imports. Relative imports cause circular dependency failures in the ADK registry.
*   ✅ **GOOD**: `from backend.agents.hr.agent import hr_agent`
*   ❌ **BAD**: `from ..hr import agent`

### B. Environment & Keys
*   **Source of Truth**: All API keys live in `auth_keys/.env`.
*   **Loading**: ADK agents must explicitly load `.env` if not running via `main.py`.
    ```python
    import os
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "../../../../../auth_keys/.env")) 
    # Adjust path depth as needed or use absolute path logic
    ```
*   **Model Init**: ALWAYS pass the API key explicitly.
    ```python
    model=Gemini(
        model="gemini-3.1-flash-lite-preview",
        api_key=os.getenv("GEMINI_API_KEY") 
    )
    ```
*   **Custom Client Injection (1.26.0+)**: For unit testing, inject a mock client directly:
    ```python
    mock_client = create_mock_genai_client()
    model = Gemini(model="gemini-3.1-flash-lite-preview", client=mock_client)
    ```

### C. ADK CLI Entry Point (`backend/agent.py`)
To enable `adk run` or `adk web` testing, `backend/agent.py` acts as the root entry point.
*   **Firebase Init**: Since ADK bypasses `main.py`, `backend/agent.py` MUST initialize `firebase_admin` if agents use Firestore/Auth.
*   **Root Agent**: Define `root_agent = my_agent` to select which agent to test.

---

## 4. Workflow: Creating a New Agent

### Step 1: Create Structure
```bash
mkdir -p backend/agents/specialist/sub_agents/weather
cd backend/agents/specialist/sub_agents/weather
touch __init__.py agent.py prompts.py
```

### Step 2: Define Prompts (`prompts.py`)
Write the instruction as a constant.
```python
WEATHER_INSTRUCTION = """You are a Weather Sub-Agent..."""
```

### Step 3: Build Agent (`agent.py`)
```python
import os
from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from backend.agents.specialist.sub_agents.weather.prompts import WEATHER_INSTRUCTION

weather_agent = LlmAgent(
    name="weather_agent",
    model=Gemini(model="gemini-3.1-flash-lite-preview", api_key=os.getenv("GEMINI_API_KEY")),
    instruction=WEATHER_INSTRUCTION
)
```

### Step 4: Export (`__init__.py`)
```python
from .agent import weather_agent
```

---

## 5. Testing & Verification

### CLI Testing
Use the project's virtual environment and the ADK CLI:
```powershell
# 1. Configure backend/agent.py to export your agent as root_agent
# 2. Run:
backend\.venv\Scripts\adk.exe run backend
# OR
backend\.venv\Scripts\adk.exe run backend/agent.py
```

### Web UI Testing
```powershell
backend\.venv\Scripts\adk.exe web --port 8001
```
Then visit `http://localhost:8001/dev-ui`.

### Evaluation Framework (1.26.0+)
Each agent should have an `evals/` directory for evaluation data:
```text
backend/agents/<agent_name>/
├── agent.py
├── prompts.py
└── evals/
    ├── welcome.test.json         ← Unit test (single session)
    ├── eval_set.evalset.json     ← Integration test (multi-session)
    └── test_config.json          ← Scoring thresholds
```

Run evals via CLI:
```powershell
backend\.venv\Scripts\adk.exe eval backend/agents/greeting/ backend/agents/greeting/evals/eval_set.evalset.json --print_detailed_results
```

See the **adk-testing-patterns** skill for full evaluation framework documentation.

---

## 6. ADK 1.26.0 Features

| Feature | Usage |
|---------|-------|
| **Token Compaction** | Automatic — reduces token usage in long multi-turn sessions |
| **Custom Client Injection** | `Gemini(client=mock_client)` for unit testing |
| **Session Rewind** | `session_service.rewind(session_id, invocation_id)` |
| **`load_skill_from_dir()`** | `from google.adk.tools import load_skill_from_dir` |
| **Parallelized Tool Resolution** | Automatic — faster startup for multi-tool agents |

---

## 7. Common Pitfalls
1.  **Missing `__init__.py`**: Makes the folder invisible to Python.
2.  **Relative Imports**: Causes "ImportError: attempted relative import with no known parent package".
3.  **Missing API Key**: Causes "403 Permission Denied" from Vertex/Gemini.
4.  **Firebase Not Initialized**: Errors when agent tries to access Firestore during standalone test.
5.  **Port Conflict**: ADK web defaults to port 8000 — same as our FastAPI server. Use `--port 8001`.

# TDAD Stack — Quick Reference Install Guide

**What this is:** The BDD contract and autonomous coding layer added to **both** the
`/sudo` manual workflow and the `/autopilot_claude` autonomous workflow.

---

## What We're Setting Up & Why

The BDD Vision Lock (`pytest-bdd`) is being added to **both** the `/sudo` and
`/autopilot_claude` dev flows. The goal is to replace ambiguous English ACs with strict
Gherkin contracts (`Given`/`When`/`Then`) so agents test against machine-readable physics
rather than interpreting narrative text.

**The only difference between the two tracks is human visibility:**

The stack has **two layers**:

### Layer 1 — BDD Contract Engine (`pytest-bdd`)
**Installs into: each project's `.venv`**

`pytest-bdd` converts plain-English Gherkin scenarios (`Given`/`When`/`Then`) into
executable Python test physics. This is the **Vision Lock** from the PRP — the step where
your English directive becomes an unambiguous, machine-readable contract that an agent can
test against without misinterpreting your intent.

- Runs inside the project venv alongside your existing `pytest` suite
- `.feature` files live next to your test files
- Zero conflict with existing `pytest-asyncio`, `pytest-cov` etc.

### Layer 2 — Autonomous Coding Engine (`aider`)
**Installs globally via `uv` — its own isolated Python 3.12 environment**

`aider` is the dev agent that enters the **Black Box** loop: it reads the failing BDD tests,
writes implementation code, runs the tests, reads the failure output, and iterates until
100% green — without you watching. It is a **CLI tool**, not a project library. It never
goes into `requirements.txt`.

- Lives at `~/.local/bin/aider` (available on PATH after install)
- Uses its own isolated Python 3.12 regardless of your project's Python version
- Scoped to `/autopilot_claude` only — the `/sudo` flow does NOT use aider

---

## Install on a New Machine

### Prerequisites
- Python (any version — aider brings its own 3.12)
- A project venv already created for AGY_AVIATIONCHAT and/or Fresh_Workspace_BMAD

---

### Step 1 — Install `aider` Globally (One-Time Per Machine)

Per the [official aider install docs](https://aider.chat/docs/install.html), the correct
method on Windows is the PowerShell one-liner. **Do NOT use `pip install aider-chat`** —
that resolves to an ancient 0.16.0 build that is incompatible with Python 3.12+.

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://aider.chat/install.ps1 | iex"
```

This will:
- Download and install `uv` to `~/.local/bin`
- Install `aider-chat` in its own isolated Python 3.12 environment
- Make `aider` available on your PATH

**Verify:**
```powershell
aider --version
```

---

### Step 2 — Install `pytest-bdd` Into Each Project Venv

Run this from each project root (where `backend/.venv` lives):

#### AGY_AVIATIONCHAT
```powershell
cd Projects\AGY_AVIATIONCHAT
.\backend\.venv\Scripts\python.exe -m pip install --prefer-binary pytest-bdd
```

#### Fresh_Workspace_BMAD
```powershell
cd Projects\Fresh_Workspace_BMAD
.\backend\.venv\Scripts\python.exe -m pip install --prefer-binary pytest-bdd
```

**Verify (run from inside the project):**
```powershell
.\backend\.venv\Scripts\python.exe -c "from pytest_bdd import given, when, then; print('pytest-bdd OK')"
```

Expected output: `pytest-bdd OK`

---

### Step 3 — Verify aider Can See the Project

From a project root, run:
```powershell
aider --version
# Should print: aider x.x.x
```

---

## What Goes Where (The Rule)

| Tool | Location | Why |
|---|---|---|
| `pytest-bdd` | Each project's `backend/.venv` | It's a test library — runs in the test suite |
| `aider` | Global (`~/.local/bin`) via `uv` | It's a CLI dev tool — like `git`, not a library |
| Both listed in | `requirements-tdad.txt` (lobby root) | Documentation / team reference |

> [!IMPORTANT]
> **Never add `aider-chat` to a project's `requirements.txt`.**
> It is a developer machine tool, not a runtime or test dependency.
> `pytest-bdd` DOES belong in `requirements.txt` — it is part of the test suite.

---

## Files Modified by This Setup

| File | Change |
|---|---|
| `Projects/AGY_AVIATIONCHAT/backend/requirements.txt` | Added `pytest-bdd>=7.0.0` |
| `Projects/Fresh_Workspace_BMAD/backend/requirements.txt` | Added `pytest-bdd>=7.0.0` + `pytest-cov`, `pytest-timeout` (were missing) |
| `requirements-tdad.txt` (lobby root — new) | Documents both tools + their correct install methods |

---

## Current Install Status (Laptop)

| Tool | Status |
|---|---|
| `pytest-bdd 8.1.0` — AGY_AVIATIONCHAT venv | ✅ Installed & verified |
| `pytest-bdd 8.1.0` — Fresh_Workspace_BMAD venv | ✅ Installed & verified |
| `aider 0.86.2` — global (`~/.local/bin/aider.exe`) | ✅ Installed & verified |

---

## Strategy Context — What We're Building & Why

*This section documents the design conversation that led to this setup.
Read this if you're picking up this work on a new machine or after a gap.*

### The Problem We're Solving

The current BMAD `/sudo` dev flow is excellent but conversational. The agent writes
a plan, you approve it, the agent codes, you review, the agent fixes, and so on.
The quality is high but the back-and-forth takes developer attention throughout.

The TDAD pipeline is designed to make the **autonomous** `/autopilot_claude` mode
production-grade. Right now autopilot can drift — it sometimes misinterprets an AC,
builds something adjacent to what was asked, or produces code that passes its own
tests but not the original intent. The root cause is that English ACs are ambiguous.

### The Two-Track Model (This is the Key Design Decision)

BDD contracts apply to **both** tracks. The only difference is whether you're watching:

| Track | Command | BDD Contracts | Difference |
|---|---|---|---|
| **Manual** | `/sudo-write-story-tests` → `/sudo-dev-story-tests` → `/sudo-code-review` | ✅ Yes | **You watch.** You can see when the agent is struggling and intervene. You approve each phase gate. |
| **Autonomous** | `/autopilot_claude` | ✅ Yes | **Headless.** Agent locks into the loop and runs until tests are green. You only see the final result. |

> [!IMPORTANT]
> **The sandbox (OpenHands) is deferred for both tracks.**
> We are not isolating the aider loop in Docker yet. The agent runs against the local
> test suite. OpenHands gets revisited once BDD contracts are proven end-to-end.

### How the BDD Vision Lock Works

Today: `/sudo-write-story-tests` generates acceptance tests from bullet-point ACs.
The agent interprets English and writes what it thinks you mean.

After TDAD: The workflow will first translate the AC into a strict Gherkin contract:

```gherkin
Feature: Aviation Lesson Routing
  Scenario: Student requests a lesson on VFR weather minimums
    Given the student is authenticated with a valid session
    And the curriculum contains a VFR weather unit
    When the student sends "What are VFR weather minimums?"
    Then the routing agent selects the WeatherSpecialist
    And the response contains "visibility" and "ceiling"
    And the response time is under 3 seconds
```

This `.feature` file becomes the **unalterable blueprint**. The agent cannot
misinterpret it — every `Given`/`When`/`Then` is a hard assertion in pytest.
The autonomous loop (`aider`) then writes implementation code until every
assertion is green. There is no room for drift.

### What the OpenHands Sandbox Is (and Why We Deferred It)

The full PRP proposed wrapping aider in an **OpenHands** secure sandbox — an
isolated Docker environment where agents can spin up real databases, run full
end-to-end suites, and verify cascading effects without touching production.

**We deferred the sandbox for now.** Reason: the sandbox adds significant
infrastructure complexity (Docker, environment parity, secret injection) that
we don't need to prove the BDD contract concept. The aider loop running against
the local test suite is the right first step. We will revisit OpenHands once we
have the BDD contract layer working end-to-end and have seen a full
`/autopilot_claude` cycle use it successfully.

### The Adversarial Audit Layer (Phase 5 — Future)

The PRP also proposed a "Clean-Room Adversarial Agent" — a fresh agent spun up
with zero context, given only the BDD contract and the final code, and asked to
audit for security holes, memory leaks, and logic flaws.

This maps directly to what `/sudo-code-review` already does — but the difference
is the zero-context injection. The current `/sudo-code-review` agent carries the
full dev session context, which can introduce builder's bias ("I know why I wrote
it that way"). A clean-room agent has no such bias.

**Status:** Designed, not yet built. The existing `bmad-code-review` skill is the
placeholder until we wire up the clean-room pattern.

### What's Changing in the Codebase (Incremental, Not a Rewrite)

The existing test files, `conftest.py`, and `pytest` configuration are untouched.
`pytest-bdd` is an additive plugin — it registers new `.feature` files as test
cases alongside the existing `test_*.py` files. No existing tests break.

The planned additions per project:
```
backend/tests/
  features/           ← NEW: Gherkin .feature files (one per story/AC group)
    routing/
      lesson_routing.feature
    voice/
      vad_session.feature
  bdd/                ← NEW: pytest-bdd step definitions
    steps_routing.py
    steps_voice.py
```

### What's Next

1. **Design the first `.feature` file** for an existing Epic 8 story — prove the
   pattern works end-to-end with the existing codebase before touching autopilot.
2. **Update `/sudo-write-story-tests`** to optionally output a `.feature` file
   alongside the standard `test_*.py` red-phase scaffold.
3. **Wire aider into `/autopilot_claude`** — the command currently uses the Claude
   API directly; we need to evaluate whether aider's loop or a raw Claude call is
   the right engine for the autonomous phase.
4. **Revisit OpenHands** once BDD contracts are proven in the local test loop.


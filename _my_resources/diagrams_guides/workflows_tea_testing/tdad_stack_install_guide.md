# TDAD Stack — Quick Reference Install Guide

**What this is:** The BDD contract and autonomous coding layer added to **both** the
`/sudo` manual workflow and the `/cicd-autopilot-claude` autonomous workflow.

---

## What We're Setting Up & Why

The BDD Vision Lock (`pytest-bdd`) is being added to **both** the `/sudo` and
`/cicd-autopilot-claude` dev flows. The goal is to replace ambiguous English ACs with strict
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
- Scoped to `/cicd-autopilot-claude` only — the `/sudo` flow does NOT use aider

---

## Install on a New Machine

### Prerequisites
- Python (any version — aider brings its own 3.12)
- A project venv already created for AGY_AVIATIONCHAT and/or Fresh_Workspace_BMAD

> [!NOTE]
> **Most of the stack ships in the repos — `git clone`/`pull` IS the install for it.**
> The BMAD testarch skills (`.claude/skills/bmad-testarch-*`), the commands
> (`.agents/commands/cicd-bdd-tests.md`, `testarch-*.md`), the TEA pins
> (`_bmad/custom/bmad-testarch-*.toml`, `_bmad/tea/config.yaml`), the pyproject marker
> registry, and the test trees (`backend/tests/features/` + `backend/tests/bdd/`) are all
> versioned files. Only TWO things are per-machine: each project venv's packages (Step 2)
> and the global `aider` (Step 1).

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

### Step 2 — Sync Each Project Venv (full requirements, not just pytest-bdd)

On a NEW machine, install the **whole pinned requirements file** — installing only
`pytest-bdd` leaves the rest of the env drifted (missing `networkx` etc. breaks suite
collection). Run from each project root (where `backend/.venv` lives):

#### AGY_AVIATIONCHAT
```powershell
cd Projects\AGY_AVIATIONCHAT
.\backend\.venv\Scripts\python.exe -m pip install --prefer-binary -r backend\requirements.txt
```

#### Fresh_Workspace_BMAD
```powershell
cd Projects\Fresh_Workspace_BMAD
.\backend\.venv\Scripts\python.exe -m pip install --prefer-binary -r backend\requirements.txt
```

**Verify (run from inside the project):**
```powershell
.\backend\.venv\Scripts\python.exe -c "from pytest_bdd import given, when, then; print('pytest-bdd OK')"
```

Expected output: `pytest-bdd OK`

> [!WARNING]
> **Interpreter discipline (lesson, 2026-07-09):** bare `python` resolves to the GLOBAL
> user Python (3.14 on the desktop) — NOT the project venv. The global env is drifted
> (running the AGY suite with it produced 35 collection errors from missing pinned deps),
> while `backend\.venv` is fully synced and collects the whole suite clean. **Always invoke
> tests through the venv:** `.\backend\.venv\Scripts\python.exe -m pytest ...`

---

### Step 3 — Verify aider Can See the Project

From a project root, run:
```powershell
aider --version
# Should print: aider x.x.x
```

---

### Step 4 — Smoke-Verify the Whole Stack (ready-made canaries)

Both projects now carry live `.feature` files, so a new machine can prove the stack in
under a minute:

```powershell
# AGY — the Epic 16 red contract (8 skip-marked scenarios; skipped = CORRECT until 16.2 dev)
cd Projects\AGY_AVIATIONCHAT
.\backend\.venv\Scripts\python.exe -m pytest backend/tests/bdd -q
# Expected: 8 skipped

# AGY — whole-suite collection health (proves no missing deps)
.\backend\.venv\Scripts\python.exe -m pytest backend/tests --collect-only -q
# Expected (2026-07-09 baseline): 2335 tests collected, 0 errors

# Fresh_Workspace_BMAD — the template smoke .feature must be GREEN
cd ..\Fresh_Workspace_BMAD
.\backend\.venv\Scripts\python.exe -m pytest backend/tests -q -k workspace_smoke
```

If the AGY bdd run reports an import error instead of `8 skipped`, you're on the wrong
interpreter (see the Step-2 warning) or the venv isn't synced.

---

## What Goes Where (The Rule)

| Tool | Location | Why |
|---|---|---|
| `pytest-bdd` | Each project's `backend/.venv` | It's a test library — runs in the test suite |
| `aider` | Global (`~/.local/bin`) via `uv` | It's a CLI dev tool — like `git`, not a library |
| `md-feedback` | MCP config — **root `.mcp.json`** per repo (Claude Code does NOT read `.claude/mcp.json` — that misplacement is why it never loaded; fixed ×4 surfaces 2026-07-09) + `.opencode/mcp.json` for opencode | Provides the AI agents with markdown annotation capabilities for `/cicd-self-audit` |
| Listed in | `requirements-tdad.txt` (lobby root) | Documentation / team reference |

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

## Current Install Status

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

The TDAD pipeline is designed to make the **autonomous** `/cicd-autopilot-claude` mode
production-grade. Right now autopilot can drift — it sometimes misinterprets an AC,
builds something adjacent to what was asked, or produces code that passes its own
tests but not the original intent. The root cause is that English ACs are ambiguous.

### The Two-Track Model (This is the Key Design Decision)

BDD contracts apply to **both** tracks. The only difference is whether you're watching:

| Track | Command | BDD Contracts | Difference |
|---|---|---|---|
| **Manual** | `/cicd-write-story-tests` (BDD Vision Lock fires inside — mandatory) → `/cicd-self-audit` → `/cicd-dev-story-tests` (hard-gates on the BDD record) → `/cicd-code-review` | ✅ Yes | **You watch.** You can see when the agent is struggling and intervene. You approve each phase gate. |
| **Autonomous** | `/cicd-autopilot-claude` | ✅ Yes | **Headless.** Agent locks into the loop and runs until tests are green. You only see the final result. `dev_AP` enforces the same BDD gate: no contract/waiver → `PIPELINE_BLOCKER` (a headless lane never authors the lock itself). |

> [!IMPORTANT]
> **The sandbox (OpenHands) is ACTIVE for Desktop tracks.**
> We are using OpenHands for `/cicd-autopilot-claude` and `opencode` (Stage 3). 
> The Mobile track remains cloud-native and defers to desktop for OpenHands.

### How the BDD Vision Lock Works

Today: `/cicd-bdd-tests` engages the Vision Lock to interactively align on expected behaviors, translating them into strict Gherkin contracts (stack-appropriate: `pytest-bdd` `.feature` for backend, BDD-structured vitest/Playwright scaffolds for frontend). Then `/cicd-write-story-tests` generates the remaining acceptance tests from the contracts.
The agent no longer interprets ambiguous English or writes what it thinks you mean.

**Enforced end-to-end (2026-07-10):** the Vision Lock is a MANDATORY phase of ① — the only exit without
a contract is a *recorded*, human-approved waiver (`bdd: waived — <rationale>` in the story frontmatter,
for stories with no behavior surface). ② (`/cicd-dev-story-tests`) and the `dev_AP` autopilot twin
**hard-gate on that frontmatter record** (`bdd: locked` + contract files on disk, or `bdd: waived`) and
refuse to plan/code without it — headless lanes raise `PIPELINE_BLOCKER` instead of self-locking.

The workflow first translates the AC into a strict Gherkin contract:

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

### What the OpenHands Sandbox Is (Active on Desktop)

The full PRP proposed wrapping aider in an **OpenHands** secure sandbox — an
isolated Docker environment where agents can spin up real databases, run full
end-to-end suites, and verify cascading effects without touching production.

**Status: Active for Desktop Tracks.** We have wired OpenHands into Stage 3 (Implement)
of `/cicd-autopilot-claude` and `/autopilot-dev-story-opencode.ps1`. The mobile track
(`/autopilot_mobile`) remains cloud-native due to infrastructure constraints; when 
mobile users need the sandbox, they remote into the desktop.

### The Adversarial Audit Layer (Phase 5 — Future)

The PRP also proposed a "Clean-Room Adversarial Agent" — a fresh agent spun up
with zero context, given only the BDD contract and the final code, and asked to
audit for security holes, memory leaks, and logic flaws.

This maps directly to what `/cicd-code-review` already does — but the difference
is the zero-context injection. The current `/cicd-code-review` agent carries the
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
   — 🔄 **UPDATE 2026-07-09: the wiring itself is PROVEN.** Fresh_Workspace (the template) runs the
   system's first `.feature` green: `backend/tests/features/template/workspace_smoke.feature` +
   **self-binding** `backend/tests/bdd/steps_template.py` (each steps module calls
   `pytest_bdd.scenarios()`; pyproject `python_files` adds `steps_*.py` — this is the house convention,
   drop a feature+steps pair in and CI runs it). Also landed: `_bmad/custom/bmad-testarch-atdd.toml` +
   `bmad-testarch-automate.toml` (lobby + AGY + Fresh) pin TEA scaffolding to pytest-bdd. **Still open:**
   the pilot on a REAL Epic-8 story in AGY (audit P2-8).
   — 🔄 **UPDATE 2026-07-09 (later session): the AGY pilot is ASSIGNED = Story 16.2** (Epic 16
   incident-response relay — better fit than an Epic-8 retrofit: greenfield code, 4 crisp behaviors).
   Its red contract is already IN the repo, skip-marked: `backend/tests/features/incident_relay.feature`
   (8 scenarios, AC-8) + `backend/tests/bdd/test_incident_relay_steps.py`; verified `8 skipped, 0 errors`,
   full suite collects 2335/0 via the venv. Supporting docs: `_bmad-output/test-artifacts/test-design-epic-16.md`
   + `atdd-checklist-16-2-always-live-trigger-pipeline.md`. Activation = 16.2 dev start (remove one
   `pytestmark` line → 8 RED → build the relay to green).
2. **Update `/cicd-write-story-tests`** to optionally output a `.feature` file
   alongside the standard `test_*.py` red-phase scaffold.
   — Note 2026-07-09: `/cicd-bdd-tests` (step ①b) already authors the `.feature`, and the new atdd toml
   instructs red-phase scaffolds to BIND to an existing ①b contract via `scenarios()` instead of
   duplicating assertions — the command-file edit itself is still open.
   — ✅ **DONE 2026-07-10:** the command files now enforce it end-to-end. ①'s Step 2 (Vision Lock) is
   MANDATORY (sole escape = a recorded, human-approved `bdd: waived` frontmatter entry); `/cicd-bdd-tests`
   writes stack-appropriate contracts + stamps `bdd: locked`/`bdd_contract:` into the story frontmatter;
   ② + `dev_AP` hard-gate on that record before any plan/code (headless → `PIPELINE_BLOCKER`). Mirrored
   to `.agents/workflows/`; guide updates in this folder same day.
3. **Wire aider into `/cicd-autopilot-claude`** — Completed.
4. **Deploy OpenHands** — Completed for Desktop tracks. Stage 3 now launches OpenHands via Docker volume mount.

<!-- CHECKPOINT id="ckpt_mrdjqxf2_c9xtcr" time="2026-07-09T13:32:42.542Z" note="auto" fixes=0 questions=0 highlights=0 sections="" -->

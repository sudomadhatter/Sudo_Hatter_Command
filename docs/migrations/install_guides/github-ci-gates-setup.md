# Setting up the GitHub gates and tests

**What this gets you:** a repo where GitHub itself refuses a bad merge. Lint or types broken on the
lines you touched — PR blocked. Tests red or coverage below the floor — PR blocked. A merge into
`main` from a branch the model doesn't allow — blocked, *including* one performed from the web UI or
the REST API, which no hook on your machine can see.

**Companion page:** [`repo-gate-stack-setup.md`](repo-gate-stack-setup.md) covers the *local* git
hooks. The two halves guard different things and neither substitutes for the other — §1 below is the
reason. Read this one when you want CI to do the refusing.

**Reference implementation:** `AGY_AVIATIONCHAT` (`pr-check.yml`) and the command centre
(`main-write-gate.yml`). Every pattern below is lifted from a workflow that is running today, and
most of them exist because something got through once.

---

## 1. Why the server side is not optional

Local hooks run at `git push`. **A merge performed on GitHub's servers never touches your machine.**
The web *Merge pull request* button and the REST API don't run `pre-push`, don't check
`core.hooksPath`, and don't consult any token under `.git/`.

Those layers aren't *bypassed* there. They are **absent**.

This is not hypothetical: PR #2 (`dabb3c3`, 2026-08-12) landed on the command centre's `main` exactly
that way, from a web session, with nothing structurally able to look at it. The server-side gate
exists because of that merge.

| | Runs where | Sees a web merge? | Enforces |
|---|---|---|---|
| `pre-push` hook + token | your machine | **no** | *authorisation* — one sign-off buys one merge |
| GitHub Actions check + ruleset | GitHub | yes | *fitness* — is this change allowed to land |

⛔ **The server gate is NOT a port of the local hook, and describing it as one is the mistake to
avoid.** Authorisation depends on a single-use token under `.git/` that by design never leaves the
machine; that half *cannot* cross to a server. Fitness is the half that can. You need both.

---

## 2. The two workflows

| Workflow | Fires on | Job |
|---|---|---|
| **PR quality gate** (`pr-check.yml`) | PRs into `main` and `epic/**` | lint, types, tests, coverage on the change |
| **Main write gate** (`main-write-gate.yml`) | PRs into `main`; pushes to `gate/**` | is this change *allowed* to reach `main` at all |

They answer different questions. The first asks *"is this code good?"* The second asks *"does this
change have the right to be here?"* — a docs-only PR can pass the first trivially and still be the
thing the second must stop.

---

## 3. Anatomy of the PR quality gate

Six patterns, each of which fixes a way a gate silently stops gating. Copy the shapes, not just the
file.

### 3.1 `fetch-depth: 0` — or the gate passes on an empty file set

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0   # REQUIRED by every changed-files step below
```

The default (`fetch-depth: 1`) cannot resolve the PR base commit. `git diff <base> HEAD` then returns
**no files**, the lint step has nothing to lint, and it **exits 0**. Green check, lint never ran.

Belt and braces — fail loudly rather than vacuously:

```yaml
BASE="${{ github.event.pull_request.base.sha }}"
if ! git cat-file -e "${BASE}^{commit}" 2>/dev/null; then
  echo "::error::Cannot resolve PR base ${BASE}. The changed-file set would be"
  echo "::error::empty and this gate would pass without linting anything. Check fetch-depth."
  exit 1
fi
```

### 3.2 The ratchet — hard on what you touched, soft on the rest

A repo with pre-existing debt can't turn on a full-repo hard gate; it would block every PR forever.
So run the check twice:

```yaml
- name: Lint (ruff) — changed files, HARD GATE
  # No continue-on-error. Must never gain one.
  run: ruff check --output-format=github $FILES

- name: Lint (ruff) — full repo, REPORT-ONLY
  continue-on-error: true
  run: ruff check backend/ --output-format=github
```

New code must be clean; debt in untouched files isn't this PR's problem. The debt count only falls.

### 3.3 Every soft step carries an owner and an expiry

⛔ **"Report-only for now" with no owner and no expiry becomes report-only forever.** So a soft step
names both, in the file:

```yaml
- name: Types (pyrefly) — full repo, REPORT-ONLY
  # OWNER:  Daniel (sudomadhatter)
  # EXPIRY: tracked in open_tasks → "clear backend pyrefly debt"
  # Measured baseline at wire-in: 470 errors. Close by driving to zero and DELETING this step.
  continue-on-error: true
```

Closing it means **deleting the step**, not flipping the flag — the hard changed-files gate above
already protects every new line.

### 3.4 A version pin is a request; verify it separately

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'      # a REQUEST
```

That line asks for 3.11. Nothing checks it against what the project *declares*. AVCH added a step
that reads `requires-python` from `pyproject.toml` and fails if the runner doesn't satisfy it — so
the pin and the declaration cannot drift apart in silence.

They had drifted: every local venv ran 3.14 while CI and production ran 3.11, which quietly made
*local green* stop implying *CI green*. Run the check **before** installing dependencies, so a wrong
interpreter fails with a readable message instead of a resolution error 200 packages deep.

### 3.5 Pin the tools where the developer gets them

```yaml
- run: pip install -r backend/requirements.txt   # ruff + pyrefly pinned HERE
```

Not `pip install ruff` inline. CI and the local venv must run identical tool versions, or a lint that
passes on your machine fails in CI for reasons neither of you can see.

### 3.6 Trigger on the epic branches too, and skip what doesn't matter

```yaml
on:
  pull_request:
    branches: [main, "epic/**"]      # story landings get the same gate as the epic's own merge
    paths:
      - 'backend/**'
      - 'frontend/**'                # docs/tooling PRs skip it entirely

concurrency:
  group: pr-${{ github.event.pull_request.number }}
  cancel-in-progress: true           # don't burn minutes on superseded pushes
```

Without `epic/**`, story work merges into the epic ungated and everything arrives at once when the
epic merges to `main`.

### 3.7 Coverage floor that only ratchets up

```yaml
- run: pytest --cov-fail-under=54    # measured baseline; raise, never lower
```

Scope `source` in `[tool.coverage.run]` — ⛔ use `source_pkgs`, never file paths; `source` silently
ignores paths and reports coverage over nothing.

---

## 4. Anatomy of the main write gate

This one has a subtlety worth understanding before you copy it: **it needs two triggers, because
`main` is reachable by two different roads.**

```yaml
on:
  # Road 1 — a PR into main. The road a web or mobile session takes.
  pull_request:
    branches: [main]

  # Road 2 — the local shipping doors, which merge on the machine.
  push:
    branches: ['gate/**']
```

**Road 1 is deliberately the weaker one.** GitHub builds the merge commit only *after* the check
passes, so at check time there are no parents to inspect — the source branch **name** is all there is
to look at.

**Road 2 exists because a required status check would otherwise refuse a locally-made merge.** That
commit merged on your machine has never been to GitHub and carries no check. So the door pushes the
finished commit to `gate/**` first, the workflow runs on it there, and the green **travels with the
commit** to `main` — checks attach to a SHA, not a branch. That's GitHub's own documented route for
direct pushes under required checks.

The check verifies the merge came from an `epic/*` or `chore/*` branch carrying a key the repo
answers to.

⛔ **Do not add `paths:` to this one.** The PR quality gate skips docs-only changes because its job
is app-code quality. This gate's job is *what may reach `main` at all* — and the merge that prompted
building it was docs-only.

⛔ **No soft steps anywhere in it.** No `continue-on-error`, no `|| true`, no `if: always()` on a
gating step. The command centre asserts their absence with a test (`test_main_write_gate_ci.py`), so
adding one turns the suite red rather than quietly disarming the gate.

---

## 5. Require the check — the ruleset

A workflow that runs and reports is not a gate. Something must **require** it.

```bash
gh api repos/{owner}/{repo}/rulesets --method POST --input ruleset.json
```

Require the check by its published **name** (`main-write-gate`), target `main`, and:

⛔ **Keep the bypass list empty.** A bypass entry for "admins" makes the gate advisory for exactly
the account most able to cause damage.

⚠️ **Rulesets need a paid plan on a private repo.** A free private repo returns:

```
403  Upgrade to GitHub Pro or make this repository public to enable this feature.
```

on both `/rulesets` and `/branches/main/protection`. **On such a repo the server half does not exist
at all** — the local hooks are the only enforcement and the PR door is a convention, not a gate.
`NEXgen-VR-Director` is in exactly this position today. Know which situation you are in before
trusting anything.

**Break-glass** (CI down, `main` must move):

```bash
gh api -X PUT repos/{owner}/{repo}/rulesets/{id} -f enforcement=disabled
```

That is the server-side twin of deleting `MAIN-PUSH-ENFORCE`. Document it beside the other kill
switches, and re-enable it the same day.

---

## 6. Verify — make a gate actually refuse something

Reading a green check proves nothing about a gate that never ran. Prove each one bites:

| Gate | Proof it works |
|---|---|
| changed-files lint | push a PR with a deliberate lint error in a touched file → **PR blocked** |
| the `fetch-depth` guard | temporarily set `fetch-depth: 1` → step **errors**, not passes |
| main write gate | open a PR into `main` from a branch named neither `epic/*` nor `chore/*` → **blocked** |
| the ruleset | confirm the merge button is disabled, not merely showing a red X |

That last distinction is the one people miss: **a red check with no ruleset is a suggestion.** If the
merge button is still clickable, the gate is decoration.

---

## Related

- [`repo-gate-stack-setup.md`](repo-gate-stack-setup.md) — the local git hook half, and the
  armed-vs-gated trap
- `.agents/rules/tests-must-gate-for-real.md` — the law these patterns implement, including the
  owner-and-expiry requirement for soft gates
- `.agents/rules/git-policy.md` — the branch model the write gate enforces

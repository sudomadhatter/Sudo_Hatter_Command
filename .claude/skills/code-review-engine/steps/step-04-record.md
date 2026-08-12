# Step 4 — Record, and hand back

Write what was found. Then return. This step's entire scope is the record and the summary.

## 1. Where the findings go

Write to `FINDINGS_SINK` if the caller supplied one; otherwise to the caller's walkthrough (the
review section it is already writing). If `STORY_FILE` is set and carries a tasks/subtasks section,
append a `### Review Findings` subsection there as well — the builder reads the story, and a
finding they never see is a finding nobody fixes.

Order matters — unresolved work first, settled work last:

```
- [ ] [Review][Decision] <title> — <detail>
- [ ] [Review][Patch] <title> [<file>:<line>]
- [x] [Review][Defer] <title> [<file>:<line>] — deferred, pre-existing
```

Every `defer` also gets a bullet in the caller's `deferred-work.md`, under a heading naming this
review and its date. Deferred work that lives only inside one review's record is deferred to
nowhere.

## 2. What the engine hands back

```
lenses_run:      <n>/<total>   (per-lens: ok | recovered-inline | dead | n/a (mode))
findings:        <d> decision · <p> patch · <w> defer   (<r> dismissed)
severity_floor:  none | CONCERNS | FAIL
notes:           <degradations, missing optional inputs, verification state>
```

Then stop. The caller composes its verdict line from this summary plus its own gates.

## 3. The boundary — what this engine never touches

The engine has no authority over anything outside the record above, and this is a hard edge, not a
default:

- **It never advances a story's state and never writes a board file.** Only a human close-out
  moves work to done; a reviewer that promotes its own subject is not a reviewer.
- **It never issues the `Verdict:` line.** It supplies a floor; the caller owns the verdict.
- **It never applies fixes on its own initiative.** The caller decides whether findings get patched
  in this pass, and by whom.
- **It never pauses the caller's flow for a decision.** `decision_needed` findings are handed back
  written down, for the caller to walk with the operator.

An engine that quietly does any of these is indistinguishable from one that was asked to.

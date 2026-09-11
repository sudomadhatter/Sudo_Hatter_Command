---
name: critical-surfaces
description: "The quick lane's line: five critical surfaces (auth and session · billing, entitlement and cost caps · security rules and data topology · FAA-facing answers · CI and the gates) that the quick lane may not touch without the operator's word. Each repo declares its own paths in `.agents/critical-surfaces.json`; `.agents/scripts/scope_check.py` answers CLEAR or OVERLAP from paths. An overlap is a SOFT stop — the agent stops and says what overlaps and why; only the operator's word, quoted into the plan, moves the lane past it. No agent override exists and the script never asks. Fires when a quick lane starts (Step 1) and at its close-out tripwire (the real diff)."
trigger: model_decision
triggers: [quick lane, quick-dev, quick dev, scope check, critical surface, critical surfaces, scope_check]
# Intent-shaped: the trigger is which LANE was called, not which file was opened. Antigravity
# judges `description:` against the request; `.agents/hooks/rule-trigger.py` matches these
# keywords and injects a pointer.

---

# Critical surfaces — the quick lane's line, and it is a file, not a feeling

The quick lane (`/smh-quick-dev` in the lobby, `/cicd-quick-dev` in a project — `git-policy` § Two
toggles) cuts ceremony, not tests, and it needs a line or it becomes the default because it is
faster. This rule is the line. Today's prose ("auth/tenancy walls, payments, PII, DB schema or
security rules, a cross-boundary contract") lived in one door's Step 1.5 and was judged by the
agent reading it; a qualification an agent evaluates by judgement is a qualification it can want
its way through. So the list is a rule, the paths are a file per repo, and the check is a script.

## The five surfaces

| Surface | Why the quick lane may not touch it |
|---|---|
| **Auth and session** | a wrong line here is every user's account |
| **Billing, entitlement, cost caps** | a wrong line here is revenue or a runaway bill |
| **Security rules and data topology** | Firestore and Storage rules are the last wall; the constitution already says ask first |
| **FAA-facing answers** | the retrieval and grounding pipeline is the product's credibility; a regression ships wrong regulatory guidance |
| **CI and the gates** | a workflow or hook edit changes what "green" means for everyone; the constitution already says ask first |

What the quick lane is for: a UI fix, a document or file update, anything off this list. What it
is not for: the surfaces on it. The stop is **soft** — see § The stop below — but it is never the
agent's to lift.

## The map — each repo declares its own paths

`<repo>/.agents/critical-surfaces.json`, five keys always present. A surface that does not apply
to that repo says so in its `why` and lists nothing, so a reader sees the decision, not a gap:

```json
{
  "surfaces": {
    "auth":    {"why": "…", "paths": ["backend/middleware/auth.py", "frontend/src/contexts/AuthContext.tsx"]},
    "billing": {"why": "…", "paths": ["backend/routers/entitlement.py", "backend/services/cost_meter.py"]},
    "rules":   {"why": "…", "paths": ["firebase/firestore.rules", "firebase/storage.rules", "firebase.json"]},
    "answers": {"why": "…", "paths": ["backend/agents/specialist/", "backend/tools/librarian.py"]},
    "ci":      {"why": "…", "paths": [".github/", ".agents/critical-surfaces.json",
                                      ".agents/scripts/scope_check.py",
                                      ".agents/rules/critical-surfaces.md"]}
  }
}
```

⛔ **The `ci` surface of every map lists the LINE ITSELF** — the map, `scope_check.py`, and this
rule. Without those three rows a quick lane can edit or empty the surface list, the checker, or this
page and still read `CLEAR`, which is the one thing § Adding a surface forbids. A line that can
widen itself is not a line, and the enforcement is a row, not a sentence.

**A path ending in `/` is a prefix; anything else is an exact repo-relative file.** That is the
convention AviationChat's `classify_changes.py` and the lobby's `sop_currency.py` already use, and
it is what keeps `backend-notes/` from matching `backend/`.

**Project law stays in the project** (`project-law.md`). The lobby's script reads the map; it does
not carry AviationChat's paths. The lobby's own map lists its gates under `ci` and says the other
four do not apply. AviationChat's map and the skeleton's placeholder map are rows on AVCH-152.

**A map that declares no paths at all is treated as no map, and says so** — the skeleton's
placeholder ships all five surfaces empty, and a map matching nothing while suppressing the
fallback would be strictly weaker than having no file. It prints
`MAP: <path> declares no paths for <repo> - generic surfaces only`.

**A repo with no map is loud, not silent.** The script falls back to a generic set — `.github/`,
`.githooks/`, `.agents/hooks/`, `.agents/scripts/git-hooks/`, `*.rules`, `firebase.json`, and the
path-segment fragments `auth`, `session`, `billing`, `payment`, `entitlement` — and prints
`MAP: none for <repo> - generic surfaces only` above the overlap lines. A fragment matches a whole
path segment or a segment prefix followed by `_`, `-` or `.` (`auth/`, `auth_service.py`,
`session.ts`), never a substring: an `author-guide.md` under `docs/` is CLEAR.

## The check

```bash
python3 .agents/scripts/scope_check.py --repo "$REPO" --paths <the planned set>   # Step 1
python3 .agents/scripts/scope_check.py --repo "$REPO" --diff origin/main            # the tripwire
```

- **Line 1 is the verdict as a bare word** — `CLEAR` or `OVERLAP` — then one line per overlap:
  `<path>  <surface>: <why>`. Read the word, not the exit code.
- Exit `0` CLEAR · `3` OVERLAP · `2` the check could not run: empty `--paths`, a `--diff` base git
  cannot resolve, a map that does not parse. **Silence is unknown scope, never clear.**
- `--repo` is required and explicit, never the cwd. `--diff <base>` is the merge-base diff of the
  real branch (what it changed since it forked), counts committed changes only, and prints
  `DIFF: <n> file(s) vs <base>`; run it after the lane's last commit.
- It never prompts, never reads the operator's answer, never writes anything, and carries no
  override flag.

## The stop — soft, and only the operator's word lifts it

`OVERLAP` means the agent **stops**: it prints the overlap lines, says in one sentence what it
would take to do this work in the full lane, and waits. The only thing that moves the lane past
this point is the operator's word **in this turn**, quoted verbatim into the plan:

```markdown
**Scope override (2026-09-10):** "<the operator's exact words>" — covers: <the overlapping paths>
```

"ok", "continue", "go ahead" are not it (`000-PLAN-FIRST-GATE` § What is NOT approval). The
literal `approved` on the plan is not it either, because at Step 1 the plan has not been written
yet, and an approval of a plan is not an approval of the surface it touches. There is no agent
override, no `--force`, no "small enough" class: the script is a fact, the override is a sentence
only the operator can write.

## The wire-in — where the doors call it

- **Step 1 of both quick lanes** (`/smh-quick-dev`, `/cicd-quick-dev`): the `--paths` call on the
  planned set. `CLEAR` → print the line and continue. `OVERLAP` → the stop above.
- **The eject tripwire — Step 5 of the same two doors, before the hand-off** (not the close-out:
  the close-out doors do not call this script, and saying they did sent a reader to the wrong
  door): the `--diff` call on the real branch — `--diff origin/main` for a Task lane or a TRUNK
  story lane, `--diff origin/epic/<KEY>-…` for a story lane on a FULL or LIGHT epic. An `OVERLAP`
  the plan carries no `Scope override` for **ejects** the lane to the full ceremony and re-arms the
  plan-first gate. An overlap the plan does carry an override for is printed and passed. An
  under-declared Step 1 is caught by the diff, not by the agent's memory.
- **`lane_qualify.py` keeps answering size** (light / task / handoff); this answers risk. They are
  different questions and neither replaces the other.

## Adding a surface, or a path

A new surface is a row in the table above with one reason, a key in every repo's map, and a
sentence in the SOP (`sop-currency`). A new path is one line in that repo's map, committed under
that repo's own key (`project-law.md`). Nothing here is edited from a quick lane: the map is on
the `ci` surface of every repo that carries one, because a line that can widen itself is not a
line.

# SCC-294 — walkthrough

**Lane:** `chore/SCC-294-jira-token-guide` · **Ticket:** SCC-294 (Task)
**Tree:** `.claude/worktrees/SCC-294-jira-token-guide` · **Base:** `origin/main` @ `a634c35`
**Lane type:** lightweight (`lane_qualify` → `LIGHT`, 5 paths, none deployable, none in the toolkit —
re-run against the **real** diff at close-out, not just the intended one)
**Verdict:** no LLM review ran — a lightweight lane has none by contract, so the deterministic gates
ARE the verdict and this close-out runs the full gate itself.

---

## What shipped

**The machine-setup kit had no Jira step at all.** Every guide in `docs/migrations/` covered secrets,
venvs, hooks and `gcloud`/`gh`/`firebase`/`keyway` — and never once mentioned `acli` or an API token.
The 60-second card ended by telling the reader to run `/cicd-resume`, **which needs the board**.

**The consequence is silent, which is why it survived two machines.** With no credential, an agent
reports "no Jira integration" and simply stops writing the board. Nothing errors. The work still
happens; the record of it does not. That is the same failure mode as an unarmed `core.hooksPath` —
a repo that looks completely normal with every gate switched off — and it is the reason the kit
leads with that one.

| File | What changed |
|---|---|
| `docs/migrations/install_guides/jira-api-token-setup.md` | **NEW** — the whole procedure: install `acli`, create ONE token, store it, point `acli` at it, verify without printing it, rotate it |
| `docs/migrations/INDEX.md` | new step **6b** row, before the step-7 anchor |
| `docs/migrations/install_guides/new_machine-migration-guide.md` | §5 gets a `⛔ Jira board access` bullet with the why and `acli jira auth status` as the check |
| `docs/migrations/install_guides/machine_setup_card.md` | the CLI-logins row now **leads** with `acli` and links the guide, instead of sending the reader to a command that needs the board |
| `docs/repo-map.md` | AUTO body regenerated (`install_guides` 5 → 7) |

### ⭐ ONE token, two consumers — and `acli` keeps its own copy

`acli jira auth login --token` reads the token from **stdin**, so the single value in the keychain
item `sudo-jira` feeds both the CLI and the REST calls. The item name is the cross-machine contract;
everything in the guide reads it by that name and nothing hardcodes a path.

But `acli` stores a **wrapped** copy under its own keychain service (`acli`, account
`jira:<site-uuid>:<account-id>`), and that copy is not the raw token — it returns 401 against
`/rest/api/3/myself` if you extract it. **So rotation is two steps, not one:** replace `sudo-jira`,
then re-run `acli jira auth login`. The guide says so where a reader will hit it.

### ⛔ `acli` cannot attach a file — that is the whole reason the token exists

`acli jira workitem attachment` has exactly two subcommands, `list` and `delete`. There is no `add`.
Uploading is REST-only:

```
POST /rest/api/3/issue/<KEY>/attachments
  header  X-Atlassian-Token: no-check     (403 without it)
  field   file=@<path>                    (multipart)
  auth    <email>:<token>                 (basic)
```

Passed to `curl -K -` over stdin so the token never enters `argv`. Verified end to end, not sketched:
six attachments landed through it this session.

---

## ⛔ Two measured ways to store the token that FAIL SILENTLY

Both of these were hit live, on a real token, and both look exactly like success. They are the
reason this guide exists as a document instead of a two-line note.

| The command | What actually gets stored |
|---|---|
| `security add-generic-password … -w` **with no value** (the interactive prompt) | **truncated at exactly 128 characters.** Fixed prompt buffer, no warning, exit 0. A token is ~192 |
| `security add-generic-password … -w "$(pbpaste)"` | **the command text.** Running a command means copying it — which replaces the token on the clipboard first |

**The keychain is innocent, and that was proved rather than assumed:** a 200-character control value
stored with `-w <value>` reads back at 200. The failure is in how the value reaches the command.

**The route that works** — shell `read` has no length limit, and the length echo is the only feedback:

```bash
printf 'Paste the token, then press Return: '; read -rs T; echo
security add-generic-password -U -a "<email>" -s sudo-jira -w "$T"
echo "stored ${#T} chars"        # ~192, never 128
unset T
```

## Pitfalls that nearly bit

- **`Last accessed` on the Atlassian token page lags by minutes.** `Never Accessed` next to a token
  that has already answered a call is normal. It proves a **negative** reliably (a token that never
  reached Jira) and a positive only late.
- **Expiry is chosen at creation and defaults SHORT.** The first replacement token was created with
  a 7-day life and would have died quietly the following week. Caught before landing; the live token
  expires **2027-08-21**, and the guide now says to write the date down.
- **`acli` fails INSIDE the sandbox** — *"failed to retrieve authenticated status"* — because it
  cannot reach the credential store, and it passes outside it. Per `.agents/rules/jira.md` that is a
  fact about the shell, never a verdict about the board. `acli` is listed in
  `.claude/settings.local.json` `sandbox.excludedCommands` for this reason.
- **`generate_repo_map.py:137` labels the tree root with the CWD basename.** Regenerating inside a
  worktree writes `SCC-294-jira-token-guide/` as the root instead of `Sudo_Hatter_Command/`, and
  `check_maps.py` then reports the AUTO block STALE. Restored by hand; proved by cp → regen → diff →
  restore that line 77 was the only delta.
- **Four `acli` flag shapes are not what they look like:** `comment create --key … --body-file`
  (not `comment --key`) · `comment update --key … --id … --body-file` · `comment delete --key … --id`
  · `attachment delete --id` **only**, no `--key` · `workitem view <KEY>` — the key is **positional**.

## Gates

Run **bare, never piped** — a pipe hands back the last stage's exit code, so a red gate reads as
green. Each line carries its own exit, at `ae5dc26`, the landing tree:

```
lane_qualify.py (REAL diff, 5 paths)          -> LIGHT   (re-armed at close-out, not just at intent)
task_preflight.py --fetch --expect-key SCC-294 -> exit 1  VERDICT: clear to close out and merge
                                                 LANE: LOCAL · GATES: ARMED · 0 error(s), 2 warning(s)
run_all.py                                    -> exit 0, 52/52 files passed
workflow_lint.py --toolkit-only               -> exit 0, 0 error(s), 0 warning(s), 8 info
check_maps.py --depth3-only --strict          -> exit 0, silent
link + anchor check (7 changed .md)           -> 121 relative links, 0 broken
sop_currency.classify() over all 8 changed paths -> no usage surface, so no SOP hunk and no `[sop-ok]`
```

**The SOP answer was computed, not assumed.** `docs/migrations/` is not in `sop_currency._SURFACES`
(`.agents/commands/` · `.agents/rules/` · `.agents/scripts/{git-hooks,*.py,*.ps1}` · `.githooks/`),
so the armed `commit-msg` gate had nothing to demand — and none of the three commits carries
`[sop-ok]`, which is the check that the exemption was real rather than opted out of.

**The two preflight warnings, in full:**

- `children` — **the board could not be read**, because `acli` cannot reach the credential store
  inside the sandbox. That is transport, never a verdict on the ticket (`.agents/rules/jira.md`).
  Checked by hand at Step 4, where the board is provably reachable because the next command
  transitions the ticket: SCC-294 is a **Task with no subtasks**.
- `worktree` — expected since SCC-62. Step 5 prunes it.

## ⚠ Landing order — another lane landed while this PR was open

**PR #57 came back `CONFLICTING`, and the lane was not wrong** — SCC-281 landed as PR #56 while this
PR sat waiting. One file overlapped, and it is the predictable one: both lanes appended a row to
`_artifacts/_main/INDEX.md` for the same date. That is the exact collision SCC-271 recorded, and the
resolution is the same — **keep BOTH rows, newest first**, and count rather than eyeball:

```
common base a634c35   -> 179 rows
this lane             -> 180  (+1, SCC-294)
origin/main           -> 180  (+1, SCC-281)
resolution (c149f71)  -> 181
```

`INDEX.md` was the **only** file the two lanes both touched; everything else auto-merged. Dropping
either row is the silent, unrecoverable index loss the guard exists to stop.

⭐ **SCC-281 also edited this very door and `task_preflight.py`** — which is why the door tells you to
check that the copy you are following is current. Its change is Step 4's rider-evidence clause (a
rider must be *named in a commit subject* to be declared); this lane declares no riders, so it does
not apply. Read, not assumed.

**Gates re-run bare on the ABSORBED tree** (`c149f71`), because the tree that merges is not the tree
they first ran on:

```
run_all.py                                    -> exit 0, 52/52 files passed
workflow_lint.py --toolkit-only               -> exit 0, 0 error(s), 0 warning(s), 8 info
check_maps.py --depth3-only --strict          -> exit 0, silent
task_preflight.py --fetch --expect-key SCC-294 -> exit 1  VERDICT: clear to close out and merge
                                                 origin/main fully absorbed · 0 error(s), 2 warning(s)
```

⭐ The re-run preflight also refused to let the neighbour's evidence stand in for this lane's:
*"verdict stamp(s) exist only in 1 walkthrough(s) whose `task.yaml` does not declare SCC-294 —
foreign evidence never gates this lane; the full gate runs."* Exactly right.

## What was NOT done

**The PC has no copy of this token.** The Windows half of the guide is written and is marked
**⛔ NOT RUN** in the guide's own "What has actually been run" table, rather than presented as
verified. A guide that claims coverage it does not have is worse than one that admits the gap.

## Your Actions

- [x] The merge itself — lands via this branch's PR.
- [x] The guide, the three kit edits and the repo-map regen — done and listed above.
- [x] The live token — created, stored, verified on both paths, expiry recorded on SCC-294.
- [x] The `_artifacts/_main/INDEX.md` collision with SCC-281 — resolved on this lane, both rows
      kept, counted (179 → 181).

**Nothing is owed on this ticket.** SCC-294's deliverable is the *document*, and the document is
written, verified against a live token and attached to the ticket.

**Storing the token on the PC is a follow-on, deliberately not held here.** It is not this ticket's
work, and a checkbox in an artifacts folder is the wrong place to keep it: the durable trail is the
⛔ **NOT RUN** row inside the guide's own "What has actually been run" table, which is the page the
PC reader has open at exactly the moment it matters. When that machine comes up, create nothing new —
the token exists and is good until **2027-08-21** — store it and run `acli jira auth login`.

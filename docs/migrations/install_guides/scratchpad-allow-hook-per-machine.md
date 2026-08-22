# Scratchpad allow-hook — pointing it at THIS machine's scratchpad

**What this buys you:** `/smh-code-review` and every other verification lane build a throwaway
runtime harness under the session scratchpad and then run it. Without this hook that is **twenty-odd
approval prompts per review**, for a directory that is deleted when the session ends. With it, they
run without a single prompt.

**Why it is a per-machine setup step and not just code.** The hook grants only commands whose every
argument sits inside *this session's* scratchpad — so it has to know where that is. Every machine
puts it somewhere different, and the path cannot be committed: one machine's root would point every
other machine's hook at a directory that does not exist there. It is the same class as
`core.hooksPath` and `~/.zshenv` — **set once per machine, never travels.**

> ⛔ **Nothing here is optional on a machine you want the benefit on, and nothing here is dangerous
> to skip.** With no configuration the hook falls silent and you get the ordinary approval prompts
> you had before it existed. It has exactly two behaviours: grant, or say nothing.

---

## Do I need this?

| Machine | Do this? |
|---|---|
| **macOS** | **No.** The built-in root already matches (`/tmp/claude-<uid>/…`, and `/private/tmp` likewise). Run §1 anyway if you want to confirm it. |
| **Windows** | **Yes**, and read §3 first — there is one thing about your machine that decides whether this can work at all. |
| **Linux** | Probably not — the built-in root is POSIX and matches `/tmp/claude-<uid>/…`. Confirm with §1. |

---

## 1. Measure your scratchpad root — never assume it

⭐ **This whole guide is measurement.** The one thing you must not do is type a path you believe is
right into a file that grants permission.

**Where the path comes from:** every Claude Code session is told its own scratchpad directory. Ask
the agent in a live session on that machine:

> *What is your scratchpad directory? Print the literal path.*

You get something shaped like this:

```
/private/tmp/claude-501/-Users-sudohatter-Sudo-Hatter-Command/697c65e7-…-ad474d8bb76d/scratchpad
└──────── the ROOT ────────┘└──── project ────┘└────────── session id ──────────┘└── leaf ──┘
```

**The root is everything before the project segment.** In the example above:
`/private/tmp/claude-501`. That is the only part you record — the project, session and `scratchpad`
segments are enforced by the hook itself and must not appear in your file.

---

## 2. Write it down

One line, absolute, no quotes, no trailing slash:

```bash
printf '%s\n' '/your/measured/root' > .claude/scratchpad-root
```

The file is gitignored. `#` comments and blank lines are allowed; the first real line wins.

**What the hook will refuse to honour** — in every case it falls back to the built-in POSIX root,
which on Windows means no grant at all, so a bad entry costs you the benefit and never safety:

| Refused | Why |
|---|---|
| a relative path (`tmp/claude-x`) | the hook only ever accepts absolute paths |
| a native Windows path (`C:\Users\…`) | see §3 — a backslash cannot appear in a grantable command |
| `/` or `//` | that would make `/<anything>/<session>/scratchpad` grantable |
| a one-segment root (`/tmp`) | too close to the above to be worth allowing |
| anything containing a shell metacharacter | those are refused inside commands too, so a root carrying one could never match |

⭐ **It widens the ROOT and nothing else.** Whatever you name still has to be followed by
`/<project>/<session-id>/scratchpad`, pinned to the session actually asking, and normalised so `..`
cannot walk out of it. A wrong entry cannot grant more than one session's disposable directory.

---

## 3. Windows — read this before §2

⛔ **One property of your machine decides whether this hook can help at all: how the Bash tool
spells paths.**

The hook refuses any command containing a backslash — `\` is one of the shell metacharacters it
bans, because a command that needs escaping is a command whose token boundaries are a matter of
interpretation. It also requires every path to be absolute and start with `/`. So:

| How your Bash tool spells the scratchpad | Can this hook grant it? |
|---|---|
| `/c/Users/you/AppData/Local/Temp/claude-…` (git-bash / MSYS) | **Yes.** Record `/c/Users/you/AppData/Local/Temp/claude-…` as your root |
| `C:/Users/you/AppData/Local/Temp/claude-…` (forward slashes, drive letter) | **No** — it does not start with `/`. Stop here and open a ticket; this needs a code change, not a config value |
| `C:\Users\you\AppData\Local\Temp\claude-…` (native) | **No** — the backslashes are refused by rule 1. Same: a ticket, not a config value |

**Measure it, don't guess.** In a session on that machine, ask the agent to run a command that
touches the scratchpad and show you the **literal command string** it used. That string is the
answer — not what the path looks like in Explorer.

> ⓘ **Why the answer is not just "support backslashes".** The hook is an allow-list of *shapes*, and
> it got that way after five review lenses found twelve escapes in the deny-list it replaced — every
> one something the parser did not recognise as a path. Backslash is both an escape character and a
> separator on Windows, so admitting it re-opens exactly the class of ambiguity the ban exists to
> remove. That is a design change with its own review, not a line in a config file.

---

## 4. Verify — the hook itself answers

Do not trust the setup until you have watched it grant. Substitute your own root and the session id
from the same session you asked in:

```bash
# PC: `python`, not `python3`
ROOT=/your/measured/root
SID=<the session id from that same session>
printf '{"tool_name":"Bash","tool_input":{"command":"cat %s/-P/%s/scratchpad/probe.txt"},"session_id":"%s"}' \
  "$ROOT" "$SID" "$SID" | python3 .agents/hooks/allow-scratchpad.py
```

| What you see | What it means |
|---|---|
| a JSON line containing `"permissionDecision": "allow"` | ✅ **working.** Prompts for scratchpad commands are gone on this machine |
| nothing at all, exit 0 | the root does not match. Re-read §1 — the usual cause is including the project or session segment in the root |
| a traceback | ⛔ **a bug, report it.** This hook is wrapped so that it can only ever remove a prompt, never add one; a traceback means that wrapper has a hole. It had exactly one, on Windows, and SCC-267 is the fix |

**Then confirm it refuses what it must**, which matters more than the grant:

```bash
printf '{"tool_name":"Bash","tool_input":{"command":"rm -rf %s/-P/%s/scratchpad/../../../.."},"session_id":"%s"}' \
  "$ROOT" "$SID" "$SID" | python3 .agents/hooks/allow-scratchpad.py
```

Silence is the correct answer. Anything else, stop and report it.

---

## 5. What you are trusting, stated plainly

The hook's guarantee is **"every argument in this command resolves inside a directory that dies with
this session"** — *not* "this command is safe".

⛔ **`bash <scratchpad>/x.sh` runs whatever the agent wrote there, and that is deliberate.** Writing
into the scratchpad was never gated, so the script's *contents* were never what this hook reviews —
only the act of running it. That is the trade the hook makes, and it is the only one it makes.

**Related:**
[`.agents/hooks/allow-scratchpad.py`](../../../.agents/hooks/allow-scratchpad.py) — the hook, whose
docstring carries the six rules and the review history ·
[the safety-net table](../../_scc_sops_prds/workflows_testing_SOP.md#the-checks-and-what-each-one-refuses)
— what every check in this system refuses to let happen

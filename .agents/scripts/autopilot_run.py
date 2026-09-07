"""autopilot_run.py - launch ONE headless `claude -p` child for ONE workflow step (SCC-430).

    autopilot_run.py run --door /cicd-dev-story-tests --seat cheshire-cat --cwd <worktree>
                         --args "AGY_AVIATIONCHAT 14.2" --key AVCH-140 --stage 2
                         [--model ...] [--effort ...] [--budget-usd 8] [--run-cap-usd 40]
                         [--fork-of <session-id>] [--session-id <uuid>]
                         [--review] [--dev-model ... --dev-base-url ...] [--no-post]

The autopilot's lead session (the March Hare) calls this once per workflow step. The child runs
the EXISTING door by name, comes back with a structured result, and the step lands on the Jira
ticket as a comment. Nothing here decides what a step should do - that is the door's job, and
the door is a file the operator edits.

  -- WHY A SCRIPT AND NOT A PROMPT ----------------------------------------------------------
This file holds the handful of rules an LLM cannot be trusted to keep about itself, because
breaking each of them looks like success from the inside:

  1. A DOOR IS A FILE. Resolve it, and exit non-zero BEFORE spending anything if it is not
     there. The retired engine (SCC-70) built a prompt saying the instructions were above it
     and then ran with nothing above it; the child improvised a whole story and reported done.
  2. THE DOOR TRAVELS AS A NAME. This script never reads a door's body, never carries a rule's
     text, and never spells out a seat's character. The child loads all three from the same
     files the operator edits, at the moment of use, through the same launcher skill a chat
     uses - so an edited door is live on the next launch with no sync step anywhere.
  3. A RESULT IS STRUCTURED OR IT IS A FAILURE. `--json-schema` SHAPES a reply; it does not
     guarantee one (measured in the S0 spike: `result` came back as a bare string). Anything
     that does not parse, or that parses without a `status`, is `failed`.
  4. A REVIEWER IS INDEPENDENT. The review child wears no seat, runs on the reviewing model,
     and runs in a session this runner has never issued. It may not fork - a fork inherits the
     author's context and, with it, the author's conclusions about their own work.
  5. THE CEILING IS OURS, NOT THE CLI'S. `--max-budget-usd` is a SOFT cap: it stops the next
     turn, not the current one. Measured, capped at $0.05: $0.496 and $0.296 actually spent.
     So the enforceable ceiling is `--run-cap-usd`, summed off the ledger before a launch.

  -- THREE MEASURED CLI FACTS THIS FILE IS SHAPED BY (S0 spike, CLI 2.1.263) -----------------
  * `--agents` IS NOT INHERITED BY A RESUME. A forked child whose seat is not re-passed prints
    "agent 'X' ... is no longer available ... Continuing with the default" and CARRIES ON. So
    `--agents` and `--agent` go on every launch, forks included (see `build_argv`).
  * A CHILD MUST BE HANDED A CLOSED STDIN or it stalls three seconds waiting for input that is
    never coming - once per step, every step.
  * A CHILD NEEDS A WRITABLE TRANSCRIPT STORE TO BE FORKABLE, and the sandbox denies the
    default one. `CLAUDE_CONFIG_DIR` moves it (see `child_home`); forking is worth 92%.

Stdlib only, Python 3.11, plain-ASCII console output (Windows consoles are cp1252) - same
constraints as its siblings. `claude` resolves from --claude, then $CLAUDE_BIN, then PATH, so
the tests can inject a stub.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

CENTRE = Path(__file__).resolve().parents[2]
JIRA_FEED = Path(__file__).resolve().parent / "jira_feed.py"

# ── Exit codes ────────────────────────────────────────────────────────────────
# 2 is a REFUSAL BY THIS SCRIPT and never a statement about the work - the same meaning it
# carries in `run_all.py` and the test harness. The lead reads these; a step that could not
# start must never be confused with a step that ran and found a problem.
OK, FAILED, REFUSED, NEEDS_HUMAN, BLOCKED = 0, 1, 2, 3, 4
BY_STATUS = {"done": OK, "failed": FAILED, "needs_human": NEEDS_HUMAN, "blocked": BLOCKED}

# ── The result contract (design 2.3 rule 3) ───────────────────────────────────
# One of the five things this runner owns. It describes the SHAPE of an answer, which is a
# property of the machinery, not of any workflow - so it lives here and nowhere else.
RESULT_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": ["done", "blocked", "needs_human", "failed"]},
        "summary": {"type": "string"},
        "artifacts": {"type": "array", "items": {"type": "string"}},
        "question": {"type": "string"},
        "evidence": {
            "type": "object",
            "properties": {"sha": {"type": "string"}, "suite_totals": {"type": "string"}},
        },
        "denials": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["status", "summary"],
}

# The reviewing model is pinned here rather than passed, so "the reviewer ran on the author's
# model" is not something a caller can bring about by forgetting a flag.
REVIEW_MODEL = "claude-opus-5"
DEFAULT_MODEL = "claude-sonnet-5"

DEFAULT_HOME = Path.home() / ".local" / "share" / "autopilot-claude-home"


def die(msg: str, code: int = REFUSED) -> "int":
    print(f"[REFUSED] {msg}", file=sys.stderr)
    return code


# ── The door ──────────────────────────────────────────────────────────────────

def resolve_door(name: str, cwd: Path, centre: Path = CENTRE) -> Path | None:
    """Where the door lives, or None. EXISTENCE ONLY - this function never opens the file.

    ⛔ That restraint is the whole of rule 2 and it is one keystroke from being lost. The
    moment this reads the body, somebody downstream will pass the body to the child "so it
    cannot be misunderstood", and from then on the autopilot is running a private copy of a
    door the operator thinks he is editing. Its own test greps this function for a read.

    The story's own tree wins over the centre: a project that ships its own version of a door
    is running that one in chat, and the child has to agree with the chat or the autopilot is
    testing something nobody else uses.
    """
    stem = name.strip().lstrip("/")
    if not stem:
        return None
    for base in (cwd, centre):
        p = base / ".agents" / "commands" / f"{stem}.md"
        if p.is_file():
            return p
    return None


# ── The seat ──────────────────────────────────────────────────────────────────

def _frontmatter(master: Path) -> dict:
    """The master's YAML header as flat key -> string. No parser, and none wanted.

    These headers are six lines of `key: value` written by a sync script, and `sync-agents.ps1`
    reads them with `Get-Content -TotalCount 12` - so anything a real YAML parser could handle
    that this cannot is already unreachable on the other side of the pipeline.
    """
    out: dict = {}
    lines = master.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return out
    for line in lines[1:]:
        if line.strip() == "---":
            break
        key, sep, val = line.partition(":")
        if sep and key.strip():
            out[key.strip()] = val.strip().strip('"').strip("'")
    return out


def render_seat(master: Path) -> dict:
    """The master's frontmatter as the JSON `--agents` wants. Deterministic, no clock, no id.

    ⛔ WHAT IS NOT IN HERE: a word of the seat's character. The `prompt` is a POINTER - it names
    the master and says to follow it. Everything the seat IS lives in that file, is read at the
    moment of use, and changes the next launch after the operator edits it. A rendered
    personality would be a second copy nobody remembers to update.

    ⛔ AND NO FILE IS WRITTEN. The seat is built in memory and handed to `--agents` on the
    command line. `.claude/agents/<seat>.md` was in an early draft and is withdrawn: a
    projection on disk is a copy that drifts, and the Zoo half already proved the pointer shape
    works (`.roomodes` roleDefinitions have always been pointers).
    """
    fm = _frontmatter(master)
    name = master.stem.replace("smh-team-", "")
    seat: dict = {
        "description": fm.get("description", name),
        "prompt": (f"Read {master.name} at .agents/commands/ from the repository root and do "
                   f"what it says, all of it - identity, doors, refusals. Team law: "
                   f".roo/rules/zoo-team.md. Front door: AGENTS.md. Do not invent the part."),
    }
    if fm.get("claude-tools"):
        seat["tools"] = [t.strip() for t in fm["claude-tools"].strip("[]").split(",") if t.strip()]
    if fm.get("claude-model"):
        seat["model"] = fm["claude-model"]
    return {name: seat}


# ── The launch ────────────────────────────────────────────────────────────────

def build_argv(*, claude: str, prompt: str, seat: dict | None, seat_name: str | None,
               model: str, session_id: str | None, fork_of: str | None,
               budget_usd: float | None, effort: str | None) -> list[str]:
    """The child's command line. Pure, ordered, and byte-stable for one seat.

    Byte-stability is not tidiness. It is what makes a cost regression legible: two launches
    of one seat that differ by a byte cannot share a prompt cache, and the bill goes up with
    nothing in the diff to explain it. `sort_keys=True` on the seat JSON is part of that.

    ⛔ `--agents` GOES ON EVERY LAUNCH, INCLUDING FORKS. It is defined per process and is not
    inherited through `--resume`; a fork without it announces the loss on stderr and then runs
    anyway, wearing the default identity with the default tools. Measured, spike table 2.

    ⛔ NEVER `--bare` - it skips hooks, LSP and plugins, and the door reaches the child THROUGH
    a generated launcher skill. A bare child cannot find the door at all.
    ⛔ NEVER `bypassPermissions` - a headless child is exactly the process that should not have
    it. `auto` denies instead of asking, the child reports the denial, and the harvest turns it
    into a permission row a human approves once.
    """
    argv = [claude, "-p", prompt,
            "--model", model,
            "--permission-mode", "auto",
            "--exclude-dynamic-system-prompt-sections",
            "--output-format", "json",
            "--json-schema", json.dumps(RESULT_SCHEMA, sort_keys=True)]
    if seat and seat_name:
        argv += ["--agents", json.dumps(seat, sort_keys=True), "--agent", seat_name]
    if effort:
        argv += ["--effort", effort]
    if budget_usd is not None:
        argv += ["--max-budget-usd", str(budget_usd)]
    if fork_of:
        argv += ["--resume", fork_of, "--fork-session"]
    elif session_id:
        argv += ["--session-id", session_id]
    return argv


def child_home(explicit: str | None) -> Path:
    """Where the child keeps its transcripts - and the reason forking works at all.

    ⛔ THE DEFAULT STORE IS UNWRITABLE UNDER THE SANDBOX, AND THE SYMPTOM NAMES SOMETHING ELSE.
    `~/.claude/projects` is deny-listed, so a sandboxed child runs perfectly, answers, and
    persists NOTHING; the next `--resume` then fails "No conversation found with session ID",
    which reads as "headless sessions cannot be forked". They can. Measured: with the store
    moved here, a fork cost $0.0020 against its parent's $0.0250 - 92% - inside the sandbox,
    with no settings change and no escalation.

    Two things have to be seeded, once, or every child dies at "Not logged in":
      * the OAuth credential, SYMLINKED and never copied - one secret, one file on disk;
      * the workspace trust flag, without which the repo's own tracked allow rows are ignored
        (and, measured, the prompt cache stops being read at all - a fork then saves nothing).
    """
    return Path(explicit or os.environ.get("AUTOPILOT_CLAUDE_HOME") or DEFAULT_HOME)


def seed_home(home: Path, workspaces: list[Path]) -> None:
    (home / "projects").mkdir(parents=True, exist_ok=True)
    real = Path.home() / ".claude" / ".credentials.json"
    link = home / ".credentials.json"
    if real.exists() and not link.exists():
        try:
            link.symlink_to(real)
        except OSError:                      # Windows without developer mode: fall back to PATH auth
            pass
    cfg = home / ".claude.json"
    try:
        data = json.loads(cfg.read_text(encoding="utf-8")) if cfg.exists() else {}
    except (OSError, json.JSONDecodeError):
        data = {}
    projects = data.setdefault("projects", {})
    for w in workspaces:
        projects.setdefault(str(w), {})["hasTrustDialogAccepted"] = True
    cfg.write_text(json.dumps(data, indent=2), encoding="utf-8")


def child_env(home: Path, *, dev_model: str | None, dev_base_url: str | None) -> dict:
    """The child's environment. The alternate model rides HERE, never in argv.

    A base URL on a command line ends up in `ps`, in a shell history and in any log that
    records an invocation. It is not a secret, but the key that follows it around usually is,
    and the habit is what matters.
    """
    env = {**os.environ, "CLAUDE_CONFIG_DIR": str(home), "PYTHONIOENCODING": "utf-8"}
    if dev_model:
        env["ANTHROPIC_MODEL"] = dev_model
    if dev_base_url:
        env["ANTHROPIC_BASE_URL"] = dev_base_url
    return env


def claude_bin(explicit: str | None) -> str | None:
    for cand in (explicit, os.environ.get("CLAUDE_BIN")):
        if cand:
            return cand
    return shutil.which("claude")


# ── The result ────────────────────────────────────────────────────────────────

def parse_result(stdout: str) -> dict:
    """The child's answer, or `failed` saying why. This function never raises.

    Three shapes arrive in practice and only the first is the good one: the CLI envelope with
    a `result` object; the envelope with `result` as a STRING the model wrote (the schema
    shapes, it does not guarantee); and something that is not JSON at all. The last two are
    `failed` - a step whose outcome cannot be read is not a step that succeeded, and defaulting
    to `done` is how a silent no-op gets recorded as work.
    """
    stdout = (stdout or "").strip()
    if not stdout:
        return {"status": "failed", "summary": "the child printed nothing"}
    try:
        envelope = json.loads(stdout)
    except json.JSONDecodeError:
        return {"status": "failed", "summary": f"stdout was not JSON: {stdout[:200]}"}
    if not isinstance(envelope, dict):
        return {"status": "failed", "summary": f"stdout was not an object: {stdout[:200]}"}

    inner = envelope.get("result")
    if isinstance(inner, str):
        try:
            inner = json.loads(inner)
        except json.JSONDecodeError:
            inner = None
    result = inner if isinstance(inner, dict) else envelope

    status = result.get("status")
    if status not in BY_STATUS:
        return {"status": "failed",
                "summary": f"no usable status in the reply: {str(result)[:200]}",
                "session_id": envelope.get("session_id"),
                "total_cost_usd": envelope.get("total_cost_usd")}
    out = dict(result)
    out.setdefault("summary", "")
    out["session_id"] = envelope.get("session_id") or result.get("session_id")
    out["total_cost_usd"] = envelope.get("total_cost_usd")
    out["usage"] = envelope.get("usage")
    return out


# ── The ledger ────────────────────────────────────────────────────────────────

def ledger_path(cwd: Path, explicit: str | None) -> Path:
    return Path(explicit) if explicit else cwd / "_artifacts" / "autopilot-ledger.json"


def read_ledger(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"steps": []}
    return data if isinstance(data, dict) and isinstance(data.get("steps"), list) else {"steps": []}


def spent(ledger: dict) -> float:
    return sum(float(s.get("total_cost_usd") or 0) for s in ledger.get("steps", []))


def seen_sessions(ledger: dict) -> set[str]:
    return {str(s.get("session_id")) for s in ledger.get("steps", []) if s.get("session_id")}


def append_ledger(path: Path, row: dict) -> None:
    ledger = read_ledger(path)
    ledger["steps"].append(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ledger, indent=2), encoding="utf-8")


# ── The step comment ──────────────────────────────────────────────────────────

def post_step(key: str, stage: str, result: dict, cwd: Path) -> bool:
    """Hand the step to `jira_feed.py step`. The ticket IS the handoff between children."""
    body = cwd / "_artifacts" / f"autopilot-step-{stage}.md"
    body.parent.mkdir(parents=True, exist_ok=True)
    body.write_text(json.dumps(result, indent=2), encoding="utf-8")
    feed = Path(os.environ.get("AUTOPILOT_JIRA_FEED") or JIRA_FEED)
    r = subprocess.run([sys.executable, str(feed), "step", "--key", key, "--stage", str(stage),
                        "--body-file", str(body), "--status", result.get("status", "failed")],
                       capture_output=True, text=True, errors="replace", encoding="utf-8")
    if r.returncode != 0:
        print(f"[FAIL] the step could not be recorded on {key}: "
              f"{(r.stderr or r.stdout or '').strip()[:300]}", file=sys.stderr)
        return False
    return True


# ── main ──────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Launch one headless claude child for one step.")
    ap.add_argument("verb", choices=["run"])
    ap.add_argument("--door", required=True, help="/name of the door the child runs")
    ap.add_argument("--seat", help="Wonderland seat, e.g. cheshire-cat (never with --review)")
    ap.add_argument("--cwd", required=True, help="the story worktree the child runs in")
    ap.add_argument("--args", default="", help="arguments passed to the door verbatim")
    ap.add_argument("--key", help="the Jira key the step is recorded on")
    ap.add_argument("--stage", default="0")
    ap.add_argument("--model")
    ap.add_argument("--effort", choices=["low", "medium", "high", "xhigh", "max"])
    ap.add_argument("--budget-usd", type=float, help="per-child cap. SOFT - see --run-cap-usd")
    ap.add_argument("--run-cap-usd", type=float, help="the ceiling this runner does enforce")
    ap.add_argument("--session-id")
    ap.add_argument("--fork-of", help="a pack session to fork; the seat is re-passed")
    ap.add_argument("--review", action="store_true", help="the independent review child")
    ap.add_argument("--dev-model")
    ap.add_argument("--dev-base-url")
    ap.add_argument("--claude", help="path to the claude CLI (else $CLAUDE_BIN, else PATH)")
    ap.add_argument("--child-home", help="the child's CLAUDE_CONFIG_DIR")
    ap.add_argument("--ledger")
    ap.add_argument("--no-post", action="store_true", help="do not touch the ticket")
    a = ap.parse_args(argv)

    cwd = Path(a.cwd).resolve()
    if not cwd.is_dir():
        return die(f"--cwd is not a directory: {cwd}")

    # 1 · the door, before anything is spent.
    door = resolve_door(a.door, cwd)
    if door is None:
        return die(f"no door named '{a.door}' under .agents/commands/ in {cwd} or {CENTRE}. "
                   f"Nothing was launched.")

    ledger = ledger_path(cwd, a.ledger)
    book = read_ledger(ledger)

    # 2 · the ceiling this runner can actually hold (the CLI's is soft).
    already = spent(book)
    if a.run_cap_usd is not None and already >= a.run_cap_usd:
        return die(f"this run has spent ${already:.2f} of its ${a.run_cap_usd:.2f} ceiling. "
                   f"Nothing was launched.")

    # 3 · the reviewer's independence.
    session_id = a.session_id
    if a.review:
        if a.fork_of:
            return die("a review child may not fork - it would inherit the author's context "
                       "and its conclusions. Launch it fresh.")
        if a.seat:
            return die("a review child wears no seat. Its independence is the point.")
        if session_id and session_id in seen_sessions(book):
            return die(f"session {session_id} is already in this run's ledger; a reviewer runs "
                       f"in a session this runner has never issued.")
        seat, seat_name = None, None
        model = a.model or REVIEW_MODEL
    else:
        if not a.seat:
            return die("--seat is required unless --review")
        master = CENTRE / ".agents" / "commands" / f"smh-team-{a.seat}.md"
        if not master.is_file():
            return die(f"no seat master at {master}")
        rendered = render_seat(master)
        seat_name = next(iter(rendered))
        seat = rendered
        model = a.model or _frontmatter(master).get("claude-model") or DEFAULT_MODEL

    if not a.fork_of and not session_id:
        session_id = str(uuid.uuid4())

    binary = claude_bin(a.claude)
    if not binary:
        return die("claude not found. Pass --claude, set CLAUDE_BIN, or put it on PATH.")

    home = child_home(a.child_home)
    seed_home(home, [cwd, CENTRE])

    argv_child = build_argv(claude=binary, prompt=f"{a.door} {a.args}".strip(),
                            seat=seat, seat_name=seat_name, model=model,
                            session_id=session_id, fork_of=a.fork_of,
                            budget_usd=a.budget_usd, effort=a.effort)

    # ⛔ stdout and stderr SEPARATELY. The CLI puts warnings on stderr - including the one that
    # says a seat was dropped - and a merged stream turns every one of them into a parse error
    # that reads as "the child failed", hiding what actually happened.
    # ⛔ stdin CLOSED. Otherwise every launch waits three seconds for input nobody is sending.
    proc = subprocess.run(argv_child, capture_output=True, text=True, errors="replace",
                          encoding="utf-8", cwd=str(cwd), stdin=subprocess.DEVNULL,
                          env=child_env(home, dev_model=a.dev_model, dev_base_url=a.dev_base_url))
    result = parse_result(proc.stdout)
    if proc.stderr and proc.stderr.strip():
        print(proc.stderr.strip()[:2000], file=sys.stderr)

    append_ledger(ledger, {
        "stage": a.stage, "door": a.door, "seat": seat_name, "review": bool(a.review),
        "session_id": result.get("session_id") or session_id,
        "status": result.get("status"), "total_cost_usd": result.get("total_cost_usd"),
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    })

    print(json.dumps(result, indent=2))
    code = BY_STATUS.get(str(result.get("status")), FAILED)
    if a.key and not a.no_post and not post_step(a.key, a.stage, result, cwd):
        return FAILED
    return code


if __name__ == "__main__":
    raise SystemExit(main())

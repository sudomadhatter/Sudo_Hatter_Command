"""The autopilot runner's negative control (SCC-430, acceptance row B).

`autopilot_run.py` launches one headless `claude -p` child per workflow step. It is the piece
of the autopilot that holds the rules **an LLM must not be trusted with** - so every case here
is a refusal, and every one of them was seen RED against a naive stub that did the plausible
thing instead. A runner whose tests only prove the happy path is a runner that will one day
launch a child with no instructions and bill for it.

  -- WHERE EACH CASE COMES FROM ------------------------------------------------------------
  DOOR   design 2.3 rule 1, and SCC-70's actual failure: the retired engine built a prompt
         saying "your instructions live in the command above" and ran with NOTHING above it.
         The child burned a full context answering from improvisation and reported success.
         The test is therefore not "exit 2" - it is **zero `claude` invocations**. An exit 2
         printed after the money is spent is the bug, not the fix.
  STATUS design 2.3 rule 3. The S0 spike measured `--json-schema` SHAPING the reply without
         guaranteeing it: with the schema applied, `result` came back as a bare string, not
         an object. So "it parsed" is not "it conformed", and anything without a `status` is
         `failed` - never `done` by default, which is how a silent no-op reads as success.
  REVIEW design 2.3 rule 5. The review child is the one place the robot could mark its own
         homework: resume the session that wrote the code, and the reviewer inherits the
         author's context and its conclusions. `zoo-team.md`'s review gate says a reviewer is
         independent; this is that gate carried into the runner instead of waived by it.
  DRIFT  design 11.3. The autopilot owns NO copy of any door, rule or seat. The moment a
         sentence of workflow law is pasted into this script, the operator edits the master
         and the robot keeps running the old one - silently, because both files still exist.
  FLAGS  the S0 spike's own measurements. `--bare` skips hooks and plugins (so the door's
         launcher skill never loads); `bypassPermissions` hands a headless child the keys.
         Byte-stability is what makes a cost regression READABLE - if two builds of the same
         seat differ, the prompt cache cannot be reasoned about at all.
  FORK   spike finding 1, and it is the nastiest of them: a resumed child whose `--agents` is
         not re-passed prints "agent 'X' ... is no longer available ... Continuing with the
         default" and **keeps going**. Nothing fails. Every later step looks normal and runs
         with the wrong identity, the wrong model and the wrong tool restrictions.
  CAP    spike finding 2: `--max-budget-usd` is a SOFT cap - it stops the next turn, not the
         current one. Probes capped at $0.05 spent $0.496 and $0.296 (10x, 6x). The only
         ceiling the runner can actually enforce is its own, read off the ledger BEFORE it
         launches anything.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from _harness import SCRIPTS, Cases, TempDir, fake_exe, path_entry, utf8_env

sys.path.insert(0, str(SCRIPTS))
import autopilot_run as ar  # noqa: E402

RUNNER = SCRIPTS / "autopilot_run.py"
CENTRE = SCRIPTS.parent.parent          # the repo root this test file lives in


def run(*args: str, env: dict | None = None) -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(RUNNER), *args], capture_output=True, text=True,
                       errors="replace", encoding="utf-8", env=env or utf8_env())
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def claude_stub(bindir: Path, log: Path, reply: dict) -> str:
    """A REAL executable standing in for `claude`, recording every invocation.

    ⛔ It APPENDS one line per launch rather than overwriting. The whole point of the DOOR
    case is counting launches, and a stub that overwrites cannot tell "never ran" from "ran
    once and was overwritten by the second". `fake_exe` handles the Windows half (a shebang
    script is not an executable there - SCC-321).
    """
    body = (
        "import json, sys, pathlib\n"
        f"log = pathlib.Path({str(log)!r})\n"
        "with log.open('a', encoding='utf-8') as fh:\n"
        "    fh.write(json.dumps(sys.argv[1:]) + '\\n')\n"
        f"print({json.dumps(json.dumps(reply))})\n"
    )
    return fake_exe(bindir, "claude", body)


def env_for(tmp: Path, stub: str, bindir: str = "bin") -> dict:
    """The runner's environment with the stub in front and its config dir INSIDE the temp tree.

    ⛔ `AUTOPILOT_CLAUDE_HOME` is not decoration. The runner seeds a child config dir (that is
    what makes a sandboxed fork possible at all) and its default is `~/.local/share/...`. A
    suite that leaves it alone writes into the operator's home on every run, which is both a
    side effect no test should have and a way for one case to see another's leftovers.
    """
    return utf8_env(CLAUDE_BIN=stub,
                    AUTOPILOT_CLAUDE_HOME=str(tmp / "child-home"),
                    PATH=path_entry(tmp / bindir) + os.pathsep + os.environ.get("PATH", ""))


def launches(log: Path) -> list[list[str]]:
    if not log.exists():
        return []
    return [json.loads(ln) for ln in log.read_text(encoding="utf-8").splitlines() if ln.strip()]


def workspace(root: Path, *, doors: tuple[str, ...] = ("cicd-dev-story-tests",)) -> Path:
    """A story worktree shaped like the real thing: it owns doors and an `_artifacts` tree."""
    cmds = root / ".agents" / "commands"
    cmds.mkdir(parents=True, exist_ok=True)
    for d in doors:
        (cmds / f"{d}.md").write_text(f"---\ndescription: {d}\n---\n\n# {d}\n", encoding="utf-8")
    (root / "_artifacts").mkdir(exist_ok=True)
    return root


c = Cases("autopilot_run - the runner's negative control")


# ── DOOR ──────────────────────────────────────────────────────────────────────
with TempDir() as tmp:
    if c.block("DOOR - a missing door exits BEFORE any claude call"):
        ws = workspace(tmp / "ws")
        log = tmp / "launches.jsonl"
        stub = claude_stub(tmp / "bin", log, {"status": "done", "summary": "ok"})
        env = env_for(tmp, stub)

        rc, out = run("run", "--door", "/no-such-door", "--seat", "gnat",
                      "--cwd", str(ws), "--key", "AVCH-140", "--stage", "2", env=env)
        c.check("D1 a missing door exits 2", rc == 2, f"rc={rc}: {out.strip()[:200]}")
        c.check("D2 ...and claude was NEVER launched", launches(log) == [],
                f"{len(launches(log))} launch(es) - the money is already spent")
        c.check("D3 ...and the refusal names the door it could not find",
                "no-such-door" in out, out.strip()[:200])

        # ANTI-VACUITY: the same call with a door that EXISTS must reach the stub, or D2
        # passes because nothing works at all.
        rc2, out2 = run("run", "--door", "/cicd-dev-story-tests", "--seat", "gnat",
                        "--cwd", str(ws), "--key", "AVCH-140", "--stage", "2",
                        "--no-post", env=env)
        c.check("D4 anti-vacuity - a door that EXISTS does launch claude",
                len(launches(log)) == 1, f"{len(launches(log))} launch(es): {out2.strip()[:200]}")

        # D5 · THE FALLBACK THAT DEFEATED THE REFUSAL (row F, AVCH-138). `resolve_door` used to
        # accept a door found in the RUNNER's own repo root. But the child loads its door through
        # a launcher skill resolved from ITS cwd, so a door in the command centre is invisible to
        # a child running in a thin project - and the check passed anyway, launching exactly the
        # nothing-above-it child rule 1 exists to prevent. `--cwd` here owns no `.agents` at all,
        # while the real centre one directory up owns every door in this repo.
        bare = tmp / "thin-project"
        (bare / ".agents").mkdir(parents=True, exist_ok=True)   # tier-2 law, no commands/
        rc3, out3 = run("run", "--door", "/cicd-code-review", "--seat", "gnat",
                        "--cwd", str(bare), "--key", "AVCH-140", "--stage", "1", env=env)
        c.check("D5 a door the CHILD cannot reach is refused, not launched from the centre",
                rc3 == 2 and len(launches(log)) == 1,
                f"rc={rc3}, launches={len(launches(log))}: {out3.strip()[:200]}")
        c.check("D6 ...and the refusal says WHICH mistake it was",
                "exists at" in out3 and "cwd" in out3, out3.strip()[:300])


# ── EVIDENCE ──────────────────────────────────────────────────────────────────
# Harvested from the retired v2 reference's war stories (row G). Theirs: on a CLEAN pass the
# reviewer did all the judgment work, found nothing to fix, and dropped the mechanical
# deliverable - because it was buried among the instructions. The lesson they drew is the one
# that transfers: separate the judgment WORK from the DELIVERABLE and make the deliverable
# un-collapsible. v3's exposure is the same shape - the schema requires only status+summary, so
# a reviewer could answer `done` with no sha while the door tells the lead to post "PASS at <sha>".
with TempDir() as tmp:
    if c.block("EVIDENCE - a review verdict without its sha is not a verdict"):
        ws = workspace(tmp / "ws")
        sid = "22222222-2222-2222-2222-222222222222"

        # V1 · the collapse: a clean-looking `done` carrying no evidence at all.
        log1 = tmp / "a.jsonl"
        stub1 = claude_stub(tmp / "bin1", log1, {"status": "done", "summary": "PASS, all clean"})
        rc, out = run("run", "--door", "/cicd-dev-story-tests", "--review",
                      "--cwd", str(ws), "--key", "AVCH-140", "--stage", "4",
                      "--session-id", sid, "--no-post",
                      env=env_for(tmp, stub1, bindir="bin1"))
        c.check("V1 a reviewer's `done` with no evidence.sha is FAILED, not accepted",
                rc == 1, f"rc={rc}: {out.strip()[:200]}")
        c.check("V2 ...and it says why, so the lead does not invent a sha",
                "evidence.sha" in out and "ONE tree" in out, out.strip()[:300])

        # V3 · ANTI-VACUITY. The same reviewer WITH a sha must pass, or V1 is just "reviews
        # always fail" and proves nothing about the missing field.
        log2 = tmp / "b.jsonl"
        stub2 = claude_stub(tmp / "bin2", log2,
                            {"status": "done", "summary": "PASS", "evidence": {"sha": "abc1234"}})
        rc2, out2 = run("run", "--door", "/cicd-dev-story-tests", "--review",
                        "--cwd", str(ws), "--key", "AVCH-140", "--stage", "4",
                        "--session-id", "33333333-3333-3333-3333-333333333333", "--no-post",
                        env=env_for(tmp, stub2, bindir="bin2"))
        c.check("V3 anti-vacuity - the same verdict WITH a sha is accepted",
                rc2 == 0, f"rc={rc2}: {out2.strip()[:200]}")

        # V4 · and the requirement is NARROW. A seated Gnat lookup owes no sha and must not be
        # failed for lacking one - a universal rule here would break every read-only child.
        log3 = tmp / "c.jsonl"
        stub3 = claude_stub(tmp / "bin3", log3, {"status": "done", "summary": "the note says X"})
        rc3, out3 = run("run", "--door", "/cicd-dev-story-tests", "--seat", "gnat",
                        "--cwd", str(ws), "--key", "AVCH-140", "--stage", "1", "--no-post",
                        env=env_for(tmp, stub3, bindir="bin3"))
        c.check("V4 a non-review child owes no sha - the rule does not leak",
                rc3 == 0, f"rc={rc3}: {out3.strip()[:200]}")


# ── LOCK ──────────────────────────────────────────────────────────────────────
# Harvested from the retired opencode engine (row G), whose own notes record the gap: "nothing
# used to stop a double-run of the SAME story". Two children in one worktree interleave their
# edits and BOTH report success - there is no error anywhere, which is why a lock and not a
# convention. The stale case matters just as much: a lock that outlives its holder locks a
# ticket forever, and the cure would be a human deleting a dotfile they have never heard of.
with TempDir() as tmp:
    if c.block("LOCK - one child per ticket, and a dead holder does not jam it"):
        ws = workspace(tmp / "ws")
        log = tmp / "launches.jsonl"
        stub = claude_stub(tmp / "bin", log, {"status": "done", "summary": "ok"})
        env = env_for(tmp, stub)
        lock = ws / "_artifacts" / ".autopilot-avch-140.lock"

        def go() -> tuple[int, str]:
            return run("run", "--door", "/cicd-dev-story-tests", "--seat", "gnat",
                       "--cwd", str(ws), "--key", "AVCH-140", "--stage", "1",
                       "--no-post", env=env)

        # L1 · a LIVE holder is a refusal, and nothing is spent proving it.
        lock.parent.mkdir(parents=True, exist_ok=True)
        lock.write_text(json.dumps({"pid": os.getpid(), "at": "2026-09-07T00:00:00+00:00"}),
                        encoding="utf-8")
        rc, out = go()
        c.check("L1 a ticket already being worked is refused, with nothing launched",
                rc == 2 and launches(log) == [],
                f"rc={rc}, launches={len(launches(log))}: {out.strip()[:200]}")
        c.check("L2 ...and the refusal names the holder rather than blaming the door",
                "already running" in out and str(os.getpid()) in out, out.strip()[:200])

        # L3 · a STALE holder (the process is gone) is stolen, not obeyed. Take a real pid and
        # let it exit - inventing a "probably dead" number is a guess that can collide.
        dead = subprocess.Popen([sys.executable, "-c", "pass"])
        dead.wait()
        lock.write_text(json.dumps({"pid": dead.pid, "at": "2026-09-07T00:00:00+00:00"}),
                        encoding="utf-8")
        rc2, out2 = go()
        c.check("L3 a dead holder's lock is stale - the ticket is not locked forever",
                rc2 == 0 and len(launches(log)) == 1,
                f"rc={rc2}, launches={len(launches(log))}: {out2.strip()[:200]}")

        # L4 · and a completed run leaves nothing behind for its own next step to trip on.
        c.check("L4 the lock is released when the child returns",
                not lock.exists(), f"{lock} still on disk after a clean run")


# ── STATUS ────────────────────────────────────────────────────────────────────
with TempDir() as tmp:
    if c.block("STATUS - a result without `status` is failed, never done"):
        ws = workspace(tmp / "ws")
        log = tmp / "launches.jsonl"
        # A well-formed CLI envelope whose `result` carries no status - exactly the shape the
        # spike measured coming back from a schema'd launch.
        stub = claude_stub(tmp / "bin", log,
                           {"session_id": "s-1", "total_cost_usd": 0.01,
                            "result": "I had a look and it seems fine.", "is_error": False})
        env = env_for(tmp, stub)
        rc, out = run("run", "--door", "/cicd-dev-story-tests", "--seat", "gnat",
                      "--cwd", str(ws), "--key", "AVCH-140", "--stage", "2",
                      "--no-post", env=env)
        c.check("S1 a result with no status exits non-zero", rc != 0, f"rc={rc}")
        c.check("S2 ...and the runner reports it as failed",
                '"status": "failed"' in out or "'status': 'failed'" in out, out.strip()[:300])

    if c.block("STATUS - unparseable stdout is failed"):
        ws = workspace(tmp / "ws2")
        log2 = tmp / "launches2.jsonl"
        garbage = fake_exe(tmp / "bin2", "claude",
                           "import sys, pathlib, json\n"
                           f"pathlib.Path({str(log2)!r}).open('a').write('[]\\n')\n"
                           "print('Warning: something happened')\n"
                           "print('not json at all')\n")
        env2 = env_for(tmp, garbage, bindir="bin2")
        rc, out = run("run", "--door", "/cicd-dev-story-tests", "--seat", "gnat",
                      "--cwd", str(ws), "--key", "AVCH-140", "--stage", "2",
                      "--no-post", env=env2)
        c.check("S3 stdout that is not JSON is failed, not a traceback",
                rc != 0 and "failed" in out, f"rc={rc}: {out.strip()[:300]}")
        c.check("S4 ...and it does not die with a stack trace",
                "Traceback" not in out, out.strip()[:300])


# ── REVIEW ────────────────────────────────────────────────────────────────────
with TempDir() as tmp:
    if c.block("REVIEW - the reviewer refuses a session the runner has already issued"):
        ws = workspace(tmp / "ws")
        log = tmp / "launches.jsonl"
        # ⛔ A reviewer's reply carries the sha it judged. A bare `done` here is the deliverable
        # collapsing (see the EVIDENCE block), and this stub used to answer exactly that - which
        # is what turned R6 red when that rule landed. A stub that cannot answer legally is a
        # stub that tests the wrong thing.
        stub = claude_stub(tmp / "bin", log,
                           {"status": "done", "summary": "ok", "evidence": {"sha": "deadbee"}})
        env = env_for(tmp, stub)
        ledger = ws / "_artifacts" / "autopilot-ledger.json"
        ledger.write_text(json.dumps(
            {"steps": [{"stage": 1, "session_id": "seen-abc", "total_cost_usd": 0.02}]}),
            encoding="utf-8")

        rc, out = run("run", "--door", "/cicd-dev-story-tests", "--cwd", str(ws),
                      "--key", "AVCH-140", "--stage", "3", "--review",
                      "--session-id", "seen-abc", "--no-post", env=env)
        c.check("R1 a review on a session id in the ledger exits 2", rc == 2, f"rc={rc}")
        c.check("R2 ...before launching anything", launches(log) == [],
                f"{len(launches(log))} launch(es)")

        rc, out = run("run", "--door", "/cicd-dev-story-tests", "--cwd", str(ws),
                      "--key", "AVCH-140", "--stage", "3", "--review",
                      "--fork-of", "seen-abc", "--no-post", env=env)
        c.check("R3 a review that forks another session exits 2", rc == 2, f"rc={rc}")
        c.check("R4 ...before launching anything", launches(log) == [],
                f"{len(launches(log))} launch(es)")

        rc, out = run("run", "--door", "/cicd-dev-story-tests", "--cwd", str(ws),
                      "--key", "AVCH-140", "--stage", "3", "--review",
                      "--seat", "gnat", "--no-post", env=env)
        c.check("R5 a review wearing a seat exits 2", rc == 2, f"rc={rc}: {out.strip()[:200]}")

        # ANTI-VACUITY: a clean review must actually run, or R1/R3/R5 pass on a broken flag.
        rc, out = run("run", "--door", "/cicd-dev-story-tests", "--cwd", str(ws),
                      "--key", "AVCH-140", "--stage", "3", "--review",
                      "--session-id", "fresh-xyz", "--no-post", env=env)
        c.check("R6 anti-vacuity - an unseen, unforked, seatless review DOES launch",
                rc == 0 and len(launches(log)) == 1,
                f"rc={rc}, {len(launches(log))} launch(es): {out.strip()[:200]}")
        if launches(log):
            argv = launches(log)[0]
            c.check("R7 ...and it carries no seat", "--agents" not in argv and "--agent" not in argv,
                    " ".join(argv)[:300])


# ── DRIFT ─────────────────────────────────────────────────────────────────────
if c.block("DRIFT - the runner carries no door, rule or seat text"):
    src = RUNNER.read_text(encoding="utf-8")
    src_flat = " ".join(src.split())

    def fragments(paths) -> list[str]:
        """Headings and sentences over 40 characters, normalised to single spaces.

        Long enough that shared vocabulary ("the operator", "exit 2") cannot match by
        accident; short enough that a pasted paragraph cannot hide by being trimmed.
        """
        out: list[str] = []
        for p in paths:
            try:
                body = p.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for line in body.splitlines():
                line = line.strip().lstrip("#>-*| ").strip()
                for frag in line.split(". "):
                    frag = " ".join(frag.split()).strip()
                    if len(frag) > 40:
                        out.append(frag)
        return out

    corpus = fragments(sorted((CENTRE / ".agents" / "commands").glob("*.md")))
    corpus += fragments(sorted((CENTRE / ".agents" / "rules").glob("*.md")))

    # N0 · ANTI-VACUITY. An empty corpus makes N1 pass by asking nothing at all.
    c.check("N0 the corpus really has workflow prose to check against",
            len(corpus) >= 500, f"{len(corpus)} fragments")
    stolen = sorted({f for f in corpus if f in src_flat})
    c.check("N1 no door or rule sentence appears in the runner",
            not stolen, f"{len(stolen)} pasted fragment(s), first: {stolen[:2]}")

    # N2 · the runner passes the door's NAME, never its body - the mechanism behind N1.
    c.check("N2 the runner never reads a door's body - it checks only that the file is there",
            "read_text" not in src.split("def resolve_door")[-1].split("\ndef ")[0])


# ── FLAGS ─────────────────────────────────────────────────────────────────────
if c.block("FLAGS - never bare, never bypass, and stdin is closed"):
    seat = ar.render_seat(CENTRE / ".agents" / "commands" / "smh-team-gnat.md")
    argv = ar.build_argv(claude="claude", prompt="/cicd-dev-story-tests AGY 14.2",
                         seat=seat, seat_name="gnat", model="claude-haiku-4-5-20251001",
                         session_id="11111111-1111-1111-1111-111111111111",
                         fork_of=None, budget_usd=8.0, effort=None)
    flat = " ".join(argv)
    c.check("F1 --bare is never passed", "--bare" not in argv, flat[:300])
    c.check("F2 bypassPermissions is never passed", "bypassPermissions" not in flat, flat[:300])
    c.check("F3 --permission-mode is auto",
            "--permission-mode" in argv and argv[argv.index("--permission-mode") + 1] == "auto",
            flat[:300])
    c.check("F4 the result comes back as JSON",
            "--output-format" in argv and argv[argv.index("--output-format") + 1] == "json", flat[:300])
    # ⛔ The one that makes F3 mean anything. `--permission-mode auto` decides what needs asking;
    # this decides who is asked, and the DEFAULT is `host` - an SDK host or a
    # --permission-prompt-tool, neither of which exists here. Without it an unattended child that
    # hits a prompt has nobody to answer it. Measured absent on CLI 2.1.258, present on 2.1.263 -
    # which is the real reason the door floors the CLI at 2.1.259 (row F, AVCH-138).
    c.check("F3b nobody is left to answer a prompt - it becomes an explicit deny",
            "--permission-prompts" in argv
            and argv[argv.index("--permission-prompts") + 1] == "none", flat[:300])
    c.check("F5 the seat is delivered by --agents + --agent (spike table 1, 42% cheaper)",
            "--agents" in argv and "--agent" in argv, flat[:300])
    c.check("F6 the model is pinned (spike finding 4: unpinned children inherit opus-5[1m])",
            "--model" in argv, flat[:300])
    c.check("F7 the door reaches the child as a NAME, not a body",
            "/cicd-dev-story-tests AGY 14.2" in argv, flat[:300])
    # Spike finding 5: without this every launch stalls three seconds on stdin.
    c.check("F8 stdin is closed at the launch site (else every child waits 3s for input)",
            "stdin=subprocess.DEVNULL" in RUNNER.read_text(encoding="utf-8"))

if c.block("FLAGS - two builds of one seat are byte-identical"):
    seat = ar.render_seat(CENTRE / ".agents" / "commands" / "smh-team-gnat.md")
    kw = dict(claude="claude", prompt="/cicd-dev-story-tests AGY 14.2", seat=seat,
              seat_name="gnat", model="claude-haiku-4-5-20251001",
              session_id="11111111-1111-1111-1111-111111111111",
              fork_of=None, budget_usd=8.0, effort=None)
    a, b = ar.build_argv(**kw), ar.build_argv(**kw)
    c.check("B1 two builds are identical", a == b,
            f"first difference at {next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), '?')}")
    seat2 = ar.render_seat(CENTRE / ".agents" / "commands" / "smh-team-gnat.md")
    c.check("B2 ...and so is the seat JSON, across two renders",
            json.dumps(seat, sort_keys=True) == json.dumps(seat2, sort_keys=True), "")


# ── FORK ──────────────────────────────────────────────────────────────────────
if c.block("FORK - a fork re-passes the seat (spike finding 1)"):
    seat = ar.render_seat(CENTRE / ".agents" / "commands" / "smh-team-gnat.md")
    argv = ar.build_argv(claude="claude", prompt="/cicd-dev-story-tests AGY 14.2",
                         seat=seat, seat_name="gnat", model="claude-haiku-4-5-20251001",
                         session_id=None, fork_of="parent-pack-id",
                         budget_usd=8.0, effort=None)
    flat = " ".join(argv)
    c.check("K1 a fork resumes its parent", "--resume" in argv and "--fork-session" in argv, flat[:300])
    c.check("K2 ...and STILL carries --agents, or the seat is silently dropped",
            "--agents" in argv and "--agent" in argv, flat[:300])
    c.check("K3 a fork never also pins a fresh session id",
            "--session-id" not in argv, flat[:300])


# ── CAP ───────────────────────────────────────────────────────────────────────
with TempDir() as tmp:
    if c.block("CAP - the run-level ceiling is checked before launching"):
        ws = workspace(tmp / "ws")
        log = tmp / "launches.jsonl"
        stub = claude_stub(tmp / "bin", log, {"status": "done", "summary": "ok"})
        env = env_for(tmp, stub)
        ledger = ws / "_artifacts" / "autopilot-ledger.json"
        ledger.write_text(json.dumps({"steps": [
            {"stage": 1, "session_id": "a", "total_cost_usd": 4.0},
            {"stage": 2, "session_id": "b", "total_cost_usd": 4.5}]}), encoding="utf-8")

        rc, out = run("run", "--door", "/cicd-dev-story-tests", "--seat", "gnat",
                      "--cwd", str(ws), "--key", "AVCH-140", "--stage", "3",
                      "--run-cap-usd", "8", "--no-post", env=env)
        c.check("C1 a run already over its ceiling exits 2", rc == 2, f"rc={rc}: {out.strip()[:200]}")
        c.check("C2 ...before launching anything (the CLI cap is soft - spike finding 2)",
                launches(log) == [], f"{len(launches(log))} launch(es)")
        c.check("C3 ...and the refusal prints what has been spent",
                "8.5" in out, out.strip()[:200])

        rc, out = run("run", "--door", "/cicd-dev-story-tests", "--seat", "gnat",
                      "--cwd", str(ws), "--key", "AVCH-140", "--stage", "3",
                      "--run-cap-usd", "20", "--no-post", env=env)
        c.check("C4 anti-vacuity - under the ceiling it launches",
                len(launches(log)) == 1, f"{len(launches(log))} launch(es): {out.strip()[:200]}")


# ── HANDOFF ───────────────────────────────────────────────────────────────────
with TempDir() as tmp:
    if c.block("HANDOFF - the runner really does hand the step to jira_feed"):
        # The seam between the runner and the ticket verb, which neither file's own tests
        # cover: `test_autopilot_run` stubs the feed away with --no-post and
        # `test_jira_feed` calls `step` directly. A signature drift between them would leave
        # both suites green and every autopilot step unrecorded on the board - and the ticket
        # IS the handoff, so an unrecorded step is a step the next child never learns about.
        ws = workspace(tmp / "ws")
        log = tmp / "launches.jsonl"
        feedlog = tmp / "feed.jsonl"
        stub = claude_stub(tmp / "bin", log,
                           {"session_id": "sess-xyz", "total_cost_usd": 0.03,
                            "usage": {"input_tokens": 9},
                            "result": json.dumps({"status": "needs_human",
                                                  "summary": "the epic branch moved",
                                                  "question": "rebase or hold?",
                                                  "artifacts": ["walkthrough.md"]})})
        feed = fake_exe(tmp / "bin", "feed_stub",
                        "import json, sys, pathlib\n"
                        f"pathlib.Path({str(feedlog)!r}).open('a', encoding='utf-8').write("
                        "json.dumps(sys.argv[1:]) + '\\n')\n"
                        "sys.exit(0)\n")
        env = utf8_env(CLAUDE_BIN=stub, AUTOPILOT_JIRA_FEED=feed,
                       AUTOPILOT_CLAUDE_HOME=str(tmp / "child-home"),
                       PATH=path_entry(tmp / "bin") + os.pathsep + os.environ.get("PATH", ""))

        rc, out = run("run", "--door", "/cicd-dev-story-tests", "--seat", "gnat",
                      "--cwd", str(ws), "--key", "AVCH-140", "--stage", "2", env=env)
        called = launches(feedlog)
        c.check("H1 the feed was called exactly once", len(called) == 1, f"{called}")
        argv = called[0] if called else []
        c.check("H2 ...with the `step` verb", argv[:1] == ["step"], f"{argv[:3]}")
        for flag in ("--key", "--stage", "--door", "--seat", "--status",
                     "--summary-file", "--session", "--usage-file", "--apply"):
            c.check(f"H3 ...carrying {flag}", flag in argv, f"{argv}")
        c.check("H4 ...the child's real status, not a default",
                "needs_human" in argv, f"{argv}")
        c.check("H5 ...and the child's real session id", "sess-xyz" in argv, f"{argv}")
        if "--summary-file" in argv:
            body = Path(argv[argv.index("--summary-file") + 1]).read_text(encoding="utf-8")
            c.check("H6 the summary file carries the child's words and its question",
                    "the epic branch moved" in body and "rebase or hold?" in body, body[:200])
            c.check("H7 ...and its artifacts, which change what the next step does",
                    "walkthrough.md" in body, body[:200])
        c.check("H8 needs_human exits 3, distinct from done(0) and failed(1)",
                rc == 3, f"rc={rc}: {out.strip()[:200]}")

    if c.block("HANDOFF - a step that could not be recorded is a FAILED step"):
        # The work may well have happened. The handoff did not, so the next child would start
        # blind - and a runner that shrugs at that is how a run silently loses a step.
        ws = workspace(tmp / "ws2")
        log2 = tmp / "launches2.jsonl"
        stub = claude_stub(tmp / "bin2", log2, {"status": "done", "summary": "all green"})
        deadfeed = fake_exe(tmp / "bin2", "feed_dead",
                            "import sys\n"
                            "print('jira-feed: NOT recorded', file=sys.stderr)\n"
                            "sys.exit(2)\n")
        env2 = utf8_env(CLAUDE_BIN=stub, AUTOPILOT_JIRA_FEED=deadfeed,
                        AUTOPILOT_CLAUDE_HOME=str(tmp / "child-home2"),
                        PATH=path_entry(tmp / "bin2") + os.pathsep + os.environ.get("PATH", ""))
        rc, out = run("run", "--door", "/cicd-dev-story-tests", "--seat", "gnat",
                      "--cwd", str(ws2 := ws), "--key", "AVCH-140", "--stage", "2", env=env2)
        c.check("H9 a child that succeeded but was not recorded exits 1 (failed)",
                rc == 1, f"rc={rc}: {out.strip()[:200]}")
        c.check("H10 ...and says which ticket it could not reach",
                "AVCH-140" in out, out.strip()[:300])
        # ANTI-VACUITY: the SAME call with --no-post must succeed, or H9 passes because the
        # runner is broken rather than because the record failed.
        rc, out = run("run", "--door", "/cicd-dev-story-tests", "--seat", "gnat",
                      "--cwd", str(ws2), "--key", "AVCH-140", "--stage", "2",
                      "--no-post", env=env2)
        c.check("H11 anti-vacuity - the same run with --no-post is done(0)",
                rc == 0, f"rc={rc}: {out.strip()[:200]}")


# ── SEAT ──────────────────────────────────────────────────────────────────────
if c.block("SEAT - the rendered JSON matches the master's own frontmatter, all six"):
    masters = sorted((CENTRE / ".agents" / "commands").glob("smh-team-*.md"))

    def header(p: Path) -> dict:
        """The master's frontmatter, parsed HERE and not by the code under test.

        ⛔ Calling `ar._frontmatter` would make every case below a tautology: a renderer that
        misread its input would be compared against the same misreading. Twelve lines of
        duplicated parsing is the price of the test measuring anything at all.
        """
        fm, body = {}, p.read_text(encoding="utf-8").splitlines()
        if not body or body[0].strip() != "---":
            return fm
        for line in body[1:]:
            if line.strip() == "---":
                break
            k, sep, v = line.partition(":")
            if sep:
                fm[k.strip()] = v.strip().strip('"').strip("'")
        return fm

    # N0 · ANTI-VACUITY, twice over: six masters must exist, and they must NOT all say the same
    # thing - a renderer that returned one constant would otherwise pass every case below.
    c.check("T0 all six Wonderland masters are present", len(masters) == 6,
            f"{[m.stem for m in masters]}")
    models = {header(m).get("claude-model") for m in masters}
    c.check("T0b ...and the seats do not all carry one model", len(models) > 1, f"{sorted(models)}")

    for m in masters:
        fm, seat_name = header(m), m.stem.replace("smh-team-", "")
        rendered = ar.render_seat(m)
        c.check(f"T1 {seat_name}: rendered under its own name", list(rendered) == [seat_name],
                f"{list(rendered)}")
        # ⛔ `.get`, NEVER `rendered[seat_name]`. A renderer that keys the seat wrongly would
        # raise KeyError here, the FILE would die mid-run, and the harness prints no `FAILED:`
        # line at all - so the mutation sweep cannot attribute the kill and every case after
        # this point is never scored. Found by mutant M3 (`return {"seat": seat}`), which came
        # back "SWEEP ERROR" rather than a kill. An empty dict makes T2-T7 FAIL, which is what
        # a test is for.
        got = rendered.get(seat_name) or {}
        c.check(f"T2 {seat_name}: description is the master's, verbatim",
                got.get("description") == fm.get("description"))
        c.check(f"T3 {seat_name}: model is the master's `claude-model`",
                got.get("model") == fm.get("claude-model"), f"{got.get('model')}")
        c.check(f"T4 {seat_name}: tools are the master's `claude-tools`",
                got.get("tools") == [t.strip() for t in fm.get("claude-tools", "").strip("[]").split(",") if t.strip()],
                f"{got.get('tools')}")
        # T5 · the prompt is a POINTER: it must name the master and carry no character of its own.
        prompt = got.get("prompt", "")
        c.check(f"T5 {seat_name}: the prompt names the master file",
                m.name in prompt, prompt[:120])
        c.check(f"T6 {seat_name}: ...and names the seat by its mode-name",
                bool(fm.get("mode-name")) and fm["mode-name"] in prompt, prompt[:120])
        c.check(f"T7 {seat_name}: ...and carries nothing else - it is a pointer, not a persona",
                0 < len(prompt) < 260, f"{len(prompt)} chars")

    # T8 · the header must stay inside the window `sync-agents.ps1` reads, or the seat silently
    # vanishes from `.roomodes` with no error anywhere.
    for m in masters:
        head = m.read_text(encoding="utf-8").splitlines()[:12]
        c.check(f"T8 {m.stem}: the frontmatter still closes inside 12 lines",
                any(ln.strip() == "---" for ln in head[1:]), f"{len(head)} lines read")

if c.block("SEAT - no agent file is ever written"):
    agents_dir = CENTRE / ".claude" / "agents"
    before = sorted(p.name for p in agents_dir.glob("*")) if agents_dir.exists() else None
    for m in sorted((CENTRE / ".agents" / "commands").glob("smh-team-*.md")):
        ar.render_seat(m)
    after = sorted(p.name for p in agents_dir.glob("*")) if agents_dir.exists() else None
    c.check("W1 rendering six seats creates no .claude/agents/ projection", before == after,
            f"before={before} after={after}")
    c.check("W2 ...and the renderer contains no write verb at all",
            not any(v in RUNNER.read_text(encoding="utf-8").split("def render_seat")[-1]
                    .split("\ndef ")[0] for v in ("write_text", "mkdir", "open(")),
            "render_seat writes to disk; the seat is built in memory and passed on argv")


raise SystemExit(c.finish())

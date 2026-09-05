"""memory_probe.py must be a gate that can FAIL, in both directions (SCC-401).

`memory_probe.py` executes shell strings read out of tracked markdown, inside the suite, on every
machine. Its denylist is the only thing standing between "a memory carries its own falsifier" and
"the suite runs whatever the last author typed". Until this file existed the whole module was
covered by four `c.check` calls inside `test_memory_store.py`, and the review measured what that
bought: shrinking `_BANNED_CMDS` to `("rm",)`, deleting BOTH redirection rules, making `probes_of`
read the entire file instead of the frontmatter, and ignoring `run_one`'s timeout each left the
suite at `-- 51/51 passed --`.

⛔ SO THE DENYLIST IS TESTED AS A TABLE, IN BOTH DIRECTIONS. A refuse-only table is half a gate:
tighten a regex and every legitimate probe in the store starts failing with nothing to catch it,
which is how `mac-sudo-command` — an ntfy TOPIC — was once read as the verb `sudo`. Every row below
is one machine-checkable claim about what this runner will and will not execute.

⛔ AND THE BOUNDARY IS PINNED AS A DECISION, NOT LEFT AS AN ACCIDENT. `sh -c "rm …"`,
`python3 -c "…"` and `find … -delete` are ALLOWED, on purpose: the store is reviewed, tracked text
and the probe's author is its own reviewer, so the denylist's job is to stop a mistake, not an
adversary. Those rows sit in ALLOW so that anyone who later decides the boundary should move has to
move a test that says why, rather than discover the hole the way this review did.
"""
from __future__ import annotations

import importlib.util
import sys
import time
from pathlib import Path

from _harness import SCRIPTS, Cases, TempDir, run_script

spec = importlib.util.spec_from_file_location("memory_probe", SCRIPTS / "memory_probe.py")
mp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mp)


# ── The denylist table ────────────────────────────────────────────────────────
# One row per claim. `REFUSE` rows must never run; `ALLOW` rows must never be blocked.

REFUSE: list[tuple[str, str]] = [
    # every banned verb, bare, at the start of the string
    *[(f"{v} something", f"bare `{v}`") for v in mp._BANNED_CMDS],
    # ...and every banned git sub-verb
    *[(f"git {v}", f"`git {v}`") for v in mp._BANNED_GIT],
    # command POSITION - a banned verb after each separator the shell honours
    ("test -f x; rm x", "after `;`"),
    ("test -f x && rm x", "after `&&`"),
    ("test -f x || rm x", "after `||`"),
    ("ls | tee /tmp/f", "after a pipe"),
    ("echo `rm x`", "inside backticks"),
    ("echo $(rm x)", "inside $()"),
    ("(rm x)", "inside a subshell"),
    ("test -f x\nrm x", "on the next line"),
    # elevation and wrappers - the verb is still what executes
    ("sudo rm -rf /", "behind sudo"),
    ("sudo ls", "sudo itself, even carrying something harmless"),
    ("env rm -rf /tmp/x", "behind env"),
    ("env FOO=1 rm /tmp/x", "behind env with an assignment"),
    ("xargs rm < /tmp/list", "behind xargs"),
    ("command rm x", "behind command"),
    ("exec rm x", "behind exec"),
    ("nohup rm x", "behind nohup"),
    ("time rm x", "behind time"),
    ("nice rm x", "behind nice"),
    ("stdbuf -o0 rm x", "behind stdbuf with a flag"),
    ("\\rm -rf /tmp/x", "backslash-escaped to dodge an alias"),
    # `git -C <path>` is `git` run somewhere else, not a different command
    ("git -C /tmp/repo push", "git -C <path> push"),
    ("git --git-dir=/tmp/x/.git commit -m y", "git --git-dir=… commit"),
    # ⛔ EVERY redirect that writes a file. The first cut spared any NUMBERED fd, so an explicit
    # `1>` wrote a file while reading as read-only (SCC-401 review).
    ("echo hi > /tmp/f", "plain >"),
    ("echo hi >> /tmp/f", "appending >>"),
    ("echo hi 1> /tmp/f", "explicit fd 1"),
    ("echo hi 1>> /tmp/f", "explicit fd 1, appending"),
    ("echo hi 2> /tmp/f", "stderr to a file is still a write"),
    ("grep -q x f >| /tmp/f", "clobber-override >|"),
    # mutation carried in a FLAG, where the command-position rules cannot see it
    ("find . -name '*.md' -delete", "find's own -delete"),
    ("find . -name x -exec rm {} +", "rm behind find -exec"),
    ("sed -i s/a/b/ f.md", "sed in place"),
    ("perl -pi -e s/a/b/ f", "perl in place"),
    ("git restore .agents/rules/jira.md", "git's own replacement for checkout"),
    ("git switch main", "the other replacement for checkout"),
]

ALLOW: list[tuple[str, str]] = [
    # read-only shapes the store uses or an author will reach for
    ("grep -q microsoft-standard-WSL2 /proc/version", "the machine-model probe"),
    ("test -x ~/.claude/notify.sh && grep -q 'mac-sudo-command' .agents/scripts/zoo_notify.py",
     "a two-clause probe naming the ntfy topic"),
    ("! printf 'a\\n' | grep -qv a", "the ugrep inversion probe"),
    ("grep -q 'JIRA_API_TOKEN' ~/.profile", "a probe reading a dotfile"),
    ("test -e ~/.codex/AGENTS.md", "a plain existence probe"),
    # ⛔ THE FALSE-POSITIVE CLASS THAT ACTUALLY HAPPENED: a hyphenated identifier is not a verb.
    ("grep -q 'mac-sudo-command' .agents/scripts/zoo_notify.py", "`sudo` inside a topic NAME"),
    ("grep -q 'remove' README.md", "a banned-ish word as a search TERM"),
    ("grep -rn 'rm -rf' docs/", "a banned verb inside a quoted pattern"),
    # ordinary read-only shapes an author will reach for
    ("ls -1 _artifacts/_memory", "a listing"),
    ("test 5 -ge 3", "an arithmetic test - `-ge`, never `>=`"),
    ("grep -c foo f 2>&1", "2>&1 duplicates an fd; it does not write a file"),
    ("git status --porcelain", "a read-only git verb"),
    ("git ls-files -s Projects/", "another read-only git verb"),
    ("command -v python3", "`command -v` is the portable `which`"),
    # ⛔ THE STATED BOUNDARY. These RUN, by decision - see this file's docstring.
    # A nested shell or an interpreter can do anything; catching them needs an ALLOWLIST of
    # observation verbs, which is a different design. Pinned here so the line is a DECISION.
    ('sh -c "rm -rf /tmp/x"', "STATED BOUNDARY: a nested shell is not caught"),
    ("python3 -c 'import os'", "STATED BOUNDARY: an interpreter is not caught"),
]

MEMO = "---\nname: {name}\ndescription: d\nmetadata:\n  type: reference\n{probe}---\n\n{body}\n"


def memo(store: Path, name: str, probe: str | None = None, body: str = "a fact") -> None:
    store.mkdir(parents=True, exist_ok=True)
    (store / f"{name}.md").write_text(
        MEMO.format(name=name, probe=f'  probe: "{probe}"\n' if probe else "", body=body),
        encoding="utf-8")


def main() -> int:
    c = Cases("memory_probe")

    if c.block("SCC-401 P1 · refuse_reason - the denylist, both directions"):
        missed = [(cmd, why) for cmd, why in REFUSE if mp.refuse_reason(cmd) is None]
        c.check(f"P1a every mutating shape is REFUSED ({len(REFUSE)} rows)",
                missed == [], f"ran anyway: {missed[:6]}")
        blocked = [(cmd, why) for cmd, why in ALLOW if mp.refuse_reason(cmd) is not None]
        c.check(f"P1b every read-only shape is ALLOWED ({len(ALLOW)} rows)",
                blocked == [], f"wrongly refused: {blocked[:6]}")
        c.check("P1c the refusal NAMES the verb it caught, so the author can fix it",
                "`rm`" in (mp.refuse_reason("rm -rf /tmp/x") or ""),
                mp.refuse_reason("rm -rf /tmp/x") or "no reason")
        # Both halves of the table have to be able to FAIL, or P1a/P1b assert nothing.
        c.check("P1d CONTROL: the table is not vacuous - REFUSE and ALLOW are both populated",
                len(REFUSE) >= 50 and len(ALLOW) >= 15, f"{len(REFUSE)}/{len(ALLOW)}")

    if c.block("SCC-401 P2 · probes_of - the frontmatter boundary is the safety property"):
        c.check("P2a a probe in the frontmatter is read",
                mp.probes_of('---\nname: x\nmetadata:\n  probe: "true"\n---\n\nbody\n') == ["true"], "")
        c.check("P2b quotes are stripped, single or double",
                mp.probes_of("---\nprobe: 'test -e x'\n---\n\nb\n") == ["test -e x"], "")
        c.check("P2c an unquoted value is read as written",
                mp.probes_of("---\nprobe: test -e x\n---\n\nb\n") == ["test -e x"], "")
        # ⛔ THE ONE THAT MATTERS: `probe:` is documented in README.md and in the memory rule, so
        # memories WILL quote it in prose. Reading the body would execute a documentation example.
        c.check("P2d ⛔ `probe:` in the BODY is never executed",
                mp.probes_of('---\nname: x\n---\n\nSee `probe: rm -rf /` in the rule.\n') == [],
                "a documentation example became a command")
        c.check("P2e a file with no frontmatter yields nothing",
                mp.probes_of("no frontmatter here\nprobe: rm -rf /\n") == [], "")
        c.check("P2f an UNTERMINATED frontmatter block yields nothing",
                mp.probes_of('---\nprobe: "rm -rf /"\n') == [],
                "a half-written file must not be trusted as frontmatter")
        c.check("P2g an empty probe value is None, not an empty command",
                mp.probes_of('---\nprobe: ""\n---\n\nb\n') == [], "")

        # ⛔ A memory may carry SEVERAL falsifiers - the machine model states five checkable facts
        # and the first cut could only ever run one of them (SCC-401 review).
        c.check("P2h ⛔ every `probe:` in the frontmatter is read, in order - not just the first",
                mp.probes_of("---\nprobe: 'true'\nname: x\nprobe: 'test -e /tmp'\n---\n\nb\n")
                == ["true", "test -e /tmp"], "")

    if c.block("SCC-401 P3 · names_a_path - what makes a MISSING probe an audit candidate"):
        c.check("P3a a path written AS CODE is a path claim",
                mp.names_a_path("---\nname: x\n---\n\nlives at `/mnt/c/Sudo_Hatter_Command`\n"), "")
        # ⛔ The two false-positive classes measured on the real store (SCC-401 review): a slash in
        # PROSE is not a path, and a REST route is not a disk path. 35 of 37 "candidates" were these.
        c.check("P3g ⛔ slashes BETWEEN code spans are prose, not a path",
                not mp.names_a_path("---\nname: x\n---\n\n`AdminScope`/JWT/`scoped_user_query` bind it\n"),
                "prose read as a filesystem path")
        c.check("P3h ⛔ a REST route is not a disk path",
                not mp.names_a_path("---\nname: x\n---\n\nit needs `PUT /rest/api/3/issue/{key}`\n"),
                "a URL route read as a filesystem path")
        c.check("P3i CONTROL: ...while a real path claim in the same file still counts",
                mp.names_a_path("---\nname: x\n---\n\nthe token lives in `~/.config/acli/`\n"), "")
        c.check("P3b a `~/` path is too",
                mp.names_a_path("---\nname: x\n---\n\nthe cache is `~/.gemini/config`\n"), "")
        c.check("P3c prose naming no path is NOT a candidate",
                not mp.names_a_path("---\nname: x\n---\n\nprefer prose to bullets.\n"), "")
        # The frontmatter itself always carries `name:`/`description:`; a path there is not a claim.
        c.check("P3d a path in the FRONTMATTER alone does not count",
                not mp.names_a_path("---\nname: x\nprobe: \"test -e /tmp/x\"\n---\n\nprose.\n"), "")

    if c.block("SCC-401 P4 · run_one - every failure branch, and the timeout that must bite"):
        with TempDir() as d:
            cwd = Path(d)
            c.check("P4a exit 0 passes", mp.run_one("true", cwd) == (True, ""), "")
            ok, why = mp.run_one("exit 7", cwd)
            c.check("P4b a nonzero exit fails and reports the code",
                    not ok and "exit 7" in why, why)
            ok, why = mp.run_one("echo boom >&2; exit 2", cwd)
            c.check("P4c stderr's last line rides along, so the author sees WHY",
                    not ok and "boom" in why, why)
            t0 = time.monotonic()
            ok, why = mp.run_one("sleep 5", cwd, timeout=1)
            elapsed = time.monotonic() - t0
            # ⛔ A hanging probe would stall run_all on every machine with nothing to catch it.
            c.check("P4d ⛔ a hanging probe is KILLED at the timeout, not waited on",
                    not ok and "timed out" in why and elapsed < 3.5, f"{elapsed:.1f}s · {why}")
            ok, why = mp.run_one("true", Path(d) / "no" / "such" / "dir")
            c.check("P4e an unrunnable cwd fails with the OS reason, never a traceback",
                    not ok and "could not run" in why, why)
            ok, why = mp.run_one("rm -rf /tmp/x", cwd)
            c.check("P4f a refused probe is NOT executed - the refusal is the result",
                    not ok and "not read-only" in why, why)

    if c.block("SCC-401 P5 · run_store - classification, and the no-shell degradation"):
        with TempDir() as d:
            store = Path(d) / "_memory"
            memo(store, "t", probe="true")
            memo(store, "f", probe="exit 1")
            memo(store, "w", probe="rm -rf /tmp/x")
            memo(store, "pathy", body="it lives at `/mnt/c/Sudo_Hatter_Command`")
            memo(store, "prosey", body="prefer prose to bullets")
            (store / "MEMORY.md").write_text("- index\n", encoding="utf-8")
            (store / "README.md").write_text("- rules\n", encoding="utf-8")
            p, f, u = mp.run_store(store, Path(d))
            c.check("P5a a true probe passes and a false one fails, BY NAME",
                    [n for n, _ in p] == ["t.md"] and [n for n, _ in f] == ["f.md", "w.md"],
                    f"passed={p} failed={f}")
            c.check("P5b MEMORY.md and README.md are exempt - they carry no claim",
                    all(n not in ("MEMORY.md", "README.md") for n, _ in p + f + u), str(u))
            c.check("P5c an unprobed memory naming a path is an audit CANDIDATE; prose is not",
                    sorted(u) == [("pathy.md", "path-naming"), ("prosey.md", "")], str(sorted(u)))

            # ⛔ No POSIX shell (the Windows side of this PC) => UNGATED, never FAILED. A red no
            # author on that machine can fix is the cry-wolf gate this module exists to avoid.
            real_which = mp.shutil.which
            mp.shutil.which = lambda name: None if name == "bash" else real_which(name)
            try:
                p2, f2, u2 = mp.run_store(store, Path(d))
            finally:
                mp.shutil.which = real_which
            c.check("P5d ⛔ with no `bash`, probes are UNGATED - not failed",
                    p2 == [] and f2 == []
                    and sorted(n for n, w in u2 if w == mp.NO_SHELL) == ["f.md", "t.md", "w.md"],
                    f"passed={p2} failed={f2} unprobed={u2}")
            c.check("P5e CONTROL: ...and with `bash` back, the same store still reds",
                    [n for n, _ in mp.run_store(store, Path(d))[1]] == ["f.md", "w.md"], "")

    if c.block("SCC-401 P6 · the CLI contract - the standalone entry point INDEX.md advertises"):
        code, out = run_script("memory_probe.py", "--store", "no/such/store")
        c.check("P6a a missing store exits 2 and says so - never a silent 0",
                code == 2 and "no store at" in out, f"exit={code}\n{out}")
        with TempDir() as d:
            store = Path(d) / "_memory"
            memo(store, "t", probe="true")
            code, out = run_script("memory_probe.py", "--store", str(store), "--cwd", d)
            c.check("P6b an all-green store exits 0 and lists the PASS row",
                    code == 0 and "[PASS] t.md" in out, f"exit={code}\n{out}")
            code, out = run_script("memory_probe.py", "--store", str(store), "--cwd", d, "--quiet")
            c.check("P6c --quiet drops the PASS rows",
                    code == 0 and "[PASS]" not in out, f"exit={code}\n{out}")
            memo(store, "f", probe="exit 1")
            code, out = run_script("memory_probe.py", "--store", str(store), "--cwd", d, "--quiet")
            c.check("P6d ⛔ one failing probe exits 1, NAMES the file, and survives --quiet",
                    code == 1 and "[FAIL] f.md" in out, f"exit={code}\n{out}")

    if c.block("SCC-401 P7 · a probe must be able to FAIL - the review's headline finding"):
        with TempDir() as d:
            repo = Path(d)
            (repo / ".agents").mkdir()
            (repo / ".agents" / "commands").write_text("x", encoding="utf-8")
            import subprocess
            for args in (("init", "-q"), ("config", "user.email", "t@t.t"),
                         ("config", "user.name", "t"), ("add", "."), ("commit", "-qm", "seed")):
                subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)
            # ⛔ The exact shape 54 of the first 59 probes had: git guarantees the path, so the
            # probe exits 0 forever whatever happens to the memory's claim.
            why = mp.cannot_fail("test -e .agents/commands", repo)
            c.check("P7a ⛔ `test -e <tracked path>` is refused as unfalsifiable, and says why",
                    why is not None and "cannot fail" in why, str(why))
            c.check("P7b ...the same shape on an UNTRACKED path is fine - a per-machine artifact "
                    "is exactly what an existence probe is for",
                    mp.cannot_fail("test -e ~/.claude/notify.sh", repo) is None, "")
            c.check("P7c ...and a CONTENT grep of a tracked file is fine - it can go red",
                    mp.cannot_fail("grep -q codex .agents/scripts/sync-agents.ps1", repo) is None, "")

        body = "---\nname: x\n---\n\nthe topic is `mac-sudo-command` in zoo_notify.py\n"
        c.check("P7d a probe naming something the body names is anchored",
                mp.is_anchored(body, "grep -q 'mac-sudo-command' .agents/scripts/zoo_notify.py"), "")
        c.check("P7e ⛔ a probe naming nothing the body names is NOT - that is a green light "
                "with no wire behind it",
                not mp.is_anchored(body, "test -e .agents/jira.conf"), "")
        c.check("P7f a probe of only shell verbs anchors nothing",
                not mp.is_anchored(body, "true"), "")

    if c.block("SCC-401 P8 · scan_store reads text and runs NOTHING"):
        with TempDir() as d:
            store = Path(d) / "_memory"
            memo(store, "p", probe="exit 1")
            memo(store, "pathy", body="it lives at `/mnt/c/Sudo_Hatter_Command`")
            memo(store, "prosey", body="prefer prose to bullets")
            rows = mp.scan_store(store)
            c.check("P8a it returns (name, probes, names_a_path) for every memory",
                    sorted(rows) == [("p.md", ["exit 1"], False),
                                     ("pathy.md", [], True),
                                     ("prosey.md", [], False)], str(sorted(rows)))
            # A false probe would have FAILED had anything executed it; nothing did.
            c.check("P8b CONTROL: the false probe is reported, not run - scan_store executes none",
                    rows[0][1] == ["exit 1"], str(rows))

    if c.block("SCC-401 P9 · the YAML quoting trap this file was written to stop repeating"):
        # ⛔ probes_of strips outer quotes; it does NOT unescape YAML. A double-quoted scalar with
        # \" inside reaches bash with literal backslashes and fails for a reason no author can
        # see in the output. Write a probe containing quotes in SINGLE quotes. Measured SCC-401.
        dq = mp.probes_of('---\nprobe: "test \\"$(command -v grep)\\" = /usr/bin/grep"\n---\n\nb\n')[0]
        sq = mp.probes_of("---\nprobe: 'test \"$(command -v grep)\" = /usr/bin/grep'\n---\n\nb\n")[0]
        c.check("P9a a SINGLE-quoted probe survives intact",
                sq == 'test "$(command -v grep)" = /usr/bin/grep', repr(sq))
        c.check("P9b ⛔ a double-quoted probe keeps its backslashes - write quotes in single quotes",
                "\\" in (dq or ""), repr(dq))

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())

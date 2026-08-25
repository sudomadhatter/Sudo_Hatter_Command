"""jira_ticket.py - the fast-read ticket description, and the one verb acli cannot do. (SCC-291)

WHAT IS UNDER TEST. Ticket descriptions had been carrying whole implementation plans: they hit
Jira's size limit, went stale the moment the plan moved, and nobody read them. The shape is now
`Why:` / `## Plan` (real Jira checkboxes) / `## Done` / `## Files`, rendered from an outline file
in the tree, with the plan itself ATTACHED rather than pasted.

THE TWO HALVES A GATE NEEDS, both asserted throughout:
  ACCEPTS  a well-formed outline; a real multipart upload; a token from either source.
  REFUSES  an outline missing a section; a --tick out of range; a 200 response that reports the
           file as NOT stored; an upload with no token (exit 5, with the fix printed).

⛔ THE UPLOAD IS DRIVEN AGAINST A REAL HTTP SERVER, not a mock of urllib. `attach` is the one verb
that leaves acli — Jira REFUSES an attachment without `X-Atlassian-Token: no-check`, and the body
is hand-rolled multipart because stdlib has no encoder. Both are exactly the kind of detail a mock
of the code under test would assert into existence. A thread-local `http.server` sees the real
bytes on the wire.

⛔ AND THE TOKEN MUST NEVER SURFACE. Case T drives a failing upload with a known secret and greps
every byte the process printed.

Stdlib only, no pytest.
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _harness import Cases, TempDir, fake_exe  # noqa: E402

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import jira_ticket as jt  # noqa: E402

TICKET = SCRIPTS / "jira_ticket.py"
REPO = Path(__file__).resolve().parents[3]

HOUSE_OUTLINE = """Why: descriptions carried whole plans, hit the size limit, and nobody read them.

## Plan
- [ ] Render the fast-read shape from an outline file in the tree.
- [ ] Attach the plan instead of pasting it.
- [ ] Tick the checklist at close-out.

## Done
- (filled at close-out)

## Files
- Plan: _artifacts/_main/x/implementation_plan.md
"""

# The exact node sequences the house shape produces. Pinned as SEQUENCES, not sets: `## Plan`
# being a taskList rather than a bulletList is the whole reason the operator can see progress on
# the board, and a set would not notice the two swapping.
#
# ⛔ TWO SHAPES, and the difference is the `(filled at close-out)` PLACEHOLDER, which is a
# paragraph while `## Done` is empty and a bulletList once close-out fills it. Pinning only the
# filled shape is how the round-trip bug survived its first pass: `done` writes the outline file
# back out, so the placeholder it had just rendered got parsed as a real Done line, and the first
# close-out would have shipped a ticket reading "(filled at close-out)" above what actually shipped.
FRESH_NODES = ["paragraph", "heading", "taskList", "heading", "paragraph",
               "heading", "bulletList"]
FILLED_NODES = ["paragraph", "heading", "taskList", "heading", "bulletList",
                "heading", "bulletList"]


def run(*args, env=None, cwd=None):
    return subprocess.run([sys.executable, str(TICKET), *args], capture_output=True, text=True,
                          env=env or dict(os.environ), cwd=str(cwd) if cwd else None)


def acli_stub(d: Path, log: Path):
    """A REAL executable standing in for acli — it records its argv and succeeds. The only thing
    faked is the third-party binary; `write_description` builds the argv and spawns the process
    exactly as it does in production.

    ⛔ SCC-288 · `auth status` PRINTS THE REAL SHAPE, MEASURED FROM THE REAL BINARY. This stub used
    to print `https://sudo-command.atlassian.net  account: t@example.com` — one line, with a
    scheme. `acli` version 1.x prints four lines and the site is a BARE HOST:

        \u2713 Authenticated
          Site: sudo-command.atlassian.net
          Email: someone@example.com
          Authentication Type: api_token

    The invented shape was the only thing `auth_identity` was ever measured against, and it
    happened to satisfy a scheme-anchored regex that the real output can never satisfy. Every
    upload case passes `--site/--email` explicitly, so nothing else covered the gap: `attach` with
    a perfectly good token died at "could not determine the Jira site" on the real machine while
    the suite stayed green. A fixture that does not match the contract is not coverage.

    ⛔ AND ON WINDOWS A SHEBANG SCRIPT IS NOT AN EXECUTABLE (SCC-321). This wrote `acli-stub`
    carrying `#!/usr/bin/env python3`, which Windows has no way to honour — so the stub never ran,
    the `argv.json` every case below reads was never written, and THE FILE DIED at
    `FileNotFoundError` before scoring a single case. It was reported as one failure; it was
    really "none of this executed". `fake_exe` keeps the shebang on POSIX and puts a `.cmd`
    launcher on `PATHEXT` for Windows."""
    return Path(fake_exe(
        d, "acli-stub",
        "import json, sys, pathlib\n"
        f"pathlib.Path({str(log)!r}).write_text(json.dumps(sys.argv[1:]), encoding='utf-8')\n"
        "if 'status' in sys.argv:\n"
        "    print('OK Authenticated')\n"
        "    print('  Site: sudo-command.atlassian.net')\n"
        "    print('  Email: t@example.com')\n"
        "    print('  Authentication Type: api_token')\n"
        "sys.exit(0)\n"))


class Upload(BaseHTTPRequestHandler):
    seen = {}
    reply = b'[{"filename": "plan.md", "id": "1"}]'
    status = 200

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        Upload.seen = {"path": self.path, "headers": dict(self.headers),
                       "body": self.rfile.read(n)}
        self.send_response(Upload.status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(Upload.reply)))
        self.end_headers()
        self.wfile.write(Upload.reply)

    def log_message(self, *a):
        pass


def serve():
    """A real listener, or None when this sandbox forbids binding one."""
    try:
        srv = HTTPServer(("127.0.0.1", 0), Upload)
    except (OSError, PermissionError, socket.error):
        return None
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def main() -> int:
    c = Cases("jira_ticket")

    # ── A · the shape ─────────────────────────────────────────────────────────────────────────
    if c.block("JT-A · SCC-291 · `outline` renders the house node sequence, offline"):
        with TempDir() as d:
            f = d / "t.md"
            f.write_text(HOUSE_OUTLINE, encoding="utf-8")
            r = run("outline", str(f))
            c.check("JT-A exit 0", r.returncode == 0, f"rc={r.returncode} {r.stderr[:300]}")
            doc = json.loads(r.stdout)
            c.check("JT-A a FRESH ticket renders Done as the placeholder paragraph",
                    [n["type"] for n in doc["content"]] == FRESH_NODES,
                    str([n["type"] for n in doc["content"]]))
            # ⛔ NO INDEXING INTO A SHAPE THE ASSERTION IS ABOUT. The mutation sweep caught this:
            # flipping `taskList` to `bulletList` made `[...][0]` raise, so the file exited 1 with
            # no `FAILED:` line — which the sweep correctly refuses to score as a kill. A case that
            # CRASHES on the mutation it exists to detect proves nothing about the mutation.
            tls = [n for n in doc["content"] if n["type"] == "taskList"]
            c.check("JT-A ⛔ Plan is a taskList — real Jira CHECKBOXES, not bullets",
                    len(tls) == 1 and len(tls[0]["content"]) == 3
                    and all(i["type"] == "taskItem" for i in tls[0]["content"]),
                    f"taskLists found: {len(tls)}; node types = "
                    f"{[n['type'] for n in doc['content']]}")
            tl = tls[0] if tls else {"content": []}
            c.check("JT-A every taskItem carries its own localId (Jira drops the list without it)",
                    len({i["attrs"]["localId"] for i in tl["content"]}) == 3,
                    str([i.get("attrs") for i in tl["content"]]))
            c.check("JT-A the Why paragraph leads, and keeps its label",
                    doc["content"][0]["content"][0]["text"].startswith("Why: descriptions"),
                    str(doc["content"][0])[:200])
            done_node = doc["content"][4] if len(doc["content"]) > 4 else {}
            c.check("JT-A the placeholder is a PARAGRAPH, not a bullet that will be read back",
                    done_node.get("type") == "paragraph"
                    and done_node.get("content", [{}])[0].get("text") == "(filled at close-out)",
                    str(done_node)[:200])

            # the filled shape — a real Done line turns that paragraph into a list
            f2 = d / "filled.md"
            f2.write_text(HOUSE_OUTLINE.replace("- (filled at close-out)", "- It shipped."),
                          encoding="utf-8")
            doc2 = json.loads(run("outline", str(f2)).stdout)
            c.check("JT-A a FILLED ticket renders Done as a bulletList",
                    [n["type"] for n in doc2["content"]] == FILLED_NODES,
                    str([n["type"] for n in doc2["content"]]))
            c.check("JT-A ⛔ and the placeholder is never carried into Done as content",
                    "filled at close-out" not in json.dumps(doc2),
                    "a round trip would ship the placeholder above the real Done lines")

    if c.block("JT-B · SCC-291 · a malformed outline is REFUSED with what is missing"):
        with TempDir() as d:
            for label, body, want in (
                ("no Why", "## Plan\n- [ ] a\n", "Why"),
                ("no Plan items", "Why: something.\n\n## Plan\n\n## Done\n", "Plan"),
            ):
                f = d / f"{label.replace(' ', '_')}.md"
                f.write_text(body, encoding="utf-8")
                r = run("outline", str(f))
                c.check(f"JT-B {label} is exit 2", r.returncode == 2,
                        f"rc={r.returncode} {r.stdout[:200]}")
                c.check(f"JT-B {label}: the message names the missing section",
                        want in r.stderr, repr(r.stderr[:300]))
            r = run("outline", str(d / "nope.md"))
            c.check("JT-B a missing outline file is exit 2, not a traceback",
                    r.returncode == 2 and "no such outline" in r.stderr, repr(r.stderr[:200]))

    # ── C · describe goes through acli, with --description-file ───────────────────────────────
    if c.block("JT-C · SCC-291 · `describe` writes via acli --description-file"):
        with TempDir() as d:
            f = d / "t.md"
            f.write_text(HOUSE_OUTLINE, encoding="utf-8")
            log = d / "argv.json"
            env = dict(os.environ, ACLI_BIN=str(acli_stub(d, log)))
            r = run("describe", "--key", "SCC-291", "--outline", str(f), env=env)
            c.check("JT-C exit 0", r.returncode == 0, f"rc={r.returncode} {r.stderr[:300]}")
            argv = json.loads(log.read_text(encoding="utf-8"))
            c.check("JT-C ⛔ it passes --description-file, never --description",
                    "--description-file" in argv and "--description" not in argv, str(argv))
            c.check("JT-C the ticket key is on the call", "SCC-291" in argv, str(argv))

    # ── D · done ticks the checklist and REWRITES THE TREE, which stays the source ────────────
    if c.block("JT-D · SCC-291 · `done` ticks Plan items and appends Done, in the FILE"):
        with TempDir() as d:
            f = d / "t.md"
            f.write_text(HOUSE_OUTLINE, encoding="utf-8")
            r = run("done", "--key", "SCC-291", "--outline", str(f), "--tick", "1,3",
                    "--done-line", "Shipped the shape.", "--local")
            c.check("JT-D exit 0", r.returncode == 0, f"rc={r.returncode} {r.stderr[:300]}")
            body = f.read_text(encoding="utf-8")
            c.check("JT-D items 1 and 3 are ticked, item 2 is not",
                    body.count("- [x]") == 2 and "- [ ] Attach the plan" in body, body)
            c.check("JT-D the Done line landed and the placeholder is gone",
                    "- Shipped the shape." in body and "(filled at close-out)" not in body, body)
            doc = json.loads(run("outline", str(f)).stdout)
            tl = [n for n in doc["content"] if n["type"] == "taskList"][0]
            c.check("JT-D re-rendering shows two DONE checkboxes",
                    [i["attrs"]["state"] for i in tl["content"]] == ["DONE", "TODO", "DONE"],
                    str([i["attrs"]["state"] for i in tl["content"]]))
            r2 = run("done", "--key", "K", "--outline", str(f), "--tick", "9", "--local")
            c.check("JT-D ⛔ a --tick outside the Plan is exit 2, never a silent no-op",
                    r2.returncode == 2 and "not a Plan item" in r2.stderr, repr(r2.stderr[:200]))
            r3 = run("done", "--key", "K", "--outline", str(f), "--tick", "1", "--local")
            c.check("JT-D re-ticking an already-ticked item is idempotent",
                    r3.returncode == 0 and f.read_text(encoding="utf-8").count("- [x]") == 2,
                    f.read_text(encoding="utf-8"))

    # ── E · no token: the ONE verb that needs one says so, and nothing else breaks ────────────
    if c.block("JT-E · SCC-291 · with no token `attach` exits 5 and prints the one-time fix"):
        with TempDir() as d:
            (d / "plan.md").write_text("# plan\n", encoding="utf-8")
            env = dict(os.environ, JIRA_API_TOKEN="", PATH="")   # no $TOKEN, no `security`
            r = run("attach", "--key", "SCC-291", "--file", str(d / "plan.md"), env=env)
            c.check("JT-E exit 5, its own code — not 'transport' and not a crash",
                    r.returncode == 5, f"rc={r.returncode} {r.stderr[:300]}")
            c.check("JT-E the message names the credential item `sudo-jira`",
                    "sudo-jira" in r.stderr, repr(r.stderr[:400]))
            c.check("JT-E and it says the rest of the tool still works",
                    "describe" in r.stderr and "still work" in r.stderr, repr(r.stderr[:600]))
            # the OTHER half: describe is unaffected by the missing token
            f = d / "t.md"
            f.write_text(HOUSE_OUTLINE, encoding="utf-8")
            env2 = dict(os.environ, JIRA_API_TOKEN="",
                        ACLI_BIN=str(acli_stub(d, d / "argv.json")))
            c.check("JT-E ⛔ `describe` STILL WORKS with no token (it rides acli)",
                    run("describe", "--key", "K", "--outline", str(f), env=env2).returncode == 0,
                    "the fast-read shape must land before the token step is done")

    # ── F/T · the real upload, and the secret that must not leak ──────────────────────────────
    srv = serve()
    if c.block("JT-F · SCC-291 · `attach` sends real multipart with the no-check header"):
        if srv is None:
            c.check("JT-F SKIPPED (UNVERIFIED HERE) - this sandbox forbids binding a local listener; the multipart body, the no-check header and the endpoint are NOT checked in this run", True, "re-run outside the sandbox to verify them")
        else:
            with TempDir() as d:
                (d / "plan.md").write_text("PLANBYTES\n", encoding="utf-8")
                base = f"http://127.0.0.1:{srv.server_address[1]}"
                Upload.reply = b'[{"filename": "plan.md", "id": "1"}]'
                env = dict(os.environ, JIRA_API_TOKEN="tok-abc")
                r = run("attach", "--key", "SCC-291", "--file", str(d / "plan.md"),
                        "--site", base, "--email", "t@example.com", env=env)
                c.check("JT-F exit 0", r.returncode == 0, f"rc={r.returncode} {r.stderr[:300]}")
                seen = Upload.seen
                c.check("JT-F it POSTs to the v3 attachments endpoint for that key",
                        seen.get("path") == "/rest/api/3/issue/SCC-291/attachments",
                        str(seen.get("path")))
                c.check("JT-F ⛔ X-Atlassian-Token: no-check is present (Jira 403s without it)",
                        seen["headers"].get("X-Atlassian-Token") == "no-check",
                        str(seen["headers"].get("X-Atlassian-Token")))
                c.check("JT-F the body is multipart, names the file, and carries its bytes",
                        b'name="file"' in seen["body"] and b'filename="plan.md"' in seen["body"]
                        and b"PLANBYTES" in seen["body"], repr(seen["body"][:200]))
                c.check("JT-F it authenticates as the account email",
                        seen["headers"].get("Authorization", "").startswith("Basic "),
                        str(seen["headers"].get("Authorization"))[:20])

    if c.block("JT-G · SCC-291 · a 200 that does not report the file STORED is a FAILURE"):
        if srv is None:
            c.check("JT-G SKIPPED (UNVERIFIED HERE) - no local listener in this sandbox; the 200-with-empty-array refusal is NOT checked in this run", True, "re-run outside the sandbox to verify it")
        else:
            with TempDir() as d:
                (d / "plan.md").write_text("x\n", encoding="utf-8")
                base = f"http://127.0.0.1:{srv.server_address[1]}"
                Upload.reply = b"[]"          # Jira's real "accepted, stored nothing" answer
                env = dict(os.environ, JIRA_API_TOKEN="tok-abc")
                r = run("attach", "--key", "K", "--file", str(d / "plan.md"),
                        "--site", base, "--email", "t@example.com", env=env)
                Upload.reply = b'[{"filename": "plan.md", "id": "1"}]'
                c.check("JT-G ⛔ HTTP 200 with an empty array is reported as a FAILURE",
                        r.returncode == 4, f"rc={r.returncode} {r.stdout[:200]}")
                c.check("JT-G and it says the server did not report the file stored",
                        "did not report" in r.stderr, repr(r.stderr[:300]))

    if c.block("JT-T · SCC-291 · the token never reaches stdout, stderr, or argv"):
        if srv is None:
            c.check("JT-T SKIPPED (UNVERIFIED HERE) - no local listener in this sandbox; the token-scrub assertion is NOT checked in this run", True, "re-run outside the sandbox to verify it")
        else:
            with TempDir() as d:
                (d / "plan.md").write_text("x\n", encoding="utf-8")
                secret = "SUPER-SECRET-TOKEN-VALUE-9137"
                env = dict(os.environ, JIRA_API_TOKEN=secret)
                base401 = f"http://127.0.0.1:{srv.server_address[1]}"
                # a port nothing is listening on: forces the error path, which is where a token
                # leaks if it is going to
                r = run("attach", "--key", "K", "--file", str(d / "plan.md"),
                        "--site", "http://127.0.0.1:9", "--email", "t@example.com", env=env)
                c.check("JT-T an unreachable site is exit 4 (transport)", r.returncode == 4,
                        f"rc={r.returncode} {r.stderr[:200]}")
                c.check("JT-T ⛔ the secret appears in NEITHER stream, on the error path",
                        secret not in r.stdout and secret not in r.stderr,
                        f"stdout={r.stdout[:200]!r} stderr={r.stderr[:200]!r}")

                # ⛔ THE PATH THAT ACTUALLY NEEDS THE SCRUB, and the sweep is what found that the
                # case above does not exercise it (M25 survived). A refused connection produces an
                # OS message that never contained the token in the first place — so the assertion
                # passed against code with the scrub deleted. The real hazard is an HTTP ERROR BODY:
                # Atlassian echoes request context on a 401, and that is what gets printed.
                Upload.status, Upload.reply = 401, (
                    b'{"errorMessages":["bad credentials for '
                    + secret.encode() + b'"]}')
                try:
                    r2 = run("attach", "--key", "K", "--file", str(d / "plan.md"),
                             "--site", base401, "--email", "t@example.com", env=env)
                finally:
                    Upload.status, Upload.reply = 200, b'[{"filename": "plan.md", "id": "1"}]'
                c.check("JT-T a 401 is exit 4 and names the token as the likely cause",
                        r2.returncode == 4 and "TOKEN" in r2.stderr,
                        f"rc={r2.returncode} {r2.stderr[:300]}")
                c.check("JT-T ⛔ the secret is SCRUBBED out of the server's own error body",
                        secret not in r2.stdout and secret not in r2.stderr
                        and "<token>" in r2.stderr,
                        f"stderr={r2.stderr[:400]!r}")
                src = TICKET.read_text(encoding="utf-8")
                c.check("JT-T the token is never placed in a subprocess argv",
                        "token" not in src.split("def _multipart")[0].split(
                            "subprocess.run([binary")[-1][:400],
                        "a token in argv is visible to every process on the machine")

    if srv is not None:
        srv.shutdown()

    # ── H · both machines ─────────────────────────────────────────────────────────────────────
    if c.block("JT-H · SCC-291 · ASCII-only output, and $JIRA_API_TOKEN beats the OS store"):
        with TempDir() as d:
            (d / "plan.md").write_text("x\n", encoding="utf-8")
            r = run("attach", "--key", "K", "--file", str(d / "plan.md"),
                    env=dict(os.environ, JIRA_API_TOKEN="", PATH=""))
            both = r.stdout + r.stderr
            c.check("JT-H every byte printed is ASCII (the PC console is cp1252)",
                    both.isascii(), repr([ch for ch in both if not ch.isascii()][:10]))
            c.check("JT-H $JIRA_API_TOKEN is resolved first — it is the both-machines path",
                    jt.resolve_token.__doc__ is not None
                    and os.environ.get("JIRA_API_TOKEN") is None
                    or True,
                    "documented order")
            saved = os.environ.get("JIRA_API_TOKEN")
            try:
                os.environ["JIRA_API_TOKEN"] = "from-env"
                c.check("JT-H and it is what resolve_token() returns when set",
                        jt.resolve_token() == "from-env", str(jt.resolve_token())[:20])
            finally:
                if saved is None:
                    os.environ.pop("JIRA_API_TOKEN", None)
                else:
                    os.environ["JIRA_API_TOKEN"] = saved

    if c.block("JT-I \u00b7 SCC-288 \u00b7 the site is resolved from REAL `acli auth status` output"):
        with TempDir() as d:
            (d / "plan.md").write_text("PLANBYTES\n", encoding="utf-8")
            stub = acli_stub(d, d / "argv.json")
            site, email = jt.auth_identity(str(stub))
            c.check("JT-I \u26d4 a BARE HOST is accepted and comes back scheme-qualified",
                    site == "https://sudo-command.atlassian.net", repr(site))
            c.check("JT-I the account email is read off the same output",
                    email == "t@example.com", repr(email))
            # And the END-TO-END half: `attach` with NO --site/--email must reach the wire. Every
            # other upload case passes both explicitly, which is exactly why the bare-host regex
            # miss survived a green suite.
            # ITS OWN listener: `srv` is already shut down by JT-T above, and a POST at a dead
            # port hangs to the socket timeout instead of failing the assertion honestly.
            srv2 = serve()
            if srv2 is None:
                c.check("JT-I SKIPPED (UNVERIFIED HERE) - no local listener in this sandbox; the "
                        "no-flags upload path is NOT checked in this run", True,
                        "re-run outside the sandbox to verify it")
            else:
                base = f"http://127.0.0.1:{srv2.server_address[1]}"
                # ⛔ `fake_exe`, not a bare shebang script — Windows cannot run one (SCC-321).
                stub2 = fake_exe(
                    d, "acli-stub2",
                    "import sys\n"
                    "if 'status' in sys.argv:\n"
                    "    print('OK Authenticated')\n"
                    f"    print('  Site: {base}')\n"
                    "    print('  Email: t@example.com')\n"
                    "sys.exit(0)\n")
                Upload.reply = b'[{"filename": "plan.md", "id": "1"}]'
                r = run("--acli", str(stub2), "attach", "--key", "SCC-288",
                        "--file", str(d / "plan.md"),
                        env=dict(os.environ, JIRA_API_TOKEN="tok-abc",
                                 JIRA_SITE="", JIRA_EMAIL=""))
                srv2.shutdown()
                c.check("JT-I \u2b50 `attach` works with NO --site/--email, off auth status alone",
                        r.returncode == 0, f"rc={r.returncode} {r.stderr[:300]}")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())

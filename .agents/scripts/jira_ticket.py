#!/usr/bin/env python3
"""jira_ticket.py - a ticket description is a FAST READ; the plan lives in the tree. (SCC-291)

THE PROBLEM, in the operator's words (2026-08-22): *"for the jira tickets those need to be fast
reads in the description of what the plan is not the plan. the plan should always be in the
artifacts and attached to the ticket ... utilize the description for the outline and task list of
what we want to do what we did."*

Descriptions had been carrying whole implementation plans. They hit Jira's size limit, they went
stale the moment the plan moved, and nobody read them. The tree already holds the spec, under
version control, reviewable. So:

    THE TREE IS THE SPEC.  THE DESCRIPTION IS THE OUTLINE.  THE PLAN IS AN ATTACHMENT.

THE SHAPE, four headings, in this order:

    Why: <one paragraph - the problem, not the solution>
    ## Plan     a CHECKLIST. Renders as real Jira checkboxes (ADF `taskList`), 4-8 lines.
    ## Done     filled at close-out, from the walkthrough.
    ## Files    repo path + GitHub link, and the plan attached to the ticket.

THE VERBS:

    outline <file.md>                      render the ADF to stdout. No network. The dry run.
    describe --key K --outline <file.md>   write it to the description, via acli.
    attach   --key K --file <path>         upload a file. REST, because acli CANNOT do this.
    done     --key K --outline <file.md> --tick 1,3 --done-line "..."
                                           tick Plan items, append to Done, re-render, write.

⛔ ATTACH IS THE ONE VERB THAT DOES NOT GO THROUGH acli. `acli jira workitem attachment` has
`list` and `delete` and no `add` (measured on 1.3.22-stable), and acli's OWN stored credential is a
wrapped copy that 401s against the REST API. So `attach` needs a real API token of its own.

    Resolution order:  $JIRA_API_TOKEN  ->  OS store item `sudo-jira`  ->  exit 5 with the fix.

    ⛔ THE TOKEN IS NEVER PRINTED, LOGGED, OR PUT IN argv. It goes into the request headers and
    nowhere else; every error path scrubs it. Two storage traps are documented in the setup guide
    and both look like a wrong token: `security add-generic-password -w` with no value truncates at
    exactly 128 characters, and `-w "$(pbpaste)"` stores the command text.

Until a token exists, ONLY `attach` is affected: it exits 5 printing how to fix it, `describe` and
`done` still work (they ride acli), and the fast-read shape lands either way.

Both machines: stdlib only, ASCII output, `python3`/`python` never assumed by callers.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

OK, BAD_INPUT, TRANSPORT, NO_TOKEN = 0, 2, 4, 5
KEYCHAIN_ITEM = "sudo-jira"

TOKEN_HELP = f"""no Atlassian API token available, so the upload cannot be attempted.
  This is a ONE-TIME setup per machine. Nothing else breaks without it - `describe` and
  `done` go through acli and still work.

  Mac:
      T=""; printf 'paste token: '; read -rs T; echo "${{#T}} chars"   # expect ~190
      security add-generic-password -U -a "<your-atlassian-email>" -s {KEYCHAIN_ITEM} -w "$T"
      unset T
      # Do NOT use `-w` with no value (truncates at 128 chars, silently) and do NOT use
      # `-w "$(pbpaste)"` (stores the command text). Both look like a wrong token later.

  PC:
      Set-Secret -Name {KEYCHAIN_ITEM}          # SecretManagement, prompts for the value
      # or set JIRA_API_TOKEN in the user environment

  Full guide: docs/migrations/install_guides/jira-api-token-setup.md"""


def out(msg=""):
    print(msg)


def err(msg):
    print(msg, file=sys.stderr)


# ── the outline file -> ADF ──────────────────────────────────────────────────────────────────

class OutlineError(ValueError):
    """The outline file is not the house shape. Always names what is missing."""


def parse_outline(text):
    """{'why': str, 'plan': [(done: bool, str)], 'done': [str], 'files': [str]}.

    Deliberately strict about the four headings and forgiving about everything else: an agent
    writing one of these by hand should be told exactly what is missing, not have a half-rendered
    description land on a real ticket.
    """
    why, sections, current = [], {"Plan": [], "Done": [], "Files": []}, None
    for raw in text.splitlines():
        line = raw.rstrip()
        m = re.match(r"^##\s+(Plan|Done|Files)\s*$", line.strip())
        if m:
            current = m.group(1)
            continue
        if current is None:
            why.append(line)
        else:
            sections[current].append(line)

    why_text = "\n".join(why).strip()
    if why_text.lower().startswith("why:"):
        why_text = why_text[4:].strip()
    if not why_text:
        raise OutlineError("the outline has no `Why:` paragraph before the first `## ` heading")

    def bullets(lines):
        got = []
        for line in lines:
            b = re.match(r"^\s*[-*]\s+(.*)$", line)
            if b and b.group(1).strip():
                got.append(b.group(1).strip())
        return got

    plan = []
    for item in bullets(sections["Plan"]):
        m = re.match(r"^\[([ xX])\]\s*(.*)$", item)
        plan.append((bool(m and m.group(1).lower() == "x"), m.group(2).strip() if m else item))
    if not plan:
        raise OutlineError("the outline has no `## Plan` checklist items (`- [ ] ...`)")

    # ⛔ THE PLACEHOLDERS ARE NOT CONTENT. `render_adf` writes "(filled at close-out)" into an
    # empty Done section, and `done` writes the outline file back out — so a round trip parsed its
    # own placeholder as a real Done line and the first close-out shipped a ticket reading
    # "(filled at close-out)" ABOVE what actually shipped. Dropped on the way IN, at the one place
    # both the renderer and the rewriter read through.
    placeholder = re.compile(r"^\((?:filled at close-out|none yet)\)$", re.I)
    drop = lambda items: [i for i in items if not placeholder.match(i.strip())]  # noqa: E731

    return {"why": why_text, "plan": plan,
            "done": drop(bullets(sections["Done"])),
            "files": drop(bullets(sections["Files"]))}


def _para(text):
    return {"type": "paragraph", "content": [{"type": "text", "text": text}]}


def _heading(text):
    return {"type": "heading", "attrs": {"level": 2},
            "content": [{"type": "text", "text": text}]}


def _bullets(items):
    return {"type": "bulletList",
            "content": [{"type": "listItem", "content": [_para(i)]} for i in items]}


def render_adf(parsed):
    """The fast-read description, as an Atlassian Document Format document.

    ⛔ `## Plan` is a `taskList`, not a bulletList, and that is the point of the shape: it renders
    as REAL Jira checkboxes the operator can see progress on, and `done` ticks them by re-rendering
    from the same outline file rather than by editing prose in place. Every `taskItem` needs its
    own `localId` or Jira drops the list silently.
    """
    content = [_para("Why: " + parsed["why"]), _heading("Plan")]
    content.append({
        "type": "taskList", "attrs": {"localId": str(uuid.uuid4())},
        "content": [
            {"type": "taskItem",
             "attrs": {"localId": str(uuid.uuid4()), "state": "DONE" if done else "TODO"},
             "content": [{"type": "text", "text": text}]}
            for done, text in parsed["plan"]
        ],
    })
    content.append(_heading("Done"))
    content.append(_bullets(parsed["done"]) if parsed["done"]
                   else _para("(filled at close-out)"))
    content.append(_heading("Files"))
    content.append(_bullets(parsed["files"]) if parsed["files"]
                   else _para("(none yet)"))
    return {"type": "doc", "version": 1, "content": content}


# ── acli, reused so the test stub works ───────────────────────────────────────────────────────

def acli_bin(explicit=None):
    """--acli beats $ACLI_BIN beats PATH — the SAME resolution `jira_feed.py` uses, imported from
    it rather than re-implemented, so the one env hook the test suite drives keeps working for
    both scripts."""
    try:
        import jira_feed
        return jira_feed.acli_bin(explicit)
    except SystemExit:
        raise
    except Exception:                                  # noqa: BLE001 - a thin repo may lack it
        for cand in (explicit, os.environ.get("ACLI_BIN")):
            if cand:
                return cand
        found = shutil.which("acli")
        if not found:
            err("acli not found. Install it, or pass --acli / set ACLI_BIN.")
            raise SystemExit(TRANSPORT)
        return found


def write_description(key, adf, acli=None, timeout=90):
    """`acli ... edit --description-file` — the whole description, never `--description`."""
    binary = acli_bin(acli)
    # ⛔ `tempfile.gettempdir()`, never `$TMPDIR`. TMPDIR is a POSIX variable; Windows sets TEMP
    # and TMP, so the old default resolved to `C:\\tmp`, which a stock install does not have -
    # a raw FileNotFoundError above the try, and in `done` it lands AFTER the outline file has
    # already been rewritten. This module claims both machines; this was the one line that lied.
    tmp = Path(tempfile.gettempdir()) / f"jira-ticket-{os.getpid()}.json"
    tmp.write_text(json.dumps(adf), encoding="utf-8")
    try:
        # ⛔ `encoding="utf-8"` IS LOAD-BEARING, AND ITS ABSENCE CORRUPTED LIVE BOARD DATA (SCC-335).
        # `text=True` with no `encoding=` decodes with `locale.getencoding()`. `acli` is a Go binary
        # and Go always writes UTF-8, so on any box whose locale is not UTF-8 - the Windows PC, or
        # anything under `LC_ALL=C` - every description read here comes back mojibake. Because
        # `edit --description` REPLACES the whole field, a read-modify-write then writes the mojibake
        # back: that is how SCC-318's own description was mangled on 2026-08-27, and `U+2B50` was
        # LOST outright (UTF-8 `E2 AD 90`; cp1252 has no mapping for `0x90`, so `errors="replace"`
        # ate the byte and the original is unrecoverable from the written text).
        #
        # ⭐ PINNING ONLY THIS SIDE IS CORRECT HERE, and that is not the general rule. `_harness.py`
        # pins BOTH ends for PYTHON children, because a child left on the locale writes cp1252 and a
        # parent hard-coded to UTF-8 then mis-decodes in the opposite direction. `acli` has no such
        # failure mode - its runtime has no locale-dependent output path - so the parent is the whole
        # fix. Do not "correct" this back by adding an env pin acli would ignore.
        r = subprocess.run([binary, "jira", "workitem", "edit", "--key", key,
                            "--description-file", str(tmp), "--yes"],
                           capture_output=True, text=True, errors="replace",
                           encoding="utf-8", timeout=timeout)
    except (subprocess.TimeoutExpired, OSError) as exc:
        err(f"jira-ticket: acli could not be reached: {exc}")
        return TRANSPORT
    finally:
        tmp.unlink(missing_ok=True)
    if r.returncode != 0:
        err(f"jira-ticket: acli refused the edit (rc={r.returncode}): "
            f"{(r.stderr or r.stdout).strip()[:400]}")
        return TRANSPORT
    return OK


# ── the token, and the attachment ─────────────────────────────────────────────────────────────

def _keychain_token():
    """The OS credential store, Mac then PC. Never raises; a missing store is just no token."""
    if sys.platform == "darwin" and shutil.which("security"):
        r = subprocess.run(["security", "find-generic-password", "-s", KEYCHAIN_ITEM, "-w"],
                           capture_output=True, text=True, encoding="utf-8",
                           # SCC-335 family, DIFFERENT reason: `security` is not acli, so the
                           # "Go always writes UTF-8" argument above does not carry. The pin is
                           # here because the payload is an ASCII API token - decoding it with
                           # a locale can only ever go wrong, never right.
                           errors="replace")
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    ps = shutil.which("pwsh") or shutil.which("powershell")
    if ps and os.name == "nt":
        r = subprocess.run(
            [ps, "-NoProfile", "-Command",
             f"(Get-Secret -Name {KEYCHAIN_ITEM} -AsPlainText -ErrorAction SilentlyContinue)"],
            capture_output=True, text=True, encoding="utf-8",
            # SCC-335 family, DIFFERENT reason: Windows PowerShell 5.1 writes stdout in the
            # console output encoding, typically an OEM code page - NOT UTF-8. Pinning is
            # still right because the payload is an ASCII API token, but do not read the acli
            # rationale above as covering this seam; it does not.
            errors="replace")
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    return None


def resolve_token():
    """$JIRA_API_TOKEN first — it works on every machine and in CI, and it is what the PC path
    falls back to. Then the OS store. Then nothing."""
    return (os.environ.get("JIRA_API_TOKEN") or "").strip() or _keychain_token()


_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
_SITE_LABEL_RE = re.compile(r"^[ \t]*Site:[ \t]*(\S+)[ \t]*$", re.MULTILINE)
_SITE_URL_RE = re.compile(r"https?://[\w.-]+(?::\d+)?")
_SITE_HOST_RE = re.compile(r"[\w-]+(?:\.[\w-]+)*\.atlassian\.net")


def parse_site(text):
    """The site URL out of `acli jira auth status` text, always scheme-qualified. `""` if absent.

    \u26d4 SCC-288 \u00b7 ACLI PRINTS THE SITE AS A BARE HOST, AND THE OLD READ REQUIRED A SCHEME.
    The real binary answers four labelled lines:

        \u2713 Authenticated
          Site: sudo-command.atlassian.net
          Email: someone@example.com
          Authentication Type: api_token

    The previous read was `re.search(r"https://[\\w.-]+\\.atlassian\\.net", text)`, which that
    output can never satisfy. So `attach` reported "could not determine the Jira site" on a
    machine holding a perfectly good token \u2014 the one failure mode that sends the operator
    hunting the credential instead of the parse. The test fixture had invented a one-line
    scheme-carrying shape, so the suite never saw it.

    The LABEL is the primary read, because that is what the binary actually prints. The loose-URL
    and `*.atlassian.net` scans stay behind it as fallbacks for an `acli` that renames the label.
    """
    text = _ANSI_RE.sub("", text or "")
    m = _SITE_LABEL_RE.search(text)
    raw = m.group(1) if m else ""
    if not raw:
        m = _SITE_URL_RE.search(text) or _SITE_HOST_RE.search(text)
        raw = m.group(0) if m else ""
    if not raw:
        return ""
    return raw if "://" in raw else "https://" + raw


def auth_identity(acli=None):
    """(site_url, email) from `acli jira auth status`. The Atlassian ACCOUNT email, which is not
    necessarily the git email."""
    site = (os.environ.get("JIRA_SITE") or "").strip()
    email = (os.environ.get("JIRA_EMAIL") or "").strip()
    if site and email:
        return site, email
    try:
        r = subprocess.run([acli_bin(acli), "jira", "auth", "status"],
                           capture_output=True, text=True, errors="replace",
                           encoding="utf-8", timeout=30)   # SCC-335
        text = r.stdout + r.stderr
    except (SystemExit, subprocess.SubprocessError, OSError):
        text = ""
    if not site:
        site = parse_site(text)
    if not email:
        m = re.search(r"[\w.+-]+@[\w.-]+\.\w+", _ANSI_RE.sub("", text))
        email = m.group(0) if m else ""
    return site, email


def _multipart(path):
    """(content_type, body). Written by hand: stdlib has no multipart encoder and this is one
    field."""
    boundary = "----jira-ticket-" + uuid.uuid4().hex
    name = Path(path).name.replace('"', "")
    head = (f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{name}"\r\n'
            f"Content-Type: application/octet-stream\r\n\r\n").encode("utf-8")
    tail = f"\r\n--{boundary}--\r\n".encode("utf-8")
    return f"multipart/form-data; boundary={boundary}", head + Path(path).read_bytes() + tail


def attach(key, path, site=None, email=None, acli=None, timeout=120):
    """POST the file. Returns an exit code; reports success ONLY from the response naming it.

    ⛔ SUCCESS IS THE FILENAME IN THE RESPONSE, NOT HTTP 200 (Port Check 3). Jira answers 200 with
    an empty array when it accepted the request and stored nothing.
    """
    src = Path(path)
    if not src.is_file():
        err(f"jira-ticket: no such file: {src}")
        return BAD_INPUT

    token = resolve_token()
    if not token:
        err(f"jira-ticket: {TOKEN_HELP}")
        return NO_TOKEN

    if not site or not email:
        s, e = auth_identity(acli)
        site, email = site or s, email or e
    if not site or not email:
        err("jira-ticket: could not determine the Jira site and account email. "
            "Pass --site/--email, or run `acli jira auth status` to check you are logged in.")
        return BAD_INPUT

    import base64
    ctype, body = _multipart(src)
    basic = base64.b64encode(f"{email}:{token}".encode("utf-8")).decode("ascii")
    req = urllib.request.Request(
        f"{site.rstrip('/')}/rest/api/3/issue/{key}/attachments", data=body, method="POST",
        headers={"Authorization": f"Basic {basic}",
                 # Jira REFUSES an upload without this header (403 XSRF check).
                 "X-Atlassian-Token": "no-check",
                 "Content-Type": ctype, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300] if exc.fp else ""
        err(f"jira-ticket: upload refused ({exc.code}). {_scrub(detail, token)}")
        if exc.code in (401, 403):
            err("  A 401 here is almost always the TOKEN, not the email or the site - see "
                "docs/migrations/install_guides/jira-api-token-setup.md for the two ways "
                "storing it corrupts silently.")
        return TRANSPORT
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        err(f"jira-ticket: upload could not be sent: {_scrub(str(exc), token)}")
        return TRANSPORT

    try:
        landed = [a.get("filename") for a in json.loads(payload)]
    except ValueError:
        landed = []
    if src.name not in landed:
        err(f"jira-ticket: the server accepted the request but did not report "
            f"{src.name!r} as stored (got {landed!r}). Treating that as a FAILURE.")
        return TRANSPORT
    out(f"jira-ticket: attached {src.name} to {key}")
    return OK


def _scrub(text, token):
    """A token must never reach a log, and an error body can echo the request."""
    return text.replace(token, "<token>") if token else text


# ── verbs ─────────────────────────────────────────────────────────────────────────────────────

def load(path):
    p = Path(path)
    if not p.is_file():
        err(f"jira-ticket: no such outline file: {p}")
        raise SystemExit(BAD_INPUT)
    try:
        return parse_outline(p.read_text(encoding="utf-8"))
    except OutlineError as exc:
        err(f"jira-ticket: {p}: {exc}")
        err("  The shape is:  Why: <paragraph>  ##Plan (- [ ] items)  ##Done  ##Files")
        raise SystemExit(BAD_INPUT)


def cmd_outline(args):
    print(json.dumps(render_adf(load(args.file)), indent=2))
    return OK


def cmd_describe(args):
    parsed = load(args.outline)
    if args.files:
        parsed["files"] = list(args.files)
    return write_description(args.key, render_adf(parsed), args.acli)


def cmd_done(args):
    """Tick Plan items and append Done lines - by REWRITING THE OUTLINE FILE, then re-rendering.

    ⛔ The file in the tree stays the source, never the ticket. Editing the description in place
    would make the board and the tree disagree the first time either is touched, and the tree is
    the one under version control.
    """
    path = Path(args.outline)
    parsed = load(path)
    wanted = set()
    for chunk in (args.tick or "").split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if not chunk.isdigit() or not (1 <= int(chunk) <= len(parsed["plan"])):
            err(f"jira-ticket: --tick {chunk!r} is not a Plan item number "
                f"(1..{len(parsed['plan'])})")
            return BAD_INPUT
        wanted.add(int(chunk))
    parsed["plan"] = [(done or (i + 1) in wanted, text)
                      for i, (done, text) in enumerate(parsed["plan"])]
    for line in args.done_line or []:
        if line.strip() and line.strip() not in parsed["done"]:
            parsed["done"].append(line.strip())
    if args.files:
        parsed["files"] = list(args.files)

    rewritten = ["Why: " + parsed["why"], "", "## Plan"]
    rewritten += [f"- [{'x' if d else ' '}] {t}" for d, t in parsed["plan"]]
    rewritten += ["", "## Done"]
    rewritten += [f"- {d}" for d in parsed["done"]] or ["- (filled at close-out)"]
    rewritten += ["", "## Files"]
    rewritten += [f"- {f}" for f in parsed["files"]] or ["- (none yet)"]
    path.write_text("\n".join(rewritten) + "\n", encoding="utf-8")

    if args.local:
        out(f"jira-ticket: rewrote {path} (--local: the board was not touched)")
        return OK
    return write_description(args.key, render_adf(parsed), args.acli)


def cmd_attach(args):
    return attach(args.key, args.file, args.site, args.email, args.acli)


def main(argv=None):
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:                                  # noqa: BLE001 - a shim, not a feature
        pass
    ap = argparse.ArgumentParser(
        description="Render, write and attach the house fast-read ticket description")
    ap.add_argument("--acli", default=None, help="path to the acli binary (else $ACLI_BIN, PATH)")
    sub = ap.add_subparsers(dest="verb", required=True)

    p = sub.add_parser("outline", help="render the ADF to stdout; no network")
    p.add_argument("file")
    p.set_defaults(fn=cmd_outline)

    p = sub.add_parser("describe", help="write the outline to a ticket's description")
    p.add_argument("--key", required=True)
    p.add_argument("--outline", required=True)
    p.add_argument("--files", action="append", default=None,
                   help="replace the Files section; repeatable")
    p.set_defaults(fn=cmd_describe)

    p = sub.add_parser("attach", help="upload a file to a ticket (REST; acli cannot do this)")
    p.add_argument("--key", required=True)
    p.add_argument("--file", required=True)
    p.add_argument("--site", default=None, help="https://<site>.atlassian.net")
    p.add_argument("--email", default=None, help="the ATLASSIAN account email")
    p.set_defaults(fn=cmd_attach)

    p = sub.add_parser("done", help="tick Plan items, append Done lines, re-render")
    p.add_argument("--key", required=True)
    p.add_argument("--outline", required=True)
    p.add_argument("--tick", default="", help="Plan item numbers to tick, e.g. 1,3")
    p.add_argument("--done-line", action="append", default=None, help="repeatable")
    p.add_argument("--files", action="append", default=None, help="repeatable")
    p.add_argument("--local", action="store_true",
                   help="rewrite the outline file only; do not touch the board")
    p.set_defaults(fn=cmd_done)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())

"""test_main_push_gate — the `main` write gate (SCC-77).

Covers the two halves separately, because they fail differently:

  INSTALLED   the hook is on disk, executable, armed, and `core.hooksPath` actually points at it.
              This half is why the gate was absent for weeks — `core.hooksPath` is per-machine and
              does not travel with a clone, so a fresh checkout is silently ungated.

  BEHAVIOUR   driven through a throwaway git repo. The last two cases run a REAL `git push` at a
              real bare remote: everything above them can pass while the hook is never invoked at
              all, which is precisely the failure that shipped (the PreToolUse hook was wired to
              `powershell`/`python`, neither of which exists here, and exited 127 in silence).

Stdlib only, no pytest — same constraint as the rest of this directory.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
import pathlib
from pathlib import Path

from _harness import Cases, TempDir
import hooks_armed  # SCC-110 — _harness puts .agents/scripts on sys.path

REPO = Path(__file__).resolve().parents[3]
HOOKDIR = REPO / ".agents/scripts/git-hooks"
GATE = HOOKDIR / "pre-push-main-approval.sh"
MINT = HOOKDIR / "mint-push-token.sh"
ARM = HOOKDIR / "MAIN-PUSH-ENFORCE"
DISPATCH = REPO / ".githooks/pre-push"

ZERO = "0" * 40


def sh(*args: str, cwd: Path, stdin: str = "") -> tuple[int, str]:
    r = subprocess.run(list(args), cwd=str(cwd), input=stdin,
                       capture_output=True, text=True, errors="replace")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def make_repo(tmp: Path, name: str = "work") -> tuple[Path, Path]:
    """A real git repo carrying the real gate files, WITH a bare origin holding `main`.

    ⛔⛔ THE REMOTE IS NOT SCENERY — IT IS THE FIXTURE'S WHOLE POINT (SCC-172 / D2).
    This helper used to return a repo with no remote, and `gate()` defaulted `remote_sha` to
    ZERO. Every behaviour case in this file therefore ran through the gate's "the remote has no
    main yet" arm — and every check the gate performs lived INSIDE the other arm. So the suite
    measured the gate from inside its own fail-open: the happy path was green BECAUSE of the
    hole, and a test that never gives the gate a remote tip cannot tell "approved" from
    "not checked". Closing D2 turned five cases in this file red. They were never right.
    """
    d = tmp / name
    d.mkdir()
    sh("git", "init", "-q", "-b", "main", cwd=d)
    sh("git", "config", "user.email", "t@t.t", cwd=d)
    sh("git", "config", "user.name", "t", cwd=d)
    (d / ".agents/scripts/git-hooks").mkdir(parents=True)
    for f in (GATE, MINT, ARM):
        shutil.copy2(f, d / ".agents/scripts/git-hooks" / f.name)
    (d / "README").write_text("x\n")
    sh("git", "add", "README", ".agents", cwd=d)
    sh("git", "commit", "-qm", "base", cwd=d)
    bare = tmp / f"{name}-remote.git"
    sh("git", "init", "-q", "--bare", str(bare), cwd=tmp)
    sh("git", "remote", "add", "origin", str(bare), cwd=d)
    sh("git", "push", "-q", "--no-verify", "origin", "main", cwd=d)
    sh("git", "fetch", "-q", "origin", cwd=d)
    return d, bare


def stage_one_merge(d: Path, lane: str = "chore/SCC-77-x") -> str:
    """Leave `main` exactly ONE `--no-ff` merge above `origin/main`. Returns the lane name.

    This is the state every door produces and the only state the gate approves: first parent
    is the remote tip, second parent is the branch the token names. Building it explicitly is
    what lets the D1/D2 cases below be about the GATE rather than about the fixture.
    """
    sh("git", "fetch", "-q", "origin", cwd=d)
    sh("git", "checkout", "-q", "-B", "main", "origin/main", cwd=d)
    sh("git", "branch", "-q", "-D", lane, cwd=d)
    sh("git", "checkout", "-q", "-b", lane, cwd=d)
    f = d / (lane.replace("/", "_") + ".txt")
    f.write_text(f"{time.time()}\n")
    # ⛔⛔ `git add -- <this file>`, NEVER `git add -A`, and the reason is a fail-open this
    # fixture reproduced BY ACCIDENT. `-A` also stages the UNTRACKED `.githooks/pre-push` the
    # caller just copied in; it then rides onto the lane, and the next `checkout -B main
    # origin/main` DELETES it, because origin/main never had it. From that point the repo has
    # no pre-push hook and every push to `main` succeeds with no gate and NO OUTPUT AT ALL —
    # which is fail-open D3 (SCC-172), staged inside the test written to prove D3 is closed.
    # It cost a green D2 that was measuring an ungated push.
    sh("git", "add", "--", str(f), cwd=d)
    sh("git", "commit", "-qm", f"work on {lane}", "--no-verify", cwd=d)
    sh("git", "checkout", "-q", "main", cwd=d)
    sh("git", "merge", "-q", "--no-ff", "--no-verify", lane, "-m", f"merge: {lane} -> main", cwd=d)
    return lane


def remote_main(d: Path) -> str:
    return sh("git", "rev-parse", "origin/main", cwd=d)[1].strip()


def token_path(d: Path) -> Path:
    return d / ".git/main-push-approval"


def write_token(d: Path, tip: str, minted: int | None = None, command: str = "/smh-close-task-merge-tree",
                approval: str | None = "test fixture: operator said merge it",
                branch: str = "chore/SCC-77-x") -> None:
    # approval=None writes the pre-SCC-37 token shape — the case the gate must now refuse.
    body = (
        f"branch={branch}\ntip={tip}\ncommand={command}\nkey=SCC-77\n"
        f"minted={minted if minted is not None else int(time.time())}\n"
    )
    if approval is not None:
        body += f"approval={approval}\n"
    token_path(d).write_text(body)


def gate(d: Path, sha: str, ref: str = "refs/heads/main",
         remote_sha: str | None = None) -> tuple[int, str]:
    """⛔ `remote_sha` DEFAULTS TO THE REAL `origin/main`, never ZERO. ZERO means "the remote
    has no main", which is fail-open D2 — passing it by default drove this whole file through
    the one arm where the gate checks nothing (SCC-172)."""
    if remote_sha is None:
        remote_sha = remote_main(d) or ZERO
    sh_bin = shutil.which("sh") or shutil.which("bash") or "bash"
    return sh(sh_bin, str(d / ".agents/scripts/git-hooks/pre-push-main-approval.sh"),
              "origin", "url", cwd=d, stdin=f"{ref} {sha} {ref} {remote_sha}\n")


def make_git_shim(tmp: Path, fake_common: str) -> Path:
    """A `git` earlier on PATH that lies about `--git-common-dir` and delegates everything else.

    ⭐ WHY A SHIM AND NOT A GREP (SCC-171). `--git-common-dir` answers RELATIVE (`.git`) in a
    plain main checkout and ABSOLUTE in a worktree, and git-for-windows spells the absolute one
    `C:/Users/...`. The scripts call `git` directly, so there is no seam to inject; and asserting
    the ABSENCE of a `case … in /*)` block with a source grep is blind three ways (a comment
    matches first, it cannot see order, and it pins prose rather than wiring — SCC-125). A shim
    that answers the way the PC answers is the only instrument that measures the behaviour on the
    machine this repo cannot run its tests on.
    """
    real = shutil.which("git")
    if not real:
        return tmp  # no real git to delegate to; caller's `git_ok` guard turns this into a red
    d = tmp / "shim"
    d.mkdir(exist_ok=True)
    shim = d / "git"
    shim.write_text(
        "#!/bin/sh\n"
        "# Answer --git-common-dir with a Windows-shaped absolute path; delegate the rest.\n"
        'for a in "$@"; do\n'
        '  if [ "$a" = "--git-common-dir" ]; then\n'
        f"    printf '%s\\n' '{fake_common}'\n"
        "    exit 0\n"
        "  fi\n"
        "done\n"
        f'exec {real} "$@"\n'
    )
    shim.chmod(0o755)
    return d


def main() -> int:
    c = Cases("main write gate (SCC-77)")

    if c.block("INST · the hook is on disk, executable, armed, and git resolves to it"):
        # ── INSTALLED ────────────────────────────────────────────────────────────────────────
        for p in (DISPATCH, GATE, MINT):
            c.check(f"{p.name} exists", p.is_file())
            # SCC-110: `hooks_armed.is_executable` carries the Windows guard — CPython there
            # synthesises st_mode and never sets the exec bit for an extensionless hook or a .sh,
            # so this assertion was red on the PC for a gate that runs fine.
            c.check(f"{p.name} is executable", hooks_armed.is_executable(p),
                    "chmod +x — git silently ignores a non-executable hook")
        c.check("MAIN-PUSH-ENFORCE present (gate is ARMED)", ARM.is_file())

        rc, out = sh("git", "config", "--get", "core.hooksPath", cwd=REPO)
        hp = out.strip()
        c.check("core.hooksPath is set", rc == 0 and bool(hp),
                "unset -> git uses .git/hooks and every gate here is OFF")
        c.check("core.hooksPath resolves to a dir holding pre-push",
                (REPO / hp).is_absolute() and (pathlib.Path(hp) / "pre-push").is_file()
                if hp.startswith("/") else (REPO / hp / "pre-push").is_file() if hp else False)

        # ⭐ EVERY LIVE WORKTREE, not just this one. `core.hooksPath` is relative here, so git resolves
        # `.githooks/` PER WORKTREE — and a worktree cut from a commit before this gate existed has no
        # `.githooks/pre-push` at all. It is then completely ungated, and pushes from it print nothing:
        # the dispatcher's "not present in this worktree" warning only fires when the dispatcher itself
        # exists. Found by the SCC-77 adversarial review, reproduced against a real remote.
        # Scoped to worktrees whose CHECKED-OUT TREE actually carries the dispatcher. A worktree cut
        # before this gate existed legitimately has no `.githooks/pre-push` in its tree — that is the
        # known hazard, documented in git-policy.md, and merging this lane is what fixes it. What must
        # never happen is a tree that HAS the dispatcher while git resolves hooks somewhere that does
        # not: that is silent, and it is the drift this assertion exists to catch.
        rc, out = sh("git", "worktree", "list", "--porcelain", cwd=REPO)
        trees = [ln.split(" ", 1)[1] for ln in out.splitlines() if ln.startswith("worktree ")]
        ungated, predating = [], []
        for t in trees:
            if not (pathlib.Path(t) / ".githooks/pre-push").is_file():
                predating.append(pathlib.Path(t).name)
                continue
            resolved = pathlib.Path(hp) if hp.startswith("/") else pathlib.Path(t) / (hp or ".git/hooks")
            if not (resolved / "pre-push").is_file():
                ungated.append(t)
        c.check("every worktree carrying the gate resolves hooks to it", not ungated,
                f"resolves elsewhere: {ungated} — pushes from these are ungated AND silent")
        if predating:
            print(f"[note] {len(predating)} worktree(s) predate the gate and are UNGATED: "
                  f"{predating} — inherent to per-worktree hook resolution; see git-policy.md "
                  f"§'A fresh clone ships this gate OFF'. Merging this lane gates the main checkout.")

    if c.block("ARM2 · the generic arm-check agrees with this gate-specific one"):
        # ── ⭐ SCC-110: the GENERIC arm-check must agree with this gate-specific one ──────────
        # Extraction was the original SCC-110 plan and was rejected on evidence: the block above
        # covers `mint-push-token.sh` and per-worktree hook resolution, neither of which
        # `hooks_armed` models, so lifting it out would have deleted coverage that SCC-77's
        # adversarial review put here. What the extraction was actually FOR was preventing two
        # checkers from drifting apart — and a cross-check catches that directly, without
        # removing anything. If these two ever disagree, one of them is wrong and this fails.
        # Only the DERIVED-set assertion is kept. An "is this repo armed" check here would be a
        # verbatim restatement of test_hooks_armed case A, and it would couple the files the wrong
        # way round — deleting SOP-ENFORCE would red a file titled "main write gate".
        generic = hooks_armed.scan(REPO)
        c.check("this gate's hook is in the generic check's DERIVED set, and executable",
                any(h["name"] == "pre-push" and h["executable"] for h in generic["hooks"]),
                "drift: hooks_armed no longer sees the hook this whole file is about")

    if c.block("SET · settings.json may never name one platform's binary"):
        # ── settings.json may never name one platform's binary again ─────────────────────────
        raw = (REPO / ".claude/settings.json").read_text()
        json.loads(raw)  # must parse
        banned = [b for b in ("powershell -", '"powershell', "python (", "C:\\\\", "C:/")
                  if b in raw]
        # bare `python`/`powershell` as the launched binary — `pwsh` and `python3` are fine.
        banned += re.findall(r'command"\s*:\s*"\s*(?:powershell|python)\b', raw)
        c.check("no hook command is bound to one platform's binaries", not banned,
                f"found {banned} — this is the exit-127 bug that hid the gate for weeks")

    # ── C5 (SCC-171) · the STRUCTURAL half, and why it is not redundant with C1-C4 ────────
    #
    # C1-C4 drive the MINTER through a `git` shim and measure real behaviour. The GATE's copy of
    # the same defect cannot be measured that way, and the reason is worth stating: on POSIX,
    # `case "$GIT_COMMON" in /*)` is a NO-OP. An absolute POSIX path matches `/*` and is left
    # alone; a relative one is resolved against a root we have already `cd`'d to, so both branches
    # land on the same file. The block only misbehaves for a string that is absolute on Windows
    # while not starting with `/` — i.e. only on the machine this suite cannot run on. There is no
    # POSIX observable, so a behavioural mutant for the gate would be UNKILLABLE, and declaring an
    # unkillable mutant is worse than declaring none (SCC-179).
    #
    # ⛔ SO THE GUARD IS STRUCTURAL — AND IT IS THE TEXTBOOK COMMENT-LITERAL TRAP (SCC-125).
    # Both scripts now carry an explanation that QUOTES the deleted block verbatim, because
    # "we removed this and here is why" is the only way the next reader learns not to add it back.
    # A naive grep matches the documentation and reports the bug as present. So comments are
    # stripped first, and C5b pins that the fixture which makes stripping necessary still exists —
    # if the explanation is ever deleted, C5 quietly degrades into a plain grep and C5b says so.
    def uncommented(text: str) -> str:
        return "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))

    NORMALISE = 'case "$GIT_COMMON"'
    if c.block("C5 · the hand-rolled --git-common-dir normalisation is gone"):
        for p in (GATE, MINT):
            c.check(f"C5 · {p.name} does not re-normalise --git-common-dir by hand",
                    NORMALISE not in uncommented(p.read_text(encoding="utf-8")),
                    "the PC path bug: an absolute `C:/…` answer does not match `/*`, so the repo "
                    "root is glued in front of it and the token goes somewhere that cannot exist")
        c.check("C5b · (control) the deleted block is still QUOTED in the comments",
                NORMALISE in MINT.read_text(encoding="utf-8"),
                "the comment-literal fixture is gone, so C5 is now an ordinary grep and no longer "
                "proves that stripping comments was load-bearing")

    if os.name == "nt":
        return c.finish()

    with TempDir() as tmp:
        d, bare = make_repo(tmp)
        # ⭐ `sha` is now a REAL merge commit sitting exactly one above origin/main, with
        # `chore/SCC-77-x` as its second parent — the only shape any door produces. The old
        # fixture used a plain base commit, which the gate could only approve because D1 and D2
        # were both open (no `^2`, no remote tip).
        stage_one_merge(d)
        sha = sh("git", "rev-parse", "HEAD", cwd=d)[1].strip()

        if c.block("BEH · the gate's refusal ladder, rung by rung"):
            # ── BEHAVIOUR ────────────────────────────────────────────────────────────────────
            rc, out = gate(d, sha, ref="refs/heads/chore/x")
            c.check("non-main ref passes with no token", rc == 0 and "REFUSED" not in out)

            # `epic/main-fix` alone proves nothing: it does not contain "refs/heads/main" as a
            # substring, so a naive substring implementation would pass it too. The refs that
            # actually discriminate are the ones where "refs/heads/main" IS a prefix/substring.
            for near in ("refs/heads/main-backup", "refs/heads/mainx", "refs/heads/epic/main-fix"):
                rc, out = gate(d, sha, ref=near)
                c.check(f"`{near}` does not trip the match", rc == 0,
                        "whole-ref equality — main-backup and mainx are the cases that catch a "
                        "substring or prefix implementation")

            rc, out = gate(d, sha)
            c.check("main with NO token is refused", rc != 0 and "REFUSED" in out)
            c.check("the refusal names both doors",
                    "/cicd-push-e2e" in out and "/smh-close-task-merge-tree" in out)
            c.check("the refusal does NOT name update-sprint-memory as a door",
                    "/cicd-update-sprint-memory" not in out,
                    "it lands on the epic branch; listing it here is the SCC-77 misreading")

            write_token(d, sha)
            rc, out = gate(d, sha)
            c.check("main WITH a valid token is allowed", rc == 0 and "approved" in out)
            c.check("the token is consumed", not token_path(d).exists(),
                    "single use — a surviving token authorises the next merge too (SCC-71)")

            rc, out = gate(d, sha)
            c.check("replaying the same push is refused", rc != 0 and "REFUSED" in out)

            write_token(d, "deadbeef" * 5)
            rc, out = gate(d, sha)
            c.check("token minted for another sha is refused", rc != 0 and "carries" in out,
                    "the check that would have caught six merges on one sign-off")
            c.check("a refused token is discarded too", not token_path(d).exists(),
                    "or a stale token waits around for a push that happens to match")

            write_token(d, sha, minted=int(time.time()) - 1860)
            rc, out = gate(d, sha)
            c.check("token older than 30 min is refused", rc != 0 and "stale" in out)

            # ⭐ SCC-37: a token WITHOUT approval evidence is refused and consumed. The minter can no
            # longer write one, so this shape is either hand-forged or pre-SCC-37 — both unspendable.
            write_token(d, sha, approval=None)
            rc, out = gate(d, sha)
            c.check("token with no approval record is refused", rc != 0 and "no operator-approval" in out,
                    "a hand-written token must not outrank the minter's own refusal")
            c.check("the approval-less token is discarded", not token_path(d).exists())

            token_path(d).write_text("garbage\n")
            rc, out = gate(d, sha)
            c.check("malformed token is refused", rc != 0 and "malformed" in out)

            # The gate does arithmetic on `minted`, which is read from a FILE. A non-numeric or
            # future-dated value must fail CLOSED, not error out or silently pass. `$(( ))` treats an
            # unset name as 0, so garbage reads as epoch 0 — ancient, hence stale. Asserted rather than
            # assumed, because "it happens to fail safe" and "it is guaranteed to" are different claims.
            token_path(d).write_text(
                f"branch=b\ntip={sha}\ncommand=/x\nkey=K\nminted=NOTANUMBER\n")
            rc, out = gate(d, sha)
            c.check("non-numeric timestamp fails CLOSED", rc != 0 and "REFUSED" in out,
                    "arithmetic on untrusted file content must never fall through to allow")

            write_token(d, sha, minted=int(time.time()) + 99999)
            rc, out = gate(d, sha)
            c.check("future-dated token is refused (clock skew)", rc != 0 and "REFUSED" in out,
                    "a negative age must not read as 'fresh'")

            # pre-push receives ONE LINE PER REF. A push carrying several refs must still be gated on
            # main wherever main appears in that list — not only when it is the first line.
            write_token(d, sha)
            r = subprocess.run(
                ["sh", str(d / ".agents/scripts/git-hooks/pre-push-main-approval.sh"), "origin", "url"],
                cwd=str(d), text=True, capture_output=True,
                input=f"refs/heads/a {sha} refs/heads/a {ZERO}\n"
                      f"refs/heads/main {sha} refs/heads/main {remote_main(d)}\n"
                      f"refs/heads/z {sha} refs/heads/z {ZERO}\n")
            c.check("multi-ref push is gated on main wherever it appears",
                    "approved" in (r.stdout + r.stderr) and not token_path(d).exists(),
                    "a `git push --all` must not smuggle main past the gate on a later line")

            rc, out = gate(d, ZERO)
            c.check("deleting main is always refused", rc != 0 and "DELETE" in out)

            arm = d / ".agents/scripts/git-hooks/MAIN-PUSH-ENFORCE"
            arm.rename(d / "arm.bak")
            rc, out = gate(d, sha)
            c.check("disarmed (no MAIN-PUSH-ENFORCE) passes through", rc == 0 and "REFUSED" not in out)
            (d / "arm.bak").rename(arm)

            (d / ".agents/scripts/git-hooks/DISABLE").write_text("")
            rc, out = gate(d, sha)
            c.check("DISABLE kill switch passes through", rc == 0 and "REFUSED" not in out)
            (d / ".agents/scripts/git-hooks/DISABLE").unlink()

        if c.block("MINT · the minter's own refusals"):
            # ── MINTER ───────────────────────────────────────────────────────────────────────
            rc, out = sh("sh", str(d / ".agents/scripts/git-hooks/mint-push-token.sh"),
                         "--command", "/smh-close-task-merge-tree", "--branch", "chore/SCC-77-x",
                         "--key", "SCC-77", "--operator-approval", "yes, merge SCC-77-x now", cwd=d)
            c.check("minter writes a token from main", rc == 0 and token_path(d).exists())
            c.check("minted token carries HEAD's sha", f"tip={sha}" in token_path(d).read_text())
            c.check("minted token records the operator's words",
                    "approval=yes, merge SCC-77-x now" in token_path(d).read_text(),
                    "the quote is the approval evidence; a token without it is refused at the push")
            rc, out = gate(d, sha)
            c.check("the minted token is accepted by the gate", rc == 0 and "approved" in out)
            # ⭐ SCC-37: the spend prints the words back — what claimed to authorise the merge is
            # visible in the push output, not only in a file nobody opens.
            # (re-mint for the echo check — the gate above consumed the token)
            sh("sh", str(d / ".agents/scripts/git-hooks/mint-push-token.sh"),
               "--command", "/smh-close-task-merge-tree", "--branch", "chore/SCC-77-x",
               "--key", "SCC-77", "--operator-approval", "yes, merge SCC-77-x now", cwd=d)
            rc, out = gate(d, sha)
            c.check("the gate PRINTS the approval words at the push",
                    rc == 0 and 'AUTHORIZED BY OPERATOR: "yes, merge SCC-77-x now"' in out,
                    "a stretched quote must survive being read back at push time")

            rc, out = sh("sh", str(d / ".agents/scripts/git-hooks/mint-push-token.sh"),
                         "--branch", "chore/x", cwd=d)
            c.check("minter requires --command", rc != 0)

            # ⭐ SCC-37: THE RECURRENCE GUARD. A non-interactive shell — every agent shell — cannot
            # mint without the operator's verbatim words. "You can move the ticket to done" read as a
            # merge sign-off is the live failure this closes: the minter now demands the words
            # themselves, so an inference has nothing to type.
            rc, out = sh("sh", str(d / ".agents/scripts/git-hooks/mint-push-token.sh"),
                         "--command", "/smh-close-task-merge-tree", "--branch", "chore/SCC-77-x",
                         "--key", "SCC-77", cwd=d)
            c.check("minter REFUSES without operator approval in a non-TTY shell",
                    rc != 0 and "no operator approval" in out,
                    "an agent shell must not be able to self-authorise a main merge")
            c.check("the refusal teaches the contract",
                    "never merge permission" in out.lower() or "NEVER merge permission" in out,
                    "the message must name the ticket-permission != merge-permission rule")

            # `-B`, not `-b`: `chore/SCC-77-x` is the staged lane and already exists.
            sh("git", "checkout", "-qB", "chore/SCC-77-off-main", cwd=d)
            rc, out = sh("sh", str(d / ".agents/scripts/git-hooks/mint-push-token.sh"),
                         "--command", "/smh-close-task-merge-tree", "--branch", "chore/SCC-77-x",
                         "--operator-approval", "merge it", cwd=d)
            c.check("minter refuses when HEAD is not main", rc != 0 and "not 'main'" in out,
                    "a token minted off main names a sha the push will not carry")
            sh("git", "checkout", "-q", "main", cwd=d)

        # ── C (SCC-171) · the token path as git gives it, and a mint that cannot lie ──────
        #
        # Two defects, one road. On the PC, `--git-common-dir` in a worktree answers
        # `C:/Users/.../.git/worktrees/<name>` — which does NOT match the `case … in /*)` arm the
        # scripts used to normalise with, so the repo root got prepended to an already-absolute
        # path. The token was then written nowhere the gate would look, and the gate refused
        # EVERY push to main. Every lane in this system is a worktree, on one of two machines.
        #
        # And the write was never checked, so the failure was SILENT AND THEN LIED: the minter
        # printed "🔑 main-push token minted" and exited 0 with nothing on disk. The close-out
        # pushed, and the gate refused for having no token — leaving the operator holding a
        # success message and a refusal that contradicted it.
        #
        # ⛔⛔ GROUND TRUTH IS THE TOKEN ON DISK, NOT THE EXIT CODE. AGY's first cut of these
        # assertions ended in `… or wrote_ok` where `wrote_ok = returncode == 0` — satisfied BY
        # THE DEFECT, so they went green on the bug and red on the fix. The three below are
        # phrased as "the bad thing did not happen", and C4 is the control that keeps them from
        # being vacuously true.
        if c.block("C · the PC token path (mint, driven by a git shim)"):
            token_path(d).unlink(missing_ok=True)
            fake_common = "C:/Users/dan/Sudo_Hatter_Command/.git/worktrees/gate-cluster"
            shim_dir = make_git_shim(tmp, fake_common)
            r = subprocess.run(
                ["sh", str(d / ".agents/scripts/git-hooks/mint-push-token.sh"),
                 "--command", "/smh-close-task-merge-tree", "--branch", "chore/SCC-77-x",
                 "--key", "SCC-77", "--operator-approval", "pc path check"],
                cwd=str(d), text=True, capture_output=True,
                env={**os.environ, "PATH": f"{shim_dir}{os.pathsep}{os.environ.get('PATH', '')}",
                     "GIT_TERMINAL_PROMPT": "0"})
            c_out = (r.stdout or "") + (r.stderr or "")
            # `C:/…` is a RELATIVE path on POSIX, so a *correct* run resolves it under the repo
            # root too — both spellings are checked, and neither can exist because the parents
            # do not.
            wrote = token_path(d).is_file() or (d / "C:").exists()
            banner = ("token minted" in c_out) or ("🔑" in c_out)

            c.check("C1 · the repo root is NOT prepended to an absolute `C:/` path",
                    f"{d}/C:" not in c_out,
                    "the PC normalisation bug: an absolute answer that does not match `/*` gets "
                    "the toplevel glued in front of it, and the token goes somewhere that cannot "
                    "exist")
            c.check("C2 · mint does NOT print the success banner when no token was written",
                    wrote or not banner,
                    "printed the minted banner with nothing on disk:\n" + c_out)
            c.check("C3 · a failed token write EXITS NON-ZERO",
                    wrote or r.returncode != 0,
                    f"exit was {r.returncode} with no token written:\n{c_out}")
            c.check("C4 · (control) the shim really did divert the token away from disk",
                    not wrote,
                    "a token WAS written — C2/C3 proved nothing this run")
            token_path(d).unlink(missing_ok=True)
            shutil.rmtree(d / "C:", ignore_errors=True)

        if c.block("E2E · a REAL git push through core.hooksPath at a real remote"):
            # ── END TO END: a real `git push`, through core.hooksPath, at a real remote ───────
            # Everything above can pass while git never invokes the hook at all.
            (d / ".githooks").mkdir()
            shutil.copy2(DISPATCH, d / ".githooks/pre-push")
            (d / ".githooks/pre-push").chmod(0o755)
            sh("git", "config", "core.hooksPath", ".githooks", cwd=d)
            token_path(d).unlink(missing_ok=True)

            before = sh("git", "--git-dir", str(bare), "rev-parse", "main", cwd=d)[1].strip()
            rc, out = sh("git", "push", "origin", "main", cwd=d)
            c.check("REAL git push to main is refused with no token", rc != 0 and "REFUSED" in out,
                    "if this passes, git is not running the hook — the whole gate is decorative")
            after = sh("git", "--git-dir", str(bare), "rev-parse", "main", cwd=d)[1].strip()
            c.check("the remote tip did NOT move", before == after,
                    "the remote already carries `main` (it must, or the gate is being asked the "
                    "D2 question instead of the real one) — so the assertion is that it is UNMOVED")

            lane = stage_one_merge(d)
            sh("sh", str(d / ".agents/scripts/git-hooks/mint-push-token.sh"),
               "--command", "/smh-close-task-merge-tree", "--branch", lane,
               "--key", "SCC-77", "--operator-approval", "yes - land it", cwd=d)
            rc, out = sh("git", "push", "origin", "main", cwd=d)
            c.check("REAL git push to main succeeds with a token", rc == 0, out.strip()[-200:])
            landed = sh("git", "--git-dir", str(bare), "rev-parse", "main", cwd=d)[1].strip()
            c.check("the merge reached the remote", landed != before and landed != "",
                    f"before={before[:9]} after={landed[:9]}")
            c.check("the token was consumed by the real push", not token_path(d).exists())

    # ── ⭐ ONE SIGN-OFF = ONE MERGE (the check the first cut of this gate did NOT have) ──────
    #
    # The sha check is not sufficient, and claiming it was is what this block exists to stop
    # recurring. A token authorises a PUSH; what SCC-71 needs gated is a MERGE. Merge six branches
    # locally, mint once, push once — the sha matches the whole way and six merges land on one
    # approval. Reproduced during review before the fix: 6 merges on the remote, one token.
    with TempDir() as tmp:
        d, bare = make_repo(tmp)
        if c.block("ONE · one sign-off = ONE merge, end to end at a real remote"):
            (d / ".githooks").mkdir()
            shutil.copy2(DISPATCH, d / ".githooks/pre-push")
            (d / ".githooks/pre-push").chmod(0o755)
            sh("git", "push", "-q", "--no-verify", "origin", "main", cwd=d)
            sh("git", "fetch", "-q", "origin", cwd=d)
            sh("git", "config", "core.hooksPath", ".githooks", cwd=d)
            mint = str(d / ".agents/scripts/git-hooks/mint-push-token.sh")

            def merge_lane(name):
                sh("git", "checkout", "-q", "-b", name, "main", cwd=d)
                (d / f"{name.replace('/', '_')}.txt").write_text("x\n")
                sh("git", "add", "-A", cwd=d)
                sh("git", "commit", "-qm", f"work {name}", cwd=d)
                sh("git", "checkout", "-q", "main", cwd=d)
                sh("git", "merge", "-q", "--no-ff", name, "-m", f"merge: {name} -> main", cwd=d)

            # --- the happy path must still work, or the fix is worse than the bug ---
            merge_lane("chore/SCC-77-a")
            rc, out = sh("sh", mint, "--command", "/smh-close-task-merge-tree",
                         "--branch", "chore/SCC-77-a", "--key", "SCC-77",
                         "--operator-approval", "yes - land it", cwd=d)
            c.check("minter accepts a single merge sitting on origin/main", rc == 0, out.strip()[:160])
            rc, out = sh("git", "push", "origin", "main", cwd=d)
            c.check("ONE merge with a token lands", rc == 0, out.strip()[-160:])
            rc, out = sh("git", "--git-dir", str(bare), "rev-list", "--count", "--merges", "main", cwd=d)
            c.check("exactly 1 merge on the remote", out.strip() == "1", f"got {out.strip()}")

            # --- the attack: batch several merges behind one sign-off ---
            sh("git", "fetch", "-q", "origin", cwd=d)
            for lane in ("chore/SCC-77-b", "chore/SCC-77-c", "chore/SCC-77-d"):
                merge_lane(lane)
            rc, out = sh("sh", mint, "--command", "/smh-close-task-merge-tree",
                         "--branch", "chore/SCC-77-b", "--key", "SCC-77",
                         "--operator-approval", "yes - land it", cwd=d)
            c.check("minter REFUSES to mint for a batch of merges", rc != 0 and "exactly one merge" in out,
                    "caught at mint time, where the message can still name the fix")

            # even a hand-forged token must not get the batch through — the gate is the backstop
            write_token(d, sh("git", "rev-parse", "HEAD", cwd=d)[1].strip())
            rc, out = sh("git", "push", "origin", "main", cwd=d)
            c.check("gate REFUSES a batched push even with a valid-looking token",
                    rc != 0 and "does not advance main by exactly one merge" in out,
                    "THE regression guard: 6 merges rode 1 token before this check existed")
            rc, out = sh("git", "--git-dir", str(bare), "rev-list", "--count", "--merges", "main", cwd=d)
            c.check("the batch did NOT reach the remote", out.strip() == "1", f"got {out.strip()}")

            # --- force-push rewind: the same invariant covers it ---
            before = sh("git", "--git-dir", str(bare), "rev-parse", "main", cwd=d)[1].strip()
            sh("git", "reset", "-q", "--hard", "main~1", cwd=d)
            write_token(d, sh("git", "rev-parse", "HEAD", cwd=d)[1].strip())
            rc, out = sh("git", "push", "--force", "origin", "main", cwd=d)
            c.check("force-push REWIND of main is refused", rc != 0 and "REFUSED" in out,
                    "delete was refused but rewind was not — same destructive outcome")
            after = sh("git", "--git-dir", str(bare), "rev-parse", "main", cwd=d)[1].strip()
            c.check("the remote tip is unchanged after the rewind attempt", before == after)

            # --- the token is for ONE NAMED branch, not a blank cheque ---
            sh("git", "fetch", "-q", "origin", cwd=d)
            sh("git", "reset", "-q", "--hard", "origin/main", cwd=d)
            merge_lane("chore/SCC-77-e")
            tip = sh("git", "rev-parse", "HEAD", cwd=d)[1].strip()
            token_path(d).write_text(
                f"branch=chore/SCC-77-a\ntip={tip}\ncommand=/x\nkey=K\nminted={int(time.time())}\n"
                f"approval=forged but present - the branch check must still fire\n")
            rc, out = sh("git", "push", "origin", "main", cwd=d)
            c.check("a token naming a DIFFERENT branch than the merge is refused",
                    rc != 0 and "authorises landing" in out,
                    "otherwise one sign-off is a blank cheque any merge can spend")

            # --- the documented escape hatch must actually work (acceptance item 6) ---
            write_token(d, "irrelevant")   # deliberately wrong; --no-verify skips the hook entirely
            rc, out = sh("git", "push", "--no-verify", "origin", "main", cwd=d)
            c.check("`git push --no-verify` bypasses the gate, as documented", rc == 0,
                    "the escape hatch is evidence, not a doc claim")

        if c.block("PRE · the Claude PreToolUse hook stands down for a valid token, asks otherwise"):
            # ── LAYER 2: the Claude PreToolUse hook must not fight the door commands ─────────
            #
            # `permissionDecision: "ask"` becomes an auto-DENY in auto mode. Before SCC-77 that hook
            # was dead (exit 127) so nobody noticed; reviving it without this means a headless
            # close-out merges, mints, then has its own push denied — leaving `main` merged locally
            # with a token that expires in 30 minutes. So it stands down when a valid token already
            # covers the push, and asks in every other case.
            hook = REPO / ".agents/hooks/require-push-approval.py"
            if hook.is_file():
                def decide(cmd="env -u GITHUB_TOKEN git push origin main"):
                    r = subprocess.run(
                        [sys.executable, str(hook)], cwd=str(d), text=True, capture_output=True,
                        input=json.dumps({"tool_name": "Bash", "cwd": str(d),
                                          "tool_input": {"command": cmd}}))
                    body = (r.stdout or "").strip()
                    if not body:
                        return "allow"
                    return json.loads(body)["hookSpecificOutput"]["permissionDecision"]

                token_path(d).unlink(missing_ok=True)
                c.check("PreToolUse ASKS on a push to main with no token", decide() == "ask")

                head = sh("git", "rev-parse", "HEAD", cwd=d)[1].strip()
                write_token(d, head)
                c.check("PreToolUse STANDS DOWN when a valid token covers the push",
                        decide() == "allow",
                        "otherwise ask->auto-deny strands a headless close-out mid-merge")

                write_token(d, "deadbeef" * 5)
                c.check("PreToolUse ASKS when the token is for another sha", decide() == "ask")

                write_token(d, head, minted=int(time.time()) - 9999)
                c.check("PreToolUse ASKS when the token is stale", decide() == "ask")

                token_path(d).write_text(f"branch=b\ntip={head}\ncommand=/x\nkey=K\nminted=NOTNUM\n")
                c.check("PreToolUse ASKS when the timestamp is garbage", decide() == "ask",
                        "fails toward asking — any doubt and the prompt still fires")

                token_path(d).unlink(missing_ok=True)
                c.check("PreToolUse ignores a push to a non-protected branch",
                        decide("git push origin HEAD:chore/x") == "allow")

    # ── D (SCC-172) · the fail-opens the edge lens MEASURED, now closed ───────────────────
    #
    # All three were approved end-to-end before they were closed - reproduced, not reasoned
    # about. Each gets its own case, because a refusal with no case is the next silent
    # regression, and each asserts its OWN reason: nine rungs print the same banner, so
    # matching "REFUSED" would let any rung stand in for the one under test.
    with TempDir() as tmp:
        d, bare = make_repo(tmp, "d")
        (d / ".githooks").mkdir()
        shutil.copy2(DISPATCH, d / ".githooks/pre-push")
        (d / ".githooks/pre-push").chmod(0o755)
        sh("git", "config", "core.hooksPath", ".githooks", cwd=d)

        if c.block("D1 · a token whose branch does not resolve is a REFUSAL, not a skip"):
            # ⛔ The branch-binding rung was the ONLY thing requiring merge-ness, and it was
            # skipped whenever `claimed` came back empty. Two shapes, both measured as APPROVED:
            # a plain non-merge commit with a token naming a branch that never existed, and a
            # real merge of one branch with a token naming another that is not checked out here.
            # Reachable with no adversarial intent at all - a fresh clone, the other machine, a
            # lane pruned before the mint, a typo.
            sh("git", "fetch", "-q", "origin", cwd=d)
            sh("git", "checkout", "-q", "-B", "main", "origin/main", cwd=d)
            (d / "plain.txt").write_text("plain\n")
            # `--`, not `-A`: see stage_one_merge. `-A` stages the untracked `.githooks/pre-push`
            # and the next checkout deletes it, leaving the repo silently ungated.
            sh("git", "add", "--", str(d / "plain.txt"), cwd=d)
            sh("git", "commit", "-qm", "a PLAIN commit on main", "--no-verify", cwd=d)
            head = sh("git", "rev-parse", "HEAD", cwd=d)[1].strip()
            write_token(d, head, branch="chore/SCC-77-never-existed")
            rc, out = gate(d, head)
            c.check("D1 · a NON-MERGE commit on main is REFUSED even with a valid-looking token",
                    rc != 0 and "MERGE commit" in out,
                    "measured as APPROVED before this: tip matched, ^1 was the remote tip, the "
                    f"branch did not resolve, so the only merge-ness check was skipped\n{out}")
            c.check("D1b · ...and the token is discarded like every other refusal",
                    not token_path(d).exists())

            lane = stage_one_merge(d)
            head = sh("git", "rev-parse", "HEAD", cwd=d)[1].strip()
            write_token(d, head, branch="epic/SCC-77-only-on-the-remote")
            rc, out = gate(d, head)
            c.check("D1c · a REAL merge with a token naming an UNRESOLVABLE branch is REFUSED",
                    rc != 0 and "does not resolve" in out,
                    "the gate used to APPROVE this and print the unverified claim back as if it "
                    f"had checked it\n{out}")

            # ⛔ The allow-half control: the rung must still pass the shape it exists to permit.
            write_token(d, head, branch=lane)
            rc, out = gate(d, head)
            c.check("D1d · (control) a token naming the branch that WAS merged still passes",
                    rc == 0 and "approved" in out,
                    "a refusal that also refuses the legitimate case is not a fix\n" + out)

        if c.block("D2 · a push that CREATES main on a remote is a REFUSAL"):
            # ⛔ Every check - the one-merge invariant AND the branch binding - lived inside
            # `remote_sha != ZERO`, with no `else`. Measured: a bare remote with no `main`,
            # THREE stacked --no-ff merges, one hand-written token -> "main push approved",
            # and `rev-list --count --merges` on the remote said 3.
            fresh = tmp / "fresh.git"
            sh("git", "init", "-q", "--bare", str(fresh), cwd=tmp)
            sh("git", "remote", "add", "fresh", str(fresh), cwd=d)
            for n in ("a", "b", "c"):                       # three stacked merges, one token
                sh("git", "fetch", "-q", "origin", cwd=d)
                stage_one_merge(d, f"chore/SCC-77-stack-{n}")
            head = sh("git", "rev-parse", "HEAD", cwd=d)[1].strip()
            write_token(d, head, branch="chore/SCC-77-stack-c")
            # ⛔ THE CONTROL THAT MAKES D2 MEAN ANYTHING. A push that is refused and a push that
            # runs no hook at all are both "the remote did not get what we expected" — and this
            # fixture really did lose its hook to a stray `git add -A`, so D2 spent a run
            # measuring an UNGATED push and calling it a fail-open. Assert the instrument first.
            c.check("D2-pre · (control) the hook is still installed before the push is judged",
                    (d / ".githooks/pre-push").is_file()
                    and sh("git", "config", "--get", "core.hooksPath", cwd=d)[1].strip() == ".githooks",
                    "no hook means an ungated push, which looks nothing like a refusal and "
                    "everything like one if you only read the remote")
            rc, out = sh("git", "push", "fresh", "main", cwd=d)
            c.check("D2 · CREATING main on a remote with no main is REFUSED",
                    rc != 0 and ("has no main yet" in out or "CREATE" in out),
                    "three merges rode one token onto a fresh remote before this\n" + out)
            rc, out = sh("git", "ls-remote", "--heads", str(fresh), "main", cwd=d)
            c.check("D2b · nothing reached the fresh remote", "refs/heads/main" not in out, out)
            token_path(d).unlink(missing_ok=True)

            # The reason is asserted separately from the ladder: driving the gate directly with
            # a ZERO remote_sha isolates the arm from anything git might decide on its own.
            sh("git", "fetch", "-q", "origin", cwd=d)
            lane = stage_one_merge(d)
            head = sh("git", "rev-parse", "HEAD", cwd=d)[1].strip()
            write_token(d, head, branch=lane)
            rc, out = gate(d, head, remote_sha=ZERO)
            c.check("D2c · the ZERO arm refuses ON ITS OWN REASON, not a shared banner",
                    rc != 0 and "one-sign-off-one-merge invariant cannot be evaluated" in out,
                    "nine rungs print the same banner; pinning `REFUSED` would let any of them "
                    f"stand in for this one\n{out}")

    # ── ⛔ D3 · THE STALE WORKTREE — the fail-open that is not in the gate at all ────────────
    #
    # The two rungs above are in `pre-push-main-approval.sh`. This one is in the DISPATCHER, and
    # it is the only fail-open here that needs no token, no merge and no remote state to trigger:
    # if `.agents/scripts/git-hooks/` is simply ABSENT from the tree, `.githooks/pre-push` used to
    # print a warning and `exit 0` for every ref, `main` included. The gate was never bypassed —
    # it was never asked. Reproduced on AGY: same repo, same refs, same missing token; from the
    # main checkout REFUSED, from a stale worktree `main -> main` LANDED.
    #
    # ⭐ THE ALLOW IS NOT DELETED, IT IS NARROWED, and both halves are asserted below. A worktree
    # cut before these scripts existed must still be able to push its own lane, or the remedy for
    # being out of date is unreachable (SCC-32). What it must not do is push `main` with nothing
    # checking anything: "no gate ran" must never be quieter than "the gate said no".
    with TempDir() as tmp:
        d, bare = make_repo(tmp)
        if c.block("D3 · a stale worktree may push its LANE, never `main`"):
            (d / ".githooks").mkdir()
            shutil.copy2(DISPATCH, d / ".githooks/pre-push")
            (d / ".githooks/pre-push").chmod(0o755)
            sh("git", "config", "core.hooksPath", ".githooks", cwd=d)
            # THE STALE STATE: the dispatcher is present (it is what git runs), the gate scripts
            # it delegates to are not. That is exactly a tree cut from a commit before SCC-77.
            shutil.rmtree(d / ".agents/scripts/git-hooks")
            c.check("D3-pre · (control) the dispatcher is installed and the gate scripts are NOT",
                    (d / ".githooks/pre-push").is_file()
                    and not (d / ".agents/scripts/git-hooks").exists()
                    and sh("git", "config", "--get", "core.hooksPath", cwd=d)[1].strip() == ".githooks",
                    "if the dispatcher is missing too, git runs no hook at all and every "
                    "assertion below passes for the wrong reason")

            before = sh("git", "--git-dir", str(bare), "rev-parse", "main", cwd=d)[1].strip()
            stage_one_merge(d, "chore/SCC-172-stale")
            rc, out = sh("git", "push", "origin", "main", cwd=d)
            c.check("D3 · pushing `main` from a tree with no gate scripts is REFUSED",
                    rc != 0 and "REFUSED" in out,
                    "this LANDED before the fix — an ungated push to main, printing a warning "
                    f"that reads like success\n{out}")
            c.check("D3b · ...and the refusal says WHY, so it is not read as the gate's own no",
                    "approval gate is not" in out and "refs/heads/main" in out,
                    "'no gate present' and 'the gate refused' need different remedies: one is "
                    f"`git merge origin/main`, the other is a sign-off\n{out}")
            after = sh("git", "--git-dir", str(bare), "rev-parse", "main", cwd=d)[1].strip()
            c.check("D3c · nothing reached the remote", before == after,
                    f"before={before[:9]} after={after[:9]}")

            # ⭐ THE HALF THAT KEEPS THE FIX HONEST. A blanket refusal here would be simpler and
            # would strand a stale worktree with no way to ship at all — including no way to pull
            # the very scripts that would re-arm it.
            sh("git", "checkout", "-q", "-b", "chore/SCC-172-lane", cwd=d)
            (d / "lane.txt").write_text("work\n", encoding="utf-8")
            sh("git", "add", "--", "lane.txt", cwd=d)
            sh("git", "commit", "-qm", "SCC-172 lane work", cwd=d)
            rc, out = sh("git", "push", "origin", "chore/SCC-172-lane", cwd=d)
            c.check("D3d · (control) the same stale tree may still push its OWN lane",
                    rc == 0,
                    "narrowing the allow to non-main refs is the fix; refusing everything is a "
                    f"different bug wearing the same commit\n{out}")
            rc, out = sh("git", "ls-remote", "--heads", str(bare), "chore/SCC-172-lane", cwd=d)
            c.check("D3e · ...and it really arrived", "chore/SCC-172-lane" in out, out)

    return c.finish()


if __name__ == "__main__":
    raise SystemExit(main())

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
import re
import shutil
import subprocess
import time
from pathlib import Path

from _harness import Cases, TempDir

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


def make_repo(tmp: Path) -> Path:
    """A real git repo carrying the real gate files."""
    d = tmp / "work"
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
    return d


def token_path(d: Path) -> Path:
    return d / ".git/main-push-approval"


def write_token(d: Path, tip: str, minted: int | None = None, command: str = "/smh-close-task-merge-tree") -> None:
    token_path(d).write_text(
        f"branch=chore/SCC-77-x\ntip={tip}\ncommand={command}\nkey=SCC-77\n"
        f"minted={minted if minted is not None else int(time.time())}\n"
    )


def gate(d: Path, sha: str, ref: str = "refs/heads/main", remote_sha: str = ZERO) -> tuple[int, str]:
    return sh("sh", str(d / ".agents/scripts/git-hooks/pre-push-main-approval.sh"),
              "origin", "url", cwd=d, stdin=f"{ref} {sha} {ref} {remote_sha}\n")


def main() -> int:
    c = Cases("main write gate (SCC-77)")

    # ── INSTALLED ────────────────────────────────────────────────────────────────────────
    for p in (DISPATCH, GATE, MINT):
        c.check(f"{p.name} exists", p.is_file())
        c.check(f"{p.name} is executable", p.is_file() and p.stat().st_mode & 0o111 != 0,
                "chmod +x — git silently ignores a non-executable hook")
    c.check("MAIN-PUSH-ENFORCE present (gate is ARMED)", ARM.is_file())

    rc, out = sh("git", "config", "--get", "core.hooksPath", cwd=REPO)
    hp = out.strip()
    c.check("core.hooksPath is set", rc == 0 and bool(hp),
            "unset -> git uses .git/hooks and every gate here is OFF")
    c.check("core.hooksPath is RELATIVE", not hp.startswith("/") and ":" not in hp,
            f"got {hp!r} — an absolute path cannot survive a clone to the other machine")
    c.check("core.hooksPath resolves to a dir holding pre-push",
            (REPO / hp / "pre-push").is_file() if hp else False)

    # ── settings.json may never name one platform's binary again ─────────────────────────
    raw = (REPO / ".claude/settings.json").read_text()
    json.loads(raw)  # must parse
    banned = [b for b in ("powershell -", '"powershell', "python (", "C:\\\\", "C:/")
              if b in raw]
    # bare `python`/`powershell` as the launched binary — `pwsh` and `python3` are fine.
    banned += re.findall(r'command"\s*:\s*"\s*(?:powershell|python)\b', raw)
    c.check("no hook command is bound to one platform's binaries", not banned,
            f"found {banned} — this is the exit-127 bug that hid the gate for weeks")

    with TempDir() as tmp:
        d = make_repo(tmp)
        sha = sh("git", "rev-parse", "HEAD", cwd=d)[1].strip()
        old = sh("git", "rev-parse", "HEAD~0", cwd=d)[1].strip()

        # ── BEHAVIOUR ────────────────────────────────────────────────────────────────────
        rc, out = gate(d, sha, ref="refs/heads/chore/x")
        c.check("non-main ref passes with no token", rc == 0 and "REFUSED" not in out)

        rc, out = gate(d, sha, ref="refs/heads/epic/main-fix")
        c.check("`epic/main-fix` does not trip the match", rc == 0,
                "must be a whole-ref match, not a substring")

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

        token_path(d).write_text("garbage\n")
        rc, out = gate(d, sha)
        c.check("malformed token is refused", rc != 0 and "malformed" in out)

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

        # ── MINTER ───────────────────────────────────────────────────────────────────────
        rc, out = sh("sh", str(d / ".agents/scripts/git-hooks/mint-push-token.sh"),
                     "--command", "/smh-close-task-merge-tree", "--branch", "chore/SCC-77-x",
                     "--key", "SCC-77", cwd=d)
        c.check("minter writes a token from main", rc == 0 and token_path(d).exists())
        c.check("minted token carries HEAD's sha", f"tip={sha}" in token_path(d).read_text())
        rc, out = gate(d, sha)
        c.check("the minted token is accepted by the gate", rc == 0 and "approved" in out)

        rc, out = sh("sh", str(d / ".agents/scripts/git-hooks/mint-push-token.sh"),
                     "--branch", "chore/x", cwd=d)
        c.check("minter requires --command", rc != 0)

        sh("git", "checkout", "-qb", "chore/SCC-77-x", cwd=d)
        rc, out = sh("sh", str(d / ".agents/scripts/git-hooks/mint-push-token.sh"),
                     "--command", "/smh-close-task-merge-tree", "--branch", "chore/SCC-77-x", cwd=d)
        c.check("minter refuses when HEAD is not main", rc != 0 and "not 'main'" in out,
                "a token minted off main names a sha the push will not carry")
        sh("git", "checkout", "-q", "main", cwd=d)

        # ── END TO END: a real `git push`, through core.hooksPath, at a real remote ───────
        # Everything above can pass while git never invokes the hook at all.
        bare = tmp / "remote.git"
        sh("git", "init", "-q", "--bare", str(bare), cwd=tmp)
        sh("git", "remote", "add", "origin", str(bare), cwd=d)
        (d / ".githooks").mkdir()
        shutil.copy2(DISPATCH, d / ".githooks/pre-push")
        (d / ".githooks/pre-push").chmod(0o755)
        sh("git", "config", "core.hooksPath", ".githooks", cwd=d)
        token_path(d).unlink(missing_ok=True)

        rc, out = sh("git", "push", "origin", "main", cwd=d)
        c.check("REAL git push to main is refused with no token", rc != 0 and "REFUSED" in out,
                "if this passes, git is not running the hook — the whole gate is decorative")
        rc, out = sh("git", "ls-remote", "--heads", str(bare), "main", cwd=d)
        c.check("nothing reached the remote", "refs/heads/main" not in out)

        sh("sh", str(d / ".agents/scripts/git-hooks/mint-push-token.sh"),
           "--command", "/smh-close-task-merge-tree", "--branch", "chore/SCC-77-x",
           "--key", "SCC-77", cwd=d)
        rc, out = sh("git", "push", "origin", "main", cwd=d)
        c.check("REAL git push to main succeeds with a token", rc == 0, out.strip()[-200:])
        rc, out = sh("git", "ls-remote", "--heads", str(bare), "main", cwd=d)
        c.check("the commit reached the remote", "refs/heads/main" in out)
        c.check("the token was consumed by the real push", not token_path(d).exists())

    return c.finish()


if __name__ == "__main__":
    raise SystemExit(main())

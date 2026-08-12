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
                  f"refs/heads/main {sha} refs/heads/main {ZERO}\n"
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

    # ── ⭐ ONE SIGN-OFF = ONE MERGE (the check the first cut of this gate did NOT have) ──────
    #
    # The sha check is not sufficient, and claiming it was is what this block exists to stop
    # recurring. A token authorises a PUSH; what SCC-71 needs gated is a MERGE. Merge six branches
    # locally, mint once, push once — the sha matches the whole way and six merges land on one
    # approval. Reproduced during review before the fix: 6 merges on the remote, one token.
    with TempDir() as tmp:
        d = make_repo(tmp)
        bare = tmp / "remote.git"
        sh("git", "init", "-q", "--bare", str(bare), cwd=tmp)
        sh("git", "remote", "add", "origin", str(bare), cwd=d)
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
                     "--branch", "chore/SCC-77-a", "--key", "SCC-77", cwd=d)
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
                     "--branch", "chore/SCC-77-b", "--key", "SCC-77", cwd=d)
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
            f"branch=chore/SCC-77-a\ntip={tip}\ncommand=/x\nkey=K\nminted={int(time.time())}\n")
        rc, out = sh("git", "push", "origin", "main", cwd=d)
        c.check("a token naming a DIFFERENT branch than the merge is refused",
                rc != 0 and "authorises landing" in out,
                "otherwise one sign-off is a blank cheque any merge can spend")

        # --- the documented escape hatch must actually work (acceptance item 6) ---
        write_token(d, "irrelevant")   # deliberately wrong; --no-verify skips the hook entirely
        rc, out = sh("git", "push", "--no-verify", "origin", "main", cwd=d)
        c.check("`git push --no-verify` bypasses the gate, as documented", rc == 0,
                "the escape hatch is evidence, not a doc claim")

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

    return c.finish()


if __name__ == "__main__":
    raise SystemExit(main())

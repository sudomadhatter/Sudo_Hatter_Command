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
ALLOWLIST = HOOKDIR / "direct-push-allowlist.sh"   # SCC-183 — sourced by BOTH of the above
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
    for f in (GATE, MINT, ARM, ALLOWLIST):
        shutil.copy2(f, d / ".agents/scripts/git-hooks" / f.name)
    (d / "README").write_text("x\n")
    sh("git", "add", "README", ".agents", cwd=d)
    sh("git", "commit", "-qm", "base", cwd=d)
    return d


def token_path(d: Path) -> Path:
    return d / ".git/main-push-approval"


def write_token(d: Path, tip: str, minted: int | None = None, command: str = "/smh-close-task-merge-tree",
                approval: str | None = "test fixture: operator said merge it") -> None:
    # approval=None writes the pre-SCC-37 token shape — the case the gate must now refuse.
    body = (
        f"branch=chore/SCC-77-x\ntip={tip}\ncommand={command}\nkey=SCC-77\n"
        f"minted={minted if minted is not None else int(time.time())}\n"
    )
    if approval is not None:
        body += f"approval={approval}\n"
    token_path(d).write_text(body)


def gate(d: Path, sha: str, ref: str = "refs/heads/main", remote_sha: str = ZERO) -> tuple[int, str]:
    sh_bin = shutil.which("sh") or shutil.which("bash") or "bash"
    return sh(sh_bin, str(d / ".agents/scripts/git-hooks/pre-push-main-approval.sh"),
              "origin", "url", cwd=d, stdin=f"{ref} {sha} {ref} {remote_sha}\n")


def direct_repo(tmp: Path, publish: bool = True) -> tuple[Path, Path, str]:
    """A scratch repo wired for REAL pushes at a REAL bare remote (SCC-183).

    `publish=False` leaves `main` absent on the remote, so a push arrives with an all-zero
    `remote_sha` — the input that must not be allowed to skip the direct-mode checks.
    """
    d = make_repo(tmp)
    bare = tmp / "remote.git"
    sh("git", "init", "-q", "--bare", str(bare), cwd=tmp)
    sh("git", "remote", "add", "origin", str(bare), cwd=d)
    (d / ".githooks").mkdir()
    shutil.copy2(DISPATCH, d / ".githooks/pre-push")
    (d / ".githooks/pre-push").chmod(0o755)
    # ⛔ TRACKED, not left in the working tree. The refuse-half cases below deliberately
    # commit junk to `.githooks/pre-push` to prove the allowlist rejects it — and while it
    # was untracked, the `git reset --hard origin/main` between cases DELETED it instead of
    # restoring it, so every later case in that loop ran with no gate installed at all and
    # its push "succeeded". Five refuse cases were reading as failures of the feature when
    # they were an artifact of case ORDER. Tracking it makes the reset self-healing, and it
    # matches the real repo, where this file is tracked.
    sh("git", "add", ".githooks/pre-push", cwd=d)
    sh("git", "commit", "-qm", "base: install the pre-push dispatcher", cwd=d)
    if publish:
        sh("git", "push", "-q", "--no-verify", "origin", "main", cwd=d)
        sh("git", "fetch", "-q", "origin", cwd=d)
    sh("git", "config", "core.hooksPath", ".githooks", cwd=d)
    return d, bare, str(d / ".agents/scripts/git-hooks/mint-push-token.sh")


def commit_file(d: Path, rel: str, body: str = "x\n", msg: str = "SCC-183 docs: edit") -> str:
    """Write + commit one path, returning its sha. Explicit path, never `git add -A`."""
    p = d / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body)
    sh("git", "add", rel, cwd=d)
    sh("git", "commit", "-qm", msg, cwd=d)
    return sh("git", "rev-parse", "HEAD", cwd=d)[1].strip()


def mint_direct(d: Path, mint: str, key: str | None = "SCC-183") -> tuple[int, str]:
    args = ["sh", mint, "--command", "/smh-quick-fix", "--direct"]
    if key is not None:
        args += ["--key", key]
    return sh(*args, "--operator-approval", "yes - push the doc fix", cwd=d)


def direct_token(d: Path, tip: str, key: str = "SCC-183") -> None:
    """A hand-written `mode=direct` token — the forged-token half the minter cannot gate."""
    token_path(d).write_text(
        f"branch=main\ntip={tip}\ncommand=/smh-quick-fix\nkey={key}\nmode=direct\n"
        f"minted={int(time.time())}\napproval=yes - push the doc fix\n")


def main() -> int:
    c = Cases("main write gate (SCC-77)")

    # ── INSTALLED ────────────────────────────────────────────────────────────────────────
    if c.block("INSTALLED · the gate is on disk, executable, armed, and hooks resolve to it"):
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

    if os.name == "nt":
        return c.finish()

    if c.block("GATE · token presence, sha binding, staleness and fail-closed parsing"):
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

            sh("git", "checkout", "-qb", "chore/SCC-77-x", cwd=d)
            rc, out = sh("sh", str(d / ".agents/scripts/git-hooks/mint-push-token.sh"),
                         "--command", "/smh-close-task-merge-tree", "--branch", "chore/SCC-77-x",
                         "--operator-approval", "merge it", cwd=d)
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
               "--key", "SCC-77", "--operator-approval", "yes - land it", cwd=d)
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
    if c.block("MERGE · one sign-off = one merge, against a real remote, and the PreToolUse hook"):
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

    # ══ SCC-183 — THE DIRECT-TO-MAIN FAST LANE ═══════════════════════════════════════════
    #
    # A THIRD door to `main`, and the only one with no review ladder behind it. What stands in
    # for that review is the path ALLOWLIST, so these cases are the whole safety argument.
    #
    # Every one of them is written against a FIRST attempt at this feature that was reviewed
    # FAIL and deleted (commit 3c66dee). Two exploits were proven against it with real pushes
    # at a real bare remote, and both are replayed below so they cannot come back quietly:
    #
    #   H1  `--direct` with no `--key` landed a commit carrying NO Jira key at all. `--key`
    #       was optional, and the gate's key assertion was wrapped in `if [ -n "$t_key" ]` —
    #       so omitting the key did not fail the check, it DELETED the check.
    #
    #   H3  `--direct` landed a commit that rewrote `pre-push-main-approval.sh` to approve
    #       everything. The path check was a DENYLIST of six product directories; `.agents/`
    #       was not among them, so the gate approved the commit that disables the gate.
    #
    # The generalisation, and the reason this is an allowlist: a denylist authored against a
    # PRODUCT repo's layout is vacuous in a GOVERNANCE repo, where the crown jewels are
    # `.agents/` and `.githooks/`, not `backend/`. Five of that list's six directories do not
    # even exist here. An allowlist cannot fail that way — an unlisted path is refused, so a
    # directory nobody thought of is safe by default instead of open by default.

    if c.block("direct: minter refuses --direct with no --key"):
        with TempDir() as tmp:
            d, bare, mint = direct_repo(tmp)
            commit_file(d, "docs/guide.md")
            rc, out = mint_direct(d, mint, key=None)
            c.check("minter REFUSES --direct with no --key",
                    rc != 0 and "--key" in out and "requir" in out.lower(),
                    f"H1 replay: a keyless direct token is what put an untraceable commit "
                    f"on main. rc={rc}: {out.strip()[:200]}")
            c.check("...and mints NOTHING when it refuses",
                    not token_path(d).exists(),
                    "a token left behind after a refusal is spendable by the next push")

    if c.block("direct: gate refuses a token with an empty key"):
        with TempDir() as tmp:
            d, bare, mint = direct_repo(tmp)
            sha = commit_file(d, "docs/guide.md", msg="tidy the guide")   # no key in message
            direct_token(d, sha, key="")          # forged: the minter would never write this
            rc, out = sh("git", "push", "origin", "main", cwd=d)
            c.check("gate REFUSES a direct token carrying an empty key",
                    rc != 0 and "key" in out.lower(),
                    "H1's other half: the key assertion must fire on ABSENCE, not be skipped "
                    "by it. The minter is not the only way a token reaches the gate")
            c.check("...and the remote did NOT move",
                    sh("git", "--git-dir", str(bare), "rev-parse", "main", cwd=d)[1].strip() != sha)

    if c.block("direct: gate refuses a commit that rewrites the gate itself"):
        # ⛔ THREAT MODEL, because the obvious version of this test proves nothing.
        #
        # Writing a NEUTERED gate into the working tree and pushing it does bypass the gate —
        # but only because the hook git runs IS the working-tree copy, so it disabled itself
        # before the allowlist was ever consulted. That is just `--no-verify` spelled slowly,
        # it is out of scope for any pre-push hook, and a test asserting it conflates two
        # causes. (The exploit probe written against the deleted implementation had exactly
        # this flaw, and it flattered the finding.)
        #
        # The harm that is IN scope is distribution: a fast-lane push puts a modified gate on
        # the REMOTE, so every machine that pulls is running it. So the property to prove is
        # narrow and real — a commit that touches the gate file AT ALL is refused, with the
        # running gate fully intact.
        with TempDir() as tmp:
            d, bare, mint = direct_repo(tmp)
            base = sh("git", "--git-dir", str(bare), "rev-parse", "main", cwd=d)[1].strip()
            g = d / ".agents/scripts/git-hooks/pre-push-main-approval.sh"
            g.write_text(g.read_text() + "\n# a real, benign edit — the gate still works\n")
            sh("git", "add", ".agents/scripts/git-hooks/pre-push-main-approval.sh", cwd=d)
            sh("git", "commit", "-qm", "SCC-183 docs: tidy", cwd=d)      # innocent subject
            sha = sh("git", "rev-parse", "HEAD", cwd=d)[1].strip()
            rc_mint, out_mint = mint_direct(d, mint)
            c.check("minter REFUSES to mint for a commit that touches the gate",
                    rc_mint != 0 and not token_path(d).exists(),
                    f"the first of two independent refusals. rc={rc_mint}")

            # ⭐ Now the GATE on its own. The minter just refused, so a push here would be
            # rejected for "no token" — which is the RIGHT outcome for the WRONG reason, and
            # would leave the allowlist itself unproven. Forge the token the minter declined
            # to write, so the only thing left standing between this commit and main is the
            # gate's own allowlist.
            direct_token(d, sha)
            rc, out = sh("git", "push", "origin", "main", cwd=d)
            c.check("gate REFUSES a direct push that modifies the gate itself",
                    rc != 0,
                    f"H3 — the fast lane must not be able to ship a change to the thing "
                    f"gating the fast lane. rc={rc}: {out.strip()[:160]}")
            c.check("...and the modified gate did NOT reach the remote",
                    sh("git", "--git-dir", str(bare), "rev-parse", "main", cwd=d)[1].strip() == base,
                    "if this lands, every machine that pulls main runs the new gate")
            c.check("...and it was the ALLOWLIST that refused it, not some other check",
                    "prose" in out or "allowlist" in out.lower(),
                    f"attribution matters: a refusal for the wrong reason leaves the "
                    f"allowlist unproven. got: {out.strip()[:200]}")

    if c.block("direct: allowlist"):
        # BOTH halves. A gate that refuses everything is as broken as one that refuses
        # nothing, and only the allow half can tell the difference.
        with TempDir() as tmp:
            d, bare, mint = direct_repo(tmp)
            for rel in ("docs/guide.md",
                        "docs/deep/nested/page.md",
                        "_my_resources/_quick_reference/notes.md",
                        "_artifacts/_main/2026-08-16_x/walkthrough.md",
                        "README.md"):
                sh("git", "fetch", "-q", "origin", cwd=d)
                sha = commit_file(d, rel, msg=f"SCC-183 docs: {rel}")
                mint_direct(d, mint)
                rc, out = sh("git", "push", "origin", "main", cwd=d)
                landed = sh("git", "--git-dir", str(bare), "rev-parse", "main", cwd=d)[1].strip()
                c.check(f"ALLOW · {rel} lands", rc == 0 and landed == sha,
                        f"rc={rc}: {out.strip()[-200:]}")

        with TempDir() as tmp:
            d, bare, mint = direct_repo(tmp)
            base = sh("git", "--git-dir", str(bare), "rev-parse", "main", cwd=d)[1].strip()
            # ⭐ TWO INDEPENDENT LAYERS, PROVEN INDEPENDENTLY.
            #
            # The minter refuses these at mint time, so a push after a normal `mint_direct`
            # is rejected for "no approval token" — the right outcome for the wrong reason,
            # and it leaves the GATE's own allowlist completely unexercised. The mutation
            # sweep caught exactly that: blinding the gate's allowlist verdict SURVIVED,
            # because no case had ever reached it. So each path is pushed twice — once
            # through the minter, once with a FORGED token that skips the minter entirely.
            for rel, why in ((".agents/rules/git-policy.md", "law, not prose"),
                             (".agents/scripts/tests/x.py", "law, not prose"),
                             (".githooks/pre-push", "the gate dispatcher"),
                             ("tests/run_all.py", "the enforcement floor"),
                             ("opencode.json", "root, but not markdown"),
                             ("requirements.txt", "root, but not markdown"),
                             ("backend/app.py", "deployable"),
                             (".github/workflows/ci.yml", "CI is deployable")):
                sh("git", "reset", "-q", "--hard", "origin/main", cwd=d)
                # A stale token from the previous iteration would make the next mint check
                # meaningless — and one DOES leak whenever a push dies before the gate runs.
                token_path(d).unlink(missing_ok=True)
                # ⛔ APPEND to a live script, never overwrite it. `.githooks/pre-push` in this
                # scratch repo is the dispatcher git is about to RUN: replacing its body with
                # junk makes the push die at `command not found` (exit 127) instead of at the
                # allowlist. That reads as a refusal and proves nothing — and because the gate
                # never ran, the token was never consumed and poisoned the next case.
                target = d / rel
                body = (target.read_text() + "\n# SCC-183 test edit\n") if target.exists() else "x\n"
                sha = commit_file(d, rel, body=body, msg=f"SCC-183 docs: {rel}")

                rc_m, _ = mint_direct(d, mint)
                c.check(f"REFUSE · {rel} ({why}) — minter", rc_m != 0 and not token_path(d).exists(),
                        "layer 1: the mint refuses before the approval is spent")

                direct_token(d, sha)          # layer 2: the gate, with the minter bypassed
                rc, out = sh("git", "push", "origin", "main", cwd=d)
                landed = sh("git", "--git-dir", str(bare), "rev-parse", "main", cwd=d)[1].strip()
                c.check(f"REFUSE · {rel} ({why}) — gate", rc != 0 and landed == base
                        and "prose" in out,
                        f"an unlisted path must be refused BY THE GATE, naming the allowlist "
                        f"as the reason. rc={rc}: {out.strip()[:160]}")

        with TempDir() as tmp:
            # One bad file poisons the whole commit — the allowlist is per-PATH, and a
            # reviewer-free lane cannot be trusted to notice the rider.
            d, bare, mint = direct_repo(tmp)
            base = sh("git", "--git-dir", str(bare), "rev-parse", "main", cwd=d)[1].strip()
            (d / "docs").mkdir(parents=True, exist_ok=True)
            (d / "docs/guide.md").write_text("legitimate doc edit\n")
            (d / ".agents/rules").mkdir(parents=True, exist_ok=True)
            (d / ".agents/rules/git-policy.md").write_text("rider\n")
            sh("git", "add", "docs/guide.md", ".agents/rules/git-policy.md", cwd=d)
            sh("git", "commit", "-qm", "SCC-183 docs: update the guide", cwd=d)
            mint_direct(d, mint)
            rc, out = sh("git", "push", "origin", "main", cwd=d)
            c.check("REFUSE · a mixed commit (one allowed file + one rider) is refused whole",
                    rc != 0 and sh("git", "--git-dir", str(bare), "rev-parse", "main",
                                   cwd=d)[1].strip() == base,
                    "otherwise the allowlist is bypassed by pairing the payload with a doc")

    if c.block("direct: minter refuses a disallowed path before minting"):
        with TempDir() as tmp:
            d, bare, mint = direct_repo(tmp)
            commit_file(d, ".agents/rules/git-policy.md", msg="SCC-183 docs: rule")
            rc, out = mint_direct(d, mint)
            c.check("minter REFUSES a disallowed path before spending the approval",
                    rc != 0 and not token_path(d).exists(),
                    "the gate is authoritative, but failing at MINT is what stops an honest "
                    "mistake from burning the operator's sign-off. rc=%s" % rc)

    if c.block("direct: shape"):
        with TempDir() as tmp:
            d, bare, mint = direct_repo(tmp)
            commit_file(d, "docs/a.md", msg="SCC-183 docs: a")
            commit_file(d, "docs/b.md", msg="SCC-183 docs: b")
            rc, out = mint_direct(d, mint)
            c.check("minter REFUSES --direct when 2 commits ahead", rc != 0,
                    "one sign-off authorises ONE commit")

            # The gate must hold the same line on its own — the minter is not its guard.
            sha = sh("git", "rev-parse", "HEAD", cwd=d)[1].strip()
            direct_token(d, sha)
            rc, out = sh("git", "push", "origin", "main", cwd=d)
            c.check("gate REFUSES a 2-ahead direct push even with a forged token", rc != 0,
                    "defence in depth: a hand-written token skips the minter entirely")

        with TempDir() as tmp:
            d, bare, mint = direct_repo(tmp)
            sh("git", "checkout", "-q", "-b", "side", cwd=d)
            commit_file(d, "docs/side.md", msg="SCC-183 docs: side")
            sh("git", "checkout", "-q", "main", cwd=d)
            sh("git", "merge", "-q", "--no-ff", "side", "-m", "SCC-183 merge: side", cwd=d)
            sha = sh("git", "rev-parse", "HEAD", cwd=d)[1].strip()
            direct_token(d, sha)
            rc, out = sh("git", "push", "origin", "main", cwd=d)
            c.check("gate REFUSES a MERGE commit carrying a direct token", rc != 0,
                    "direct mode authorises one plain commit; a merge goes through the "
                    "merge path, which checks the branch the token names")

    if c.block("direct: fail-closed"):
        # Every degenerate input must REFUSE. `tests-must-gate-for-real` Rule 1: a check
        # whose empty or missing input reads as a pass is not a check.
        with TempDir() as tmp:
            d, bare, mint = direct_repo(tmp)
            sha = commit_file(d, "docs/guide.md", msg="SCC-183 docs: guide")
            direct_token(d, sha)
            (d / ".agents/scripts/git-hooks/direct-push-allowlist.sh").unlink(missing_ok=True)
            rc, out = sh("git", "push", "origin", "main", cwd=d)
            c.check("gate REFUSES when the allowlist predicate is missing",
                    rc != 0 and "allowlist is missing" in out,
                    "a deleted predicate must refuse, never skip. The dispatcher's own "
                    "'not present -> push allowed, UNCHECKED' is NOT the pattern here. "
                    "Pinned to the REASON: the sweep showed a later check silently covering "
                    f"for this one, which leaves it unproven. got: {out.strip()[:160]}")

        with TempDir() as tmp:
            d, bare, mint = direct_repo(tmp, publish=False)   # remote has no main
            sha = commit_file(d, "docs/guide.md", msg="SCC-183 docs: guide")
            direct_token(d, sha)
            rc, out = sh("git", "push", "origin", "main", cwd=d)
            c.check("gate REFUSES a direct push that CREATES main (all-zero remote sha)",
                    rc != 0 and "CREATE main" in out,
                    "the merge invariants are skipped for a zero remote sha on purpose; "
                    "inheriting that for direct mode skips key, allowlist and shape at once. "
                    "Pinned to the REASON — with the check inverted, the one-commit test "
                    f"refused it anyway and the sweep recorded a survivor. got: {out.strip()[:160]}")

        with TempDir() as tmp:
            d, bare, mint = direct_repo(tmp)
            sh("git", "commit", "-q", "--allow-empty", "-m", "SCC-183 docs: nothing", cwd=d)
            sha = sh("git", "rev-parse", "HEAD", cwd=d)[1].strip()
            direct_token(d, sha)
            rc, out = sh("git", "push", "origin", "main", cwd=d)
            c.check("gate REFUSES a direct push whose changed set is EMPTY", rc != 0,
                    "an empty set satisfies 'every path is allowed' vacuously")

    if c.block("direct: refuses a symlink at an allowed path"):
        with TempDir() as tmp:
            d, bare, mint = direct_repo(tmp)
            base = sh("git", "--git-dir", str(bare), "rev-parse", "main", cwd=d)[1].strip()
            (d / "docs").mkdir(parents=True, exist_ok=True)
            (d / "docs/evil").symlink_to("../.agents/scripts/git-hooks/pre-push-main-approval.sh")
            sh("git", "add", "docs/evil", cwd=d)
            sh("git", "commit", "-qm", "SCC-183 docs: add a link", cwd=d)
            sha = sh("git", "rev-parse", "HEAD", cwd=d)[1].strip()
            rc_m, _ = mint_direct(d, mint)
            c.check("minter REFUSES a symlink too", rc_m != 0,
                    "layer 1 — but the gate is the authority, so it is proven separately below")
            # Forged token on purpose: going through the minter would leave the GATE's own
            # mode check unproven, which is precisely what the mutation sweep caught.
            direct_token(d, sha)
            rc, out = sh("git", "push", "origin", "main", cwd=d)
            c.check("gate REFUSES a symlink even at an allowed path",
                    rc != 0 and sh("git", "--git-dir", str(bare), "rev-parse", "main",
                                   cwd=d)[1].strip() == base,
                    "the path reads as docs/, so the allowlist alone would pass it. This "
                    "lane has no reviewer, so the mode check has to be mechanical")

    return c.finish()


if __name__ == "__main__":
    raise SystemExit(main())

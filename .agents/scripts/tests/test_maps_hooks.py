"""test_maps_hooks.py - the three maps hook delegates, driven by REAL git. (SCC-288 / R3)

WHY THIS FILE EXISTS. SCC-290 shipped 146 lines of shell in three delegates --
`pre-commit-maps.sh`, `commit-msg-maps.sh`, `pre-push-maps-verify.sh` -- and every one of them was
pinned only by source greps over the dispatcher text. The close-out review proved what that buys:
four mutants survived a full green suite.

    S1  `.githooks/pre-commit` never invokes the maps delegate ......... 58/58 files passed
    S2  `pre-commit-maps.sh` exits 0 instead of regenerating ........... 58/58 files passed
    S3  the push remedy says `--staged` again (the unusable one) ....... 58/58 files passed
    S4  `commit-msg-maps.sh` loses its MERGE_HEAD carve-out ............ 58/58 files passed

That is the source-grep blindness this house already records, sitting on the gates themselves. So
every case below drives a REAL `git commit`, `git merge` or `git push` through a real
`core.hooksPath`, and asserts on what git actually did -- never on what a file says.

⭐ THE ALLOW HALF IS LOAD-BEARING, same rule as `test_git_hooks.py`. A maps hook that regenerates on
every commit gets disabled inside a week, and a push gate that refuses a clean tree strands the
operator. MH-2 and MH-4 are negative controls and they carry the same weight as the refusals.

Stdlib only, no pytest.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _harness import Cases, TempDir  # noqa: E402

REPO = Path(__file__).resolve().parents[3]
SCRIPTS = REPO / ".agents" / "scripts"
HOOKDIR = SCRIPTS / "git-hooks"

# The modules `refresh_maps.py` actually reaches, resolved once. A fixture that copies the whole
# scripts folder would drag 4.9 MB per case; a fixture that copies too few dies in SETUP, which
# reads exactly like a failed assertion (the "red test dies before its assertion" shape).
MODULES = ("refresh_maps.py", "check_maps.py", "generate_repo_map.py",
           "generate_doc_graph.py", "record_map_changes.py")

GIT_ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")

SOP_TEXT = (
    "# Workflows + testing SOP\n\n"
    "## The doors\n\n"
    "- `/cicd-code-review` - review a story.\n"
    "- `/smh-quick-dev` - the task lane's dev cycle.\n"
)

REPO_MAP_SCAFFOLD = (
    "# Repo map\n\n"
    "<!-- CURATED -->\n\n"
    "<!-- REPO-MAP:AUTO-START -->\nstale placeholder\n<!-- REPO-MAP:AUTO-END -->\n"
)


def git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(root), env=GIT_ENV,
                          capture_output=True, text=True, errors="replace")


def out(r: subprocess.CompletedProcess) -> str:
    return (r.stdout or "") + (r.stderr or "")


def write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def seed(tmp: Path, *, dispatchers=("pre-commit",), delegates=("pre-commit-maps.sh",)) -> Path:
    """A real repo carrying the REAL dispatcher and the REAL delegate, armed the way git arms them.

    ⛔ The dispatchers are copied whole, not stubbed. `.githooks/pre-commit` chains two delegates in
    a load-bearing ORDER and `.githooks/commit-msg` chains four; a fixture that hand-writes a
    one-line hook proves the delegate runs when something calls it, which is the one thing S1 shows
    nobody had checked. Delegates NOT listed are simply absent, and every dispatcher here treats an
    absent delegate as "say so, allow" (SCC-32) -- so a case can arm exactly one gate.
    """
    root = tmp / "wk"
    root.mkdir(parents=True)
    git(root, "init", "-q", "-b", "main")

    (root / ".agents" / "scripts").mkdir(parents=True)
    for m in MODULES:
        shutil.copy2(SCRIPTS / m, root / ".agents" / "scripts" / m)
    (root / ".agents" / "scripts" / "git-hooks").mkdir(parents=True)
    for d in delegates:
        shutil.copy2(HOOKDIR / d, root / ".agents" / "scripts" / "git-hooks" / d)
        (root / ".agents" / "scripts" / "git-hooks" / d).chmod(0o755)
    (root / ".githooks").mkdir()
    for h in dispatchers:
        shutil.copy2(REPO / ".githooks" / h, root / ".githooks" / h)
        (root / ".githooks" / h).chmod(0o755)

    write(root / "AGENTS.md", "# workspace\n")
    write(root / ".agents" / "commands" / "cicd-code-review.md", "# review\n")
    write(root / ".agents" / "commands" / "smh-quick-dev.md", "# dev\n")
    write(root / ".agents" / "rules" / "a.md", "# a\n\nSee [x](../../docs/x.md).\n")
    write(root / "docs" / "x.md", "# x\n")
    write(root / "docs" / "repo-map.md", REPO_MAP_SCAFFOLD)
    write(root / "docs" / "_scc_sops_prds" / "workflows_testing_SOP.md", SOP_TEXT)
    write(root / "_artifacts" / "note.md", "# note\n")
    git(root, "add", "-A")
    git(root, "commit", "-qm", "seed")

    # The baseline maps, built by the script itself so the fixture converges in ONE pass - the
    # same reason `test_refresh_maps.seed_repo` does it this way rather than calling the two
    # generators side by side.
    subprocess.run([sys.executable, ".agents/scripts/refresh_maps.py", "--repair"],
                   cwd=str(root), env=GIT_ENV, capture_output=True, text=True)
    git(root, "commit", "-qm", "maps")
    v = subprocess.run([sys.executable, ".agents/scripts/refresh_maps.py", "--verify"],
                       cwd=str(root), env=GIT_ENV, capture_output=True, text=True)
    assert v.returncode == 0, f"fixture did not converge: {out(v)}"

    git(root, "config", "core.hooksPath", ".githooks")   # LAST: the seed itself is ungated
    return root


def committed(root: Path) -> list[str]:
    return [p for p in git(root, "show", "--pretty=", "--name-only", "HEAD").stdout.splitlines()
            if p.strip()]


def main() -> int:
    c = Cases("maps hooks (executable)")

    # ── MH-1 · REFRESH: a real `git commit` regenerates the maps and CARRIES them ─────────────
    # Kills S1 (the dispatcher never calls the delegate) and S2 (the delegate exits 0). Neither
    # mutant changes any source string a grep guard reads, and both leave the maps stale in a
    # commit that looks complete.
    if c.block("MH-1 · SCC-290 · a real commit through .githooks/pre-commit stages the maps"):
        with TempDir() as tmp:
            root = seed(tmp)
            write(root / ".agents" / "rules" / "b.md", "# b\n\nSee [x](../../docs/x.md).\n")
            git(root, "add", "--", ".agents/rules/b.md")
            r = git(root, "commit", "-m", "SCC-290 add a rule")
            files = committed(root)
            c.check("MH-1 the commit succeeded", r.returncode == 0, out(r))
            c.check("MH-1 the doc graph rode along in the SAME commit",
                    "docs/doc-graph.json" in files and "docs/doc-graph.md" in files,
                    f"committed: {files}")
            c.check("MH-1 and the graph now knows the new file",
                    "b.md" in (root / "docs" / "doc-graph.json").read_text(encoding="utf-8"),
                    "the delegate ran but regenerated nothing")
            v = subprocess.run([sys.executable, ".agents/scripts/refresh_maps.py", "--verify"],
                               cwd=str(root), env=GIT_ENV, capture_output=True, text=True)
            c.check("MH-1 the tree it left behind is NOT stale", v.returncode == 0, out(v))

    # ── MH-2 · ALLOW: an _artifacts-only commit is untouched ──────────────────────────────────
    # The negative control. The common commit in this repo cannot affect a map, and a hook that
    # rewrites two files anyway is one the operator disables.
    if c.block("MH-2 · SCC-290 · an _artifacts-only commit carries ONLY the artifact"):
        with TempDir() as tmp:
            root = seed(tmp)
            write(root / "_artifacts" / "note.md", "# note, edited\n")
            git(root, "add", "--", "_artifacts/note.md")
            r = git(root, "commit", "-m", "SCC-290 artifacts only")
            c.check("MH-2 the commit succeeded", r.returncode == 0, out(r))
            c.check("MH-2 no map was dragged in", committed(root) == ["_artifacts/note.md"],
                    str(committed(root)))

    # ── MH-3 · REFUSE: a real `git push` on a stale tree, and the remedy must WORK ────────────
    # Kills S3. `--staged` is trigger-gated on the staged set, so on the three trees `--verify`
    # exists to catch -- a merge, a `--no-verify` commit, an unarmed clone -- it exits 0 and
    # writes nothing. A gate whose printed remedy is a no-op leaves `--no-verify` as the only way
    # past, and this case runs the remedy it prints rather than trusting the string.
    if c.block("MH-3 · SCC-290 · a stale tree is REFUSED at push, and the printed remedy fixes it"):
        with TempDir() as tmp:
            root = seed(tmp, dispatchers=("pre-push",), delegates=("pre-push-maps-verify.sh",))
            bare = tmp / "remote.git"
            git(root, "init", "-q", "--bare", str(bare))
            git(root, "remote", "add", "origin", str(bare))
            git(root, "checkout", "-qb", "lane")
            write(root / "docs" / "y.md", "# y\n")
            git(root, "add", "--", "docs/y.md")
            git(root, "commit", "-qm", "SCC-290 slip past the hook", "--no-verify")

            r = git(root, "push", "-q", "origin", "lane")
            text = out(r)
            c.check("MH-3 the push is REFUSED", r.returncode != 0, text or "(silent success)")
            c.check("MH-3 the remedy it prints is --repair", "--repair" in text, text[-400:])
            c.check("MH-3 and it does NOT print the no-op --staged", "--staged" not in text,
                    text[-400:])

            fix = subprocess.run([sys.executable, ".agents/scripts/refresh_maps.py", "--repair"],
                                 cwd=str(root), env=GIT_ENV, capture_output=True, text=True)
            c.check("MH-3 the remedy WROTE something (a no-op remedy is the defect)",
                    "regenerated and staged" in out(fix), out(fix) or "(silent)")
            git(root, "commit", "-qm", "SCC-290 repair the maps", "--no-verify")
            again = git(root, "push", "-q", "origin", "lane")
            c.check("MH-3 and the push now goes through", again.returncode == 0, out(again))

    # ── MH-4 · ALLOW: a clean tree pushes without a word ──────────────────────────────────────
    if c.block("MH-4 · SCC-290 · a push from a CURRENT tree is allowed"):
        with TempDir() as tmp:
            root = seed(tmp, dispatchers=("pre-push",), delegates=("pre-push-maps-verify.sh",))
            bare = tmp / "remote.git"
            git(root, "init", "-q", "--bare", str(bare))
            git(root, "remote", "add", "origin", str(bare))
            git(root, "checkout", "-qb", "lane")
            r = git(root, "push", "-q", "origin", "lane")
            c.check("MH-4 exit 0", r.returncode == 0, out(r))
            c.check("MH-4 and it said nothing about stale maps",
                    "STALE" not in out(r), out(r)[-300:])

    # ── MH-5 · the MERGE carve-out, both halves ───────────────────────────────────────────────
    # Kills S4. The truth checks judge CONTENT an author is answerable for; git writes a merge
    # message and a merge has no author to answer for the two sides' combined broken references.
    # Without the carve-out the ratchet blocks the merge outright and there is no message to put
    # `[maps-ok]` in -- but a carve-out that swallowed the ordinary commit too would disarm the
    # gate entirely, so both halves are asserted from the same fixture.
    if c.block("MH-5 · SCC-290 · the ratchet refuses a COMMIT and lets a MERGE through"):
        with TempDir() as tmp:
            root = seed(tmp, dispatchers=("commit-msg",), delegates=("commit-msg-maps.sh",))
            bad = "# bad\n\n[gone](../../docs/does/not/exist.md)\n"

            git(root, "checkout", "-qb", "side")
            write(root / ".agents" / "rules" / "bad.md", bad)
            git(root, "add", "--", ".agents/rules/bad.md")
            git(root, "commit", "-qm", "SCC-290 a new broken ref", "--no-verify")

            git(root, "checkout", "-q", "main")
            direct = git(root, "commit", "--allow-empty", "-m", "SCC-290 plain commit")
            c.check("MH-5 control: an ordinary commit still passes when it breaks nothing",
                    direct.returncode == 0, out(direct))

            write(root / ".agents" / "rules" / "bad2.md", bad)
            git(root, "add", "--", ".agents/rules/bad2.md")
            refused = git(root, "commit", "-m", "SCC-290 add a broken ref directly")
            c.check("MH-5 an ordinary commit that ADDS a broken ref is REFUSED",
                    refused.returncode != 0, out(refused) or "(it was allowed)")
            c.check("MH-5 and it names the ratchet", "broken doc references went" in out(refused),
                    out(refused)[-400:])
            git(root, "reset", "-q", "HEAD", "--", ".agents/rules/bad2.md")
            (root / ".agents" / "rules" / "bad2.md").unlink()

            merged = git(root, "merge", "--no-ff", "-m", "Merge branch 'side'", "side")
            c.check("MH-5 the MERGE of that same content is ALLOWED",
                    merged.returncode == 0, out(merged) or "(the merge was refused)")
            c.check("MH-5 and it really was a merge commit",
                    len(git(root, "rev-list", "--parents", "-n", "1",
                            "HEAD").stdout.split()) == 3,
                    git(root, "rev-list", "--parents", "-n", "1", "HEAD").stdout.strip())

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())

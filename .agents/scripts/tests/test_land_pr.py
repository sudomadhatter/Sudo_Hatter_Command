"""SCC-183 — `land_pr.py`, the PR door.

⛔ The one case that matters is `prose/enumerated`. Three cuts of this lane's plan shipped a
`_is_prose` rule that was wrong in the same way each time — written from what the author had in
mind rather than from what `git ls-files` returns — and each miss admitted a file that tells every
agent on both machines where to go. So the refusal table below is **derived from the real repo**,
not hand-written: it walks every tracked path, and asserts on the SHAPE of what survives. A
hand-written row list cannot catch the file nobody remembered.

Stdlib only, no pytest, matching every other file here.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from _harness import Cases, TempDir

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

import land_pr  # noqa: E402 — sys.path set above, as every test here does
import main_write_gate  # noqa: E402


REPO_ROOT = SCRIPTS.parents[1]


def git(repo: Path, *args: str) -> tuple[int, str]:
    r = subprocess.run(["git", "-C", str(repo), *args],
                       capture_output=True, text=True, errors="replace")
    return r.returncode, (r.stdout or "").strip()


def scratch(d: Path, branch: str = "chore/SCC-999-scratch") -> Path:
    """A repo shaped enough for the checks: a jira.conf, a commands master, an origin."""
    repo = d / "repo"
    (repo / ".agents/commands").mkdir(parents=True)
    (repo / ".agents/commands/x.md").write_text("# x\n", encoding="utf-8")
    (repo / ".agents/jira.conf").write_text('JIRA_KEYS="SCC"\n', encoding="utf-8")
    (repo / "docs").mkdir()
    (repo / "docs/seed.md").write_text("seed\n", encoding="utf-8")
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@t.t")
    git(repo, "config", "user.name", "t")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "SCC-999 seed")

    bare = d / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True)
    git(repo, "remote", "add", "origin", str(bare))
    git(repo, "push", "-q", "origin", "main")
    git(repo, "checkout", "-q", "-b", branch)
    return repo


def commit(repo: Path, rel: str, body: str = "x\n") -> None:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", f"SCC-999 touch {rel}")


class Gh:
    """The injected `gh` seam. Records argv; answers from a prefix table. No network, ever."""

    def __init__(self, table: dict | None = None, available: bool = True) -> None:
        self.calls: list[list[str]] = []
        self.table = table or {}
        self.available = available

    def __call__(self, *args: str) -> tuple[int, str]:
        self.calls.append(list(args))
        if not self.available:
            return 127, "gh: command not found"
        for prefix, resp in self.table.items():
            if list(args[:len(prefix)]) == list(prefix):
                return resp
        return 0, ""

    def argv(self) -> list[str]:
        return [" ".join(c) for c in self.calls]

    def wrote(self) -> list[str]:
        """Every call that is not a read — the assertion `--dry-run` must survive."""
        writes = ("create", "merge", "edit", "close", "reopen", "comment")
        return [" ".join(c) for c in self.calls
                if any(w in c for w in writes)]


def pr_json(number: int, state: str, url: str = "", oid: str = "",
            merge_sha: str = "") -> tuple[int, str]:
    return 0, json.dumps([{
        "number": number,
        "state": state,
        "url": url or f"https://github.com/x/y/pull/{number}",
        "headRefOid": oid,
        "mergeCommit": {"oid": merge_sha} if merge_sha else None,
    }])


def main() -> int:  # noqa: C901 — a table-driven suite, flat on purpose
    c = Cases("land_pr")

    # ------------------------------------------------------------------ AC-4
    if c.block("A · ⛔ prose/enumerated — the predicate against the REAL repo"):
        rc, out = git(REPO_ROOT, "ls-files")
        tracked = [p for p in out.splitlines() if p.strip()]
        c.check("prose/enumerated/repo-readable", rc == 0 and len(tracked) > 1000,
                f"{len(tracked)} tracked files")

        allowed = [p for p in tracked if land_pr.is_prose(p)]

        # The three shape assertions. Each is a defect this lane actually shipped.
        root = [p for p in allowed if "/" not in p]
        c.check("prose/no-root-file-is-prose", not root, f"root allowed: {root}")

        doors = [p for p in allowed
                 if p.rsplit("/", 1)[-1] in ("AGENTS.md", "CLAUDE.md", "GEMINI.md")]
        c.check("prose/no-front-door-is-prose", not doors, f"front doors allowed: {doors}")

        nonmd = [p for p in allowed if not p.endswith(".md")]
        c.check("prose/only-markdown", not nonmd, f"non-.md allowed: {nonmd}")

        mig = [p for p in allowed if p.startswith("docs/migrations/")]
        c.check("prose/no-migration-guide", not mig, f"migrations allowed: {mig}")

        outside = [p for p in allowed
                   if not p.startswith(("docs/", "_artifacts/", "_my_resources/"))]
        c.check("prose/only-the-three-roots", not outside, f"outside: {outside}")

        # ...and it must not be vacuous: the legitimate outputs still land.
        for good in ("docs/repo-map.md", "_artifacts/_memory/MEMORY.md",
                     "_artifacts/_main/INDEX.md"):
            c.check(f"prose/allows/{good}", land_pr.is_prose(good))

        # The named mutants (plan § mutation table). Each must be refused.
        for bad in ("router.md", "_artifacts/CLAUDE.md", "docs/AGENTS.md",
                    "_my_resources/GEMINI.md", "docs/.maps-state.json",
                    "docs/migrations/install_guides/machine_setup_card.md",
                    ".claude/hooks/require-push-approval.py", ".claude/settings.json",
                    ".agents/rules/git-policy.md", ".opencode/commands/x.md",
                    "opencode.json", "requirements.txt", "tests/x.md", ""):
            c.check(f"prose/refuses/{bad or '<empty>'}", not land_pr.is_prose(bad))

    # ------------------------------------------------------------------ AC-4b
    if c.block("B · precedence — refusals are evaluated FIRST"):
        # `docs/CLAUDE.md` matches an allow arm AND a refusal. The refusal must win.
        c.check("precedence/refusal-wins", not land_pr.is_prose("docs/CLAUDE.md"))
        c.check("precedence/deep-front-door",
                not land_pr.is_prose("_artifacts/_main/2026-01-01_x/AGENTS.md"))

    # ------------------------------------------------------------------ AC-4, both halves
    if c.block("C · merge_eligible — EITHER half alone must refuse the hook"):
        with TempDir() as d:
            repo = scratch(d)
            hook = [("100644", ".claude/hooks/require-push-approval.py")]
            ok, why = land_pr.merge_eligible(repo, hook)
            c.check("eligible/refuses-the-permission-hook", not ok, why)

            # lane_qualify alone rates it LIGHT — that was audit F1's measurement, and it is
            # why the second predicate exists. Pin it, so a future widening of lane_qualify
            # cannot silently become this door's behaviour.
            import lane_qualify
            v, _ = lane_qualify.classify(repo, [".claude/hooks/require-push-approval.py"], False)
            c.check("eligible/lane_qualify-alone-says-LIGHT", v == "LIGHT",
                    f"lane_qualify={v} — is_prose is the half that refuses it")

            ok, why = land_pr.merge_eligible(repo, [("100644", ".agents/rules/git-policy.md")])
            c.check("eligible/refuses-toolkit-prose", not ok, why)
            # ⛔ And it must be lane_qualify's half that refuses it, naming it as TOOLKIT. The
            # first cut normalised with `lstrip("./")`, which eats the leading dot, so
            # lane_qualify saw `agents/rules/…`, rated it LIGHT, and only is_prose still
            # refused — one of the two halves silently switched off while the suite stayed
            # green. `lane_qualify.norm`'s own docstring warns about this; it has now been got
            # wrong three times in this repo.
            c.check("eligible/toolkit-refused-BY-lane_qualify", "toolkit" in why.lower(), why)
            c.check("norm/keeps-the-leading-dot",
                    land_pr.norm(".agents/x.md") == ".agents/x.md"
                    and land_pr.norm(".claude/y.json") == ".claude/y.json",
                    land_pr.norm(".agents/x.md"))

            ok, why = land_pr.merge_eligible(repo, [("100644", "_artifacts/_memory/x.md"),
                                                    ("100644", "docs/notes.md")])
            c.check("eligible/allows-prose-only", ok, why)

            ok, why = land_pr.merge_eligible(repo, [])
            c.check("eligible/refuses-the-empty-set", not ok, why)

            ok, why = land_pr.merge_eligible(repo, [("160000", "Projects/AGY")])
            c.check("eligible/refuses-a-gitlink", not ok, why)

            ok, why = land_pr.merge_eligible(repo, [("120000", "docs/link.md")])
            c.check("eligible/refuses-a-symlink", not ok, why)

    # ------------------------------------------------------------------ N13
    if c.block("D · R2 uses the REAL gate pattern, never a re-typed copy"):
        keys = main_write_gate.read_jira_keys(REPO_ROOT)
        pat = main_write_gate.branch_pattern(keys)
        for name in ("chore/SCC-183-x", "epic/SCC-1-y"):
            c.check(f"branch/agrees/{name}",
                    bool(pat.match(name)) and land_pr.branch_ok(name, keys)[0])
        for name in ("claude/story-x", "chore/SCC-183", "main", "chore/AVCH-1-x"):
            c.check(f"branch/refuses/{name}",
                    not pat.match(name) and not land_pr.branch_ok(name, keys)[0])

    # ------------------------------------------------------------------ AC-5
    if c.block("E · check P — one row per PR state"):
        with TempDir() as d:
            repo = scratch(d)
            commit(repo, "docs/a.md")
            git(repo, "push", "-q", "-u", "origin", "HEAD")
            head = git(repo, "rev-parse", "HEAD")[1]

            # none → falls through and creates
            gh = Gh({("pr", "list"): (0, "[]")})
            rc, lines = land_pr.run(repo, merge=False, dry_run=True, gh=gh)
            c.check("P/none/creates", any("pr create" in a for a in gh.argv()),
                    "; ".join(gh.argv()))

            # OPEN, no --merge → URL, exit 0, no second PR
            gh = Gh({("pr", "list"): pr_json(11, "OPEN")})
            rc, lines = land_pr.run(repo, merge=False, dry_run=True, gh=gh)
            c.check("P/open/no-second-pr", rc == 0
                    and not any("pr create" in a for a in gh.argv()), f"rc={rc}")
            c.check("P/open/url-is-last-line", lines[-1].endswith("/pull/11"), lines[-1])

            # ⛔ OPEN + --merge → must FALL THROUGH, not exit 0
            gh = Gh({("pr", "list"): pr_json(11, "OPEN", oid=head)})
            rc, lines = land_pr.run(repo, merge=True, dry_run=True, gh=gh)
            c.check("P/open+merge/falls-through-to-merge",
                    any("pr merge" in a for a in gh.argv()), "; ".join(gh.argv()))

            # ⛔ CLOSED unmerged → refuse BY NAME, never exit 0
            gh = Gh({("pr", "list"): pr_json(7, "CLOSED")})
            rc, lines = land_pr.run(repo, merge=False, dry_run=True, gh=gh)
            blob = "\n".join(lines)
            c.check("P/closed/refuses-by-name", rc != 0 and "closed" in blob.lower()
                    and "7" in blob, f"rc={rc}: {blob[-160:]}")
            c.check("P/closed/opens-no-pr", not any("pr create" in a for a in gh.argv()))

            # MERGED and HEAD is that merge's ancestor → landed, exit 0
            gh = Gh({("pr", "list"): pr_json(9, "MERGED", oid=head, merge_sha=head)})
            rc, lines = land_pr.run(repo, merge=False, dry_run=True, gh=gh)
            c.check("P/merged/reports-landed", rc == 0 and "landed" in "\n".join(lines).lower(),
                    f"rc={rc}")

            # MERGED but new commits since → a NEW PR
            gh = Gh({("pr", "list"): pr_json(9, "MERGED", oid=head, merge_sha=head)})
            commit(repo, "docs/b.md")
            git(repo, "push", "-q", "origin", "HEAD")
            rc, lines = land_pr.run(repo, merge=False, dry_run=True, gh=gh)
            c.check("P/merged+new-commits/opens-a-new-pr",
                    any("pr create" in a for a in gh.argv()), "; ".join(gh.argv()))

    # ------------------------------------------------------------------ AC-2, AC-3
    if c.block("F · R1–R8 each refuse BY NAME"):
        with TempDir() as d:
            rc, lines = land_pr.run(d, merge=False, dry_run=True, gh=Gh())
            c.check("R1/not-a-repo", rc != 0 and "repo" in "\n".join(lines).lower())

        with TempDir() as d:
            repo = scratch(d, branch="claude/story-lane")
            rc, lines = land_pr.run(repo, merge=False, dry_run=True, gh=Gh())
            c.check("R2/bad-branch", rc != 0 and "branch" in "\n".join(lines).lower())

        with TempDir() as d:
            repo = scratch(d, branch="chore/AVCH-1-wrong-project")
            rc, lines = land_pr.run(repo, merge=False, dry_run=True, gh=Gh())
            c.check("R3/wrong-key", rc != 0 and "AVCH" in "\n".join(lines))

        with TempDir() as d:
            repo = scratch(d)
            commit(repo, "docs/a.md")
            (repo / "docs/dirty.md").write_text("dirty\n", encoding="utf-8")
            rc, lines = land_pr.run(repo, merge=False, dry_run=True, gh=Gh())
            c.check("R4/dirty-tree", rc != 0 and "dirty" in "\n".join(lines).lower())

        with TempDir() as d:
            repo = scratch(d)
            gh = Gh({("pr", "list"): (0, "[]")})
            rc, lines = land_pr.run(repo, merge=False, dry_run=True, gh=gh)
            c.check("R5/nothing-to-land", rc != 0
                    and "nothing to land" in "\n".join(lines).lower(), f"rc={rc}")

        with TempDir() as d:
            repo = scratch(d)
            commit(repo, "docs/a.md")
            git(repo, "push", "-q", "-u", "origin", "HEAD")
            git(repo, "reset", "-q", "--hard", "HEAD~1")
            commit(repo, "docs/c.md")
            gh = Gh({("pr", "list"): (0, "[]")})
            rc, lines = land_pr.run(repo, merge=False, dry_run=True, gh=gh)
            c.check("R6/diverged", rc != 0 and "diverg" in "\n".join(lines).lower(), f"rc={rc}")

        with TempDir() as d:
            repo = scratch(d)
            commit(repo, "docs/a.md")
            rc, lines = land_pr.run(repo, merge=False, dry_run=False, gh=Gh(available=False))
            blob = "\n".join(lines).lower()
            c.check("R7/gh-missing-names-the-fix", rc != 0 and "gh" in blob
                    and ("install" in blob or "auth" in blob), blob[-160:])

        with TempDir() as d:
            repo = scratch(d)
            commit(repo, ".claude/settings.json", "{}\n")
            git(repo, "push", "-q", "-u", "origin", "HEAD")
            gh = Gh({("pr", "list"): (0, "[]")})
            rc, lines = land_pr.run(repo, merge=True, dry_run=True, gh=gh)
            c.check("R8/ineligible-hands-back-not-merges",
                    not any("pr merge" in a for a in gh.argv()), "; ".join(gh.argv()))

    # ------------------------------------------------------------------ AC-7
    if c.block("G · the merge is a MERGE COMMIT — never squash, never rebase"):
        with TempDir() as d:
            repo = scratch(d)
            commit(repo, "docs/a.md")
            git(repo, "push", "-q", "-u", "origin", "HEAD")
            head = git(repo, "rev-parse", "HEAD")[1]
            gh = Gh({("pr", "list"): pr_json(12, "OPEN", oid=head),
                     ("pr", "view"): (0, json.dumps({"mergedAt": None}))})
            land_pr.run(repo, merge=True, dry_run=True, gh=gh)
            merges = [a for a in gh.argv() if "pr merge" in a]
            c.check("merge/uses---merge", merges and all("--merge" in m for m in merges),
                    "; ".join(merges))
            c.check("merge/never---squash", not any("--squash" in m for m in gh.argv()))
            c.check("merge/never---rebase", not any("--rebase" in m for m in gh.argv()))

    # ------------------------------------------------------------------ AC-8 / N3
    if c.block("H · the ancestry refusal fires on BOTH paths"):
        with TempDir() as d:
            repo = scratch(d)
            commit(repo, "docs/a.md")
            git(repo, "push", "-q", "-u", "origin", "HEAD")
            # origin/main moves on underneath us
            other = d / "other"
            subprocess.run(["git", "clone", "-q", str(d / "origin.git"), str(other)], check=True)
            git(other, "config", "user.email", "t@t.t")
            git(other, "config", "user.name", "t")
            commit(other, "docs/sibling.md")
            git(other, "push", "-q", "origin", "main")
            git(repo, "fetch", "-q", "origin")

            gh = Gh({("pr", "list"): (0, "[]")})
            rc, lines = land_pr.run(repo, merge=False, dry_run=True, gh=gh)
            blob = "\n".join(lines).lower()
            c.check("ancestry/refuses-at-CREATE-time", rc != 0 and "stale" in blob,
                    f"rc={rc}: {blob[-200:]}")
            c.check("ancestry/opens-no-stale-pr", not any("pr create" in a for a in gh.argv()))

            head = git(repo, "rev-parse", "HEAD")[1]
            gh = Gh({("pr", "list"): pr_json(13, "OPEN", oid=head)})
            rc, lines = land_pr.run(repo, merge=True, dry_run=True, gh=gh)
            c.check("ancestry/refuses-before-MERGE",
                    rc != 0 and not any("pr merge" in a for a in gh.argv()), f"rc={rc}")

    # ------------------------------------------------------------------ AC-6, F7, N14
    if c.block("I · --dry-run writes NOTHING; and it degrades offline"):
        with TempDir() as d:
            repo = scratch(d)
            commit(repo, "docs/a.md")
            git(repo, "push", "-q", "-u", "origin", "HEAD")
            gh = Gh({("pr", "list"): (0, "[]")})
            before = git(repo, "rev-parse", "origin/main")[1]
            rc, lines = land_pr.run(repo, merge=True, dry_run=True, gh=gh)
            # ⛔ NOT `check(..., True)`. The recorder cannot prove the REAL seam is safe, so
            # assert on the real seam: GhCli(dry_run=True) must refuse to execute a write, and
            # must still be able to read. A tautology here would be a guard that cannot fail.
            c.check("dry-run/is_write-knows-a-merge", land_pr.is_write(("pr", "merge", "5")))
            c.check("dry-run/is_write-knows-a-create", land_pr.is_write(("pr", "create")))
            c.check("dry-run/is_write-lets-reads-through",
                    not land_pr.is_write(("pr", "list")) and not land_pr.is_write(("pr", "view"))
                    and not land_pr.is_write(("auth", "status")))
            rcw, outw = land_pr.GhCli(dry_run=True)("pr", "merge", "999999", "--merge")
            c.check("dry-run/real-seam-refuses-the-write",
                    rcw == 0 and "dry-run" in outw.lower(), f"rc={rcw} {outw!r}")
            c.check("dry-run/origin-main-unmoved",
                    git(repo, "rev-parse", "origin/main")[1] == before)
            c.check("dry-run/prints-the-argv",
                    any("pr create" in ln for ln in lines), lines[-1] if lines else "")

            # N14: offline, --dry-run still previews rather than dying at R7
            rc, lines = land_pr.run(repo, merge=False, dry_run=True, gh=Gh(available=False))
            c.check("dry-run/degrades-offline", rc == 0, f"rc={rc}: {lines[-1] if lines else ''}")

    return c.finish()


if __name__ == "__main__":
    raise SystemExit(main())

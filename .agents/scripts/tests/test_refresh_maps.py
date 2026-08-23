"""refresh_maps.py - the pre-commit maps refresh and the two truth checks. (SCC-290)

WHAT IS UNDER TEST. `docs/repo-map.md`'s AUTO block and `docs/doc-graph.*` are machine-generated
and nothing regenerated them between manual ceremonies, so they were stale almost always. This
script regenerates them from a `pre-commit` hook, stages exactly what it wrote, and refuses the
commit on two truth checks. `--verify` is the same regeneration compared against disk, wired into
`pre-push` and `check_maps` check 10 to catch the commits the hook never saw (a merge, a
`--no-verify`).

⛔ HONESTY NOTE ON THE ORDER THESE WERE WRITTEN. Cases here were written against a first draft of
`refresh_maps.py`, not before it - the script and its shape were settled together. That makes them
characterization checks by construction, so they do NOT carry the usual "seen red" warrant. The
mutation sweep is what certifies them instead: every decision in the source is mutated and each
mutant must kill a NAMED case below. A green suite here is not the evidence; the sweep is.

THE GATE HALVES, both of which every case set has to hold:
  REFUSES  a commit that adds a broken doc reference; a door the SOP does not name; a write that
           did not land.
  ALLOWS   a commit touching only `_artifacts/`; a re-run with nothing to change; a vendor door.
A gate that only ever refuses is as broken as one that never does.

Stdlib only, no pytest.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _harness import Cases, TempDir  # noqa: E402

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import refresh_maps as rmod  # noqa: E402

REFRESH = SCRIPTS / "refresh_maps.py"
GIT_ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")


def git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(root), env=GIT_ENV,
                          capture_output=True, text=True)


def write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def run(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(REFRESH), *args], cwd=str(root),
                          env=GIT_ENV, capture_output=True, text=True)


def truth(root: Path, message: str = "SCC-290 a commit") -> subprocess.CompletedProcess:
    """Drive the commit-msg half the way git does: a real message FILE on argv.

    ⛔ The truth checks live in `commit-msg`, not beside the regeneration, because their escape
    hatch is a token in the MESSAGE and pre-commit cannot see one. Found by the ratchet refusing
    the very commit that introduced it: that commit widened the graph's scope, so 52 and 77 were
    not measurements of the same thing, and no count-based rule can be satisfied across that.
    """
    f = root / ".git" / "COMMIT_EDITMSG_TEST"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(message, encoding="utf-8")
    return run(root, "--truth", str(f))


REPO_MAP_SCAFFOLD = (
    "# Repo map\n\n"
    "<!-- CURATED: hand-written above. Regen:\n"
    "     mode=content, collapse-threshold=8 files. Edit the CURATED block above. -->\n\n"
    "<!-- REPO-MAP:AUTO-START -->\nstale placeholder\n<!-- REPO-MAP:AUTO-END -->\n"
)

SOP_TEXT = (
    "# Workflows + testing SOP\n\n"
    "## The doors\n\n"
    "- `/cicd-code-review` - review a story.\n"
    "- `/smh-quick-dev` - the task lane's dev cycle.\n"
)


def seed_repo(tmp: Path) -> Path:
    """A minimal but REAL workspace: a git repo with the two roots, a scaffolded repo-map, an SOP
    naming its two doors, and a committed doc-graph so the ratchet has a baseline."""
    root = tmp / "wk"
    root.mkdir(parents=True)
    git(root, "init", "-q", "-b", "main")
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

    # ⛔ THE BASELINE IS BUILT BY THE HOOK ITSELF, not by calling the generators side by side.
    # `docs/doc-graph.*` land INSIDE `docs/`, which the repo-map walks, so a baseline built from
    # one snapshot records "2 files" where the converged tree has 4 — and every case then measured
    # its own broken fixture instead of the code. That is exactly the ordering defect `run_staged`
    # fixes, so the seed exercises the fix rather than reproducing the bug.
    write(root / "docs" / "x.md", "# x\n\nSeeded.\n")   # a REAL staged change, or nothing triggers
    git(root, "add", "--", "docs/x.md")
    subprocess.run([sys.executable, str(REFRESH), "--staged"], cwd=str(root), env=GIT_ENV,
                   capture_output=True, text=True)
    git(root, "commit", "-qm", "maps")
    v = subprocess.run([sys.executable, str(REFRESH), "--verify"], cwd=str(root), env=GIT_ENV,
                       capture_output=True, text=True)
    assert v.returncode == 0, f"fixture did not converge in ONE refresh: {v.stdout}"
    return root


def staged(root: Path) -> list[str]:
    return [p for p in git(root, "diff", "--cached", "--name-only").stdout.splitlines() if p]


def main() -> int:
    c = Cases("refresh maps")

    # ── A · ALLOW: a commit the maps cannot depend on does nothing at all ─────────────────────
    # The common commit in this repo is artifacts-only. It must cost one `git diff --cached` and
    # write nothing — a hook that regenerates on every commit gets disabled within a week.
    if c.block("RM-A · SCC-290 · an _artifacts-only commit is a NO-OP"):
        with TempDir() as tmp:
            root = seed_repo(tmp)
            write(root / "_artifacts" / "note.md", "# note, edited\n")
            git(root, "add", "--", "_artifacts/note.md")
            before = {rel: (root / rel).read_bytes()
                      for rel in ("docs/repo-map.md", "docs/doc-graph.json")}
            r = run(root, "--staged")
            c.check("RM-A exit 0", r.returncode == 0, f"rc={r.returncode} {r.stdout}{r.stderr}")
            c.check("RM-A nothing was rewritten",
                    all((root / rel).read_bytes() == b for rel, b in before.items()),
                    "a map changed on a commit that cannot affect one")
            c.check("RM-A only the artifact is staged",
                    staged(root) == ["_artifacts/note.md"], str(staged(root)))
            c.check("RM-A and it printed nothing", r.stdout.strip() == "", repr(r.stdout))

    # ── B · REFRESH: a staged .agents/ doc regenerates AND stages both maps ───────────────────
    if c.block("RM-B · SCC-290 · a staged .agents/ doc regenerates and STAGES the maps"):
        with TempDir() as tmp:
            root = seed_repo(tmp)
            write(root / ".agents" / "rules" / "new.md", "# new\n\nLinks [x](../../docs/x.md).\n")
            git(root, "add", "--", ".agents/rules/new.md")
            r = run(root, "--staged")
            c.check("RM-B exit 0", r.returncode == 0, f"rc={r.returncode} {r.stdout}{r.stderr}")
            now = set(staged(root))
            c.check("RM-B the doc graph is regenerated AND staged",
                    {"docs/doc-graph.md", "docs/doc-graph.json"} <= now, str(sorted(now)))
            # ⛔ NOT the repo-map: `.agents` is IN `grm.DEFAULT_IGNORES`, so the map does not
            # walk the toolkit and a `.agents/` edit genuinely cannot change it. Asserted as a
            # fact rather than left unsaid — the first draft of this case demanded the repo-map
            # here, which would only have passed by making the hook rewrite a file for nothing.
            c.check("RM-B ⛔ the repo-map is NOT touched — .agents/ is outside what it walks",
                    "docs/repo-map.md" not in now, str(sorted(now)))
            g = json.loads((root / "docs" / "doc-graph.json").read_text(encoding="utf-8"))
            c.check("RM-B the new doc is a node in the regenerated graph",
                    ".agents/rules/new.md" in {n["path"] for n in g["nodes"]},
                    str(sorted(n["path"] for n in g["nodes"])))
            c.check("RM-B it says what it staged, one line per file",
                    r.stdout.count("regenerated and staged") == 2, repr(r.stdout))

    # ── B2 · the OTHER half: a docs/ change DOES restage the repo-map ─────────────────────────
    # Without this, RM-B alone is satisfied by a hook that never regenerates the repo-map at all.
    if c.block("RM-B2 · SCC-290 · a staged docs/ file restages the repo-map too"):
        with TempDir() as tmp:
            root = seed_repo(tmp)
            write(root / "docs" / "guide.md", "# guide\n")
            git(root, "add", "--", "docs/guide.md")
            r = run(root, "--staged")
            now = set(staged(root))
            c.check("RM-B2 exit 0", r.returncode == 0, f"rc={r.returncode} {r.stdout}{r.stderr}")
            c.check("RM-B2 the repo-map is regenerated AND staged (docs/ IS walked)",
                    "docs/repo-map.md" in now, str(sorted(now)))
            # docs/ collapses to a count at this size (threshold=8), so the observable is the
            # COUNT moving, not the filename appearing. Asserted against the committed baseline so
            # the case cannot pass on a map that never changed.
            auto = (root / "docs" / "repo-map.md").read_text(encoding="utf-8")
            was = git(root, "show", "HEAD:docs/repo-map.md").stdout
            c.check("RM-B2 the repo-map's AUTO block actually MOVED (docs/ file count)",
                    auto != was and "5 files" in auto and "5 files" not in was,
                    f"now={[l for l in auto.splitlines() if 'files:' in l]} "
                    f"was={[l for l in was.splitlines() if 'files:' in l]}")

    # ── B3 · ISOLATE the repo-map trigger — RM-B2 alone does not test it ─────────────────────
    # ⛔ THE MUTATION SWEEP FOUND THIS (M5 survived). In RM-B2 the staged file is a `.md` under
    # `docs/`, so the DOC-GRAPH trigger fires, and a doc-graph write forces a repo-map rebuild
    # anyway ("always after: a doc-graph write can itself have changed what the repo-map sees").
    # Delete the repo-map trigger entirely and RM-B2 still passes. Only a staged file that the
    # repo-map walks and the doc graph does NOT can tell them apart.
    if c.block("RM-B3 · SCC-290 · a non-markdown docs file triggers the repo-map ALONE"):
        with TempDir() as tmp:
            root = seed_repo(tmp)
            write(root / "docs" / "diagram.txt", "not markdown\n")
            git(root, "add", "--", "docs/diagram.txt")
            r = run(root, "--staged")
            now = set(staged(root))
            c.check("RM-B3 exit 0", r.returncode == 0, f"rc={r.returncode} {r.stdout}{r.stderr}")
            c.check("RM-B3 the repo-map IS regenerated and staged",
                    "docs/repo-map.md" in now, str(sorted(now)))
            c.check("RM-B3 ⛔ and the doc graph is NOT — a .txt is not a node",
                    not ({"docs/doc-graph.md", "docs/doc-graph.json"} & now), str(sorted(now)))

    # ── B4 · THE FIRST RUN, where the ordering actually bites ────────────────────────────────
    # ⛔ THE MUTATION SWEEP FOUND THIS TOO (M11, M12 survived RM-C). Once `docs/doc-graph.*` exist,
    # only their CONTENT changes, and the repo-map collapses `docs/` to a file COUNT — so the
    # ordering bug is invisible in a settled tree. It bites exactly once: on the run that CREATES
    # those two files, which raises the count. That is also the only run where a graph that reads
    # its own output can be caught. So the case has to start from a tree with no doc graph at all.
    if c.block("RM-B4 · SCC-290 · the FIRST refresh converges in ONE run"):
        with TempDir() as tmp:
            root = tmp / "wk"
            root.mkdir(parents=True)
            git(root, "init", "-q", "-b", "main")
            write(root / "AGENTS.md", "# workspace\n")
            write(root / ".agents" / "commands" / "cicd-code-review.md", "# review\n")
            write(root / ".agents" / "commands" / "smh-quick-dev.md", "# dev\n")
            write(root / ".agents" / "rules" / "a.md", "# a\n\n[x](../../docs/x.md)\n")
            write(root / "docs" / "x.md", "# x\n")
            write(root / "docs" / "repo-map.md", REPO_MAP_SCAFFOLD)
            write(root / "docs" / "_scc_sops_prds" / "workflows_testing_SOP.md", SOP_TEXT)
            git(root, "add", "-A")
            git(root, "commit", "-qm", "seed")
            # ⛔ THE STAGED FILE MUST BE UNDER `.agents/`, NOT `docs/`, AND THE SWEEP IS WHAT
            # PROVED IT (M11 survived a `docs/` version of this case). `.agents` is IN the
            # repo-map's ignore set, so it triggers the DOC GRAPH ONLY — and the doc graph writes
            # its two files into `docs/`, which the repo-map DOES walk. That is the only shape
            # where "a doc-graph write forces a repo-map rebuild" is load-bearing; stage a `docs/`
            # file instead and the repo-map was already going to be rebuilt for its own reasons.
            write(root / ".agents" / "rules" / "new.md", "# new\n\n[x](../../docs/x.md)\n")
            git(root, "add", "--", ".agents/rules/new.md")

            r = run(root, "--staged")
            c.check("RM-B4 exit 0", r.returncode == 0, f"rc={r.returncode} {r.stdout}{r.stderr}")
            c.check("RM-B4 the doc graph was CREATED",
                    (root / "docs" / "doc-graph.json").exists(), "no graph written")
            v = run(root, "--verify")
            c.check("RM-B4 ⛔ ONE run converges — --verify is clean immediately after",
                    v.returncode == 0,
                    f"still stale after the run that created the files: {v.stdout}")
            v2 = run(root, "--staged")
            c.check("RM-B4 and a second --staged writes nothing more",
                    "regenerated and staged" not in v2.stdout, repr(v2.stdout))

    # ── C · IDEMPOTENT: nothing to change means nothing staged ────────────────────────────────
    if c.block("RM-C · SCC-290 · a second run changes nothing and stages nothing"):
        with TempDir() as tmp:
            root = seed_repo(tmp)
            write(root / ".agents" / "rules" / "new.md", "# new\n")
            git(root, "add", "--", ".agents/rules/new.md")
            run(root, "--staged")
            git(root, "commit", "-qm", "SCC-290 add a rule")
            git(root, "add", "--", ".agents/rules/new.md")
            r = run(root, "--staged")
            c.check("RM-C exit 0", r.returncode == 0, f"rc={r.returncode} {r.stdout}{r.stderr}")
            c.check("RM-C no map was re-staged",
                    not ({"docs/repo-map.md", "docs/doc-graph.md", "docs/doc-graph.json"}
                         & set(staged(root))), str(staged(root)))
            c.check("RM-C and --verify agrees the tree is current",
                    run(root, "--verify").returncode == 0,
                    run(root, "--verify").stdout)

    # ── D · --verify REFUSES a stale tree, and names the file ─────────────────────────────────
    if c.block("RM-D · SCC-290 · --verify refuses a stale map and NAMES it"):
        with TempDir() as tmp:
            root = seed_repo(tmp)
            p = root / "docs" / "repo-map.md"
            p.write_text(p.read_text(encoding="utf-8").replace(
                "<!-- REPO-MAP:AUTO-START -->", "<!-- REPO-MAP:AUTO-START -->\nHAND EDITED\n"),
                encoding="utf-8")
            r = run(root, "--verify")
            c.check("RM-D exit 1", r.returncode == 1, f"rc={r.returncode} {r.stdout}")
            c.check("RM-D the stale file is NAMED", "docs/repo-map.md" in r.stdout, repr(r.stdout))
            # ⛔ THE REMEDY MUST BE THE MODE THAT CAN ACTUALLY FIX THIS. `--verify` fires on a
            # merge / --no-verify / unarmed-clone tree, and all three have an EMPTY index, which
            # `--staged` is gated on. Printing `--staged` here sent the operator to a command
            # that exits 0 and writes nothing. Asserted both ways so the wrong one cannot creep
            # back beside the right one.
            c.check("RM-D the remedy printed is --repair, NOT the trigger-gated --staged",
                    "--repair" in r.stdout and "--staged" not in r.stdout, repr(r.stdout))
            c.check("RM-D ⛔ --verify WROTE NOTHING (it is a read-only check)",
                    "HAND EDITED" in p.read_text(encoding="utf-8"),
                    "verify repaired the file instead of reporting it")

    # ── D2 · THE MERGE CASE: stale tree, NOTHING staged — the remedy must actually work ───────
    # ⛔ FOUND AT THIS LANE'S OWN CLOSE-OUT, by the hook refusing this lane's push. `git merge`
    # runs `pre-merge-commit`, NOT `pre-commit`, so a merge that brings in a `docs/` file leaves
    # the maps stale with a CLEAN tree behind it. `--verify` then refuses the push and prints
    # `--staged` as the remedy — but `--staged` is trigger-gated on the STAGED set, and after a
    # merge nothing is staged, so it returns 0 having written nothing. The operator is handed a
    # command that cannot fix what it was named to fix, and the only way out is `--no-verify`:
    # a gate whose only escape is the bypass teaches everyone to reach for the bypass.
    # `--repair` is the trigger-free mode, and it is what `--verify` must name.
    if c.block("RM-D2 · SCC-290 · --repair fixes a stale tree with an EMPTY index"):
        with TempDir() as tmp:
            root = seed_repo(tmp)
            # A merge's shape: new content on disk, committed, index empty, maps not regenerated.
            write(root / "docs" / "merged.md", "# merged\n\nSee [x](x.md).\n")
            git(root, "add", "--", "docs/merged.md")
            git(root, "commit", "-qm", "SCC-290 arrive by merge", "--no-verify")
            c.check("RM-D2 the fixture really is stale", run(root, "--verify").returncode == 1,
                    "the merge shape did not go stale - the case proves nothing")
            c.check("RM-D2 and the index really is empty", staged(root) == [], str(staged(root)))

            # The documented remedy, on the tree it is documented for.
            s1 = run(root, "--staged")
            c.check("RM-D2 --staged alone cannot fix it (this is WHY --repair exists)",
                    run(root, "--verify").returncode == 1,
                    f"--staged fixed an empty index; the trigger gate is gone: {s1.stdout}")

            r = run(root, "--repair")
            c.check("RM-D2 --repair exit 0", r.returncode == 0,
                    f"rc={r.returncode} {r.stdout}{r.stderr}")
            c.check("RM-D2 ⛔ ONE --repair converges", run(root, "--verify").returncode == 0,
                    f"still stale after --repair: {run(root, '--verify').stdout}")
            c.check("RM-D2 it STAGES what it wrote, so the fix is one `git commit` away",
                    {"docs/doc-graph.md", "docs/doc-graph.json", "docs/repo-map.md"}
                    <= set(staged(root)), str(sorted(staged(root))))
            c.check("RM-D2 the new doc reached the graph",
                    "docs/merged.md" in {n["path"] for n in json.loads(
                        (root / "docs" / "doc-graph.json").read_text(encoding="utf-8"))["nodes"]},
                    "the repair regenerated stale content")
            c.check("RM-D2 a second --repair is a silent no-op",
                    "regenerated and staged" not in run(root, "--repair").stdout,
                    repr(run(root, "--repair").stdout))

    # ── D4 · THE DOORS MUST NAME THE REMEDY THAT WORKS ────────────────────────────────────────
    # ⛔ THE ACCEPTANCE LENS CAUGHT THIS, NOT A TEST. The --repair commit's own changelog row
    # claimed "every message that names a remedy now names --repair" -- and four sites in
    # /smh-update-maps-indexes still said --staged, in both mirrors. That door is exactly where an
    # operator lands after check 10 fires, so it handed them the loop --repair exists to close.
    # A prose claim nothing checks is a claim that rots; this is the check.
    if c.block("RM-D4 · SCC-290 · no house door prescribes --staged as the stale-maps remedy"):
        root = Path(__file__).resolve().parents[3]
        offenders = []
        for d in ("\u002eagents/commands", "\u002eopencode/commands", "\u002eclaude/skills"):
            base = root / d
            if not base.is_dir():
                continue
            for f in sorted(base.rglob("*.md")):
                for i, line in enumerate(f.read_text(encoding="utf-8",
                                                     errors="replace").splitlines(), 1):
                    if "refresh_maps.py --staged" in line and "never `--staged`" not in line:
                        offenders.append(f"{f.relative_to(root)}:{i}")
        c.check("RM-D4 no door hands the operator the trigger-gated mode", not offenders,
                str(offenders))
        # ⛔ ANTI-VACUITY. If the scan reaches no doors at all, the check above passes on nothing -
        # exactly the empty-input pass `tests-must-gate-for-real` §5 bans.
        seen = sum(1 for f in (root / ".agents" / "commands").rglob("*.md"))
        c.check("RM-D4 the scan actually reached the door folder", seen > 20, f"{seen} doors seen")

    # ── E · the round trip: a commit made through the hook leaves --verify green ──────────────
    if c.block("RM-E · SCC-290 · a commit made with the hook leaves --verify at exit 0"):
        with TempDir() as tmp:
            root = seed_repo(tmp)
            write(root / "docs" / "guide.md", "# guide\n\n[x](x.md)\n")
            git(root, "add", "--", "docs/guide.md")
            run(root, "--staged")
            cm = git(root, "commit", "-qm", "SCC-290 add a guide")
            r = run(root, "--verify")
            c.check("RM-E the commit landed", cm.returncode == 0, cm.stderr[-200:])
            c.check("RM-E --verify is clean straight after", r.returncode == 0, r.stdout)
            c.check("RM-E the maps rode THAT commit, not a later one",
                    "docs/doc-graph.json" in git(
                        root, "show", "--name-only", "--format=", "HEAD").stdout,
                    git(root, "show", "--name-only", "--format=", "HEAD").stdout)

    # ── F · RATCHET: adding a broken reference refuses the commit ─────────────────────────────
    # Not "zero broken refs" — there are 75 in the live tree, mostly stale guides. The contract is
    # that THIS commit may not add one.
    if c.block("RM-F · SCC-290 · the ratchet refuses a NEW broken reference, and names it"):
        with TempDir() as tmp:
            root = seed_repo(tmp)
            write(root / ".agents" / "rules" / "bad.md",
                  "# bad\n\nPoints at [gone](../../docs/does/not/exist.md).\n")
            git(root, "add", "--", ".agents/rules/bad.md")
            run(root, "--staged")                       # regeneration is the other half
            r = truth(root)
            c.check("RM-F exit 1", r.returncode == 1, f"rc={r.returncode} {r.stdout}")
            c.check("RM-F the ratchet is what fired", "broken doc references went" in r.stdout,
                    repr(r.stdout))
            c.check("RM-F the NEW ref is named with its source",
                    "docs/does/not/exist.md" in r.stdout and ".agents/rules/bad.md" in r.stdout,
                    repr(r.stdout))
            c.check("RM-F the bypass is printed", "--no-verify" in r.stdout, repr(r.stdout))
            c.check("RM-F ⛔ and the RE-BASELINE hatch is printed, distinct from the bypass",
                    "[maps-ok]" in r.stdout and "SCOPE changed" in r.stdout, repr(r.stdout))
            # the hatch actually works, and only from the message body
            ok = truth(root, "SCC-290 widen the graph's scope [maps-ok]")
            c.check("RM-F [maps-ok] in the message re-baselines, on the record",
                    ok.returncode == 0 and "on the record" in ok.stdout, ok.stdout)
            # ⛔ a COMMENT line is not a decision — git seeds the message file with `# ...` help
            commented = truth(root, "SCC-290 a commit\n# put [maps-ok] here to re-baseline\n")
            c.check("RM-F ⛔ the token in a COMMENT line does NOT opt out",
                    commented.returncode == 1,
                    "a template that merely mentions the token would exempt every commit")

    if c.block("RM-F2 · SCC-290 · ALLOW: a commit that adds no broken ref passes the ratchet"):
        with TempDir() as tmp:
            root = seed_repo(tmp)
            write(root / ".agents" / "rules" / "good.md", "# good\n\n[x](../../docs/x.md)\n")
            git(root, "add", "--", ".agents/rules/good.md")
            run(root, "--staged")
            r = truth(root)
            c.check("RM-F2 exit 0 — the ratchet allows a clean commit",
                    r.returncode == 0, f"rc={r.returncode} {r.stdout}")

    # ── G · REVERSE DOOR: a door the SOP does not name refuses the commit ─────────────────────
    if c.block("RM-G · SCC-290 · a house door missing from the SOP refuses the commit"):
        with TempDir() as tmp:
            root = seed_repo(tmp)
            write(root / ".agents" / "commands" / "cicd-new.md", "# new door\n")
            git(root, "add", "--", ".agents/commands/cicd-new.md")
            run(root, "--staged")
            r = truth(root)
            c.check("RM-G exit 1", r.returncode == 1, f"rc={r.returncode} {r.stdout}")
            c.check("RM-G the missing door is named as /cicd-new",
                    "/cicd-new" in r.stdout, repr(r.stdout))
            c.check("RM-G and the SOP is named as the place to fix it",
                    "workflows_testing_SOP.md" in r.stdout, repr(r.stdout))

    if c.block("RM-G2 · SCC-290 · ALLOW: vendor and -AP doors are NOT required in the SOP"):
        with TempDir() as tmp:
            root = seed_repo(tmp)
            for name in ("dev.md", "tea.md", "bmad-help.md", "cicd-code-review-AP.md",
                         "testarch-ci.md"):
                write(root / ".agents" / "commands" / name, "# vendor\n")
            git(root, "add", "--", ".agents/commands")
            run(root, "--staged")
            r = truth(root)
            c.check("RM-G2 exit 0 — the vendor set and the -AP twins are exempt",
                    r.returncode == 0, f"rc={r.returncode} {r.stdout}")

    if c.block("RM-G3 · SCC-290 · the door check ALSO passes when the SOP already names it"):
        with TempDir() as tmp:
            root = seed_repo(tmp)
            write(root / ".agents" / "commands" / "cicd-new.md", "# new door\n")
            sop = root / "docs" / "_scc_sops_prds" / "workflows_testing_SOP.md"
            sop.write_text(sop.read_text(encoding="utf-8") + "- `/cicd-new` - the new door.\n",
                           encoding="utf-8")
            git(root, "add", "--", ".agents/commands/cicd-new.md",
                "docs/_scc_sops_prds/workflows_testing_SOP.md")
            run(root, "--staged")
            r = truth(root)
            c.check("RM-G3 exit 0 once the SOP names it", r.returncode == 0,
                    f"rc={r.returncode} {r.stdout}")

    # ── G4 · a FILE PATH is not the door being NAMED ─────────────────────────────────────────
    # ⛔ Blind Hunter, SCC-288. The regex anchored on `/` with a `(?![\w-])` lookahead, and `.md`
    # passes that lookahead -- so `.agents/commands/cicd-new.md` appearing anywhere in the SOP
    # (a file-layout table, a fenced `cat`) satisfied the check. The whole point is that the
    # OPERATOR-facing page names the door the operator types.
    if c.block("RM-G4 · SCC-290 · the SOP mentioning the FILE does not count as naming the door"):
        with TempDir() as tmp:
            root = seed_repo(tmp)
            write(root / ".agents" / "commands" / "cicd-new.md", "# new door\n")
            sop = root / "docs" / "_scc_sops_prds" / "workflows_testing_SOP.md"
            sop.write_text(sop.read_text(encoding="utf-8")
                           + "See `.agents/commands/cicd-new.md` for the file.\n",
                           encoding="utf-8")
            git(root, "add", "--", ".agents/commands/cicd-new.md",
                "docs/_scc_sops_prds/workflows_testing_SOP.md")
            run(root, "--staged")
            r = truth(root)
            c.check("RM-G4 the commit is still REFUSED - the file path is not the door",
                    r.returncode == 1, f"rc={r.returncode} {r.stdout}")

    # ── H · both machines: the kill switch, and ASCII-only output ─────────────────────────────
    if c.block("RM-H · SCC-290 · the DISABLE kill switch, and ASCII-only console output"):
        with TempDir() as tmp:
            root = seed_repo(tmp)
            write(root / ".agents" / "rules" / "bad.md",
                  "# bad\n\n[gone](../../docs/does/not/exist.md)\n")
            git(root, "add", "--", ".agents/rules/bad.md")
            run(root, "--staged")
            loud = truth(root)
            (root / ".agents" / "scripts" / "git-hooks").mkdir(parents=True, exist_ok=True)
            (root / ".agents" / "scripts" / "git-hooks" / "DISABLE").write_text("", encoding="utf-8")
            quiet = truth(root)
            c.check("RM-H the same commit is refused without the switch",
                    loud.returncode == 1, f"rc={loud.returncode}")
            c.check("RM-H and allowed with it", quiet.returncode == 0,
                    f"rc={quiet.returncode} {quiet.stdout}")
            both = loud.stdout + loud.stderr
            c.check("RM-H every byte it prints is ASCII (the PC console is cp1252)",
                    both.isascii(),
                    repr([ch for ch in both if not ch.isascii()][:10]))

    # ── J · an UNTRACKED file is not part of the repository, and no map may name it ──────────
    # ⛔ REVIEW FINDING R1 (SCC-288), reproduced then closed. The generators walk the FILESYSTEM,
    # so a scratch `.md` nobody committed became a graph node. Two consequences, and the second is
    # the worse one: `--verify` refuses the PUSH of unrelated committed work, and the `--repair`
    # it prints as the remedy then WRITES that phantom into a tracked artifact bound for main.
    # Scratch files are constant in this workflow. The module's stated ACCEPTED LIMIT covers
    # unstaged edits to TRACKED files; it never covered files git does not have.
    #
    # Both generators are asserted, because they fail differently: the doc graph gains a NODE, and
    # the repo-map's content-mode summary is a FILE COUNT that ticks up.
    if c.block("RM-J · SCC-288 · an untracked scratch file changes NO map, and blocks NO push"):
        with TempDir() as tmp:
            root = seed_repo(tmp)
            before = {rel: (root / rel).read_bytes()
                      for rel in ("docs/repo-map.md", "docs/doc-graph.json")}
            write(root / ".agents" / "rules" / "zz-scratch-probe.md", "# scratch\n")
            write(root / "docs" / "zz-scratch-probe.md", "# scratch\n")

            v = run(root, "--verify")
            c.check("RM-J --verify still exit 0 - a scratch file cannot refuse a push",
                    v.returncode == 0, f"rc={v.returncode} {v.stdout}")

            r = run(root, "--repair")
            c.check("RM-J --repair exit 0", r.returncode == 0, f"rc={r.returncode} {r.stdout}")
            c.check("RM-J --repair wrote NOTHING (it must not stage a phantom)",
                    all((root / rel).read_bytes() == b for rel, b in before.items()),
                    "the remedy the gate prints edited a tracked map to name an untracked file")
            c.check("RM-J and nothing at all was staged", staged(root) == [], str(staged(root)))
            c.check("RM-J the phantom is not a node in the graph",
                    "zz-scratch-probe" not in (root / "docs" / "doc-graph.json")
                    .read_text(encoding="utf-8"),
                    "an untracked file is in the committed graph")

            # ⭐ THE OTHER HALF, or the fix is just "ignore new files". The instant it is STAGED it
            # is part of the commit being made, and both maps must pick it up.
            git(root, "add", "--", ".agents/rules/zz-scratch-probe.md",
                "docs/zz-scratch-probe.md")
            s = run(root, "--staged")
            c.check("RM-J once STAGED, the same file regenerates the maps", s.returncode == 0,
                    f"rc={s.returncode} {s.stdout}")
            c.check("RM-J and it IS a node now",
                    "zz-scratch-probe" in (root / "docs" / "doc-graph.json")
                    .read_text(encoding="utf-8"),
                    "staging it changed nothing - the filter is too wide")

    # ── J2 · the DIRECTORY half of the same rule, both ways ──────────────────────────────────
    # ⛔ The first cut of the R1 fix pruned a directory when its subtree "produced no lines",
    # which is a different fact from "git does not have it" — measured against the real map, it
    # dropped two tracked directories whose only files are DOTFILES the walk already hides. So the
    # predicate answers for the directory itself, and both halves are asserted here: a directory
    # git has something under survives even when nothing in it is visible, and a directory that
    # exists only because of untracked files never reaches the map.
    if c.block("RM-J2 · SCC-288 · a tracked dir survives; an untracked-only dir never appears"):
        with TempDir() as tmp:
            root = seed_repo(tmp)
            write(root / "keepme" / ".memlog.md", "# hidden but tracked\n")
            git(root, "add", "--", "keepme/.memlog.md")
            write(root / "phantom" / "scratch.md", "# never committed\n")
            run(root, "--repair")
            book = (root / "docs" / "repo-map.md").read_text(encoding="utf-8")
            c.check("RM-J2 the tracked dir is in the map though its only file is hidden",
                    "keepme/" in book, "a real tracked directory was pruned out of the map")
            c.check("RM-J2 the untracked-only dir is NOT",
                    "phantom/" not in book, "an untracked directory reached a committed map")

    # ── I · argument discipline ───────────────────────────────────────────────────────────────
    if c.block("RM-I · SCC-290 · exactly one mode, or exit 2"):
        with TempDir() as tmp:
            root = seed_repo(tmp)
            for args in ([], ["--staged", "--verify"], ["--staged", "--truth", "x"],
                         ["--repair", "--verify"], ["--repair", "--staged"]):
                r = run(root, *args)
                c.check(f"RM-I {args or ['(no flag)']} is exit 2",
                        r.returncode == 2, f"rc={r.returncode} {r.stdout}{r.stderr}")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())

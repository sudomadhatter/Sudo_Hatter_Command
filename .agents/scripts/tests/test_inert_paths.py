"""task_preflight.py — the inert-path predicate and the ceremony tier (SCC-451).

The gate used to ask *"what folder is this in"*. Anything under `backend/ frontend/ firebase/
functions/ mobile/ .github/` was a deployable product change, full stop — so
`frontend/scripts/INDEX.md`, a markdown map that ships nothing, was refused by the standing-push
door and handed to `/cicd-push-e2e`, which refuses back in a TRUNK project. The routing graph had
no exit node, which is why the gate got skipped by hand.

It asks a different question now: **does anything read this file when the system runs, or does a
gate read it as law?**

  ── WHY THESE CASES ────────────────────────────────────────────────────────────────────────
**Markdown is not the test**, and three counterexamples are pinned as controls because each one
would ship if the predicate keyed on the extension: `.agents/rules/*.md` IS the law;
`backend/knowledge/aviationchat_pitch.md` is loaded at runtime by a loader that raises if it is
missing; `frontend/public/INDEX.md` is served verbatim on production (measured 2026-09-12:
`curl https://aviationchat.org/INDEX.md` -> 200).

**Every guard runs AFTER the glob matches**, so a declaration can only ever *propose* a carve-out.
That is the same self-protection `scope_check.py:76-78` gives `critical-surfaces.json` — a line
that can widen itself is not a line.

**The two failure directions are opposite and both are pinned.** An absent declaration means the
defaults (absence is a decision). A malformed one means NOTHING is inert (corruption is not a
decision) — this predicate fails toward ceremony, never toward a wide carve-out.

**`tiny` is unreachable without line evidence.** `ceremony_tier` is called at two moments: quick-dev
Step 1 has a planned path list and no diff, while Step 5 and both standing-push doors have a real
one. A tier is never lowered on an assumption.

**The entry-point exclusion is by PATTERN and it is not a threshold.** Reverse-dependency count is
flatly wrong for entry points — measured over AviationChat's 146 frontend components,
`app/layout.tsx` has reach 0 and wraps every screen, `app/dashboard/page.tsx` has reach 0 and is an
entire user journey. Nothing imports a page; the router loads it. SCC-452 replaces the line count
with that reach score and this exclusion still binds there, which is why it is a separate rule.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from _harness import SCRIPTS, Cases, TempDir
import _pf_fixtures as pf

sys.path.insert(0, str(SCRIPTS))
import task_preflight as tp  # noqa: E402

ROOT = SCRIPTS.parents[1]
COMMANDS = ROOT / ".agents/commands"

DOORS = ("cicd-non-crit-pr-push", "smh-non-crit-pr-push",
         "cicd-quick-dev", "smh-quick-dev")


def body(name: str) -> str:
    return (COMMANDS / f"{name}.md").read_text(encoding="utf-8")


def bare(root: Path, **files: str) -> Path:
    """A repo-shaped directory with no git — the predicate reads files, never history."""
    repo = root / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    for rel, text in files.items():
        p = repo / rel.replace("|", "/")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return repo


def declare(repo: Path, *globs: str) -> None:
    rows = [{"glob": g, "why": "test"} for g in globs]
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents/inert-paths.json").write_text(
        json.dumps({"inert": rows}, indent=2), encoding="utf-8")


def surfaces(repo: Path, *paths: str) -> None:
    """A minimal critical-surfaces map in the shape scope_check.py parses.

    ⛔ Every declared path is CREATED: `parse_map` refuses a row naming no file, on the rule
    that a dead row reads as a protected surface. A fixture that skipped this would return
    `(None, err)` and silently test the error arm instead of the veto.
    """
    for p in paths:
        if not p.endswith("/"):
            f = repo / p
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("x\n", encoding="utf-8")
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents/critical-surfaces.json").write_text(json.dumps({
        "surfaces": {
            "auth": {"why": "test", "paths": list(paths)},
            "billing": {"why": "nothing here", "paths": []},
            "rules": {"why": "nothing here", "paths": []},
            "answers": {"why": "nothing here", "paths": []},
            "ci": {"why": "nothing here", "paths": []},
        }
    }, indent=2), encoding="utf-8")


# The six paths the ticket measured, and what each must answer. The first three are already
# accepted today (they are outside PRODUCT_DIRS entirely) and are controls: this lane must not
# change them. The next two are the whole point. The last is the control that must NOT move.
MEASURED = [
    ("_my_resources/notes.md",             False, "outside the product dirs — accepted today"),
    ("_artifacts/_main/INDEX.md",           False, "outside the product dirs — accepted today"),
    ("docs/repo-map.md",                    False, "outside the product dirs — accepted today"),
    ("frontend/scripts/INDEX.md",           False, "a map file under a product dir — THE FIX"),
    ("backend/agents/INDEX.md",             False, "a map file under a product dir — THE FIX"),
    ("frontend/src/components/Button.tsx",  True,  "real product code — must STILL hand off"),
]


def main() -> int:
    c = Cases("task_preflight.py — the inert predicate and the ceremony tier (SCC-451)")

    # ── A ─────────────────────────────────────────────────────────────────────────────────
    if c.block("A · inert_paths / deployable_paths on the six measured paths"):
        with TempDir() as t:
            repo = bare(t)                                  # no declaration -> the defaults
            paths = [p for p, _, _ in MEASURED]
            got = tp.deployable_paths(repo, paths)
            for p, deployable, why in MEASURED:
                c.check(f"A · {p} -> {'deployable' if deployable else 'carries on'} ({why})",
                        (p in got) == deployable, f"deployable_paths={got}")
            c.check("A · the defaults are basenames, never extensions "
                    "(`*.md` would match the law and the runtime docs)",
                    tp.DEFAULT_INERT == ("INDEX.md", "README.md"),
                    repr(getattr(tp, "DEFAULT_INERT", None)))
            c.check("A · inert_paths names WHAT was carved out, so a door can say it — and it "
                    "answers about the FILE, not its folder, so an artifact INDEX is in the list "
                    "even though the prefix test never reached it",
                    sorted(tp.inert_paths(repo, paths))
                    == ["_artifacts/_main/INDEX.md", "backend/agents/INDEX.md",
                        "frontend/scripts/INDEX.md"],
                    repr(tp.inert_paths(repo, paths)))

    # ── B ─────────────────────────────────────────────────────────────────────────────────
    if c.block("B · the hard guards — served, law, runtime doc — each pinned BOTH ways"):
        with TempDir() as t:
            repo = bare(t)
            declare(repo, "INDEX.md", "README.md")

            # SERVED. Next.js hands out `public/` verbatim; measured live at 200.
            served = ["frontend/public/INDEX.md", "frontend/static/README.md"]
            c.check("⛔ B · a file under public/ or static/ is NEVER inert — it is ON PRODUCTION",
                    tp.deployable_paths(repo, served) == served,
                    repr(tp.deployable_paths(repo, served)))
            c.check("B · …and the same basename outside a served folder still carries on",
                    tp.deployable_paths(repo, ["frontend/scripts/INDEX.md"]) == [],
                    repr(tp.deployable_paths(repo, ["frontend/scripts/INDEX.md"])))

            # LAW. A rule or a command body is markdown AND it is the law.
            law = [".agents/rules/git-policy.md", ".agents/commands/smh-quick-dev.md"]
            c.check("⛔ B · nothing under .agents/rules/ or .agents/commands/ is ever inert",
                    tp.inert_paths(repo, law) == [], repr(tp.inert_paths(repo, law)))
            # ⛔ AND THE CASE THAT MAKES THAT CHECK NON-VACUOUS. The two paths above match no
            # declared glob, so they would come back empty with the LAW guard deleted - the
            # assertion passed for the wrong reason. `README.md` IS a default glob, so this is
            # the first case where the guard is the only thing standing between a law file and
            # the carve-out. It reproduced the repo's own `norm()` scar: `lstrip("./")` takes a
            # CHARACTER SET, so it ate the leading dot off `.agents/...` and the prefix test
            # could never match (lane_qualify.norm carries the same warning in its docstring).
            law_readme = [".agents/rules/README.md", ".agents/commands/README.md"]
            c.check("⛔ B · a README under .agents/rules/ or .agents/commands/ is NOT inert - "
                    "it matches a DEFAULT glob, so only the law guard stops it",
                    tp.inert_paths(repo, law_readme) == [],
                    repr(tp.inert_paths(repo, law_readme)))
            c.check("B · …and a leading `./` on the same path does not change the answer",
                    tp.inert_paths(repo, ["./.agents/rules/README.md"]) == [],
                    repr(tp.inert_paths(repo, ["./.agents/rules/README.md"])))
            # ⛔ THE TWO DOORS MUST NOT DISAGREE ON A SPELLING. `lane_qualify` normalises its
            # input before calling the predicate; the fenced door commands pass argv straight
            # through. With the prefix test un-normalised, `./frontend/src/x.tsx` was HANDOFF
            # through one door and "carry on" through the other - and a SERVED production file
            # appeared in neither list, so the door printed nothing about it at all.
            dotted = ["./frontend/src/components/Button.tsx"]
            c.check("⛔ B · a `./`-spelled product path is still deployable - the doors cannot "
                    "disagree with lane_qualify about a spelling",
                    tp.deployable_paths(repo, dotted) == dotted,
                    repr(tp.deployable_paths(repo, dotted)))
            dotted_served = ["./frontend/public/INDEX.md"]
            c.check("⛔ B · a `./`-spelled SERVED file appears as deployable, never in neither "
                    "list",
                    tp.deployable_paths(repo, dotted_served) == dotted_served,
                    repr(tp.deployable_paths(repo, dotted_served)))
            # ⛔ THIS PIN WAS VACUOUS AND A SURVIVING MUTANT SAID SO (N5, 2026-09-12: "served-guard
            # directory arm dropped - `parts[:-1]` always"). `frontend/public/` matches NEITHER
            # default basename, so `inert_paths` returned `[]` from the glob step and the served
            # guard was never reached - the assertion passed with the guard deleted. Same failure
            # mode as the law-guard pin at 6463df0a: an assertion about a guard must use input the
            # glob actually ADMITS, or it is testing nothing.
            with TempDir() as t2:
                served = bare(t2)
                # Right-anchored on whole components, so a bare word matches the DIRECTORY itself.
                declare(served, "public", "private")
                c.check("⛔ B · a planned DIRECTORY that IS the served folder is not inert - and "
                        "the glob ADMITS it, so the served guard is the only thing refusing",
                        tp.inert_paths(served, ["frontend/public/"]) == [],
                        repr(tp.inert_paths(served, ["frontend/public/"])))
                c.check("B · CONTROL: the same glob on a NON-served directory IS inert, so the "
                        "check above cannot pass by the glob missing",
                        tp.inert_paths(served, ["frontend/private/"]) == ["frontend/private/"],
                        repr(tp.inert_paths(served, ["frontend/private/"])))

            # RUNTIME DOC. Markdown a loader reads, and the loader raises if it is missing.
            runtime = "backend/knowledge/aviationchat_pitch.md"
            c.check("⛔ B · a runtime-loaded doc is not inert under the defaults "
                    "(it matches no basename)",
                    tp.deployable_paths(repo, [runtime]) == [runtime],
                    repr(tp.deployable_paths(repo, [runtime])))

            # …and the declaration cannot widen its way to it.
            declare(repo, "*.md")
            c.check("⛔ B · a BARE-EXTENSION glob is refused at load — it would match the law, "
                    "the runtime docs and everything else",
                    tp.load_inert(repo) == (), repr(tp.load_inert(repo)))
            c.check("⛔ B · …so the runtime doc survives a `*.md` declaration",
                    tp.deployable_paths(repo, [runtime]) == [runtime],
                    repr(tp.deployable_paths(repo, [runtime])))

    # ── C ─────────────────────────────────────────────────────────────────────────────────
    if c.block("C · the declaration cannot widen itself, and corruption is not a decision"):
        with TempDir() as t:
            repo = bare(t)
            declare(repo, "INDEX.md", ".agents/inert-paths.json")
            decl = ".agents/inert-paths.json"
            c.check("⛔ C · the declaration lists ITSELF and is still deployable — "
                    "a line that can widen itself is not a line",
                    tp.inert_paths(repo, [decl]) == [], repr(tp.inert_paths(repo, [decl])))

            c.check("C · an ABSENT declaration means the defaults (absence is a decision)",
                    tp.load_inert(bare(t / "none")) == ("INDEX.md", "README.md"),
                    repr(tp.load_inert(bare(t / "none"))))

            (repo / ".agents/inert-paths.json").write_text("{not json", encoding="utf-8")
            c.check("⛔ C · a MALFORMED declaration means NOTHING is inert — not the defaults. "
                    "This predicate fails toward ceremony",
                    tp.load_inert(repo) == (), repr(tp.load_inert(repo)))
            c.check("⛔ C · …so a map file under a product dir hands off again while it is broken",
                    tp.deployable_paths(repo, ["frontend/scripts/INDEX.md"])
                    == ["frontend/scripts/INDEX.md"],
                    repr(tp.deployable_paths(repo, ["frontend/scripts/INDEX.md"])))

    # ── D ─────────────────────────────────────────────────────────────────────────────────
    if c.block("D · check_scope: an all-inert diff is LOCAL, and .github/ still hands off"):
        with TempDir() as t:
            repo = pf.make_repo(t, deployable=True)
            pf.branch(repo, "chore/SCC-1-maps",
                      {"frontend/scripts/INDEX.md": "# map\n",
                       "backend/agents/INDEX.md": "# map\n"}, push=False)
            import wf_common as wf
            rep = wf.Report()
            lane, touched = tp.check_scope(repo, "chore/SCC-1-maps", rep)
            c.check("D · an all-inert diff under product dirs -> LOCAL, nothing touched",
                    (lane, touched) == ("LOCAL", []), f"{lane} {touched}")

            pf.branch(repo, "chore/SCC-2-ci", {".github/workflows/x.yml": "on: push\n"},
                      push=False)
            rep2 = wf.Report()
            lane2, touched2 = tp.check_scope(repo, "chore/SCC-2-ci", rep2)
            c.check("⛔ D · CONTROL — a repo with a product surface STILL hands off on .github/; "
                    "the carve-out narrows nothing about CI paths",
                    lane2 == "HANDOFF" and ".github/" in touched2, f"{lane2} {touched2}")

    # ── A2 ────────────────────────────────────────────────────────────────────────────────
    if c.block("A2 · all_inert() - the predicate that skips the plan and the TDD"):
        with TempDir() as t:
            repo = bare(t)
            maps = ["frontend/scripts/INDEX.md", "backend/agents/INDEX.md"]
            c.check("A2 · a diff of nothing but map files under product dirs IS all-inert",
                    tp.all_inert(repo, maps) is True, repr(tp.all_inert(repo, maps)))
            # ⛔ THE HOLE THIS PREDICATE EXISTS TO CLOSE. The doors first read "nothing ships"
            # as "all inert" - and in the COMMAND CENTRE nothing ever ships, because the lobby
            # has no product dirs at all. So every lobby diff, an edit to `git-policy.md`
            # included, satisfied the short-circuit and skipped the plan, the literal `approved`
            # and the RED/GREEN. The question is not "does anything ship" but "is EVERY path
            # inert", and only the second one is false for a rule edit.
            c.check("⛔ A2 · a RULE edit is NOT all-inert - nothing ships in the lobby either, "
                    "so 'nothing ships' can never be the test",
                    tp.all_inert(repo, [".agents/rules/git-policy.md"]) is False,
                    repr(tp.all_inert(repo, [".agents/rules/git-policy.md"])))
            c.check("⛔ A2 · one real file alongside six map files is NOT all-inert",
                    tp.all_inert(repo, maps + ["frontend/src/components/Button.tsx"]) is False,
                    repr(tp.all_inert(repo, maps + ["frontend/src/components/Button.tsx"])))
            c.check("⛔ A2 · an EMPTY path list is NOT all-inert - silence is unknown scope, "
                    "never empty scope",
                    tp.all_inert(repo, []) is False, repr(tp.all_inert(repo, [])))
            c.check("⛔ A2 · a served map file is NOT all-inert (it is on production)",
                    tp.all_inert(repo, ["frontend/public/INDEX.md"]) is False,
                    repr(tp.all_inert(repo, ["frontend/public/INDEX.md"])))
            declare(repo, "*.md")
            c.check("⛔ A2 · a malformed/over-wide declaration makes nothing all-inert",
                    tp.all_inert(repo, maps) is False, repr(tp.all_inert(repo, maps)))

    # ── E ─────────────────────────────────────────────────────────────────────────────────
    if c.block("E · ceremony sizes to the NON-INERT part of a mixed diff"):
        with TempDir() as t:
            repo = bare(t)
            surfaces(repo)                                   # a map with nothing listed
            mixed = ["frontend/src/components/Button.tsx"] + [
                f"frontend/{d}/INDEX.md" for d in ("a", "b", "c", "d", "e", "f")]
            c.check("E · one component plus six INDEX files is a ONE-file ceremony",
                    tp.deployable_paths(repo, mixed)
                    == ["frontend/src/components/Button.tsx"],
                    repr(tp.deployable_paths(repo, mixed)))
            c.check("E · …and that sizes to `tiny` at 12 lines, where the raw 7-file count "
                    "would not",
                    tp.ceremony_tier(repo, mixed, lines=12, structural=False) == "tiny",
                    tp.ceremony_tier(repo, mixed, lines=12, structural=False))

    # ── F ─────────────────────────────────────────────────────────────────────────────────
    if c.block("F · no dead end remains: the TRUNK handoff names a door that RUNS"):
        b = body("cicd-non-crit-pr-push")
        c.check("F · the HANDOFF routing reads the mode instead of assuming an epic",
                "epic_mode.py" in b, "epic_mode.py absent from the door body")
        c.check("F · TRUNK is named, and it routes to /cicd-quick-dev, not /cicd-push-e2e",
                "TRUNK" in b and "/cicd-quick-dev" in b,
                f"TRUNK={'TRUNK' in b} quick-dev={'/cicd-quick-dev' in b}")

    # ── G ─────────────────────────────────────────────────────────────────────────────────
    if c.block("G · ceremony_tier's three vetoes — critical surface, manifest, entry point"):
        with TempDir() as t:
            repo = bare(t)
            surfaces(repo, "backend/middleware/auth.py")
            tiny = dict(lines=1, structural=False)
            c.check("⛔ G · a critical surface is an ABSOLUTE veto — one line still means full",
                    tp.ceremony_tier(repo, ["backend/middleware/auth.py"], **tiny) == "full",
                    tp.ceremony_tier(repo, ["backend/middleware/auth.py"], **tiny))
            c.check("G · a dependency manifest is full",
                    tp.ceremony_tier(repo, ["frontend/package.json"], **tiny) == "full",
                    tp.ceremony_tier(repo, ["frontend/package.json"], **tiny))
            c.check("G · CI config is full",
                    tp.ceremony_tier(repo, [".github/workflows/pr-check.yml"], **tiny) == "full",
                    tp.ceremony_tier(repo, [".github/workflows/pr-check.yml"], **tiny))
            c.check("G · an ordinary small change with line evidence is tiny",
                    tp.ceremony_tier(repo, ["frontend/src/lib/fmt.ts"], **tiny) == "tiny",
                    tp.ceremony_tier(repo, ["frontend/src/lib/fmt.ts"], **tiny))
            c.check("G · …and the same change over 50 lines is quick",
                    tp.ceremony_tier(repo, ["frontend/src/lib/fmt.ts"],
                                     lines=51, structural=False) == "quick",
                    tp.ceremony_tier(repo, ["frontend/src/lib/fmt.ts"],
                                     lines=51, structural=False))
            # The veto's own failure direction. A map that cannot be read has not cleared
            # anything, and a tier that fell through to `tiny` here would be the exact hole
            # the absolute veto exists to close.
            (repo / ".agents/critical-surfaces.json").write_text("{not json",
                                                                 encoding="utf-8")
            c.check("⛔ G · an UNREADABLE critical-surfaces map forces full, never tiny",
                    tp.ceremony_tier(repo, ["frontend/src/lib/fmt.ts"], **tiny) == "full",
                    tp.ceremony_tier(repo, ["frontend/src/lib/fmt.ts"], **tiny))

    # ── G2 ────────────────────────────────────────────────────────────────────────────────
    if c.block("G2 · the veto in an UNMAPPED repo - six of nine projects carry no map"):
        with TempDir() as t:
            repo = bare(t)                        # no .agents/critical-surfaces.json at all
            tiny = dict(lines=3, structural=False)
            # ⛔ `scope_check.load_map` returns (None, None) with no map and ([], None) for an
            # empty one - both FALSY, so a veto written as `if rows and overlaps(...)` simply
            # does not run. Measured 2026-09-12: six of the nine repos under Projects/ have no
            # map (B-L-WorldWide, BRKN_Tattoos, NEXGen-Films, NEXgen-VR-Director,
            # OpenChat-Openrouter, sudo-command-center). `scope_check.main` does NOT stop there -
            # it falls back to GENERIC with fragment matching - so Step 1 said OVERLAP on an auth
            # file while Step 1.5 said `tiny` about the same path, in the same command.
            c.check("⛔ G2 · an auth path is `full` in a repo with NO map - the fallback is the "
                    "same GENERIC set scope_check uses, never an empty veto",
                    tp.ceremony_tier(repo, ["backend/middleware/auth.py"], **tiny) == "full",
                    tp.ceremony_tier(repo, ["backend/middleware/auth.py"], **tiny))
            surfaces(repo)                        # a map that declares NOTHING
            c.check("⛔ G2 · …and a map declaring no paths is WEAKER than no map, so it must not "
                    "be quieter - still `full`",
                    tp.ceremony_tier(repo, ["backend/middleware/auth.py"], **tiny) == "full",
                    tp.ceremony_tier(repo, ["backend/middleware/auth.py"], **tiny))
            c.check("G2 · CONTROL: an ordinary file in an unmapped repo is still tiny",
                    tp.ceremony_tier(repo, ["frontend/src/lib/fmt.ts"], **tiny) == "tiny",
                    tp.ceremony_tier(repo, ["frontend/src/lib/fmt.ts"], **tiny))

    # ── G3 ────────────────────────────────────────────────────────────────────────────────
    if c.block("G3 · the declaration's shape check is SEMANTIC, not a spelling blacklist"):
        with TempDir() as t:
            repo = bare(t)
            # The bypass: a literal-prefix test on `*.` is trivially spelled around, and
            # PurePosixPath.match is fnmatch-based, so `?*.md` matches every .md with a
            # one-or-more-character stem - including the runtime-loaded knowledge docs.
            for g in ("?*.md", "*[.]md", "[a-z]*.md", "?*", "*?", "*.md", "**/*.md", "*", "**"):
                declare(repo, g)
                c.check(f"⛔ G3 · `{g}` is refused - it carves out by EXTENSION, which takes the "
                        f"runtime-loaded docs with it",
                        tp.load_inert(repo) == (), f"{g} -> {tp.load_inert(repo)}")
            # …and the false refusal the spelling check also caused: a SCOPED extension glob is
            # safe and must load. `docs/*.md` cannot reach a knowledge folder.
            for g in ("docs/*.md", "frontend/docs/*.md"):
                declare(repo, g)
                c.check(f"G3 · `{g}` is SCOPED and loads - the check must not refuse a glob that "
                        f"cannot reach a runtime doc",
                        tp.load_inert(repo) == (g,), f"{g} -> {tp.load_inert(repo)}")
            declare(repo, "/INDEX.md")
            c.check("⛔ G3 · a leading-slash glob is refused - it loads clean and matches NOTHING, "
                    "which is a dead row reading as a live guard",
                    tp.load_inert(repo) == (), repr(tp.load_inert(repo)))

    # ── H ─────────────────────────────────────────────────────────────────────────────────
    if c.block("H · an entry point with reach 0 is NEVER tiny"):
        with TempDir() as t:
            repo = bare(t)
            surfaces(repo)
            for p in ("frontend/src/app/layout.tsx",
                      "frontend/src/app/dashboard/page.tsx",
                      "backend/main.py"):
                c.check(f"⛔ H · {p} is an entry point — 3 lines, still full",
                        tp.ceremony_tier(repo, [p], lines=3, structural=False) == "full",
                        tp.ceremony_tier(repo, [p], lines=3, structural=False))
            c.check("⛔ H · without line evidence `tiny` is UNREACHABLE — a tier is never "
                    "lowered on an assumption",
                    tp.ceremony_tier(repo, ["frontend/src/lib/fmt.ts"]) == "quick",
                    tp.ceremony_tier(repo, ["frontend/src/lib/fmt.ts"]))
            c.check("H · a structural change (add/delete/rename) is never tiny either",
                    tp.ceremony_tier(repo, ["frontend/src/lib/fmt.ts"],
                                     lines=3, structural=True) == "quick",
                    tp.ceremony_tier(repo, ["frontend/src/lib/fmt.ts"],
                                     lines=3, structural=True))
            # ⛔ THE APP-ROUTER SHAPES A FIXED-DEPTH GLOB LIST CANNOT REACH. `PurePosixPath.match`
            # is right-anchored on WHOLE COMPONENTS, so every glob pins an exact segment count -
            # and the App Router puts route handlers at `app/api/<name>/route.ts` or deeper,
            # layouts inside `(route groups)`, and pages under `[dynamic]` segments. Each one
            # came back `tiny`: "the plan is two sentences and the walkthrough is three", for an
            # API route handler.
            for p in ("frontend/src/app/api/chat/route.ts",
                      "frontend/src/app/api/v1/chat/route.ts",
                      "frontend/src/app/(app)/dashboard/layout.tsx",
                      "frontend/src/app/(marketing)/blog/[slug]/page.tsx",
                      "frontend/src/app/dashboard/page.jsx",
                      "frontend/src/app/deeply/nested/route/page.tsx"):
                c.check(f"⛔ H · {p} is an entry point at ANY depth",
                        tp.ceremony_tier(repo, [p], lines=3, structural=False) == "full",
                        tp.ceremony_tier(repo, [p], lines=3, structural=False))
            c.check("H · CONTROL: a file merely NAMED like one is not an entry point",
                    tp.ceremony_tier(repo, ["frontend/src/lib/page.helper.ts"],
                                     lines=3, structural=False) == "tiny",
                    tp.ceremony_tier(repo, ["frontend/src/lib/page.helper.ts"],
                                     lines=3, structural=False))
            c.check("⛔ H · …and a `page.tsx` OUTSIDE an app/ tree is not an entry point either",
                    tp.ceremony_tier(repo, ["frontend/src/components/page.tsx"],
                                     lines=3, structural=False) == "tiny",
                    tp.ceremony_tier(repo, ["frontend/src/components/page.tsx"],
                                     lines=3, structural=False))
            # ⛔ THE FILE CAP COUNTED THE WRONG LIST. It counted `ships` - the DEPLOY_DIRS
            # survivors - so outside the product dirs it was permanently 0 and the 5-file rule
            # was dead. In the command centre that is EVERY diff: 40 files at 10 lines read
            # `tiny`. It counts the non-inert paths now, which is what "how big is this change"
            # actually means.
            many = [f".agents/rules/probe_{i}.md" for i in range(40)]
            c.check("⛔ H · 40 non-inert files at 10 lines is NOT tiny - the file cap counts the "
                    "non-inert paths, never the deployable ones",
                    tp.ceremony_tier(repo, many, lines=10, structural=False) == "quick",
                    tp.ceremony_tier(repo, many, lines=10, structural=False))
            c.check("H · CONTROL: five non-inert files at 10 lines is still tiny",
                    tp.ceremony_tier(repo, many[:5], lines=10, structural=False) == "tiny",
                    tp.ceremony_tier(repo, many[:5], lines=10, structural=False))
            c.check("H · …and six is not (the cap is 5)",
                    tp.ceremony_tier(repo, many[:6], lines=10, structural=False) == "quick",
                    tp.ceremony_tier(repo, many[:6], lines=10, structural=False))

    # ── I ─────────────────────────────────────────────────────────────────────────────────
    if c.block("I · the doors CALL the seams; nobody re-implements the threshold"):
        for name in DOORS:
            b = body(name)
            c.check(f"I · {name} calls deployable_paths",
                    "deployable_paths" in b, "not found in the body")
        for name in ("cicd-quick-dev", "smh-quick-dev"):
            b = body(name)
            c.check(f"I · {name} calls ceremony_tier",
                    "ceremony_tier" in b, "not found in the body")
            c.check(f"I · {name} calls all_inert and gates the short-circuit on `all-inert:`",
                    "all_inert" in b and "all-inert:" in b,
                    f"all_inert={'all_inert' in b} label={'all-inert:' in b}")
            # ⛔ THE MUTANT THIS BLOCKS. The first draft of both doors read an empty `ships:` as
            # the short-circuit; in the lobby nothing ever ships, so a rule edit skipped the
            # plan and the TDD. A body that still tells the reader to gate on `ships:` being
            # empty has the hole back, whatever it computes.
            c.check(f"⛔ I · {name} does NOT gate the short-circuit on an empty `ships:`",
                    "`ships:` empty" not in b, "the body still reads 'ships: empty' as all-inert")
        for name in DOORS:
            b = body(name)
            c.check(f"⛔ I · {name} does not re-type the prefix list as a startswith test",
                    "startswith(PRODUCT_DIRS" not in b,
                    "the body still re-implements the prefix test")
        c.check("I · the seam names exist on the module, so the doors' import cannot go stale",
                all(hasattr(tp, n) for n in
                    ("load_inert", "inert_paths", "deployable_paths", "ceremony_tier")),
                repr([n for n in ("load_inert", "inert_paths", "deployable_paths",
                                  "ceremony_tier") if not hasattr(tp, n)]))

    # ── J · MUTANTS THAT SURVIVED THE SUITE AT b01dbe25 ───────────────────────────────────
    # The Test-Adequacy lens ran 45 hand-written mutants against this file. These three lived:
    # the suite passed with the code deliberately broken, which means nothing here was asking
    # the question. Each pin below was seen RED against its own mutant before being kept.
    if c.block("J · the boundary, the empty glob, and the declared map - three surviving mutants"):
        with TempDir() as t:
            repo = bare(t)
            surfaces(repo, "backend/middleware/auth.py")

            # ⛔ R3 · `lines <= TINY_MAX_LINES` -> `<` SURVIVED. Every existing pin used 3 lines
            # or 40+, so the boundary itself was never touched. A threshold nobody tests AT the
            # threshold is a number, not a rule.
            at = tp.TINY_MAX_LINES
            c.check(f"⛔ J · exactly TINY_MAX_LINES ({at}) is still `tiny` - the comparison is "
                    f"`<=`, and an off-by-one here silently narrows every quick lane",
                    tp.ceremony_tier(repo, ["frontend/src/lib/fmt.ts"],
                                     lines=at, structural=False) == "tiny",
                    tp.ceremony_tier(repo, ["frontend/src/lib/fmt.ts"],
                                     lines=at, structural=False))
            c.check(f"J · …and one line over ({at + 1}) is `quick`, so the pin above cannot pass "
                    f"by the threshold being ignored",
                    tp.ceremony_tier(repo, ["frontend/src/lib/fmt.ts"],
                                     lines=at + 1, structural=False) == "quick",
                    tp.ceremony_tier(repo, ["frontend/src/lib/fmt.ts"],
                                     lines=at + 1, structural=False))

        # ⛔ N2 · dropping the `not g` clause SURVIVED. An empty glob is not exotic - it is what
        # a hand-edited declaration leaves behind, and `PurePosixPath(x).match("")` raises, so
        # the refusal is what stands between a stray comma and a crashing gate.
        with TempDir() as t:
            repo = bare(t)
            declare(repo, "INDEX.md", "")
            c.check("⛔ J · an EMPTY glob refuses the whole declaration - nothing is inert",
                    tp.load_inert(repo) == (), repr(tp.load_inert(repo)))
            c.check("J · …and the caller sees it: a path the good glob would have carved out "
                    "stays deployable while the declaration is broken",
                    tp.inert_paths(repo, ["frontend/scripts/INDEX.md"]) == [],
                    repr(tp.inert_paths(repo, ["frontend/scripts/INDEX.md"])))

        # ⛔ N9 · "declared rows ignored, GENERIC always" SURVIVED. Every veto pin used a path
        # the GENERIC fallback ALSO matches (`auth`), so the repo's own map was never the thing
        # being read. A repo that declares a surface the house list has never heard of is the
        # only input that can tell the two apart.
        with TempDir() as t:
            repo = bare(t)
            own = "backend/ranking/weights.py"          # matches no GENERIC fragment
            surfaces(repo, own)
            c.check("⛔ J · a surface this repo DECLARED is an absolute veto even though the "
                    "GENERIC fallback has never heard of it",
                    tp.ceremony_tier(repo, [own], lines=3, structural=False) == "full",
                    tp.ceremony_tier(repo, [own], lines=3, structural=False))
            c.check("J · CONTROL: an undeclared sibling in the same folder is NOT vetoed, so "
                    "the check above is reading the map and not the folder",
                    tp.ceremony_tier(repo, ["backend/ranking/format.py"],
                                     lines=3, structural=False) == "tiny",
                    tp.ceremony_tier(repo, ["backend/ranking/format.py"],
                                     lines=3, structural=False))

    return c.finish()


if __name__ == "__main__":
    raise SystemExit(main())

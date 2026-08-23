#!/usr/bin/env python3
"""refresh_maps.py - keep the generated maps current WITHOUT a ceremony. (SCC-290)

THE PROBLEM. `docs/repo-map.md`'s AUTO block and `docs/doc-graph.*` are machine-generated, and
nothing regenerated them between manual runs of `/smh-update-maps-indexes`. So they were stale
almost always: measured 2026-08-22, the repo-map AUTO block disagreed with disk and the committed
doc-graph named a worktree that had been pruned weeks earlier. A map nobody can trust is worse
than no map -- it is read as current.

THE SPLIT, and it is the whole design. There are two layers in these files:

  GENERATED  the AUTO block, the node/edge lists.  A script owns it.  ->  THIS FILE, on every commit.
  CURATED    one-line purposes, INDEX prose, the pointers in AGENTS.md.  A person owns it.
             -> `/smh-update-maps-indexes`, still, because a hook cannot write prose.

This file owns the generated layer and makes the hand layer fail LOUD: once the machine half is
always current, a drift report is only ever about the half a human has to fix.

WHY A GIT HOOK AND NOT A CLAUDE HOOK. A Claude `Stop` hook fires in Claude Code only -- one of
four platforms, on one of two machines -- and it leaves a dirty tree the operator did not ask for.
A git hook fires for every platform and every tool that commits, and it stages what it wrote so
the commit is complete. The post-commit drift recorder already journals the same way.

  --staged   pre-commit. Regenerate what the staged set can have changed, write only on a real
             difference, and `git add` exactly those paths. Regeneration ONLY.
  --repair   by hand. The same write, with NO trigger gate: the remedy for a tree that is stale
             with an EMPTY index -- a merge commit, a `--no-verify` commit, or a clone whose
             hooks were never armed. `--verify` names this mode, because `--staged` cannot fix
             any of those three (nothing is staged, so nothing triggers).
  --truth    commit-msg. The two truth checks below, fatal, honouring `[maps-ok]` in the message.
  --verify   pre-push and `check_maps` check 10. Regenerate to memory, byte-compare with disk,
             name what differs, exit 1. This is what catches a merge commit and a `--no-verify`.

⛔ WHY THE TRUTH CHECKS SIT IN `commit-msg` AND NOT BESIDE THE REGENERATION. They need a recorded
escape hatch, and **pre-commit cannot see the commit message** — the same reason `sop-currency.sh`
lives there and says so in its own header. Found the hard way: the ratchet refused the very commit
that introduced it (52 -> 77) because that commit WIDENED THE GRAPH'S SCOPE, so the two numbers were
not measurements of the same thing. Any future root addition, or any change to the resolver, does
that again. `[maps-ok]` in the commit message is the auditable re-baseline — it stays in the log
forever, which is the design: a silent bypass teaches nothing, a recorded one is evidence.

THE TWO TRUTH CHECKS, both fatal under --truth:

  RATCHET        `broken_paths` in the doc graph may not EXCEED the count committed at HEAD. It
                 does not demand zero -- there are 75 today, mostly stale references in old guides
                 -- it demands that this commit not add one. New breakage is named with its source.
  REVERSE DOOR   every house door in `.agents/commands/` must be named as `/<name>` in the SOP.
                 Armed at zero misses because the SOP already names all of them; it fires the day
                 someone adds or renames a door and forgets the page the operator actually reads.

BYPASSES, all recorded: `[maps-ok]` in the commit message (the truth checks only, and it names
itself in the log forever), `git commit --no-verify` (everything, once), and
`.agents/scripts/git-hooks/DISABLE` (the kill switch every hook in this repo honours). `--verify` at
push, `check_maps` check 10 and `run_all.py` are the three that a bypass still has to get past.

SCOPE, and it is not the whole working tree: only files GIT'S INDEX HAS are mapped (`in_index`).
An untracked scratch `.md` is not part of the repository, so no committed map may name one -- and
until SCC-288 one did, which refused pushes of unrelated work and then wrote the phantom in when
the operator ran the printed remedy. A file `git add`ed a moment ago IS in the index and IS mapped.

ACCEPTED LIMIT, stated rather than hidden: the CONTENT read from each of those files is the working
tree's, not the index's, so an unstaged edit to a TRACKED file leaks into the staged map. The
alternative -- checking the index out to a temp dir -- costs seconds on every commit. `--verify` at
push and check 10 catch it.

Both machines: stdlib only, ASCII output, `sys.executable` never assumed. Run from anywhere.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
SCRIPTS = HERE.parent
sys.path.insert(0, str(SCRIPTS))

import check_maps as cm            # noqa: E402  (declared_mode / default_regen_ignore: ONE source)
import generate_doc_graph as dg    # noqa: E402
import generate_repo_map as grm    # noqa: E402

REPO_MAP = "docs/repo-map.md"
DOC_GRAPH_MD = "docs/doc-graph.md"
DOC_GRAPH_JSON = "docs/doc-graph.json"
SOP = "docs/_scc_sops_prds/workflows_testing_SOP.md"
COMMANDS = ".agents/commands"

# Doors the SOP is not expected to name: the index itself, the abandoned `-AP` twins, and the
# BMAD vendor set (installed by that tool, not authored here). Everything else is a HOUSE door and
# the operator's page must name it.
VENDOR_DOORS = {
    "analyst", "architect", "bmad-help", "bmad-master", "dev", "pm", "qa", "sm", "tea",
    "tech-writer", "ux-designer",
}


def sh(args, cwd, check=False):
    r = subprocess.run(args, cwd=str(cwd), capture_output=True, text=True)
    if check and r.returncode != 0:
        raise SystemExit(f"refresh-maps: `{' '.join(args)}` failed: {r.stderr.strip()[:200]}")
    return r


def repo_root(start=None):
    r = sh(["git", "rev-parse", "--show-toplevel"], start or Path.cwd())
    if r.returncode != 0 or not r.stdout.strip():
        return None
    return Path(r.stdout.strip()).resolve()


def disabled(root):
    """The kill switch every hook in this repo honours, checked at both spellings."""
    return ((root / ".agents" / "scripts" / "git-hooks" / "DISABLE").exists()
            or (root / "scripts" / "git-hooks" / "DISABLE").exists())


# --- what the staged set can have changed ------------------------------------------------------

def ignored_tops(root):
    """Top-level names the repo-map regen does not walk - so a commit touching only these can
    change nothing generated. Read from `check_maps`, never re-listed here: check 1 compares
    against exactly this set, and two copies of an ignore list drift into a map that fails its
    own linter."""
    is_home, is_bmad = cm.detect_mode(root)
    ign = set(grm.DEFAULT_IGNORES)
    ign.update(x.strip() for x in cm.default_regen_ignore(is_home, is_bmad).split(",") if x.strip())
    return ign


def staged_paths(root):
    r = sh(["git", "diff", "--cached", "--name-only"], root)
    return [p for p in r.stdout.splitlines() if p.strip()]


def triggered(paths, root):
    """Which artifacts the staged set can have invalidated: a subset of {repo-map, doc-graph}.

    ⛔ THE TWO ARTIFACTS HAVE DISJOINT, ALMOST OPPOSITE SCOPES, and conflating them is a hook that
    silently does nothing. `.agents` is IN the repo-map's own ignore set (`grm.DEFAULT_IGNORES`) --
    the map deliberately does not walk the toolkit -- while `.agents` is one of the doc graph's two
    ROOTS. Gating both on the repo-map's ignore set, as this function first did, meant a staged
    `.agents/rules/x.md` triggered nothing at all: the exact commit the hook exists for. Caught by
    RM-B, which is why that case asserts both artifacts by name rather than "something was staged".

    ⛔ AND THE REPO-MAP TRIGGER IS BROADER THAN THE PLAN'S FIRST DRAFT, deliberately. That draft
    said "a top-level entry was added or removed". This repo's map declares `mode=content`, so the
    AUTO block carries FUNCTION SIGNATURES: editing the body of any walked `.py` or `.ts` changes
    it with nothing added and nothing deleted. Under the narrow rule that commit leaves the map
    stale and the NEXT push is refused by --verify -- the failure landing on someone who changed
    nothing about maps. So the rule is what the regen actually walks.
    """
    ign = ignored_tops(root)
    want = set()
    for p in paths:
        top = p.split("/", 1)[0]
        if top not in ign:
            want.add("repo-map")
        if p.lower().endswith(".md") and top in dg.DEFAULT_ROOT_NAMES:
            want.add("doc-graph")
    return want


# --- regeneration, to memory --------------------------------------------------------------------

def in_index(root):
    """A predicate on an absolute path: does git's INDEX have this?  None if git cannot say.

    It answers for DIRECTORIES as well as files -- a directory is "had" when the index holds
    anything beneath it. `generate_repo_map.walk` needs that: pruning a directory on "it produced
    no visible lines" instead dropped two real tracked directories from the live map, because
    their only files are dotfiles the walk already hides.

    ⛔ REVIEW FINDING R1 (SCC-288). Both generators walk the FILESYSTEM, so an untracked scratch
    `.md` -- and this workflow makes those constantly -- became a graph node and ticked the
    repo-map's content-mode file count up. Two consequences, and the second is the worse one:
    `--verify` read the difference as a stale map and REFUSED THE PUSH of unrelated committed
    work, and the `--repair` it prints as the remedy then WROTE the phantom into a tracked
    artifact bound for `main`. The gate blocked correct work and its own fix corrupted the map.

    THE INDEX, not `HEAD`, and not "tracked": a file `git add`ed a moment ago IS part of the
    commit being made and both maps must pick it up. That is exactly what `--staged` exists for,
    so the rule is "git has it", which the index answers and `HEAD` does not.

    Returns None -- meaning DO NOT FILTER -- when git cannot answer. A generator that mapped
    nothing because a subprocess failed would hand `--repair` an empty tree to commit.
    """
    r = sh(["git", "ls-files", "--cached", "-z"], root)
    if r.returncode != 0:
        return None
    have = {(root / p).resolve() for p in r.stdout.split("\0") if p}
    if not have:
        return None                                   # an empty repo: nothing to filter against
    for f in list(have):
        have.update(f.parents)                        # every ancestor directory git implies
    return lambda full: Path(full).resolve() in have


def fresh_repo_map(root):
    """The repo-map with a freshly built AUTO block spliced in. None when there is no map."""
    path = root / REPO_MAP
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    if grm.AUTO_START not in text or grm.AUTO_END not in text:
        return None                                   # unscaffolded: the ceremony's job, not ours
    body = grm.build_auto_body(str(root), threshold=8,
                               mode=cm.declared_mode(text), ignores=ignored_tops(root),
                               keep=in_index(root))
    head = text.split(grm.AUTO_START, 1)[0]
    tail = text.split(grm.AUTO_END, 1)[1]
    return head + body + tail


def fresh_doc_graph(root):
    """(markdown, json) for the doc graph, or (None, None) where there is nothing to anchor."""
    roots = [root / n for n in dg.DEFAULT_ROOT_NAMES if (root / n).is_dir()]
    if not roots:
        return None, None
    graph = dg.build_graph(roots, set(dg.DEFAULT_IGNORES), root, exclude=[DOC_GRAPH_MD],
                           keep=in_index(root))
    md = dg.splice(str(root / DOC_GRAPH_MD), dg.render_auto(graph, 15))
    return md, json.dumps(graph, indent=2)


def regenerate(root, want):
    """{relative path: fresh text} for everything in `want`. Nothing is written here."""
    out = {}
    if "repo-map" in want:
        rm = fresh_repo_map(root)
        if rm is not None:
            out[REPO_MAP] = rm
    if "doc-graph" in want:
        md, js = fresh_doc_graph(root)
        if md is not None:
            out[DOC_GRAPH_MD] = md
            out[DOC_GRAPH_JSON] = js
    return out


def differs(root, rel, fresh):
    """True when disk does not already hold `fresh`. A missing file counts as different."""
    p = root / rel
    if not p.exists():
        return True
    return p.read_text(encoding="utf-8") != fresh


# --- the two truth checks ------------------------------------------------------------------------

def broken_at_head(root):
    """`broken_paths` recorded in the doc graph at HEAD; None when there is no baseline to ratchet
    against (a first commit, a repo with no graph yet). None means 'do not ratchet', never 'zero'."""
    r = sh(["git", "show", f"HEAD:{DOC_GRAPH_JSON}"], root)
    if r.returncode != 0 or not r.stdout.strip():
        return None
    try:
        return int(json.loads(r.stdout)["counts"]["broken_paths"])
    except (ValueError, KeyError, TypeError):
        return None


def ratchet(root, fresh_json):
    """Refuse a commit that ADDS a broken doc reference. Never demands zero (Decision 5).

    Names the new refs with their source file, because "broken_paths went 75 -> 76" is not
    actionable and a number nobody can act on gets bypassed.
    """
    if fresh_json is None:
        return []
    base = broken_at_head(root)
    if base is None:
        return []
    new = json.loads(fresh_json)
    now = int(new["counts"]["broken_paths"])
    if now <= base:
        return []
    old_raw = sh(["git", "show", f"HEAD:{DOC_GRAPH_JSON}"], root).stdout
    def broken_set(g):
        return {(d["from"], d["target"]) for d in g.get("dangling", [])
                if "/" in d["target"].strip("/")}
    added = sorted(broken_set(new) - broken_set(json.loads(old_raw)))
    lines = [f"broken doc references went {base} -> {now}. New ones:"]
    lines += [f"    {src}  ->  {tgt}" for src, tgt in added[:20]]
    if len(added) > 20:
        lines.append(f"    ... and {len(added) - 20} more (see {DOC_GRAPH_JSON})")
    return lines


def house_doors(root):
    """Every door the SOP must name: `.agents/commands/*.md` minus INDEX, the `-AP` twins, and the
    BMAD vendor set."""
    d = root / COMMANDS
    if not d.is_dir():
        return []
    out = []
    for f in sorted(d.glob("*.md")):
        name = f.stem
        if name == "INDEX" or name.endswith("-AP") or name in VENDOR_DOORS:
            continue
        if name.startswith("bmad-") or name.startswith("testarch-"):
            continue
        out.append(name)
    return out


def reverse_door_check(root):
    """Every house door is named as `/<name>` in the operator's SOP.

    ⛔ This is the check that runs the OTHER way round from every other one here. The rest ask "is
    the generated thing current with the tree". This asks "is the tree named in the page a human
    reads" -- and nothing else in this system asks that. It is armed at zero misses because the SOP
    already names all of them, so the first failure is real drift, never a backlog.

    Retiring a door means DELETING its file, and a deleted door cannot be un-named. A door renamed
    without an SOP edit is precisely the drift this exists to catch.
    """
    sop = root / SOP
    if not sop.exists():
        return []                                     # a project clone has no SOP to keep current
    text = sop.read_text(encoding="utf-8")
    missing = [n for n in house_doors(root)
               # ⛔ `(?![\w-])` alone lets a FILE PATH satisfy the check: `.agents/commands/x.md`
               # matches at the `/`, and `.` passes the lookahead. The SOP must name the DOOR
               # (`/x`), not merely mention the file, so `.md` is excluded explicitly.
               if not re.search(r"/" + re.escape(n) + r"(?![\w-]|\.md)", text)]
    if not missing:
        return []
    return [f"door(s) not named in {SOP}: " + ", ".join("/" + m for m in missing),
            "    the SOP is the page the operator reads to know what to type - add the row, "
            "or delete the door"]


# --- the two modes ---------------------------------------------------------------------------------

def _land(root, rel, text, wrote):
    """Write `rel` if it differs, then PROVE it by reading the file back. Returns False on a
    write that did not land (Port Check 3: verify the FILE, never the call's return value)."""
    if not differs(root, rel, text):
        return True
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    if p.read_text(encoding="utf-8") != text:
        print(f"  ! refresh-maps: {rel} did not land as written - commit refused")
        return False
    wrote.append(rel)
    return True


def run_staged(root):
    want = triggered(staged_paths(root), root)
    if not want:
        return 0
    return converge(root, want)


def run_repair(root):
    """Regenerate EVERYTHING and stage it, with no trigger gate. (SCC-290, found at close-out)

    ⛔ WHY THIS EXISTS AND `--staged` IS NOT ENOUGH. `--staged` asks "what can the STAGED set have
    changed?" and does nothing when the answer is nothing — which is right on a commit and wrong
    everywhere else. Three trees are stale with an EMPTY index, and `--staged` cannot touch any of
    them: a merge commit (`git merge` runs `pre-merge-commit`, never `pre-commit`), a
    `--no-verify` commit, and a clone whose `core.hooksPath` was never set. Those are the exact
    three `--verify` was built to catch, so `--verify` printing `--staged` as the remedy handed the
    operator a command that returns 0 and fixes nothing, leaving `--no-verify` as the only way
    past. A gate whose only escape is the bypass is a gate everybody bypasses.
    """
    return converge(root, {"repo-map", "doc-graph"})


def converge(root, want):
    """Write the wanted maps, in the one order that settles, and stage what actually changed."""
    # ⛔ ORDER IS LOAD-BEARING: THE DOC GRAPH FIRST, THE REPO-MAP AFTER IT LANDS.
    # `docs/doc-graph.md` and `.json` live under `docs/`, which the repo-map WALKS. A repo-map
    # built from the pre-write tree is therefore stale the instant those two files change, and the
    # next `--verify` refuses the push over a file this very hook just wrote. Building both from
    # one snapshot (the first draft) never converges. RM-C is the case that catches it.
    fresh, wrote = {}, []
    if "doc-graph" in want:
        md, js = fresh_doc_graph(root)
        if md is not None:
            fresh[DOC_GRAPH_MD], fresh[DOC_GRAPH_JSON] = md, js
            for rel in (DOC_GRAPH_MD, DOC_GRAPH_JSON):
                if not _land(root, rel, fresh[rel], wrote):
                    return 1
            # ⛔ STAGED HERE, NOT AT THE END, AND THAT IS PART OF THE SAME ORDER. The repo-map is
            # built from the files GIT'S INDEX HAS (`in_index`, SCC-288 / R1), and a doc-graph
            # this run has only written to disk is not in the index yet. Staging at the end left
            # the repo-map blind to two files it walks, so the commit landed a map that `--verify`
            # immediately called stale -- convergence lost on the very first generation.
            if not stage(root, wrote):
                return 1

    # Always after: a doc-graph write can itself have changed what the repo-map sees.
    # Compute it only when it can be used - a full tree walk plus a `git rev-parse` subprocess
    # on every commit is exactly the cost RM-A argues a hook must not pay to do nothing.
    rm = fresh_repo_map(root) if ("repo-map" in want or wrote) else None
    if rm is not None:
        fresh[REPO_MAP] = rm
        if not _land(root, REPO_MAP, rm, wrote):
            return 1
        if REPO_MAP in wrote and not stage(root, [REPO_MAP]):
            return 1

    for rel in sorted(wrote):
        print(f"  refresh-maps: regenerated and staged {rel}")
    return 0


def stage(root, rels):
    """`git add` exactly these paths. False on failure, having said why."""
    if not rels:
        return True
    r = sh(["git", "add", "--"] + sorted(rels), root)
    if r.returncode != 0:
        print(f"  ! refresh-maps: could not stage {sorted(rels)}: {r.stderr.strip()[:200]}")
        return False
    return True


OPT_OUT = "[maps-ok]"


def run_truth(root, msg_file):
    """The ratchet and the reverse door check, from `commit-msg`. `[maps-ok]` re-baselines."""
    message = ""
    if msg_file:
        try:
            message = Path(msg_file).read_text(encoding="utf-8", errors="replace")
        except OSError:
            return 0                                  # no message to read: nothing to judge
    # ⛔ A COMMENT LINE IS NOT A DECISION. `git commit` seeds the file with `# ...` help text, and a
    # template that merely MENTIONS the token would opt every commit out silently.
    body = "\n".join(ln for ln in message.splitlines() if not ln.lstrip().startswith("#"))
    if OPT_OUT in body:
        print(f"  refresh-maps: {OPT_OUT} - the truth checks are re-baselined by this commit, "
              "on the record.")
        return 0

    fresh = regenerate(root, {"doc-graph"})
    problems = ratchet(root, fresh.get(DOC_GRAPH_JSON)) + reverse_door_check(root)
    if not problems:
        return 0
    print("  ! refresh-maps: commit REFUSED")
    for line in problems:
        print("    " + line if not line.startswith("    ") else line)
    print(f"    re-baseline on the record: put {OPT_OUT} in the commit message (use this when the "
          "graph's SCOPE changed, not to wave a real broken link through)")
    print("    bypass everything once: git commit --no-verify | disable: "
          "touch .agents/scripts/git-hooks/DISABLE")
    return 1


def verify(root):
    """[stale relative paths]. Regenerates everything and byte-compares; writes nothing.

    The write-order caveat in `run_staged` does not apply here: nothing is written, so the
    repo-map is measured against the tree as it stands. If the doc graph is stale this reports
    THAT too, and the `--repair` run that fixes it re-derives the repo-map in the right order.
    """
    fresh = regenerate(root, {"repo-map", "doc-graph"})
    return [rel for rel, text in sorted(fresh.items()) if differs(root, rel, text)]


def run_verify(root):
    stale = verify(root)
    if not stale:
        return 0
    print("  ! refresh-maps: generated maps are STALE:")
    for rel in stale:
        print(f"      {rel}")
    print("    regenerate: python3 .agents/scripts/refresh_maps.py --repair   (PC: python)")
    print("    then commit them. A merge commit or a --no-verify commit is the usual cause -")
    print("    neither runs pre-commit, so --repair (no trigger gate) is the one that fixes it.")
    return 1


def main(argv=None):
    try:
        sys.stdout.reconfigure(errors="replace")      # PC console is cp1252; never crash a hook
    except Exception:                                 # noqa: BLE001 - a shim, not a feature
        pass
    ap = argparse.ArgumentParser(description="Regenerate and stage the centre's generated maps")
    ap.add_argument("--staged", action="store_true",
                    help="pre-commit: regenerate what the staged set changed and stage it")
    ap.add_argument("--truth", metavar="MSGFILE", nargs="?", const="", default=None,
                    help="commit-msg: the ratchet + the reverse door check; [maps-ok] opts out")
    ap.add_argument("--repair", action="store_true",
                    help="by hand: regenerate ALL the maps and stage them, with no trigger gate "
                         "- the remedy after a merge or a --no-verify commit")
    ap.add_argument("--verify", action="store_true",
                    help="pre-push / check 10: compare a fresh regen with disk, exit 1 if stale")
    ap.add_argument("--root", default=None, help="repo to act on (default: the git repo of CWD)")
    args = ap.parse_args(argv)
    modes = [args.staged, args.truth is not None, args.verify, args.repair]
    if sum(bool(m) for m in modes) != 1:
        ap.error("pass exactly one of --staged, --repair, --truth <msgfile> or --verify")

    root = Path(args.root).resolve() if args.root else repo_root()
    if root is None:
        return 0                                      # not a git repo: nothing to refresh
    if disabled(root):
        return 0
    if args.staged:
        return run_staged(root)
    if args.repair:
        return run_repair(root)
    if args.truth is not None:
        return run_truth(root, args.truth)
    return run_verify(root)


if __name__ == "__main__":
    sys.exit(main())

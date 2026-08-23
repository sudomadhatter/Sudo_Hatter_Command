"""generate_doc_graph.py — the centre's ONLY graph, and the one the operator asked for. (SCC-290)

The command centre carries no code graph (SCC-289): a code graph parses code, and this repo is
markdown. This is what maps it instead — a link graph over the docs.

WHAT THIS TICKET CHANGED, and why each half is load-bearing:

1. **A SECOND ROOT.** The graph scanned `.agents/` only, so `docs/` — the SOPs, the migration
   guides, and `workflows_testing_SOP.md`, the ONE document the operator ever asked to have
   mapped — was in no graph at all. It now scans `.agents/` AND `docs/`.

2. **LOBBY-RELATIVE IDS.** With two roots there is no single directory every node hangs off, so
   node ids are relative to the LOBBY (`.agents/rules/x.md`, `docs/_scc_sops_prds/y.md`). That
   also kills a whole class of false "dangling" ref: a rule linking `../../docs/x.md` used to
   escape the scanned root and resolve to nothing.

3. **NO ABSOLUTE PATH IN THE OUTPUT.** The committed `doc-graph.json` recorded
   `root: …/.claude/worktrees/SCC-270-code-review-graph-swap/.agents` — a worktree that no longer
   exists. Every regen from a different tree rewrote that line, so the file churned on every lane
   and its `root` was a lie the moment the tree was pruned. Relative roots make the artifact
   identical whoever regenerates it, which is also what lets the pre-commit hook stage it (B4)
   without every lane conflicting on it.

Determinism is not a nicety here — `refresh_maps.py --verify` compares a regen against the
committed bytes, so a generator whose output depends on cwd, root ORDER, or filesystem walk order
would refuse every push. Cases D, E and F are that contract.

Written RED first. Stdlib only, no pytest.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _harness import Cases, TempDir  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import generate_doc_graph as dg  # noqa: E402

REPO = Path(__file__).resolve().parents[3]
GEN = REPO / ".agents" / "scripts" / "generate_doc_graph.py"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture_lobby(tmp: Path) -> Path:
    """A minimal two-root lobby: `.agents/` and `docs/`, cross-linked BOTH ways.

    `.git` is a real directory here because the lobby default walks up looking for one — the same
    probe has to work in a worktree, where `.git` is a FILE, so case G drives that shape too.
    """
    lobby = tmp / "lobby"
    (lobby / ".git").mkdir(parents=True)
    write(lobby / ".agents" / "rules" / "a.md",
          "# a\n\nSee [x](../../docs/x.md) and the SOP at [sop](../../docs/sop/big.md).\n")
    write(lobby / ".agents" / "commands" / "cicd-foo.md", "# foo\n")
    write(lobby / "docs" / "x.md",
          "# x\n\nBack to [a](../.agents/rules/a.md), and the door `cicd-foo.md`.\n")
    write(lobby / "docs" / "sop" / "big.md",
          "# big\n\nNames [a](../../.agents/rules/a.md).\n")
    return lobby


def run_gen(lobby: Path, cwd: Path, extra: list[str] | None = None) -> tuple[int, str, str]:
    """Invoke the generator the way the hook will — a real argv, an explicit cwd."""
    argv = [sys.executable, str(GEN), "--lobby", str(lobby),
            "--root", str(lobby / ".agents"), "--root", str(lobby / "docs"),
            "--output", str(lobby / "docs" / "doc-graph.md"),
            "--json", str(lobby / "docs" / "doc-graph.json")]
    r = subprocess.run(argv + (extra or []), capture_output=True, text=True, cwd=str(cwd))
    return r.returncode, r.stdout, r.stderr


def graph_of(lobby: Path) -> dict:
    """The graph, or an empty dict when the generator wrote nothing.

    Tolerant on purpose: a generator that refuses the argv must fail its cases, not abort the
    file. An exception here reports as a crash and hides every later block.
    """
    f = lobby / "docs" / "doc-graph.json"
    if not f.exists():
        return {"nodes": [], "edges": [], "dangling": [], "counts": {"broken_paths": -1}}
    return json.loads(f.read_text(encoding="utf-8"))


def edge_set(graph: dict) -> set[tuple[str, str]]:
    return {(e["from"], e["to"]) for e in graph["edges"]}


def main() -> int:
    c = Cases("doc graph")

    # ── A · the second root, and links ACROSS the two of them ─────────────────────────────────
    # The defect: `.agents/rules/a.md` → `../../docs/x.md` escaped the single scanned root and was
    # recorded as dangling. 17 of the SOP's 38 flagged refs were this same false positive.
    if c.block("DG-A · SCC-290 · two roots, and cross-root links resolve BOTH ways"):
        with TempDir() as tmp:
            lobby = fixture_lobby(tmp)
            rc, out, err = run_gen(lobby, cwd=lobby)
            c.check("DG-A exit 0", rc == 0, f"rc={rc} err={err[-300:]}")
            g = graph_of(lobby)
            paths = {n["path"] for n in g["nodes"]}
            c.check("DG-A both roots are IN the graph, under lobby-relative ids",
                    {".agents/rules/a.md", "docs/x.md", "docs/sop/big.md"} <= paths,
                    f"nodes={sorted(paths)}")
            edges = edge_set(g)
            c.check("DG-A .agents → docs resolves (the `../../docs/x.md` shape)",
                    (".agents/rules/a.md", "docs/x.md") in edges, f"edges={sorted(edges)}")
            c.check("DG-A docs → .agents resolves (the return direction)",
                    ("docs/x.md", ".agents/rules/a.md") in edges, f"edges={sorted(edges)}")
            c.check("DG-A a nested docs page reaches back into .agents too",
                    ("docs/sop/big.md", ".agents/rules/a.md") in edges, f"edges={sorted(edges)}")
            c.check("DG-A and the deep cross-root target is not dangling",
                    (".agents/rules/a.md", "docs/sop/big.md") in edges,
                    f"dangling={g['dangling']}")
            c.check("DG-A ⛔ zero broken-path refs in a fixture where every link is real",
                    g["counts"]["broken_paths"] == 0, f"dangling={g['dangling']}")

    # ── B · the bare-basename fallback survives the move to two roots ─────────────────────────
    if c.block("DG-B · SCC-290 · a unique bare basename still resolves"):
        with TempDir() as tmp:
            lobby = fixture_lobby(tmp)
            run_gen(lobby, cwd=lobby)
            g = graph_of(lobby)
            c.check("DG-B `cicd-foo.md` named bare from docs/ finds the one command file",
                    ("docs/x.md", ".agents/commands/cicd-foo.md") in edge_set(g),
                    f"edges={sorted(edge_set(g))}")

    # ── C · no absolute path may reach the committed artifacts ────────────────────────────────
    # The committed json recorded a worktree that has since been pruned. An absolute root means
    # the file changes for every tree that regenerates it — which makes it unstageable by a hook
    # and unverifiable at push.
    if c.block("DG-C · SCC-290 · the artifacts carry RELATIVE roots, never an absolute path"):
        with TempDir() as tmp:
            lobby = fixture_lobby(tmp)
            run_gen(lobby, cwd=lobby)
            g = graph_of(lobby)
            c.check("DG-C `root` is the list of lobby-relative roots",
                    g.get("root") == [".agents", "docs"], f"root={g.get('root')!r}")
            raw_json = (lobby / "docs" / "doc-graph.json").read_text(encoding="utf-8")
            raw_md = (lobby / "docs" / "doc-graph.md").read_text(encoding="utf-8")
            leak = str(lobby)
            c.check("DG-C the lobby's absolute path appears NOWHERE in the json",
                    leak not in raw_json,
                    f"leaked at {raw_json.find(leak)}: {raw_json[max(0, raw_json.find(leak) - 60):][:180]!r}")
            c.check("DG-C nor anywhere in the markdown (the `Scope:` line included)",
                    leak not in raw_md,
                    f"leaked at {raw_md.find(leak)}: {raw_md[max(0, raw_md.find(leak) - 60):][:180]!r}")
            c.check("DG-C the Scope line names both roots",
                    ".agents" in raw_md and "docs" in raw_md.split("**Scope:**", 1)[-1][:200],
                    raw_md.split("**Scope:**", 1)[-1][:200])

    # ── D · determinism: same tree, twice, byte-identical ─────────────────────────────────────
    # `refresh_maps.py --verify` regenerates and byte-compares against the committed file. A
    # generator that is not deterministic refuses every push, so this is a hard contract.
    if c.block("DG-D · SCC-290 · two runs produce byte-identical artifacts"):
        with TempDir() as tmp:
            lobby = fixture_lobby(tmp)
            run_gen(lobby, cwd=lobby)
            if not (lobby / "docs" / "doc-graph.json").exists():
                c.check("DG-D the generator produced no artifacts to compare", False,
                        "run_gen wrote nothing")
                return c.finish()
            first = ((lobby / "docs" / "doc-graph.md").read_bytes(),
                     (lobby / "docs" / "doc-graph.json").read_bytes())
            run_gen(lobby, cwd=lobby)
            second = ((lobby / "docs" / "doc-graph.md").read_bytes(),
                      (lobby / "docs" / "doc-graph.json").read_bytes())
            c.check("DG-D the markdown is byte-identical", first[0] == second[0],
                    f"{len(first[0])} vs {len(second[0])} bytes")
            c.check("DG-D the json is byte-identical", first[1] == second[1],
                    f"{len(first[1])} vs {len(second[1])} bytes")

    # ── E · cwd-independence. The hook runs at the repo root; a human runs it from anywhere. ──
    if c.block("DG-E · SCC-290 · the output does not depend on the cwd it was run from"):
        with TempDir() as tmp:
            lobby = fixture_lobby(tmp)
            run_gen(lobby, cwd=lobby)
            from_lobby = (lobby / "docs" / "doc-graph.json").read_bytes()
            elsewhere = tmp / "somewhere" / "else"
            elsewhere.mkdir(parents=True)
            run_gen(lobby, cwd=elsewhere)
            c.check("DG-E identical bytes from an unrelated cwd",
                    (lobby / "docs" / "doc-graph.json").read_bytes() == from_lobby,
                    "the generator resolved something against the process cwd")

    # ── F · root ORDER cannot change the artifact ─────────────────────────────────────────────
    # Two lanes regenerating the same tree must produce the same bytes even if one of them typed
    # the roots the other way round; otherwise the hook stages a spurious diff.
    if c.block("DG-F · SCC-290 · --root order does not change the output"):
        with TempDir() as tmp:
            lobby = fixture_lobby(tmp)
            run_gen(lobby, cwd=lobby)
            forward = (lobby / "docs" / "doc-graph.json").read_bytes()
            argv = [sys.executable, str(GEN), "--lobby", str(lobby),
                    "--root", str(lobby / "docs"), "--root", str(lobby / ".agents"),
                    "--output", str(lobby / "docs" / "doc-graph.md"),
                    "--json", str(lobby / "docs" / "doc-graph.json")]
            subprocess.run(argv, capture_output=True, text=True, cwd=str(lobby))
            c.check("DG-F reversed --root order, identical bytes",
                    (lobby / "docs" / "doc-graph.json").read_bytes() == forward,
                    "node/edge ordering leaked the argv order into the artifact")

    # ── G · the lobby default: a .git DIRECTORY and a .git FILE (a worktree) both work ────────
    # `.claude/worktrees/<slug>/.git` is a FILE. A probe that only accepts a directory anchors the
    # graph at the wrong place in exactly the trees this system does its work in.
    if c.block("DG-G · SCC-290 · the lobby is found with no --lobby, in a repo AND in a worktree"):
        for label, make_git in (("a .git directory", lambda p: (p / ".git").mkdir()),
                                ("a .git FILE (worktree)",
                                 lambda p: (p / ".git").write_text("gitdir: /elsewhere\n",
                                                                   encoding="utf-8"))):
            with TempDir() as tmp:
                lobby = tmp / "lobby"
                (lobby / ".agents" / "rules").mkdir(parents=True)
                (lobby / "docs").mkdir(parents=True)
                make_git(lobby)
                write(lobby / ".agents" / "rules" / "a.md", "# a\n\n[x](../../docs/x.md)\n")
                write(lobby / "docs" / "x.md", "# x\n")
                r = subprocess.run(
                    [sys.executable, str(GEN),
                     "--root", str(lobby / ".agents"), "--root", str(lobby / "docs"),
                     "--output", str(lobby / "docs" / "doc-graph.md"),
                     "--json", str(lobby / "docs" / "doc-graph.json")],
                    capture_output=True, text=True, cwd=str(tmp))
                ok = r.returncode == 0 and (lobby / "docs" / "doc-graph.json").exists()
                g = graph_of(lobby) if ok else {}
                c.check(f"DG-G {label}: the lobby is inferred and roots are relative",
                        ok and g.get("root") == [".agents", "docs"],
                        f"rc={r.returncode} root={g.get('root')!r} err={r.stderr[-200:]}")

    # ── H · the LIVE tree: the SOP is in the graph. This is the operator's actual ask. ────────
    # ── S · an UNINITIALIZED SUBMODULE is a blind spot, not a broken link ────────────────
    # SCC-288 R9. `git worktree add` does NOT initialize submodules, so every lane in this system
    # works in a tree where `Projects/*` is an empty directory. The generator probed those targets
    # with a plain `is_file()`, got False, and called them dangling - so the SAME commit counted
    # 74 broken refs from the main checkout and 77 from a worktree, and the commit-msg ratchet
    # refused every worktree commit. The prior lane papered over it with `[maps-ok]`, which
    # re-baselines a number that was never real.
    #
    # A repo does NOT assert that a file inside an uninitialized submodule is missing. It asserts
    # it cannot see it. Those are different facts and only one of them is a broken link.
    def sub_fixture(tmp, initialized):
        lobby = fixture_lobby(tmp)
        write(lobby / ".gitmodules",
              '[submodule "Projects/Sub"]\n\tpath = Projects/Sub\n'
              '\turl = https://example.com/sub.git\n')
        if initialized:
            write(lobby / "Projects" / "Sub" / ".git", "gitdir: ../../.git/modules/Sub\n")
            write(lobby / "Projects" / "Sub" / "docs" / "thing.md", "# thing\n")
        else:
            (lobby / "Projects" / "Sub").mkdir(parents=True, exist_ok=True)
        write(lobby / ".agents" / "rules" / "sub.md",
              "# sub\n\nInto the submodule: [thing](../../Projects/Sub/docs/thing.md).\n"
              "Not a submodule at all: [gone](../../Projects/NotASub/docs/gone.md).\n")
        return lobby

    if c.block("DG-S · SCC-288 · an uninitialized submodule is BLIND, not broken"):
        with TempDir() as tmp:
            lobby = sub_fixture(tmp, initialized=False)
            rc, out, err = run_gen(lobby, cwd=lobby)
            c.check("DG-S exit 0", rc == 0, f"rc={rc} err={err[-300:]}")
            g = graph_of(lobby)
            unres = {u["target"] for u in g.get("unresolvable", [])}
            dang = {d["target"] for d in g["dangling"]}
            c.check("DG-S ⛔ the ref into the EMPTY submodule is not counted broken",
                    "../../Projects/Sub/docs/thing.md" not in dang, f"dangling={sorted(dang)}")
            c.check("DG-S and it is REPORTED as unresolvable, not silently dropped",
                    any("Projects/Sub" in u for u in unres), f"unresolvable={sorted(unres)}")
            c.check("DG-S ⭐ negative control: a path under a dir that is NOT a declared "
                    "submodule is still broken",
                    any("NotASub" in d for d in dang), f"dangling={sorted(dang)}")
            blind_broken = g["counts"]["broken_paths"]
            blind_unres = g["counts"]["unresolvable"]

        with TempDir() as tmp:
            lobby = sub_fixture(tmp, initialized=True)
            rc, out, err = run_gen(lobby, cwd=lobby)
            c.check("DG-S exit 0 (initialized)", rc == 0, f"rc={rc} err={err[-300:]}")
            g2 = graph_of(lobby)
            c.check("DG-S ⭐⛔ THE INVARIANT THE RATCHET NEEDS: broken_paths is the SAME "
                    "whether the submodule is checked out or not",
                    g2["counts"]["broken_paths"] == blind_broken,
                    f"initialized={g2['counts']['broken_paths']} blind={blind_broken}")
            # ⛔ AND the classification itself must match, not just the total. Excusing only the
            # UNINITIALIZED ones passes the line above while still moving refs between buckets as
            # the checkout state changes - measured on the live repo as main=74 / worktree=71.
            c.check("DG-S ⭐⛔ and so is the unresolvable count - a CHECKED-OUT submodule is "
                    "still not the lobby's to adjudicate",
                    g2["counts"]["unresolvable"] == blind_unres,
                    f"initialized={g2['counts']['unresolvable']} blind={blind_unres}")
            c.check("DG-S a real file inside a checked-out submodule is NOT an `external` edge",
                    not any("Projects/Sub" in e["target"] for e in g2.get("external", [])),
                    f"external={g2.get('external')}")

    if c.block("DG-H · SCC-290 · the live graph contains the SOP and the docs/ tree"):
        live = REPO / "docs" / "doc-graph.json"
        if not live.exists():
            c.check("DG-H SKIPPED — no committed doc-graph.json in this tree", True, str(live))
        else:
            g = json.loads(live.read_text(encoding="utf-8"))
            paths = {n["path"] for n in g["nodes"]}
            sop = "docs/_scc_sops_prds/workflows_testing_SOP.md"
            c.check("DG-H the committed graph declares BOTH roots, relatively",
                    g.get("root") == [".agents", "docs"], f"root={g.get('root')!r}")
            c.check("DG-H ⭐ the SOP is a node — the one document the operator asked to map",
                    sop in paths,
                    f"{len(paths)} nodes; docs/ nodes = "
                    f"{sum(1 for p in paths if p.startswith('docs/'))}")
            c.check("DG-H the SOP is REFERENCED by something (in-degree > 0)",
                    any(n["path"] == sop and n["in"] > 0 for n in g["nodes"]),
                    str([n for n in g["nodes"] if n["path"] == sop]))
            c.check("DG-H .agents/ nodes survived the move to two roots",
                    sum(1 for p in paths if p.startswith(".agents/")) > 100,
                    f"{sum(1 for p in paths if p.startswith('.agents/'))} .agents nodes")

    # ── I · mermaid labels are not paths, and code fences still are ──────────────────────────
    # A mermaid label breaks lines with a literal `\n` inside a quoted string, and clean_target
    # turns every backslash into a slash — so one diagram node emitted three broken-path refs
    # naming files nobody ever wrote. The SOP carries 45 diagrams. Measured: 80 -> 75 repo-wide
    # broken paths, and ZERO edges lost.
    if c.block("DG-I · SCC-290 · mermaid labels are stripped; real code-fence refs are NOT"):
        with TempDir() as tmp:
            lobby = fixture_lobby(tmp)
            write(lobby / "docs" / "diag.md",
                  "# diag\n\n```mermaid\nflowchart TD\n"
                  '  D["docs/\\nAGENTS.md (law) + adapters\\nworkspace-standard.md"]\n'
                  "```\n\nAnd a real one in a shell block:\n\n"
                  "```bash\ngit add -- docs/x.md\n```\n")
            run_gen(lobby, cwd=lobby)
            g = graph_of(lobby)
            bad = [d["target"] for d in g["dangling"] if d["from"] == "docs/diag.md"]
            c.check("DG-I the mermaid label emits NO path refs",
                    not any("/n" in t for t in bad), f"dangling from diag.md: {bad}")
            c.check("DG-I ⛔ a code fence's real reference SURVIVES (the strip is mermaid-only)",
                    ("docs/diag.md", "docs/x.md") in edge_set(g),
                    f"edges from diag.md = "
                    f"{[e for e in edge_set(g) if e[0] == 'docs/diag.md']}")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())

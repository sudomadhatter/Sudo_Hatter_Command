"""The review engine's negative-control fixture (SCC-129) — INTACTNESS, and nothing more.

  ── ⛔ WHAT THIS FILE ASSERTS, AND WHAT IT DELIBERATELY DOES NOT ────────────────────────────
It asserts the seeded fixture under `fixtures/nc_review_engine/` is still **intact**: every
seeded defect is literally present in `bad.diff`, the clean control carries none of them, both
diffs still apply to the committed base, and the manifest still maps exactly one defect onto each
of the engine's five lenses.

**It never asserts that an LLM found anything, and the name says `fixture` for that reason.**
It cannot: the engine is five markdown files executed by a model
(`.agents/skills/code-review-engine/`), while this suite is stdlib-only, deterministic and
LLM-free — nothing in `.agents/scripts/` computes a verdict, a severity or a floor. A test here
called "the engine rejects the bad diff" would be a claim its own code could not make.

So SCC-129 is split in half, and both halves are real:

| Half | Proves | Runs |
|---|---|---|
| **mechanical** (this file) | the control is still armed — nobody has quietly neutered it | every `run_all.py`, forever |
| **live** (`fixtures/nc_review_engine/README.md`) | the engine actually rejects `bad.diff` and passes `clean.diff` | at a review gate, evidence pasted into that lane's walkthrough |

The two are not redundant. A live run proves the engine worked **once**; it cannot stop someone
deleting the seeded defect a year from now, and a recorded transcript asserted as a test would rot
into characterization. This file is the half that keeps the control from dying silently — which is
the way this kind of control actually dies. It is the padlock, not the inspection.

  ── WHY THE CHECKS ARE SHAPED THIS WAY ─────────────────────────────────────────────────────
1. **Bytes and wiring, never prose.** Every check binds a manifest field to the diff text it
   governs (marker → added lines, lens → the five-lens set, `expected_severity` → step-03's four
   levels). No engine sentence is pinned anywhere here. SCC-125 F3 proved the other way round:
   guards that matched the DESCRIPTION of a rule let a file mutated to the exact opposite meaning
   score 323/323. `README.md` is held to existence and non-emptiness ONLY, on purpose — pinning
   its prose would re-buy that exact defect.
2. **Every check that could be vacuous ships a counter-example** — not every check, and the
   distinction is the honest one: a structural row like "this file exists" cannot be vacuous, so
   proving it can fail would be theatre. The rows that CAN quietly stop meaning anything all
   carry one: the five marker self-proofs, the `git apply --check` corruption probe, the `parse`
   arity mutation, and the assertion predicate against an independently-written stub. A check
   that cannot fail is a finding (`tests-must-gate-for-real`), and this file's whole subject is a
   control that must be able to fail — ⚠ **which it got wrong once, here, and shipped:** the
   assertion counter-example originally gutted its own input by dropping assertion-bearing lines
   and then asserted none remained. Empty by construction. Two independent lenses caught it.
3. **Non-empty is asserted BEFORE anything quantified.** Every per-defect loop below is vacuously
   true over an empty list — `all()` over an empty set is `True`, the exact form that once let a
   case pass against a gutted detector. The defect list is proven non-empty first, and every
   marker is proven non-empty before it is counted.
4. **Every red names the `NC_` id and the remedy.** The first person to see one of these fail is
   whoever edits the fixture months from now, and a refusal they cannot act on gets reverted
   blind or `--no-verify`d. Same principle as the resurrection lint naming its replacement.

Stdlib only, no pytest — same constraint as every sibling here. Nothing under `fixtures/` is ever
executed or imported: `run_all.py` globs `test_*.py` non-recursively in this directory only.
"""
from __future__ import annotations

import ast
import json
import re
import subprocess
from pathlib import Path

from _harness import Cases, TempDir

ROOT = Path(__file__).resolve().parents[3]
FIX = Path(__file__).resolve().parent / "fixtures" / "nc_review_engine"

# Where the fixture's own diffs are allowed to point. A fixture diff naming a path outside this
# prefix could be applied for real against live repo files, so it is a checked safety property.
FIX_PREFIX = ".agents/scripts/tests/fixtures/nc_review_engine/"

MANIFEST, BAD, CLEAN, SPEC, README = "manifest.json", "bad.diff", "clean.diff", "spec.md", "README.md"
# ONE SPEC PER CHANGE. A single spec covering both diffs made the Acceptance Auditor correctly
# report every section the diff in front of it did not implement — noise on the bad diff, fatal on
# the clean control, where three "missing implementation" findings would have measured the
# fixture's spec-scoping instead of the engine. Found by the live control, on its first run.
CLEAN_SPEC = "spec-refunds.md"
# The live half's run log. README.md's escalation rule ("the same defect missed on two
# consecutive runs means redesign it") needs somewhere to compute "consecutive" FROM — without
# it the rule is unenforceable prose, and "this control has not been run in eight lanes" is
# invisible. Evidence still lives in each lane's walkthrough; this is the index into them.
RUNS = "live_runs.jsonl"
BASE_FILES = ("codebase/billing.py", "codebase/helpers.py")
REQUIRED = (MANIFEST, BAD, CLEAN, SPEC, CLEAN_SPEC, README, RUNS) + BASE_FILES

# step-01's five lenses. One seeded defect each, so the live control also proves each lens is
# ALIVE — a lens that silently stopped working is otherwise invisible.
LENSES = frozenset({"blind", "edge", "literal", "acceptance", "test-adequacy"})

# step-03 §2 normalizes every reviewer vocabulary into exactly these four. A manifest declaring
# anything else makes the live control's pass criterion unreadable against step-03's floor table.
SEVERITIES = frozenset({"critical", "important", "suggestion", "nitpick"})

REMEDY = ("restore the marker line verbatim, or redesign the defect and update manifest.json "
          "in the SAME commit — never delete one half")


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8-sig", errors="replace")


def added(diff_text: str) -> str:
    """The ADDED lines of a unified diff, '+' stripped, joined.

    Added lines only: a marker matched anywhere in the raw diff would also match it in a REMOVED
    line or a context line, so deleting the seeded defect would leave the guard green.
    """
    return "\n".join(ln[1:] for ln in diff_text.splitlines()
                     if ln.startswith("+") and not ln.startswith("+++"))


def added_by_file(diff_text: str) -> dict[str, str]:
    """Added lines, grouped by the file they belong to.

    Needed because a whole-diff scan cannot answer a per-file question: "does the clean control's
    TEST file assert anything" is not the same as "does any added line in the diff contain the
    word assert". Gut the test body to `pass`, leave one comment saying "no assert needed" in the
    other file, and an unscoped check stays green — the comment-literal inversion this repo
    already has a memory for.
    """
    out: dict[str, list[str]] = {}
    cur: str | None = None
    for ln in diff_text.splitlines():
        if ln.startswith("+++"):
            m = re.match(r"^\+\+\+ [ab]/(.+)$", ln)
            cur = m.group(1).strip() if m else None       # `+++ /dev/null` -> no file
            if cur:
                out.setdefault(cur, [])
            continue
        if cur is not None and ln.startswith("+"):
            out[cur].append(ln[1:])
    return {k: "\n".join(v) for k, v in out.items()}


def diff_paths(diff_text: str) -> list[str]:
    """Every repo-relative path a unified diff touches, from its ---/+++ headers.

    `/dev/null` carries no `a/`|`b/` prefix and so drops out here, which is what makes a
    file-creation hunk readable as "this diff adds a file" rather than as a path.
    """
    out = []
    for ln in diff_text.splitlines():
        m = re.match(r"^(?:\+\+\+|---) [ab]/(.+)$", ln)
        if m:
            out.append(m.group(1).strip())
    return out


def is_test_path(path: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    return name.startswith("test_") or name.endswith("_test.py")


def has_assertion(text: str) -> bool:
    """Does this test source actually assert anything?

    Factored out so the counter-example can feed it an INDEPENDENTLY-WRITTEN stub instead of a
    mutation of its own input. The first version of this proof gutted the real text by dropping
    assertion-bearing lines and then checked no assertion-bearing lines remained — empty by
    construction, so the row was a tautology that reduced to the check above it. A check whose
    counter-example is the De Morgan complement of the check proves nothing.
    """
    return any("assert" in ln or "raise AssertionError" in ln for ln in text.splitlines())


# An independently-written stub with the shape of a gutted specimen: a test in name only.
# `has_assertion` must return False for it, or the check above cannot detect the real thing.
GUTTED_STUB = "def test_refund_reduces_the_paid_total() -> None:\n    pass\n"


def lens_rows(step01: str) -> set[str]:
    """The lens names step-01's fan-out table actually routes.

    LENSES below is otherwise a local literal, and the set-equality check is one-directional:
    a sixth defect in the manifest goes red, but a sixth lens added to the ENGINE leaves the
    fixture at five with every case green — silently retiring the fixture's whole reason for
    existing (one defect per lens, so a live run proves each lens is alive). SCC-126 added the
    fifth lens days before this fixture was written, so a sixth is the demonstrated pattern.
    """
    body = step01.split("## The lenses", 1)[-1].split("\n## ", 1)[0]
    return {m.group(1).strip() for m in re.finditer(r"^\|\s*\*\*(.+?)\*\*\s*\|", body, re.M)}


def flat(text: str) -> str:
    """Whitespace-collapsed, for matching PROSE across the author's line wrapping.

    Used on spec text ONLY. A spec clause is prose, and where its author happened to wrap the
    line is not part of the rule — pinning it byte-exact makes the guard fail on a reflow that
    changed nothing. Diff markers are deliberately NOT matched this way: those pin code, where
    a line break is a real difference.
    """
    return " ".join(text.split())


def parse_arity(src: str) -> tuple[bool, str]:
    """Is `helpers.parse` still the one-parameter function NC_LITERAL depends on?

    `bad.diff` calls `helpers.parse(raw, strict=True)`. That is a defect ONLY while the real
    definition takes one argument — add a `strict` parameter and the call binds cleanly, the
    seeded defect evaporates, and every other check in this file stays green: the marker is
    still in the diff, and neither diff touches `helpers.py` so `git apply --check` never reads
    it. `helpers.py` warns about this in prose, and prose is precisely what this file's own
    docstring says cannot gate.
    """
    try:
        tree = ast.parse(src)
    except SyntaxError as exc:
        return False, f"codebase/helpers.py does not parse: {exc}"
    fn = next((n for n in tree.body
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "parse"),
              None)
    if fn is None:
        return False, "no top-level `def parse` — NC_LITERAL has no definition left to violate"
    a = fn.args
    total = len(a.posonlyargs) + len(a.args) + len(a.kwonlyargs)
    if total == 1 and a.vararg is None and a.kwarg is None:
        return True, ""
    extra = ", ".join(x.arg for x in (*a.posonlyargs, *a.args, *a.kwonlyargs)[1:])
    return False, (f"`parse` now takes {total} parameter(s)"
                   + (f" ({extra})" if extra else "")
                   + (" plus **kwargs" if a.kwarg else "")
                   + " — if it accepts `strict`, NC_LITERAL is disarmed and bad.diff's call binds")


def git_apply_check(diff_path: Path) -> tuple[int, str]:
    """`git apply --check`, run BARE — no pipe, so the exit code is git's own."""
    try:
        r = subprocess.run(["git", "-C", str(ROOT), "apply", "--check", str(diff_path)],
                           capture_output=True, text=True, errors="replace")
    except OSError as exc:                      # git absent is a finding, never a skip
        return 127, f"could not run git: {exc}"
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


def main() -> int:
    c = Cases("review-engine negative control (SCC-129) — fixture intactness")

    # ── A. Structure ──────────────────────────────────────────────────────────────────────
    c.check("fixture directory exists", FIX.is_dir(), "" if FIX.is_dir() else f"missing: {FIX}")
    for rel in REQUIRED:
        p = FIX / rel
        ok = p.is_file() and bool(read(p).strip())
        c.check(f"{rel} exists and is non-empty", ok,
                "" if ok else ("absent" if not p.is_file() else "present but empty"))

    raw = read(FIX / MANIFEST) if (FIX / MANIFEST).is_file() else ""
    man: dict = {}
    try:
        loaded = json.loads(raw) if raw.strip() else None
        parsed = isinstance(loaded, dict)
        detail = "" if parsed else f"top level is {type(loaded).__name__}, expected an object"
        man = loaded if parsed else {}
    except json.JSONDecodeError as exc:
        parsed, detail = False, f"invalid JSON: {exc}"
    c.check("manifest.json parses as a JSON object", parsed, detail)

    # The eval-harness convention for negative controls: `_negative_control: true` + `NC_` ids.
    neg = man.get("_negative_control") is True
    c.check("manifest declares _negative_control: true", neg,
            "" if neg else f"got {man.get('_negative_control')!r} — the convention is a literal true")

    # ⛔ The manifest names the two specs, and a LIVE RUN follows the manifest, not the constants
    # below. Existence alone is not enough: swap the two keys and every file still exists, every
    # clause is still findable in *some* spec, and all rows stay green — while the bad arm gets
    # audited against the refunds spec, where `record_payment` is never mentioned, so NC_ACCEPT
    # becomes uncatchable with no attributable cause. So pin the VALUES, not just resolvability.
    for key, want in (("spec", SPEC), ("clean_spec", CLEAN_SPEC)):
        named = man.get(key)
        ok = named == want and (FIX / str(named)).is_file()
        c.check(f"manifest `{key}` names {want} and it exists", ok,
                "" if ok else (f"declares {named!r}, expected {want!r} — a live run passes this as "
                               f"STORY_FILE, so the arms would be audited against each other's spec"))
    c.check("the two specs are distinct files",
            man.get("spec") != man.get("clean_spec"),
            "" if man.get("spec") != man.get("clean_spec")
            else "both keys name the same file — one spec per change is the whole point")

    defects = man.get("defects") if isinstance(man.get("defects"), list) else []
    defects = [d for d in defects if isinstance(d, dict)]

    # ⛔ NON-EMPTY FIRST. Every loop below is vacuously green over an empty list.
    c.check("manifest declares at least one defect", bool(defects),
            "" if defects else "no usable defect objects — every check below would be vacuous")

    ids = [d.get("id", "") for d in defects]
    bad_ids = sorted(i for i in ids if not i.startswith("NC_"))
    c.check("every defect id carries the NC_ prefix", bool(ids) and not bad_ids,
            "" if ids and not bad_ids
            else (f"not NC_-prefixed: {bad_ids}" if bad_ids else "no ids to check"))
    c.check("defect ids are unique", bool(ids) and len(set(ids)) == len(ids),
            "" if ids and len(set(ids)) == len(ids)
            else f"{len(ids) - len(set(ids))} duplicate(s) in {sorted(ids)}")

    # ── B. Lens coverage — one defect per lens, so the control proves each lens is ALIVE ───
    # First, bind the count to the ENGINE rather than to the literal below it: a sixth lens
    # added upstream must fail HERE, or the fixture quietly stops covering the fan-out.
    step01 = ROOT / ".agents/skills/code-review-engine/steps/step-01-review.md"
    routed = lens_rows(read(step01)) if step01.is_file() else set()
    c.check("step-01 still routes exactly as many lenses as the fixture seeds",
            len(routed) == len(LENSES),
            "" if len(routed) == len(LENSES) else
            f"step-01's fan-out table routes {len(routed)} lens(es) {sorted(routed)} but the "
            f"fixture seeds {len(LENSES)} — seed the new lens or the control stops covering it")

    lenses = {d.get("lens") for d in defects}
    c.check("the five engine lenses each carry exactly one seeded defect",
            lenses == set(LENSES) and len(defects) == len(LENSES),
            f"missing={sorted(LENSES - lenses)} unexpected={sorted(x for x in lenses - LENSES if x)} "
            f"count={len(defects)}" if lenses != set(LENSES) or len(defects) != len(LENSES) else "")

    for d in defects:
        did, sev = d.get("id", "?"), d.get("expected_severity")
        c.check(f"{did}: expected_severity is one of step-03's four levels", sev in SEVERITIES,
                "" if sev in SEVERITIES else f"got {sev!r}, not one of {sorted(SEVERITIES)}")
    # step-03 §5: only a surviving `critical` forces FAIL. Without one seeded, the live half's
    # pass criterion ("bad.diff must come back FAIL") is unreachable by the engine's own table.
    has_crit = any(d.get("expected_severity") == "critical" for d in defects)
    c.check("bad.diff seeds at least one `critical` — the floor it must force is FAIL", has_crit,
            "" if has_crit else "no critical seeded; step-03 §5 could never return FAIL on this fixture")

    # ── C. Intactness — the seeded defects are still literally in the bad diff ─────────────
    bad_txt = read(FIX / BAD) if (FIX / BAD).is_file() else ""
    clean_txt = read(FIX / CLEAN) if (FIX / CLEAN).is_file() else ""
    spec_txt = read(FIX / SPEC) if (FIX / SPEC).is_file() else ""
    bad_added, clean_added = added(bad_txt), added(clean_txt)

    c.check("bad.diff carries added lines to inspect", bool(bad_added.strip()),
            "" if bad_added.strip() else "no '+' lines — every marker check below would be vacuous")

    for d in defects:
        did, marker = d.get("id", "?"), d.get("diff_must_contain", "")
        n = bad_added.count(marker) if marker else 0
        ok = bool(marker) and n == 1
        c.check(f"{did}: still seeded in bad.diff, exactly once", ok,
                "" if ok else (f"no diff_must_contain declared — {REMEDY}" if not marker
                               else f"marker {marker!r} found {n}x in added lines (want 1) — {REMEDY}"))

    # The acceptance defect is only a defect RELATIVE to the spec, so the clause it violates is
    # pinned too: delete that line from spec.md and the seeded defect stops being one.
    acc = [d for d in defects if d.get("lens") == "acceptance"]
    acc_pinned = bool(acc) and all(d.get("spec_must_contain") for d in acc)
    c.check("the acceptance defect pins the spec clause it violates", acc_pinned,
            "" if acc_pinned else
            (f"{[d.get('id') for d in acc if not d.get('spec_must_contain')]} declares no "
             f"spec_must_contain — {REMEDY}" if acc else "no acceptance defect declared"))
    for d in defects:
        want = d.get("spec_must_contain")
        did = d.get("id", "?")
        if want is None:
            continue                            # only the spec-relative defects declare one
        found = bool(want) and flat(str(want)) in flat(spec_txt)
        c.check(f"{did}: the spec clause it violates is still in spec.md", found,
                "" if found else f"{want!r} absent from spec.md — {REMEDY}")

    # ── D. Self-proof — every intactness check above is proven ABLE to fail ────────────────
    # ⛔ The mutation must be proven to APPLY, and "the text changed" cannot prove it: joining
    # splitlines() drops the trailing newline, so a mutated-vs-original comparison is unequal
    # even when nothing was removed. It is the dropped-line COUNT that carries the proof —
    # otherwise a marker declared but never seeded scores a green self-proof row.
    for d in defects:
        did, marker = d.get("id", "?"), d.get("diff_must_contain", "")
        lines = bad_txt.splitlines()
        kept = [ln for ln in lines
                if not (ln.startswith("+") and not ln.startswith("+++")
                        and marker and marker in ln)]
        dropped = len(lines) - len(kept)
        after = added("\n".join(kept)).count(marker) if marker else 1
        ok = bool(marker) and dropped > 0 and after == 0
        c.check(f"  ^ {did}: that check is proven able to fail", ok,
                "" if ok else (f"the mutation removed {dropped} line(s) and left {after} match(es) — "
                               "it cannot demonstrate this check detects its own removal"))

    # ── E. The clean control carries none of them ─────────────────────────────────────────
    # Both halves, always: a reviewer that flags everything is as broken as one that flags
    # nothing, and the bad-diff half alone cannot tell you which you have.
    c.check("clean.diff carries added lines to inspect", bool(clean_added.strip()),
            "" if clean_added.strip() else "no '+' lines — the clean control would prove nothing")
    for d in defects:
        did, marker = d.get("id", "?"), d.get("diff_must_contain", "")
        ok = bool(marker) and marker not in clean_added
        c.check(f"{did}: absent from the clean control", ok,
                "" if ok else f"marker {marker!r} leaked into clean.diff — the control is contaminated")

    # ── F. Rot guard — both diffs still apply to the committed base ───────────────────────
    for rel in (BAD, CLEAN):
        p = FIX / rel
        rc, out = git_apply_check(p) if p.is_file() else (1, "diff file absent")
        c.check(f"{rel} still applies to the committed base", rc == 0,
                "" if rc == 0 else f"git apply --check exit {rc}: {out[:300]} — the fixture "
                                   f"drifted from codebase/; regenerate the diff against it")

    # ...and that apply-check is proven able to refuse. A corrupted context line must not apply.
    ctx = next((i for i, ln in enumerate(bad_txt.splitlines())
                if ln.startswith(" ") and ln.strip()), None)
    c.check("bad.diff carries a context line to corrupt", ctx is not None,
            "" if ctx is not None else "no context lines — the apply-check proof below is vacuous")
    if ctx is not None:
        lines = bad_txt.splitlines()
        lines[ctx] = " NC_CORRUPTION_PROOF = 'this line is not in the committed base'"
        with TempDir() as tmp:
            probe = tmp / "corrupted.diff"
            probe.write_text("\n".join(lines) + "\n", encoding="utf-8")
            rc, out = git_apply_check(probe)
            c.check("  ^ that apply-check is proven able to fail", rc != 0,
                    "" if rc != 0 else "a corrupted diff still applied — the rot guard is vacuous")

    # ── C2. Preconditions that live OUTSIDE the added lines ───────────────────────────────
    # ⛔ A seeded defect is only a defect relative to something. For NC_LITERAL that is a
    # signature (F2 below); for NC_ACCEPT a spec clause (above); for NC_BLIND it is the
    # docstring in `codebase/billing.py` saying the total INCLUDES tax — which appears in
    # bad.diff only as a CONTEXT line, and `added()` keeps `+` lines only, so no marker check
    # can see it. Reword that docstring, regenerate bad.diff, and all sixty cases stay green
    # while the Blind Hunter has nothing left to find.
    base_txt = read(FIX / "codebase" / "billing.py") if (FIX / "codebase" / "billing.py").is_file() else ""
    for d in defects:
        want, did = d.get("base_must_contain"), d.get("id", "?")
        if want is None:
            continue                            # only base-relative defects declare one
        found = bool(want) and flat(str(want)) in flat(base_txt)
        c.check(f"{did}: the base-state line it contradicts is still in codebase/billing.py",
                found, "" if found else f"{want!r} absent from the base module — {REMEDY}")
    based = [d for d in defects if d.get("base_must_contain")]
    c.check("the blind defect pins the base-state line it contradicts",
            any(d.get("lens") == "blind" and d.get("base_must_contain") for d in defects),
            "" if based else "no defect pins a base-state precondition; NC_BLIND needs one")

    # ⛔ `spec_must_contain` is optional, so the loop above `continue`s past a defect that lost
    # it — silently deleting a check. Pin the COUNT of spec-relative pins so dropping one from
    # the manifest goes red instead of quietly reducing coverage.
    pinned = sorted(d.get("id", "?") for d in defects if d.get("spec_must_contain"))
    c.check("both spec-relative defects still carry their clause pin", len(pinned) >= 2,
            "" if len(pinned) >= 2 else
            f"only {pinned} pin a spec clause; NC_ACCEPT and NC_TESTADQ both must — {REMEDY}")

    # ── F2. NC_LITERAL's premise — the definition the seeded call fails to bind against ────
    hp = FIX / "codebase" / "helpers.py"
    sig_ok, sig_detail = parse_arity(read(hp)) if hp.is_file() else (False, "helpers.py absent")
    c.check("NC_LITERAL's premise holds: helpers.parse takes exactly one parameter",
            sig_ok, sig_detail)
    # ...and that check is proven able to fail, on the exact "fix" README.md warns against.
    disarmed, _ = parse_arity("def parse(text: str, strict: bool = False) -> list[str]:\n"
                              "    return []\n")
    c.check("  ^ that check is proven able to fail", not disarmed,
            "" if not disarmed else "a two-parameter `parse` still passed — the premise is unguarded")

    # ── G. The test-adequacy gap is a property of the diff, not a string ──────────────────
    # NC_TESTADQ's subject is something ABSENT, and no marker can prove an absence — so its
    # marker pins the new logic that ought to have been tested, and this pair pins the gap.
    bad_paths, clean_paths = diff_paths(bad_txt), diff_paths(clean_txt)
    c.check("bad.diff names the files it touches", bool(bad_paths),
            "" if bad_paths else "no ---/+++ headers parsed — the two checks below would be vacuous")

    bad_tests = sorted(p for p in bad_paths if is_test_path(p))
    c.check("bad.diff ships new logic with NO test file — the seeded test-adequacy gap",
            bool(bad_paths) and not bad_tests,
            "" if bad_paths and not bad_tests
            else (f"test files present: {bad_tests} — NC_TESTADQ is no longer seeded" if bad_tests
                  else "no paths parsed"))

    clean_tests = [p for p in clean_paths if is_test_path(p)]
    c.check("clean.diff DOES ship a test for what it adds", bool(clean_tests),
            "" if clean_tests else
            "no test file in the clean control — a Test-Adequacy finding against it would be "
            "CORRECT, and the control would fail for the right reason at the wrong time")

    # A filename is not a test. Gutting that file's body to `pass` would leave the row above
    # green while the clean control stopped demonstrating the tested shape it exists to show —
    # the same vacuity class this file's docstring guards against everywhere else.
    # Scoped to the TEST file's own hunk — an `assert` in the other file must not satisfy it.
    test_added = "\n".join(txt for path, txt in added_by_file(clean_txt).items()
                           if is_test_path(path))
    real_asserts = has_assertion(test_added)
    c.check("clean.diff's test actually asserts something", real_asserts,
            "" if real_asserts else "the added test file carries no assertion — a test in name only")
    # ...and proven able to fail by running the SAME predicate over an independently-written
    # stub, never over a mutation of its own input (see `has_assertion`).
    stub_asserts = has_assertion(GUTTED_STUB)
    c.check("  ^ the assertion check is proven able to fail", real_asserts and not stub_asserts,
            "" if not stub_asserts else
            "has_assertion() returned True for a stub whose body is `pass` — it cannot tell a "
            "real test from a test in name only")

    # ── H. The live half's run log — shape only, never "all hits" ─────────────────────────
    # ⛔ This deliberately does NOT assert every defect was found. A check that went red on a
    # recorded miss would punish honest recording and pressure the next person to leave the
    # miss out — turning the log into a record of successes, which is no record at all. What
    # is asserted is that each entry is COMPLETE: it says which sha, which diff, what floor
    # came back, and a verdict for every one of the five seeded defects, hit or miss.
    lines = [ln for ln in read(FIX / RUNS).splitlines() if ln.strip()] if (FIX / RUNS).is_file() else []
    c.check("live_runs.jsonl records at least one run", bool(lines),
            "" if lines else "no runs logged — the control may never have been run live")

    entries, broken = [], []
    for i, ln in enumerate(lines, 1):
        try:
            obj = json.loads(ln)
            entries.append(obj) if isinstance(obj, dict) else broken.append(f"line {i}: not an object")
        except json.JSONDecodeError as exc:
            broken.append(f"line {i}: {exc}")
    c.check("every live_runs.jsonl line is a JSON object", bool(lines) and not broken,
            "; ".join(broken) if broken else ("no lines to parse" if not lines else ""))

    # `key_read` records which roles saw the answer key on that run. Contamination belongs in the
    # log, not only in a note someone has to remember to write: the first run had it in the step-2
    # verifier, the role whose revised severities DECIDE the clean arm.
    need = {"date", "sha", "ticket", "diff", "floor", "results", "key_read"}
    thin = [f"{e.get('diff', '?')}@{e.get('sha', '?')}: missing {sorted(need - set(e))}"
            for e in entries if not need <= set(e)]
    newest = max((str(e.get("date", "")) for e in entries), default="never")
    c.check("every logged run names its sha, diff, floor, results and key_read",
            bool(entries) and not thin,
            "; ".join(thin) if thin else (f"{len(entries)} run(s), newest {newest}" if entries
                                          else "no entries"))

    # ⛔ Scoped to entries that overlap the CURRENT ids. Renaming a defect is an explicitly
    # permitted redesign, and a check that reddened every historical entry on a rename would make
    # rewriting the log the path of least resistance — the same pressure the design note above
    # avoids by never asserting a hit.
    ids = {str(d.get("id", "")) for d in defects}
    partial = [f"{e.get('diff')}@{e.get('sha')}: {sorted(ids - set(e.get('results') or {}))}"
               for e in entries
               if e.get("diff") == BAD and (set(e.get("results") or {}) & ids)
               and not ids <= set(e.get("results") or {})]
    c.check("every logged bad.diff run reports a verdict for all five seeded defects",
            bool(entries) and not partial,
            "; ".join(f"no verdict for {p}" for p in partial) if partial
            else (f"{sum(1 for e in entries if e.get('diff') == BAD)} bad-arm run(s)" if entries
                  else "no entries"))

    # ── I. The two safeguards that are prose, and are load-bearing anyway ─────────────────
    # README.md is held to existence-only everywhere else in this file, on purpose (SCC-125:
    # pinning a DESCRIPTION of wiring is vacuous). These two strings are the exception, and the
    # distinction is real: they have no separate implementation to diverge from, so their
    # PRESENCE is the safeguard rather than a description of one. The answer key is greppable —
    # a lens that never opens a file still gets `manifest.json`'s marker, expected severity and
    # pre-written failure text in the output of an ordinary `grep "def parse"` — so the
    # prohibition is all that stands between a review and a readback.
    readme = read(FIX / README) if (FIX / README).is_file() else ""
    for label, needle in (
        ("the answer-key prohibition", "Do not open `manifest.json`, `README.md`, `bad.diff` or `clean.diff`"),
        ("the both-halves rule", "A reviewer that flags everything is as broken as one that flags nothing"),
        # SCC-147: the control's own budget. NC_LITERAL is catchable ONLY by opening
        # `codebase/helpers.py`, which `bad.diff` does not touch — i.e. only via the ONE
        # top-up `standard` allows and `capped` forbids. Flip this row to `capped` and the
        # seeded literal defect becomes unreachable, so the control quietly stops
        # discriminating between lenses — which is the whole point of SCC-129 — with every
        # one of this file's cases still green. Proven by the review, which flipped it and
        # watched 67/67 pass. It belongs in THIS list rather than in the existence-only
        # majority for the same reason as the two above: the row IS the safeguard, not a
        # description of one.
        ("the interactive budget both arms run", "| `lens_budget` | `standard` | `standard` |"),
    ):
        present = flat(needle) in flat(readme)
        c.check(f"README still carries {label}", present,
                "" if present else f"{needle!r} is gone — without it the live control silently "
                                   f"degrades into a readback that passes whatever the engine does")

    # Safety: a fixture diff naming a real repo path could be applied against live files.
    every = bad_paths + clean_paths
    stray = sorted(p for p in every if not p.startswith(FIX_PREFIX))
    c.check("both diffs touch ONLY paths inside the fixture", bool(every) and not stray,
            "" if every and not stray
            else (f"outside the fixture: {stray}" if stray else "no paths parsed at all"))

    return c.finish()


if __name__ == "__main__":
    raise SystemExit(main())

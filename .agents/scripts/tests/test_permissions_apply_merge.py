"""The applies must NEVER delete an approval the operator clicked (SCC-414).

⛔ THE DEFECT THIS FILE EXISTS TO HOLD. Both apply scripts used to REPLACE the store's arrays with
the tracked ones. A click lands in the live store and works, until the next `--apply` overwrites the
array from the tracked file - the click was never in the tracked file, so it is gone. The operator
re-clicks, and the next apply deletes it again.

Measured 2026-09-05 on the live Antigravity store, from a copy taken immediately before the apply:
178 allow rows in, 123 out - **58 of the operator's own grants destroyed by one routine apply**.
In the operator's words: *"I keep approving in chat and it doesn't seem to store."*

Both scripts are driven through their injectable params (`store=`/`rendered=` on Antigravity, an
in-memory memento dict on Zoo), so every case here runs on ANY machine - Ubuntu, Windows or Mac -
and touches no real store. That matters: the seams existed for exactly this and nothing drove them.
"""
from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / ".agents" / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


AG = _load("antigravity_permissions_apply")
ZOO = _load("zoo_permissions_apply")

CLICKED = "command(the-operator-clicked-this)"
TRACKED = "command(from-the-tracked-source)"


# --- the shared helper, both platforms -------------------------------------------------------

def test_A_merge_keeps_store_only_rows_and_puts_tracked_first():
    for mod in (AG, ZOO):
        got = mod.merge_keep_store_only([TRACKED], [CLICKED, TRACKED])
        assert got == [TRACKED, CLICKED], f"{mod.__name__}: {got}"


def test_A2_merge_never_duplicates_a_row_present_on_both_sides():
    for mod in (AG, ZOO):
        got = mod.merge_keep_store_only([TRACKED], [TRACKED])
        assert got == [TRACKED], f"{mod.__name__}: {got}"


# --- Antigravity, end to end through the real apply() -----------------------------------------

def _ag_fixture(td: Path) -> tuple[Path, Path]:
    store = td / "config.json"
    store.write_text(json.dumps({
        "userSettings": {AG.KEY: {"allow": [CLICKED], "deny": []},
                         "remoteControlHostname": "keep-me"}}), encoding="utf-8")
    rendered = td / "antigravity.json"
    rendered.write_text(json.dumps({
        "userSettings": {AG.KEY: {"allow": [TRACKED], "deny": []}}}), encoding="utf-8")
    return store, rendered


def test_B_antigravity_apply_PRESERVES_the_operators_click():
    """⛔ THE REGRESSION. Before SCC-414 this row vanished on every apply."""
    with tempfile.TemporaryDirectory() as td:
        store, rendered = _ag_fixture(Path(td))
        AG.apply(store, rendered)
        allow = json.loads(store.read_text(encoding="utf-8"))["userSettings"][AG.KEY]["allow"]
        assert CLICKED in allow, f"the operator's click was DELETED by the apply: {allow}"
        assert TRACKED in allow, f"the tracked row did not land: {allow}"


def test_B2_antigravity_prune_still_deletes_it_because_that_is_what_prune_MEANS():
    """CONTROL: without this, test_B could pass on a function that never writes anything."""
    with tempfile.TemporaryDirectory() as td:
        store, rendered = _ag_fixture(Path(td))
        AG.apply(store, rendered, prune=True)
        allow = json.loads(store.read_text(encoding="utf-8"))["userSettings"][AG.KEY]["allow"]
        assert allow == [TRACKED], allow


def test_B3_antigravity_apply_preserves_every_other_key_in_the_store():
    with tempfile.TemporaryDirectory() as td:
        store, rendered = _ag_fixture(Path(td))
        AG.apply(store, rendered)
        cfg = json.loads(store.read_text(encoding="utf-8"))
        assert cfg["userSettings"]["remoteControlHostname"] == "keep-me"


def test_C_status_reads_a_kept_click_as_IN_SYNC_not_drift():
    """A store-only row is the operator's own approval. Reporting it as DRIFT (and exiting 1) is
    what made a healthy store look broken and invited the destructive apply."""
    with tempfile.TemporaryDirectory() as td:
        store, rendered = _ag_fixture(Path(td))
        AG.apply(store, rendered)
        s = AG.status(store, rendered)
        assert s.startswith(AG.IN_SYNC), s
        assert "store-only" in s, f"the kept row should be NAMED, not hidden: {s}"


def test_C2_status_still_reports_DRIFT_when_a_TRACKED_row_is_missing():
    """CONTROL for test_C: the check must still be able to fail."""
    with tempfile.TemporaryDirectory() as td:
        store, rendered = _ag_fixture(Path(td))
        s = AG.status(store, rendered)          # never applied - tracked row absent
        assert s.startswith("DRIFT"), s
        assert "tracked-missing=1" in s, s


# --- Zoo, end to end through the real apply() against a temp sqlite store ----------------------

def test_C3_ZOO_status_also_reads_a_kept_click_as_IN_SYNC():
    """SCC-413 parity: the Antigravity side got this and Zoo did not, so a kept click still read
    DRIFT on Zoo - the same 'healthy store looks broken' signal that invites a destructive prune."""
    assert ZOO.diff_counts(["a", "b", CLICKED], ["a", "b"]).startswith("in sync")
    assert "store-only" in ZOO.diff_counts(["a", CLICKED], ["a"])


def test_C4_ZOO_status_still_reports_DRIFT_on_a_MISSING_tracked_row():
    """CONTROL for C3 - the check must still be able to fail."""
    got = ZOO.diff_counts(["a"], ["a", "b"])
    assert got.startswith("DRIFT") and "1 tracked entries missing" in got, got


def _zoo_db(td: Path) -> Path:
    db = td / "state.vscdb"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE ItemTable (key TEXT PRIMARY KEY, value TEXT)")
    con.execute("INSERT INTO ItemTable VALUES (?, ?)",
                (ZOO.ZOO_KEY, json.dumps({"allowedCommands": [CLICKED], "deniedCommands": []})))
    con.commit(); con.close()
    return db


def _zoo_read(db: Path) -> dict:
    con = sqlite3.connect(db)
    try:
        return json.loads(con.execute("SELECT value FROM ItemTable WHERE key=?",
                                      (ZOO.ZOO_KEY,)).fetchone()[0])
    finally:
        con.close()


def test_D_zoo_apply_PRESERVES_the_operators_click():
    with tempfile.TemporaryDirectory() as td:
        db = _zoo_db(Path(td))
        memento = _zoo_read(db)
        ZOO.apply(db, memento, [TRACKED], [])
        allow = _zoo_read(db)["allowedCommands"]
        assert CLICKED in allow, f"the operator's click was DELETED by the apply: {allow}"
        assert TRACKED in allow, allow


def test_D2_zoo_prune_still_deletes_it():
    """CONTROL, same shape as B2."""
    with tempfile.TemporaryDirectory() as td:
        db = _zoo_db(Path(td))
        memento = _zoo_read(db)
        ZOO.apply(db, memento, [TRACKED], [], prune=True)
        assert _zoo_read(db)["allowedCommands"] == [TRACKED]


def test_D3_zoo_apply_never_turns_a_master_toggle_off():
    with tempfile.TemporaryDirectory() as td:
        db = _zoo_db(Path(td))
        memento = _zoo_read(db)
        memento["autoApprovalEnabled"] = True
        ZOO.apply(db, memento, [TRACKED], [])
        assert _zoo_read(db).get("autoApprovalEnabled") is True


# --- the platform seams, exercised from ANY machine -------------------------------------------

def test_E_candidate_dbs_finds_the_MAC_paths_when_home_looks_like_a_mac():
    """The darwin branch and the isolated second seat existed and nothing drove them. Runs green on
    Ubuntu: candidate_dbs takes `home=` precisely so a platform can be simulated."""
    if sys.platform != "darwin":
        return                                   # the branch is chosen by sys.platform; see E2
    with tempfile.TemporaryDirectory() as td:
        home = Path(td)
        mac = home / "Library" / "Application Support" / "Code" / "User" / "globalStorage"
        iso = home / "vscode-isolated" / "User" / "globalStorage"
        for d in (mac, iso):
            d.mkdir(parents=True); (d / "state.vscdb").write_text("x", encoding="utf-8")
        got = [str(p) for p in ZOO.candidate_dbs(home=home, windows_users=Path(td) / "none")]
        assert any("Library/Application Support" in p for p in got), got
        assert any("vscode-isolated" in p for p in got), got


def test_E2_the_mac_branch_is_PRESENT_in_the_source_on_every_platform():
    """E can only run on a Mac, so on Ubuntu it would pass vacuously. This one cannot: it reads the
    source and fails anywhere if the darwin arm or the isolated seat is dropped."""
    src = (ROOT / ".agents" / "scripts" / "zoo_permissions_apply.py").read_text(encoding="utf-8")
    assert 'sys.platform == "darwin"' in src, "the Mac branch of candidate_dbs is gone"
    assert "Library" in src and "Application Support" in src, "the Mac user-data path is gone"
    assert "vscode-isolated" in src, "the isolated second seat is gone"
    assert 'pgrep' in src, "the Mac/Linux arm of vscode_running is gone"


def test_F_the_apply_docstrings_do_not_promise_a_replace_any_more():
    """The behaviour changed; a docstring still saying `Write the rendered grants into the store`
    would be the stale-comment failure this house bans."""
    ag = (ROOT / ".agents" / "scripts" / "antigravity_permissions_apply.py").read_text(encoding="utf-8")
    assert "prune" in ag, "the --prune escape hatch is missing"
    assert "Merge the rendered grants" in ag, "apply()'s docstring still describes the old replace"


if __name__ == "__main__":
    import traceback
    _fns = [(n, f) for n, f in sorted(globals().items())
            if n.startswith("test_") and callable(f)]
    _failed = []
    for _name, _fn in _fns:
        try:
            _fn()
        except BaseException:
            _failed.append(_name)
            traceback.print_exc()
    print(f"-- {len(_fns) - len(_failed)}/{len(_fns)} passed --"
          + (f"  FAILED: {', '.join(_failed)}" if _failed else ""))
    sys.exit(1 if _failed else 0)

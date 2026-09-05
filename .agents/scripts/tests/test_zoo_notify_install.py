"""Per-machine install of the Zoo notifier as a background service — behavior gate (SCC-355).

⛔ Why this file exists at all. SCC-355 shipped `zoo_notify.py --watch` — a FOREGROUND blocking
poll loop — plus an SOP row telling the operator to run it, and nothing that runs it. Zoo
contributes no event hook, so a process must be alive to poll; none ever was, and the whole
feature was silent on the Mac from the day it landed until the operator reported it. The delivery
gap, not the classifier, is what made it 100% silent. So the install is now a script with a test,
exactly like its sibling `zoo_permissions_apply.py`.

⛔ Nothing here touches the real `~/Library/LaunchAgents` or the real Startup folder: every case
passes an explicit `home=` into a TemporaryDirectory, and `launchctl` is never invoked. A test that
installs a live launchd agent on the machine running the suite is not a test, it is an install.

⛔ Path assertions compare `Path` PARTS, never `str(...)` — the same scar as its sibling suite:
`str(p).endswith("...")` is False the moment `Path` is a `WindowsPath`, so a suite authored on the
Mac would go red on the PC it is supposed to protect. [[mac-authored-code-hides-windows-bugs]]
"""
from __future__ import annotations

import json
import plistlib
import sys
import tempfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[3]
INSTALL = ROOT / ".agents" / "scripts" / "zoo_notify_install.py"
NOTIFY = ROOT / ".agents" / "scripts" / "zoo_notify.py"


def _mod():
    import importlib.util
    spec = importlib.util.spec_from_file_location("zoo_notify_install", INSTALL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _home(tmp: Path) -> Path:
    (tmp / "Library" / "LaunchAgents").mkdir(parents=True, exist_ok=True)
    (tmp / "Library" / "Logs").mkdir(parents=True, exist_ok=True)
    return tmp


def _repo(tmp: Path) -> Path:
    """A stand-in checkout that is NOT a git worktree.

    ⛔ These cases used to pass `repo=ROOT`, and ROOT is `.claude/worktrees/<lane>/` whenever this
    suite runs inside a lane — which is always, because every commit-producing lane isolates. The
    worktree guard then refused them, correctly. A test that only passes from the main checkout is
    a test that fails for everyone doing the work.
    """
    repo = tmp / "checkout"
    (repo / ".agents" / "scripts").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / "scripts" / "zoo_notify.py").write_text("# stand-in", encoding="utf-8")
    return repo


# --- it has to exist, and it must not be a foreground-only story --------------------------

def test_installer_exists():
    assert INSTALL.is_file(), f"{INSTALL} does not exist — the delivery gap is still open"


def test_the_notifier_it_installs_exists():
    assert NOTIFY.is_file(), "the installer would point launchd at a script that is not there"


# --- the Mac branch: a launchd agent that survives logout, reboot and a crash --------------

def test_mac_plist_runs_at_load_and_keeps_alive():
    """⛔ The two keys that ARE the fix. Without RunAtLoad it never starts on login; without
    KeepAlive it dies once and stays dead — either way the operator is back to a silent Mac."""
    m = _mod()
    with tempfile.TemporaryDirectory() as d:
        p = m.build_plist(repo=ROOT, home=_home(Path(d)), platform="darwin")
        assert p["RunAtLoad"] is True
        assert p["KeepAlive"] is True
        assert p["Label"] == m.LABEL


def test_mac_plist_invokes_the_watcher_with_an_absolute_script_path():
    m = _mod()
    with tempfile.TemporaryDirectory() as d:
        p = m.build_plist(repo=ROOT, home=_home(Path(d)), platform="darwin")
        args = p["ProgramArguments"]
        assert "--watch" in args, args
        script = Path(args[1])
        assert script.is_absolute(), script
        assert script.parts[-3:] == (".agents", "scripts", "zoo_notify.py"), script.parts[-3:]


def test_mac_plist_never_points_at_a_virtualenv_interpreter():
    """⭐ Measured hazard, not a hypothetical: at build time `sys.executable` in this repo was
    `Projects/AGY_AVIATIONCHAT/backend/.venv/bin/python3`. Baking that in ties the operator's
    notifications to one project's virtualenv — rebuild or delete it and the agent dies silently.
    The command centre is stdlib-only by law, so the system interpreter is the correct answer."""
    m = _mod()
    with tempfile.TemporaryDirectory() as d:
        p = m.build_plist(repo=ROOT, home=_home(Path(d)), platform="darwin")
        # ⛔ PurePosixPath, not Path — this is a DARWIN artifact (`platform="darwin"` above), so
        # its interpreter is a POSIX path whatever machine runs the suite. On Windows,
        # `Path("/usr/bin/python3")` is a WindowsPath whose `.is_absolute()` is **False** (no
        # drive letter) and whose parts start `('\\', 'usr', …)`, so this case went red on the PC
        # while the Mac plist it checks was perfectly correct. That is the exact scar this file's
        # own header names — assert on POSIX semantics for a POSIX artifact.
        # [[mac-authored-code-hides-windows-bugs]] (SCC-338)
        interp = PurePosixPath(p["ProgramArguments"][0])
        assert ".venv" not in interp.parts, interp
        assert "venv" not in interp.parts, interp
        assert interp.is_absolute(), interp


def test_mac_plist_carries_the_ntfy_topic_because_launchd_never_sources_zshrc():
    """⛔ NTFY_TOPIC lives in ~/.zshrc, which launchd does not read. It happens to equal the
    built-in default today, so the bug would be invisible until the operator changed the topic
    and his phone quietly stopped receiving. [[zshrc-is-invisible-to-automation]]"""
    m = _mod()
    with tempfile.TemporaryDirectory() as d:
        p = m.build_plist(repo=ROOT, home=_home(Path(d)), platform="darwin", topic="a-test-topic")
        assert p["EnvironmentVariables"]["NTFY_TOPIC"] == "a-test-topic"


def test_mac_plist_path_reaches_homebrew_because_terminal_notifier_lives_there():
    """launchd's default PATH is /usr/bin:/bin:/usr/sbin:/sbin — terminal-notifier is at
    /opt/homebrew/bin, so the banner half dies while the push half keeps working. That asymmetry
    is exactly the 'it half works' report this lane exists to prevent a second time."""
    m = _mod()
    with tempfile.TemporaryDirectory() as d:
        p = m.build_plist(repo=ROOT, home=_home(Path(d)), platform="darwin")
        path = p["EnvironmentVariables"]["PATH"]
        assert "/opt/homebrew/bin" in path.split(":"), path
        assert "/usr/local/bin" in path.split(":"), path


def test_mac_plist_forces_unbuffered_output_or_the_log_stays_empty():
    """⛔ Found by installing it for real, not by reading the code. The agent came up, launchctl
    listed it, `ps` showed it watching — and `~/Library/Logs/zoo-notify.log` was EMPTY, because
    Python block-buffers stdout whenever it is not a TTY and a poll loop never produces enough
    output to flush. An empty log is precisely the state the log exists to rule out: 'started but
    doing nothing' and 'never started' look identical again, which is where this whole session
    began. PYTHONUNBUFFERED, not `-u`, so ProgramArguments[1] stays the script path."""
    m = _mod()
    with tempfile.TemporaryDirectory() as d:
        p = m.build_plist(repo=ROOT, home=_home(Path(d)), platform="darwin")
        assert p["EnvironmentVariables"].get("PYTHONUNBUFFERED") == "1", p["EnvironmentVariables"]


def test_windows_command_is_unbuffered_too():
    m = _mod()
    body = m.build_cmd(repo=ROOT)
    assert "PYTHONUNBUFFERED=1" in body, body


def test_mac_plist_writes_logs_so_a_silent_watcher_can_be_diagnosed():
    """A background process with no log is indistinguishable from one that never started —
    which is the position this session opened in."""
    m = _mod()
    with tempfile.TemporaryDirectory() as d:
        home = _home(Path(d))
        p = m.build_plist(repo=ROOT, home=home, platform="darwin")
        for key in ("StandardOutPath", "StandardErrorPath"):
            assert key in p, key
            assert Path(p[key]).is_absolute(), p[key]
            assert "Logs" in Path(p[key]).parts, p[key]


def test_apply_writes_a_readable_plist_and_reports_the_file_not_the_exit_code():
    """⛔ House law: on a write, verify the FILE. `--apply` re-reads what it wrote."""
    m = _mod()
    with tempfile.TemporaryDirectory() as d:
        home = _home(Path(d))
        rc = m.apply(repo=_repo(Path(d)), home=home, platform="darwin", load=False)
        assert rc == 0
        target = m.plist_path(home)
        assert target.is_file(), target
        back = plistlib.loads(target.read_bytes())
        assert back["Label"] == m.LABEL
        assert back["RunAtLoad"] is True


def test_apply_refuses_a_git_worktree_path_because_the_lane_gets_pruned():
    """⛔ Caught while installing this very lane. `--repo` defaults to the tree the script is
    standing in, and this work was built inside `.claude/worktrees/zoo-notify-fix/`. Applying from
    there bakes the WORKTREE path into a login agent that outlives the lane by design — close-out
    prunes the worktree, and from the next login the operator has a loaded launchd job pointing at
    a deleted directory and no notifications, with nothing on screen to say so. The service must
    point at the main checkout or refuse."""
    m = _mod()
    with tempfile.TemporaryDirectory() as d:
        home = _home(Path(d))
        lane = Path(d) / "repo" / ".claude" / "worktrees" / "some-lane"
        (lane / ".agents" / "scripts").mkdir(parents=True)
        (lane / ".agents" / "scripts" / "zoo_notify.py").write_text("# stand-in", encoding="utf-8")
        rc = m.apply(repo=lane, home=home, platform="darwin", load=False)
        assert rc != 0, "installing from a worktree must fail loudly, not silently"
        assert not m.plist_path(home).exists(), "and it must write nothing"


def test_apply_is_idempotent():
    m = _mod()
    with tempfile.TemporaryDirectory() as d:
        home = _home(Path(d))
        m.apply(repo=_repo(Path(d)), home=home, platform="darwin", load=False)
        first = m.plist_path(home).read_bytes()
        m.apply(repo=_repo(Path(d)), home=home, platform="darwin", load=False)
        assert m.plist_path(home).read_bytes() == first, "a second apply must change nothing"


def test_dry_run_writes_nothing():
    m = _mod()
    with tempfile.TemporaryDirectory() as d:
        home = _home(Path(d))
        m.apply(repo=_repo(Path(d)), home=home, platform="darwin", load=False, dry_run=True)
        assert not m.plist_path(home).exists(), "a dry run must leave the disk untouched"


# --- --status: the audit amendment. Loaded is not the same as working ---------------------

def test_status_reports_not_installed_before_apply():
    m = _mod()
    with tempfile.TemporaryDirectory() as d:
        report = m.status(home=_home(Path(d)), platform="darwin")
        assert report["installed"] is False
        assert report["script_exists"] is None, "nothing to check when nothing is installed"


def test_status_catches_a_plist_whose_script_path_no_longer_exists():
    """⭐ The audit's amendment (Lens 3 observation). The plist embeds this repo's ABSOLUTE path;
    move or rename the repo and launchd keeps happily loading an agent that points at nothing.
    `launchctl list` still shows it. Only reading the path back catches it."""
    m = _mod()
    with tempfile.TemporaryDirectory() as d:
        home = _home(Path(d))
        m.apply(repo=_repo(Path(d)), home=home, platform="darwin", load=False)
        assert m.status(home=home, platform="darwin")["script_exists"] is True

        target = m.plist_path(home)
        data = plistlib.loads(target.read_bytes())
        data["ProgramArguments"][1] = str(Path(d) / "moved-away" / "zoo_notify.py")
        target.write_bytes(plistlib.dumps(data))

        report = m.status(home=home, platform="darwin")
        assert report["installed"] is True
        assert report["script_exists"] is False, "a dead ProgramArguments path must be reported"


def test_remove_deletes_the_plist():
    m = _mod()
    with tempfile.TemporaryDirectory() as d:
        home = _home(Path(d))
        m.apply(repo=_repo(Path(d)), home=home, platform="darwin", load=False)
        assert m.plist_path(home).is_file()
        m.remove(home=home, platform="darwin", unload=False)
        assert not m.plist_path(home).exists()


def test_remove_on_a_clean_machine_is_not_an_error():
    m = _mod()
    with tempfile.TemporaryDirectory() as d:
        assert m.remove(home=_home(Path(d)), platform="darwin", unload=False) == 0


# --- the PC branch: authored here, RUN by the operator ------------------------------------

def test_windows_writes_a_startup_command_not_a_plist():
    m = _mod()
    with tempfile.TemporaryDirectory() as d:
        home = Path(d)
        rc = m.apply(repo=_repo(Path(d)), home=home, platform="win32", load=False)
        assert rc == 0
        target = m.startup_path(home)
        assert target.is_file(), target
        assert target.suffix == ".cmd", target
        assert "Startup" in target.parts, target.parts


def test_windows_command_starts_minimised_with_pythonw_and_sets_the_topic():
    """⛔ `python` opens a console window that sits on the operator's desktop forever, and closing
    it kills the watcher. `pythonw` is the windowless interpreter. And the topic must be set here
    for the same reason it is set in the plist: a Startup .cmd inherits no shell profile."""
    m = _mod()
    with tempfile.TemporaryDirectory() as d:
        body = m.build_cmd(repo=ROOT, topic="a-test-topic")
        assert "pythonw" in body, body
        assert "--watch" in body, body
        assert "a-test-topic" in body, body
        assert "\r\n" in body, "a .cmd must use CRLF or cmd.exe mis-parses it"
        assert "python3" not in body, "the PC has no `python3` — [[one-pc-windows-and-wsl]]"


def test_windows_status_round_trips():
    m = _mod()
    with tempfile.TemporaryDirectory() as d:
        home = Path(d)
        assert m.status(home=home, platform="win32")["installed"] is False
        m.apply(repo=_repo(Path(d)), home=home, platform="win32", load=False)
        report = m.status(home=home, platform="win32")
        assert report["installed"] is True
        assert report["script_exists"] is True


def test_an_unknown_platform_says_so_instead_of_pretending():
    m = _mod()
    with tempfile.TemporaryDirectory() as d:
        report = m.status(home=Path(d), platform="linux")
        assert report["installed"] is False
        assert "supported" in (report.get("note") or "").lower(), report


# --- the CLI is reachable, and read-only by default ---------------------------------------

def test_cli_defaults_to_status_and_writes_nothing():
    import subprocess
    with tempfile.TemporaryDirectory() as d:
        home = _home(Path(d))
        proc = subprocess.run([sys.executable, str(INSTALL), "--home", str(home)],
                              capture_output=True, text=True, timeout=60)
        assert proc.returncode in (0, 1), proc.stderr
        assert not m_plist(home).exists(), "a bare invocation must never install anything"
        assert proc.stdout.strip(), "status must say something"


def m_plist(home: Path) -> Path:
    return home / "Library" / "LaunchAgents" / "com.sudohatter.zoo-notify.plist"


def test_cli_json_is_machine_readable():
    import subprocess
    with tempfile.TemporaryDirectory() as d:
        home = _home(Path(d))
        proc = subprocess.run([sys.executable, str(INSTALL), "--home", str(home), "--json"],
                              capture_output=True, text=True, timeout=60)
        payload = json.loads(proc.stdout)
        assert "installed" in payload, payload


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
    print(f"-- {len(_fns) - len(_failed)}/{len(_fns)} passed --")
    if _failed:
        # mutation_sweep.py attributes a kill by a line STARTING with "FAILED:" (its L186), so
        # this must be its own line - on the tally line it reads as an unattributable sweep error
        print("FAILED: " + ", ".join(_failed))
    sys.exit(1 if _failed else 0)

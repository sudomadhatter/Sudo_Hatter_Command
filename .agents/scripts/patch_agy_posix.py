#!/usr/bin/env python3
"""Surgical binary patcher for Antigravity (agy) on Linux/WSL. (SCC-450)

In Remote-WSL, VS Code renders the webview within the Windows desktop Electron wrapper.
The embedded `index.html` inside `agy` inspects `navigator.userAgent`, observes "Windows",
and forces `window.process.platform = "win32"`.
Downstream, `vscode-uri` transforms POSIX paths (`/home/...`) into Windows backslash paths
(`\\home\\...`). When `AddTrackedWorkspace` calls the Linux `agy` daemon, Go's `filepath.IsAbs`
rejects it, leaving Antigravity with no tracked workspace and running outside repo law.

This script safely patches the embedded webview zip inside `/home/dlohn/.gemini/bin/agy` so that
`index.html` sets `window.process.platform = "linux"` on Linux/WSL systems.
The patch preserves exact byte offsets, local header lengths, central directory offsets,
and the total binary file length (`213,582,080` bytes).

Usage:
    python3 patch_agy_posix.py --check
    python3 patch_agy_posix.py --apply
    python3 patch_agy_posix.py --restore
"""
from __future__ import annotations

import argparse
import io
import os
import shutil
import struct
import sys
import time
import zipfile
import zlib
from pathlib import Path

DEFAULT_BIN_PATH = Path.home() / ".gemini" / "bin" / "agy"
ZIP_START = 184733042
ZIP_END = 188067463
EXPECTED_ZIP_LEN = ZIP_END - ZIP_START  # 3,334,421 bytes


def find_zip_bounds(data: bytes | bytearray) -> tuple[int, int]:
    """Dynamically verify zip boundaries in agy binary."""
    # Check fixed offset first
    if len(data) >= ZIP_END and data[ZIP_START:ZIP_START+4] == b"PK\x03\x04":
        if data[ZIP_END-22:ZIP_END-18] == b"PK\x05\x06":
            return ZIP_START, ZIP_END

    # Fallback: scan for the zip containing index.html
    pos = len(data)
    while True:
        pos = data.rfind(b"PK\x05\x06", 0, pos)
        if pos == -1:
            break
        eocd = data[pos:pos+22]
        _, _, _, total_records, cd_size, cd_offset, comment_len = struct.unpack("<HHHHIIH", eocd[4:22])
        zip_start = pos - (cd_size + cd_offset)
        if zip_start >= 0 and data[zip_start:zip_start+4] == b"PK\x03\x04":
            zip_end = pos + 22 + comment_len
            try:
                zf = zipfile.ZipFile(io.BytesIO(data[zip_start:zip_end]))
                if "index.html" in zf.namelist() and "main.js" in zf.namelist():
                    return zip_start, zip_end
            except Exception:
                pass
    raise RuntimeError("Failed to locate embedded web assets zip in agy binary")


def check_status(bin_path: Path) -> str:
    """Returns 'patched', 'unpatched', or 'unknown'."""
    if not bin_path.exists():
        return "missing"
    data = bin_path.read_bytes()
    zip_start, zip_end = find_zip_bounds(data)
    zf = zipfile.ZipFile(io.BytesIO(data[zip_start:zip_end]))
    html = zf.read("index.html")
    if b"? \"linux\"" in html:
        return "patched"
    if b"? \"win32\"" in html:
        return "unpatched"
    return "unknown"


def apply_patch(bin_path: Path) -> bool:
    """Applies the POSIX platform patch to agy with backup and verification."""
    if not bin_path.exists():
        print(f"ERROR: Target binary does not exist: {bin_path}", file=sys.stderr)
        return False

    status = check_status(bin_path)
    if status == "patched":
        print(f"Binary is already patched: {bin_path}")
        return True
    if status != "unpatched":
        print(f"ERROR: Cannot patch binary with status '{status}'", file=sys.stderr)
        return False

    # 1. Create timestamped backup
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_path = bin_path.with_name(f"{bin_path.name}.bak.{timestamp}")
    shutil.copy2(bin_path, backup_path)
    print(f"Created backup: {backup_path}")

    # Keep a link/copy of the first pristine original backup if not present
    orig_backup = bin_path.with_name(f"{bin_path.name}.bak.orig")
    if not orig_backup.exists():
        shutil.copy2(bin_path, orig_backup)
        print(f"Preserved original baseline backup: {orig_backup}")

    # 2. Read binary
    bin_data = bytearray(bin_path.read_bytes())
    orig_len = len(bin_data)
    zip_start, zip_end = find_zip_bounds(bin_data)
    zip_bytes = bytearray(bin_data[zip_start:zip_end])

    # 3. Read index.html from zip
    zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    info = zf.getinfo("index.html")
    orig_html = zf.read("index.html")

    target_old = b"? \"win32\""
    target_new = b"? \"linux\""
    if target_old not in orig_html:
        print("ERROR: Target string not found in index.html", file=sys.stderr)
        return False

    base_html = orig_html.replace(target_old, target_new)

    # 4. Use 2-space padding inside comment so deflate level 6 produces exactly 1616 compressed bytes
    idx = base_html.find(b"<!-- Preconnect")
    if idx == -1:
        print("ERROR: Preconnect comment not found in index.html", file=sys.stderr)
        return False

    patched_html = base_html[:idx+4] + b"  " + base_html[idx+4:]
    c = zlib.compressobj(6, zlib.DEFLATED, -15)
    comp = c.compress(patched_html) + c.flush()
    if len(comp) != info.compress_size:
        print(f"ERROR: Compressed length mismatch: got {len(comp)}, expected {info.compress_size}", file=sys.stderr)
        return False

    new_crc = zlib.crc32(patched_html) & 0xffffffff
    new_uncomp_size = len(patched_html)

    # 5. Patch local header
    hdr_off = info.header_offset
    struct.pack_into("<III", zip_bytes, hdr_off + 14, new_crc, len(comp), new_uncomp_size)

    # 6. Replace compressed bytes
    name_len = int.from_bytes(zip_bytes[hdr_off+26:hdr_off+28], "little")
    extra_len = int.from_bytes(zip_bytes[hdr_off+28:hdr_off+30], "little")
    comp_off = hdr_off + 30 + name_len + extra_len
    zip_bytes[comp_off:comp_off + len(comp)] = comp

    # 7. Patch central directory header
    cd_idx = zip_bytes.find(b"PK\x01\x02")
    cd_found = False
    while cd_idx != -1:
        entry_name_len = int.from_bytes(zip_bytes[cd_idx+28:cd_idx+30], "little")
        entry_name = zip_bytes[cd_idx+46:cd_idx+46+entry_name_len]
        if entry_name == b"index.html":
            struct.pack_into("<III", zip_bytes, cd_idx + 16, new_crc, len(comp), new_uncomp_size)
            cd_found = True
            break
        entry_extra_len = int.from_bytes(zip_bytes[cd_idx+30:cd_idx+32], "little")
        entry_comm_len = int.from_bytes(zip_bytes[cd_idx+32:cd_idx+34], "little")
        cd_idx = zip_bytes.find(b"PK\x01\x02", cd_idx + 46 + entry_name_len + entry_extra_len + entry_comm_len)

    if not cd_found:
        print("ERROR: Failed to find index.html in central directory", file=sys.stderr)
        return False

    # 8. Verify patched zip in memory
    verify_zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    test_read = verify_zf.read("index.html")
    if b"? \"linux\"" not in test_read or b"? \"win32\"" in test_read:
        print("ERROR: Verification of patched index.html failed", file=sys.stderr)
        return False

    # 9. Splice back into binary
    assert len(zip_bytes) == (zip_end - zip_start)
    bin_data[zip_start:zip_end] = zip_bytes
    assert len(bin_data) == orig_len

    # 10. Write binary safely via temp file
    temp_bin = bin_path.with_name(f"{bin_path.name}.tmp.{os.getpid()}")
    temp_bin.write_bytes(bin_data)
    os.chmod(temp_bin, 0o755)
    temp_bin.replace(bin_path)

    print(f"SUCCESS: Successfully patched {bin_path} (exact size: {len(bin_data):,} bytes)")
    return True


def restore_backup(bin_path: Path) -> bool:
    """Restores the most recent backup."""
    candidates = sorted(bin_path.parent.glob(f"{bin_path.name}.bak.*"), reverse=True)
    if not candidates:
        print(f"ERROR: No backups found for {bin_path}", file=sys.stderr)
        return False
    target_bak = candidates[0]
    shutil.copy2(target_bak, bin_path)
    os.chmod(bin_path, 0o755)
    print(f"Restored {bin_path} from {target_bak}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Surgical binary patcher for Antigravity POSIX paths.")
    parser.add_argument("--bin", type=Path, default=DEFAULT_BIN_PATH, help="Path to agy binary")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="Check current patch status")
    group.add_argument("--apply", action="store_true", help="Apply POSIX patch to agy")
    group.add_argument("--restore", action="store_true", help="Restore binary from backup")
    args = parser.parse_args()

    if args.check:
        status = check_status(args.bin)
        print(f"Antigravity binary: {args.bin}")
        print(f"Status: {status}")
        return 0 if status == "patched" else 1

    if args.apply:
        success = apply_patch(args.bin)
        return 0 if success else 1

    if args.restore:
        success = restore_backup(args.bin)
        return 0 if success else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

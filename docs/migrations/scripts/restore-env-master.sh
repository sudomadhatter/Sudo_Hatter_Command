#!/usr/bin/env bash
# restore-env-master.sh — macOS / Linux twin of Restore-EnvMaster.ps1.
#
# Splits docs/migrations/auth_keys/_secrets/master.env back into the individual
# .env / credential files it was exported from, at their original relative paths.
#
# Run from ANYWHERE (the script finds the lobby root itself — three levels up):
#   bash docs/migrations/scripts/restore-env-master.sh
#   bash docs/migrations/scripts/restore-env-master.sh --master-path /Volumes/USB/master.env
#   bash docs/migrations/scripts/restore-env-master.sh --dry-run       # show, write nothing
#
# Behavior — deliberately identical to the PowerShell original:
#   - Creates missing directories (e.g. auth_keys/) as needed.
#   - A target that already exists with DIFFERENT content is copied to
#     <name>.pre-restore.bak before being overwritten.
#   - Identical content is left alone and reported as "unchanged".
#   - Writes UTF-8 without BOM (safe for python-dotenv, Next.js, docker).
#   - Refuses absolute paths, or paths containing "..", found inside the master.
#
# WHY THIS EXISTS: Restore-EnvMaster.ps1 is path-separator-bound even under pwsh
# (it does $relPath.Replace('/', '\')), so on macOS it would write "backend\.env"
# as ONE literal filename instead of nesting it. That script is left untouched;
# this is its POSIX twin. Keep the two in sync if either changes.
#
# macOS ships bash 3.2, so nothing here uses bash 4+ syntax (no mapfile, no
# associative arrays, no ${var^^}).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"   # docs/migrations/scripts -> lobby root
MASTER_PATH=""
DRY_RUN=0

while [ $# -gt 0 ]; do
  case "$1" in
    --master-path) MASTER_PATH="${2:-}"; shift 2 ;;
    --root)        ROOT="${2:-}";        shift 2 ;;
    --dry-run)     DRY_RUN=1;            shift ;;
    -h|--help)     sed -n '2,30p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

[ -n "$MASTER_PATH" ] || MASTER_PATH="$ROOT/docs/migrations/auth_keys/_secrets/master.env"

if [ ! -f "$MASTER_PATH" ]; then
  echo "Master file not found: $MASTER_PATH" >&2
  exit 1
fi

echo "Lobby root : $ROOT"
echo "Master     : $MASTER_PATH"
[ "$DRY_RUN" -eq 1 ] && echo "MODE       : DRY RUN — nothing will be written"
echo ""

TMP_BLOCK="$(mktemp)"
trap 'rm -f "$TMP_BLOCK"' EXIT

written=0
current=""
had_lines=0

write_target() {
  rel="$1"

  # Path safety — same two rules as the PowerShell original.
  case "$rel" in
    /*|[A-Za-z]:*) echo "Unsafe path in master file (absolute): $rel" >&2; exit 1 ;;
    *..*)          echo "Unsafe path in master file (..): $rel"       >&2; exit 1 ;;
  esac

  dest="$ROOT/$rel"

  # Match the PS behavior exactly: lines joined with \n plus a trailing \n, and an
  # empty block still yields a single newline.
  if [ "$had_lines" -eq 0 ]; then printf '\n' > "$TMP_BLOCK"; fi

  if [ -f "$dest" ] && cmp -s "$TMP_BLOCK" "$dest"; then
    echo "  unchanged  $rel"
    return
  fi

  if [ "$DRY_RUN" -eq 1 ]; then
    if [ -f "$dest" ]; then echo "  WOULD back up + overwrite  $rel"; else echo "  WOULD create              $rel"; fi
    written=$((written + 1))
    return
  fi

  mkdir -p "$(dirname "$dest")"

  if [ -f "$dest" ]; then
    cp -p "$dest" "$dest.pre-restore.bak"
    echo "  backed up  $rel -> $rel.pre-restore.bak"
  fi

  cat "$TMP_BLOCK" > "$dest"
  chmod 600 "$dest"           # these are credentials; do not leave them group/world readable
  echo "  restored   $rel"
  written=$((written + 1))
}

# `|| [ -n "$line" ]` so a final line with no trailing newline is not dropped.
while IFS= read -r line || [ -n "$line" ]; do
  line="${line%$'\r'}"        # master.env is usually exported on Windows -> CRLF

  case "$line" in
    '# >>> FILE: '*)
      if [ -n "$current" ]; then
        echo "Marker mismatch: new FILE started before END of $current" >&2; exit 1
      fi
      current="${line#\# >>> FILE: }"
      current="$(printf '%s' "$current" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
      : > "$TMP_BLOCK"
      had_lines=0
      ;;
    '# <<< END FILE:'*)
      if [ -z "$current" ]; then
        echo "Marker mismatch: END without a matching FILE marker" >&2; exit 1
      fi
      write_target "$current"
      current=""
      ;;
    *)
      if [ -n "$current" ]; then
        printf '%s\n' "$line" >> "$TMP_BLOCK"
        had_lines=1
      fi
      ;;
  esac
done < "$MASTER_PATH"

if [ -n "$current" ]; then
  echo "Master file ended mid-block: $current never closed" >&2
  exit 1
fi

echo ""
if [ "$DRY_RUN" -eq 1 ]; then
  echo "Dry run complete. $written file(s) WOULD be written/updated. Re-run without --dry-run to apply."
else
  echo "Done. $written file(s) written/updated (mode 600)."
  echo "Now run the verification checklist in docs/migrations/install_guides/new_machine-migration-guide.md (section 4)."
fi

#!/usr/bin/env bash
# Installs the skills in this folder as user-level Claude Code skills (~/.claude/skills/<name>).
# Safe to re-run: it only replaces a directory that it installed itself (marked with .installed-by-claudecloudfiles).
# A same-named skill that came from somewhere else is left alone, and a warning is printed.
set -euo pipefail
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST_ROOT="${HOME}/.claude/skills"
MARKER=".installed-by-claudecloudfiles"
mkdir -p "$DEST_ROOT"
for skill in "$SRC_DIR"/*/; do
  name="$(basename "$skill")"
  [ -f "$skill/SKILL.md" ] || continue
  dest="$DEST_ROOT/$name"
  if [ -e "$dest" ] && [ ! -f "$dest/$MARKER" ]; then
    echo "skip $name: $dest exists and was not installed by this script (not overwriting)" >&2
    continue
  fi
  rm -rf "$dest"
  cp -R "$skill" "$dest"
  touch "$dest/$MARKER"
  chmod +x "$dest"/scripts/*.py 2>/dev/null || true
  echo "installed $name -> $dest"
done

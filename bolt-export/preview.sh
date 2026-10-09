#!/usr/bin/env bash
# Preview the Knowledge Centre inside a COPY of the Bolt site.
#   ./bolt-export/preview.sh /path/to/adsyet-mainsite [work-dir]
# Copies the Bolt project (never modifies it), overlays bolt-export/, then
# type-checks, lints, builds and starts the dev server on :5199.
set -euo pipefail
SRC="${1:?path to adsyet-mainsite clone}"
WORK="${2:-${TMPDIR:-/tmp}/kc-preview}"
HERE="$(cd "$(dirname "$0")" && pwd)"

mkdir -p "$WORK"
(cd "$SRC" && tar --exclude=./.git --exclude=./node_modules --exclude=./dist -cf - .) | (cd "$WORK" && tar -xf -)
cp -a "$HERE"/src/. "$WORK"/src/
cp -a "$HERE"/public/. "$WORK"/public/
[ -e "$WORK/node_modules" ] || ln -s "$SRC/node_modules" "$WORK/node_modules"

cd "$WORK"
echo "== typecheck";  npx tsc --noEmit -p tsconfig.app.json
echo "== lint";       npx eslint src/App.tsx src/components/Navigation.tsx src/components/knowledge-centre src/pages src/hooks src/lib src/data
echo "== build";      npx vite build --logLevel warn
echo "== dev server on http://localhost:5199/resources/"
exec npx vite --port 5199 --strictPort

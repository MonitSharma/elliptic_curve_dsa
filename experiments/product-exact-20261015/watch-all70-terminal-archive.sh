#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-exact-20261015
d=$r/all70-complete-20261016
mkdir -p "$d"
cd "$r"
echo $$ > "$d/launcher.pid"
trap 'echo $? > "$d/launcher.exit"' EXIT
while true; do
 if [ -f "$r/all70-native67-20261016/census-launcher.exit" ]; then break; fi
 if [ -f "$r/all70-cache67-20261016/cache-launcher.exit" ] && [ "$(cat "$r/all70-cache67-20261016/cache-launcher.exit")" != 0 ]; then break; fi
 if [ -f "$r/all70-native67-20261016/launcher.exit" ] && [ "$(cat "$r/all70-native67-20261016/launcher.exit")" != 0 ]; then break; fi
 sleep 15
done
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 16777216
python3 "$r/collect_all70_terminal.py" > "$d/collect.log" 2>&1

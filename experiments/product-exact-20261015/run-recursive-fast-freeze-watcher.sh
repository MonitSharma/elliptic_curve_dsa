#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > recursive-fast-freeze-watcher.pid
trap 'rc=$?; echo "$rc" > "$root/recursive-fast-freeze-watcher.exit"' EXIT
while [ ! -f recursive-unfold-fast-20261016/launcher.exit ]; do sleep 20; done
test "$(cat recursive-unfold-fast-20261016/launcher.exit)" = 0
python3 freeze_recursive_fast.py > recursive-fast-freeze.log

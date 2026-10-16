#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > repair67-freeze-watcher.pid
trap 'rc=$?; echo "$rc" > "$root/repair67-freeze-watcher.exit"' EXIT
while [ ! -f repair-to67-rank-20261016/launcher.exit ]; do sleep 20; done
test "$(cat repair-to67-rank-20261016/launcher.exit)" = 0
python3 freeze_repair67.py > repair67-freeze.log
echo FIXED_REPAIRED67_ENDPOINT_FROZEN_NATIVE_AND_CENSUS_NOT_LAUNCHED

#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > product95-freeze-watcher.pid
trap 'rc=$?; echo "$rc" > "$root/product95-freeze-watcher.exit"' EXIT
while [ ! -f product-to95-rank-20261016/launcher.exit ]; do sleep 20; done
test "$(cat product-to95-rank-20261016/launcher.exit)" = 0
python3 freeze95.py product > product95-freeze.log
echo PREDECLARED_PRODUCT95_FINAL_SOURCE_FROZEN_NO_CENSUS_OR_NONCE

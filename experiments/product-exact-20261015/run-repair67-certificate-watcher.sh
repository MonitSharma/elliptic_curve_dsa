#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > repair67-certificate-watcher.pid
trap 'rc=$?; echo "$rc" > "$root/repair67-certificate-watcher.exit"' EXIT
while [ ! -f repair67-universal-20261016/launcher.exit ]; do sleep 20; done
test "$(cat repair67-universal-20261016/launcher.exit)" = 0
python3 audit_repair67.py consolidate > repair67-universal-20261016/consolidation.log 2>&1
echo COMPOSED_A29_RELATIVE67_CERTIFICATE_AND_PER_INPUT_TRANSFER_FROZEN

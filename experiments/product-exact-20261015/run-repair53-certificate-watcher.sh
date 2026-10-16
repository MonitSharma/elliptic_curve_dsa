#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > repair53-certificate-watcher.pid
trap 'rc=$?; echo "$rc" > "$root/repair53-certificate-watcher.exit"' EXIT
while [ ! -f repair53-universal-20261016/launcher.exit ]; do sleep 20; done
test "$(cat repair53-universal-20261016/launcher.exit)" = 0
python3 consolidate_repair53_certificate.py > repair53-universal-20261016/consolidation.log
echo A29_RELATIVE53_CERTIFICATE_AND_SEPARATE_CONDITIONAL_MASK_COMPANION_FROZEN

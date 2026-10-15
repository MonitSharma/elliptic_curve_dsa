#!/bin/bash
set -u
ulimit -c 0
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/shadow-opaque-merged.pid
trap 'echo $? > evidence/shadow-opaque-merged.exit' EXIT
input=opaque-merged-v1-proof-spans.tsv
free -m > evidence/shadow-opaque-merged.resources
sha256sum tool/target/release/shadow_value_scan "$input" ../product-exact-20261015/tip/ops.bin > evidence/shadow-opaque-merged-before.sha256
prlimit --as=8589934592 -- tool/target/release/shadow_value_scan ../product-exact-20261015/tip/ops.bin "$input" > evidence/shadow-opaque-merged.json 2> evidence/shadow-opaque-merged.log || exit $?
sha256sum tool/target/release/shadow_value_scan "$input" ../product-exact-20261015/tip/ops.bin > evidence/shadow-opaque-merged-after.sha256
cmp evidence/shadow-opaque-merged-before.sha256 evidence/shadow-opaque-merged-after.sha256

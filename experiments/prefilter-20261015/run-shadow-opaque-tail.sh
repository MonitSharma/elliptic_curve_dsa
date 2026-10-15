#!/bin/bash
set -u
ulimit -c 0
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/shadow-opaque-tail.pid
trap 'echo $? > evidence/shadow-opaque-tail.exit' EXIT
input=/home/hclau/ecdsa_research/prefilter-macro-20261016/additional/opaque-tail-v1-proof-spans.tsv
free -m > evidence/shadow-opaque-tail.resources
sha256sum tool/target/release/shadow_value_scan "$input" ../product-exact-20261015/tip/ops.bin > evidence/shadow-opaque-tail-before.sha256
prlimit --as=8589934592 -- tool/target/release/shadow_value_scan ../product-exact-20261015/tip/ops.bin "$input" > evidence/shadow-opaque-tail.json 2> evidence/shadow-opaque-tail.log || exit $?
sha256sum tool/target/release/shadow_value_scan "$input" ../product-exact-20261015/tip/ops.bin > evidence/shadow-opaque-tail-after.sha256
cmp evidence/shadow-opaque-tail-before.sha256 evidence/shadow-opaque-tail-after.sha256

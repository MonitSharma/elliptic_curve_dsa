#!/bin/bash
set -u
ulimit -c 0
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/reset-projection-complete-helpers.pid
trap 'echo $? > evidence/reset-projection-complete-helpers.exit' EXIT
export RAYON_NUM_THREADS=1
free -m > evidence/reset-projection-complete-helpers.resources
input=/home/hclau/ecdsa_research/prefilter-macro-20261016/additional/complete-helper-proof-spans.tsv
sha256sum tool/target/release/reset_projection_external tool/target/release/shadow_value_scan "$input" ../product-exact-20261015/tip/ops.bin > evidence/reset-projection-complete-helpers-before.sha256
prlimit --as=8589934592 -- tool/target/release/reset_projection_external ../product-exact-20261015/tip/ops.bin evidence/reset-projection-complete-helpers 100000 "$input" > evidence/reset-projection-complete-helpers.report.log 2> evidence/reset-projection-complete-helpers.progress.log || exit $?
prlimit --as=8589934592 -- tool/target/release/shadow_value_scan ../product-exact-20261015/tip/ops.bin "$input" > evidence/shadow-value-complete-helpers.json 2> evidence/shadow-value-complete-helpers.log || exit $?
sha256sum tool/target/release/reset_projection_external tool/target/release/shadow_value_scan "$input" ../product-exact-20261015/tip/ops.bin > evidence/reset-projection-complete-helpers-after.sha256
cmp evidence/reset-projection-complete-helpers-before.sha256 evidence/reset-projection-complete-helpers-after.sha256

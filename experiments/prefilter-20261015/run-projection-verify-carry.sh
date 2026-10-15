#!/bin/bash
set -u
ulimit -c 0
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/projection-verify-carry.pid
trap 'echo $? > evidence/projection-verify-carry.exit' EXIT
export RAYON_NUM_THREADS=1
free -m > evidence/projection-verify-carry.resources
summaries="evidence/reset-projection-tip.summary.json evidence/reset-projection-symbols-tip.summary.json evidence/reset-projection-comparators.summary.json evidence/reset-projection-top1-complete.summary.json evidence/reset-projection-all-scopes-tip.summary.json evidence/reset-projection-carry.summary.json"
sha256sum tool/target/release/projection_verify $summaries ../product-exact-20261015/tip/ops.bin > evidence/projection-verify-carry-before.sha256
for name in all-failing-tip sensitivity-structured sensitivity-arbitrary; do
prlimit --as=8589934592 -- tool/target/release/projection_verify ../product-exact-20261015/tip/ops.bin packets/$name.tsv 32 $summaries > evidence/projection-verify-carry-$name.json 2> evidence/projection-verify-carry-$name.log || exit $?
done
sha256sum tool/target/release/projection_verify $summaries ../product-exact-20261015/tip/ops.bin > evidence/projection-verify-carry-after.sha256
cmp evidence/projection-verify-carry-before.sha256 evidence/projection-verify-carry-after.sha256

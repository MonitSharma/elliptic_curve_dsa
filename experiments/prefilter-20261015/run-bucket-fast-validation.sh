#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
trap 'echo $? > /home/hclau/ecdsa_research/prefilter-20261015/evidence/bucket-fast-validation.exit' EXIT
export RAYON_NUM_THREADS=1
while ! test -f evidence/bucket-validation.exit; do sleep 2; done
free -m > evidence/bucket-fast-validation.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -45 >> evidence/bucket-fast-validation.resources
OPS=/home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin
RAIL_SHADOW=1 tool/target/release/bucket_fast_screen "$OPS" 1 128 2 evidence/bucket-fast-shadow-128.jsonl model-source 128 > evidence/bucket-fast-shadow-128.log 2> evidence/bucket-fast-shadow-128.err || exit $?
tool/target/release/bucket_fast_screen "$OPS" 1 128 2 evidence/bucket-fast-128.jsonl model-source 128 > evidence/bucket-fast-128.log 2> evidence/bucket-fast-128.err || exit $?
tool/target/release/bucket_fast_screen "$OPS" 1 1024 2 evidence/bucket-fast-1024.jsonl model-source 128 > evidence/bucket-fast-1024.log 2> evidence/bucket-fast-1024.err || exit $?
tool/target/release/bucket_fast_screen "$OPS" 1046072871506 9 2 evidence/bucket-fast-positive9.jsonl model-source 128 > evidence/bucket-fast-positive9.log 2> evidence/bucket-fast-positive9.err || exit $?
sha256sum tool/target/release/bucket_fast_screen tool/src/bucket_fast_screen_body.rs tool/src/simd_screen_ffi.rs tool/src/rail_fast_ffi.rs tool/src/rail_advisory.rs > evidence/bucket-fast.sha256
exit 0

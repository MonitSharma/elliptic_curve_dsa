#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
trap 'echo $? > /home/hclau/ecdsa_research/prefilter-20261015/evidence/advisory-validation.exit' EXIT
export RAYON_NUM_THREADS=1
free -m > evidence/advisory-validation.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -45 >> evidence/advisory-validation.resources
OPS=/home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin
tool/target/release/advisory_screen "$OPS" 1 128 2 evidence/advisory-128.jsonl model-source > evidence/advisory-128.log 2> evidence/advisory-128.err
code=$?
if test "$code" -ne 0; then exit "$code"; fi
ADVISORY_MODE=off tool/target/release/advisory_screen "$OPS" 1 128 2 evidence/simd-ascending-128.jsonl model-source > evidence/simd-ascending-128.log 2> evidence/simd-ascending-128.err
code=$?
if test "$code" -ne 0; then exit "$code"; fi
ADVISORY_FORCE_BATCH=7 tool/target/release/advisory_screen "$OPS" 1046072871510 1 1 evidence/advisory-positive.jsonl model-source > evidence/advisory-positive.log 2> evidence/advisory-positive.err
exit $?

#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
trap 'echo $? > /home/hclau/ecdsa_research/prefilter-20261015/evidence/bucket-scale-validation.exit' EXIT
export RAYON_NUM_THREADS=1
while ! test -f evidence/bucket-fast-validation.exit; do sleep 2; done
free -m > evidence/bucket-scale-validation.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -60 >> evidence/bucket-scale-validation.resources
OPS=/home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin
tool/target/release/bucket_fast_screen "$OPS" 1 1024 2 evidence/bucket-fast-look1024-t2.jsonl model-source 1024 > evidence/bucket-fast-look1024-t2.log 2> evidence/bucket-fast-look1024-t2.err || exit $?
tool/target/release/bucket_fast_screen "$OPS" 1 1024 16 evidence/bucket-fast-look1024-t16.jsonl model-source 1024 > evidence/bucket-fast-look1024-t16.log 2> evidence/bucket-fast-look1024-t16.err || exit $?
exit 0

#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015/scalar-split-v1
echo $$ > run-v2.pid
trap 'echo $? > run-v2.exit' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
free -m > resources-v2.log
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -25 >> resources-v2.log
printf '%s  %s\n' 3bb2304219fb336795ea88d4bf81174883cdd33702f5975819b812c3dffca30f ../../scalar-fast-20261015/libscalar_fast_batch.so | sha256sum --check || exit $?
cmp scalar_batch_original.c ../../scalar-fast-20261015/scalar_batch.c || exit $?
sha256sum scalar_batch_original.c public_comb.h scalar_split.c scalar_split.h libscalar_split.so validate-bench-v2.py ../../scalar-fast-20261015/scalar_batch.c ../../scalar-fast-20261015/libscalar_fast_batch.so > before-v2.sha256
timeout 600 /usr/bin/time -v prlimit --as=8589934592 -- python3 validate-bench-v2.py > validation-benchmark-v2.log 2> validation-benchmark-v2.err || exit $?
sha256sum scalar_batch_original.c public_comb.h scalar_split.c scalar_split.h libscalar_split.so validate-bench-v2.py ../../scalar-fast-20261015/scalar_batch.c ../../scalar-fast-20261015/libscalar_fast_batch.so > after-v2.sha256
cmp before-v2.sha256 after-v2.sha256

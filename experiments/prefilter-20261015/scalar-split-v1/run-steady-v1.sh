#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015/scalar-split-v1
echo $$ > steady-v1.pid
trap 'echo $? > steady-v1.exit' EXIT
export OMP_NUM_THREADS=1 RAYON_NUM_THREADS=1
free -m > steady-v1.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -20 >> steady-v1.resources
sha256sum scalar_split.c libscalar_split.so bench-steady-v1.py ../../scalar-fast-20261015/libscalar_fast_batch.so > steady-v1-before.sha256
timeout 600 /usr/bin/time -v prlimit --as=8589934592 -- python3 bench-steady-v1.py > steady-v1.log 2> steady-v1.err || exit $?
sha256sum scalar_split.c libscalar_split.so bench-steady-v1.py ../../scalar-fast-20261015/libscalar_fast_batch.so > steady-v1-after.sha256
cmp steady-v1-before.sha256 steady-v1-after.sha256

#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > a29-conditional-coverage-v1/run.pid
trap 'echo $? > a29-conditional-coverage-v1/run.exit' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
free -m > a29-conditional-coverage-v1/resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -25 >> a29-conditional-coverage-v1/resources
sha256sum a29-conditional-coverage-v1/coverage.py a29-conditional-prefix-v1/public-discrepancy-guard.bin ../mask-evaluator-20261016/libmask8.so ../scalar-fast-20261015/libscalar_fast_batch.so > a29-conditional-coverage-v1/before.sha256
timeout 180 /usr/bin/time -v prlimit --as=8589934592 -- python3 a29-conditional-coverage-v1/coverage.py > a29-conditional-coverage-v1/result.log 2> a29-conditional-coverage-v1/stderr.log || exit $?
sha256sum a29-conditional-coverage-v1/coverage.py a29-conditional-prefix-v1/public-discrepancy-guard.bin ../mask-evaluator-20261016/libmask8.so ../scalar-fast-20261015/libscalar_fast_batch.so > a29-conditional-coverage-v1/after.sha256
cmp a29-conditional-coverage-v1/before.sha256 a29-conditional-coverage-v1/after.sha256

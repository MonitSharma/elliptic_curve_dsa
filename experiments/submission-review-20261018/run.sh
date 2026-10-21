#!/bin/bash
set -u
cd "/home/hclau/ecdsa_research/wide95-703-review-20261018-085419/candidate"
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 100663296
/usr/bin/time -v ./benchmark.sh > ../benchmark.log 2>&1
rc=$?
echo "$rc" > ../benchmark.exit
exit "$rc"

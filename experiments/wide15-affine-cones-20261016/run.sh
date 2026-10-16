#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/wide15-affine-cones-20261016
echo $$ > run.pid
trap 'rc=$?; echo "$rc" > run.exit' EXIT
ulimit -v 12582912
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
timeout --signal=TERM --kill-after=10 900 bash -c 'python3 -u tests.py && python3 -u cone-tests.py && python3 -u scan.py'

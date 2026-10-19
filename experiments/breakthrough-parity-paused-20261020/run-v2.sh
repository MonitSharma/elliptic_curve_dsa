#!/usr/bin/env bash
set -u
cd /home/hclau/ecdsa_research/breakthrough-parity-paused-20261020 || exit 1
export CARGO_BUILD_JOBS=2 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 33554432
python3 repair-v2.py > repair-v2.log 2>&1
exit $?

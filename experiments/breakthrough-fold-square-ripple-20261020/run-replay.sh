#!/usr/bin/env bash
set -u
cd /home/hclau/ecdsa_research/breakthrough-fold-square-ripple-20261020 || exit 1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 33554432
python3 replay.py > replay.log 2>&1
exit $?

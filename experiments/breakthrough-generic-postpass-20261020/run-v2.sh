#!/usr/bin/env bash
set -u
cd /home/hclau/ecdsa_research/breakthrough-generic-postpass-20261020 || exit 1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 33554432
python3 audit-v2.py > audit-v2.log 2>&1
rc=$?
printf '%s\n' "$rc" > run-v2.exit
exit "$rc"

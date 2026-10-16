#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/wide15-retained4096-20261016
echo $$ > launcher.pid
trap 'rc=$?; echo "$rc" > launcher.exit' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 run.py

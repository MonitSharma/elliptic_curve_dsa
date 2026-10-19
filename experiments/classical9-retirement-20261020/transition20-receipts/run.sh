#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/classical9-retirement-20261020
trap 'rc=$?; printf "%s\n" "$rc" > run.exit' EXIT
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 RAYON_NUM_THREADS=1
python3 audit_and_launch.py

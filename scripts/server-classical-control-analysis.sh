#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/overnight-20261014
evidence=coordinator-classical-controls
mkdir -p "$evidence"
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"' EXIT
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 8388608
date -u
hostname
python3 ../server-preflight.py
git -C ../product rev-parse HEAD
sha256sum analyze-classical-controls.py analyze-wire-lifetimes.py server-classical-control-analysis.sh ../product/ops.bin
/usr/bin/time -v python3 analyze-classical-controls.py ../product/ops.bin "$evidence/analysis.json"

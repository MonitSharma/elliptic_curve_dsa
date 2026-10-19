#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-classical-nine-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-classical-nine-20261019/gate.exit' EXIT
export RESEARCH_SLOTS=3 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 RAYON_NUM_THREADS=1
python3 ../autonomous-20261019/preflight_v7.py > gate-preflight.json
sha256sum qualify.py run-gate.sh refresh_record.py ../autonomous-20261019/preflight_v7.py > GATE_DRIVER.sha256
ulimit -v 33554432
python3 qualify.py

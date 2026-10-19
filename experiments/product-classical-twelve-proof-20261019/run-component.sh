#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-classical-twelve-proof-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-classical-twelve-proof-20261019/component.exit' EXIT
python3 ../autonomous-20261019/preflight_v11.py > component-preflight.json
sha256sum component.py run-component.sh ../autonomous-20261019/preflight_v11.py > COMPONENT_SOURCE.sha256
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 33554432
python3 component.py > component.log 2>&1

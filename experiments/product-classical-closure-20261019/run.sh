#!/bin/bash
set -euo pipefail
cd /mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments/product-classical-closure-20261019
trap 'rc=$?; printf "%s\n" "$rc" > run.exit' EXIT
sha256sum research-tool.bin input.ops.bin launch_local.py run.sh STATUS.md > SOURCE.sha256
ulimit -v 12582912
export CLASSICAL_WIDE_CAP=9 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 RAYON_NUM_THREADS=1
/usr/bin/time -v ./research-tool.bin input.ops.bin closure9 2ef31475f03b40a72d5522d830717aef4c1675d0e1a061bf0bfed78ab7d2f265 > closure.log 2>&1

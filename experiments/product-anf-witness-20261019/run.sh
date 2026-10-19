#!/bin/bash
set -euo pipefail
cd /mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments/product-anf-witness-20261019
trap 'rc=$?; printf "%s\n" "$rc" > run.exit' EXIT
sha256sum *.py *.rs run.sh STATUS.md > SOURCE.sha256
python3 run.py

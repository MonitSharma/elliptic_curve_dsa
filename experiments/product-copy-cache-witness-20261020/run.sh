#!/bin/bash
set -euo pipefail
cd /mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments/product-copy-cache-witness-20261020
trap 'rc=$?; printf "%s\n" "$rc" > run.exit' EXIT
sha256sum *.py *.rs run.sh PLAN.md > SOURCE.sha256
python3 run.py

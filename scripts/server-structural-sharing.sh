#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/followup-20261015
cd "$root"
trap 'rc=$?; printf "%s\n" "$rc" > audit.exit' EXIT
ulimit -v 4194304
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
hostname
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json
git -C /home/hclau/ecdsa_research/product rev-parse HEAD
git -C /home/hclau/ecdsa_research/product status --short
sha256sum *.py server-structural-sharing.sh > audit-source.sha256
python3 audit-structural-sharing.py /home/hclau/ecdsa_research/product/ops.bin c5-structural.json
python3 audit-structural-sharing.py /home/hclau/ecdsa_research/overnight-20261014/product-evidence/b3-baseline/run/ops.bin b3-structural.json

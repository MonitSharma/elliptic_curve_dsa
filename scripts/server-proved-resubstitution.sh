#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/followup-20261015
cd "$root"
trap 'rc=$?; printf "%s\n" "$rc" > proof-search.exit' EXIT
ulimit -v 8388608
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > proof-search-preflight.json
sha256sum search-proved-resubstitution.py analyze-wire-lifetimes.py server-proved-resubstitution.sh > proof-search-source.sha256
/home/hclau/ecdsa_research/.venv/bin/python search-proved-resubstitution.py /home/hclau/ecdsa_research/overnight-20261014/product-evidence/b3-baseline/run/ops.bin b3-resubstitution

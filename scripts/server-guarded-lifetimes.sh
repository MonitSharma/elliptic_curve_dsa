#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014
evidence="$root/${1:-coordinator-guarded-lifetimes-v1}"
mkdir -p "$evidence"
trap 'code=$?; printf "%s\n" "$code" > "$evidence/run.exit"' EXIT
ulimit -v 8388608
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
date -u
hostname
python3 /home/hclau/ecdsa_research/server-preflight.py
sha256sum "$root/analyze-guarded-lifetimes.py" "$root/analyze-wire-lifetimes.py" "$root/test_guarded_lifetimes.py" "$root/server-guarded-lifetimes.sh" > "$evidence/source.sha256"
cd "$root"
python3 -m unittest test_guarded_lifetimes
/usr/bin/time -v python3 analyze-guarded-lifetimes.py /home/hclau/ecdsa_research/product/ops.bin "$evidence/analysis.json"

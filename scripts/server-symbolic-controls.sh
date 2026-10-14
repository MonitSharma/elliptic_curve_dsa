#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014
evidence="$root/coordinator-symbolic-controls-v2"
mkdir -p "$evidence"
echo "$$" > "$evidence/run.pid"
trap 'code=$?; printf "%s\n" "$code" > "$evidence/run.exit"' EXIT
ulimit -v 8388608
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
date -u
hostname
python3 /home/hclau/ecdsa_research/server-preflight.py > "$evidence/preflight.json"
sha256sum "$root/analyze-symbolic-controls.py" "$root/test_symbolic_controls.py" "$root/server-symbolic-controls.sh" "$root/analyze-wire-lifetimes.py" > "$evidence/source.sha256"
cd "$root"
python3 -m unittest test_symbolic_controls
/usr/bin/time -v timeout 900 python3 analyze-symbolic-controls.py /home/hclau/ecdsa_research/product/ops.bin "$evidence/analysis.json"

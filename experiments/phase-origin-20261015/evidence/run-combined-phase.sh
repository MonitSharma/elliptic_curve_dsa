#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/phase-origin-20261015
prior=/home/hclau/ecdsa_research/repair-integration-20261015
echo $$ > "$root/combined-phase.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/combined-phase.exit"' EXIT
ulimit -v 16777216
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/combined-phase-preflight.json"
sha256sum "$prior/witness-target/release/product_paired_diagnostic" "$prior/combined-b3/ops.bin" "$prior/packets/structured.tsv" > "$root/combined-phase-inputs.sha256"
/usr/bin/time -v "$prior/witness-target/release/product_paired_diagnostic" "$prior/combined-b3/ops.bin" "$prior/packets/structured.tsv" > "$root/combined-phase.log" 2>&1

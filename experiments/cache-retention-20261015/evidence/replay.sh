#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/cache-retention-20261015
old=/home/hclau/ecdsa_research/toffoli-readiness-20261015
base=/home/hclau/ecdsa_research/overnight-20261014/product-evidence/b3-baseline/run/ops.bin
echo $$ > "$root/replay.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/replay.exit"' EXIT
ulimit -v 16777216
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/replay-preflight.json"
sha256sum "$old/wide-replay/paired_diagnostic" "$old/wide-replay/crate/src/main.rs" > "$root/replay-binary-source.sha256"
for family in independent structured; do
  /usr/bin/time -v "$old/wide-replay/paired_diagnostic" "$base" "$root/128-1000000.bin" "$root/128-1000000-generation.log" "$family" "$root/$family.tsv" > "$root/$family.log" 2>&1
  cmp "$root/$family.tsv" "$old/wide-replay/$family.tsv"
done
sha256sum "$root"/*.tsv "$root/independent.log" "$root/structured.log" > "$root/replay-bindings.sha256"

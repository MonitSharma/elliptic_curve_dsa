#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/followup-20261015
old=/home/hclau/ecdsa_research/overnight-20261014
evidence="$root/guarded-zero-paired"
mkdir -p "$evidence"
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"' EXIT
ulimit -v 16777216
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$evidence/preflight.json"
test -e "$root/guarded-zero-evidence-v2/benchmark.exit"
test -e "$root/b3-guarded-zero/ops.bin"
test "$(grep -c 'GUARDED_ZERO removed=2 ' "$root/guarded-zero-evidence-v2/benchmark.log")" = 1
binary="$old/product-b3-replay-target/release/product_paired_diagnostic"
base="$old/product-evidence/b3-baseline/run/ops.bin"
candidate="$root/b3-guarded-zero/ops.bin"
sha256sum "$binary" "$base" "$candidate" "$old/product-b3-replay/src/main.rs" > "$evidence/bindings.sha256"
for family in independent structured candidate; do
 /usr/bin/time -v "$binary" "$base" "$candidate" "$family" "$evidence/$family.tsv" > "$evidence/$family.log" 2>&1
done
sha256sum "$evidence"/*.tsv > "$evidence/packets.sha256"

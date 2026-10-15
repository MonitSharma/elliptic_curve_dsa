#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/rail-repair-20261015
old=/home/hclau/ecdsa_research/arithmetic-repair-20261015
echo $$ > "$root/known.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/known.exit"' EXIT
ulimit -v 16777216
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/known-preflight.json"
python3 "$root/prepare-known.py"
for mode in baseline repair; do
  test -f "$root/flex-$mode-stream.sha256"
  /usr/bin/time -v "$old/fixed-target/release/product_paired_diagnostic" "$root/flex-$mode-b3/ops.bin" "$root/known15.tsv" > "$root/known-$mode.log" 2>&1
done
sha256sum "$root"/known-*.log > "$root/known-logs.sha256"

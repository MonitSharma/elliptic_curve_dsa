#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/shake8-20261015
echo $$ > variants-bench.pid
trap 'rc=$?; echo "$rc" > variants-bench.exit' EXIT
# Four-round unrolling does not compile in the pinned upstream source.
# Preserve that failed build; benchmark the independently validated variants.
for round in 1 2; do
 for variant in baseline full; do
  SHAKE8_LIB="libshake8-$variant.so" python3 bench-select.py > "$variant-select-$round.jsonl"
 done
done
sha256sum libshake8-baseline.so libshake8-full.so > variants.sha256

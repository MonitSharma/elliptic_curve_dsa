#!/usr/bin/env bash
set -euo pipefail
evidence=/home/hclau/ecdsa_research/overnight-20261014/product-evidence/classical-xor-factors
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/paired.exit"' EXIT
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 16777216
runner=/home/hclau/ecdsa_research/overnight-20261014/product-replay/target/release/product_paired_diagnostic
base=/home/hclau/ecdsa_research/product/ops.bin
candidate="$evidence/ops.bin"
sha256sum "$runner" "$base" "$candidate" > "$evidence/paired-inputs.sha256"
date -u
/usr/bin/time -v "$runner" "$base" "$candidate" baseline "$evidence/baseline-packet.tsv"
/usr/bin/time -v "$runner" "$base" "$candidate" independent "$evidence/independent.tsv"
/usr/bin/time -v "$runner" "$base" "$candidate" structured "$evidence/structured.tsv"
date -u

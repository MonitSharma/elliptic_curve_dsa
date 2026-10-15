#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/zero-mr-slice-20261016
echo $$ > publish.pid
trap 'rc=$?; echo "$rc" > publish.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > publish-preflight.json
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
python3 prepare.py
(cd tool; cargo build --release --locked --offline > ../publish-build.log 2>&1)
cc -O3 -march=skylake-avx512 -fPIC -shared -Itool tool/zero8.c -o libzero8_slice.new.so
mv libzero8_slice.new.so libzero8_slice.so
INPUT=/home/hclau/ecdsa_research/prefilter-20261015/evidence/census-coordinates4096.tsv
tool/target/release/product_paired_diagnostic /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin "$INPUT" tip.compact16.bin > tip-published.log 2>&1
tool/target/release/product_paired_diagnostic /home/hclau/ecdsa_research/product-exact-20261015/candidate-final/ops.bin "$INPUT" candidate.compact16.bin > candidate-published.log 2>&1
sha256sum tool/src/main.rs tool/zero8.c libzero8_slice.so tip.compact16.bin candidate.compact16.bin > published.sha256

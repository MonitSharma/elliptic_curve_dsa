#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/hclau/ecdsa_research/zero-known-cone-20261016
cd "$ROOT"
echo $$ > run.pid
trap 'rc=$?; echo "$rc" > "$ROOT/run.exit"' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 prepare.py > prepare.log 2>&1
(cd tool; cargo build --release --locked --offline > ../build.log 2>&1)
tool/target/release/product_paired_diagnostic /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin /home/hclau/ecdsa_research/prefilter-20261015/evidence/census-coordinates4096.tsv tip-known49.compact16.bin > validation.log 2>&1
sha256sum tip-known49.compact16.bin tool/src/main.rs tool/zero8.c > source-and-program.sha256

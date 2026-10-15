#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/hclau/ecdsa_research/repair-zero-mr-20261016
cd "$ROOT"
echo $$ > run.pid
trap 'rc=$?; echo "$rc" > "$ROOT/run.exit"' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 prepare.py > prepare.log 2>&1
(cd tool; cargo build --release --locked --offline > ../build.log 2>&1)
INPUT=/home/hclau/ecdsa_research/product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin
sha256sum "$INPUT" > input-before.sha256
grep -q '^1cd3457b44bd21d65921ce0d5b8352573a9c6f2bb2706430d367f68e5a7e5522 ' input-before.sha256
tool/target/release/product_paired_diagnostic "$INPUT" /home/hclau/ecdsa_research/prefilter-20261015/evidence/census-coordinates4096.tsv repair.compact16.bin > validation.log 2>&1
sha256sum "$INPUT" > input-after.sha256
cmp input-before.sha256 input-after.sha256
sha256sum repair.compact16.bin tool/src/main.rs tool/zero8.c > published.sha256

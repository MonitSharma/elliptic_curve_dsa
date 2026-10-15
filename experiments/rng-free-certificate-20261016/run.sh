#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/rng-free-certificate-20261016
echo $$ > run.pid
trap 'rc=$?; echo "$rc" > run.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
python3 prepare.py
(cd tool; cargo build --release --locked --offline > ../build.log 2>&1)
tool/target/release/product_paired_diagnostic /home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin /home/hclau/ecdsa_research/prefilter-20261015/evidence/census-coordinates4096.tsv > verify.log 2>&1
sha256sum main.rs tri.rs tool/target/release/product_paired_diagnostic > source.sha256

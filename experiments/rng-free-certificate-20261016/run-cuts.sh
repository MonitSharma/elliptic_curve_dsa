#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/rng-free-certificate-20261016
echo $$ > cuts.pid
trap 'rc=$?; echo "$rc" > cuts.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > cuts-preflight.json
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
python3 prepare.py
(cd tool; cargo build --release --locked --offline > ../cuts-build.log 2>&1)
tool/target/release/product_paired_diagnostic /home/hclau/ecdsa_research/payload-model-20261016/before-census.bin /home/hclau/ecdsa_research/prefilter-20261015/evidence/census-coordinates4096.tsv /home/hclau/ecdsa_research/payload-model-20261016/cut-guards.csv > cuts-verify.log 2>&1
sha256sum main.rs tri.rs tool/target/release/product_paired_diagnostic > cuts-source.sha256

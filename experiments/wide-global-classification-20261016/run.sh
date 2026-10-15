#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/wide-global-classification-20261016
echo $$ > run.pid
trap 'echo $? > run.exit' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json
ulimit -v 16777216
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/product-exact-20261015/target-endpoint-census
export PATH=/home/hclau/.cargo/bin:$PATH
python3 prepare.py > prepare.log 2>&1
cargo build --release --offline --locked --manifest-path tool/Cargo.toml > build.log 2>&1
sha256sum /home/hclau/ecdsa_research/wide15-record-20261016/evidence/final-ops.bin > input.sha256
grep -q '^1d8c05eeee7b43dd694506b5efe963c771461b7e690bc62f409947b2306b7d77 ' input.sha256
/usr/bin/time -v timeout 600 "$CARGO_TARGET_DIR/release/value_prefilter" /home/hclau/ecdsa_research/wide15-record-20261016/evidence/final-ops.bin > sites.jsonl 2> census.log
python3 summarize.py > summary.log 2>&1

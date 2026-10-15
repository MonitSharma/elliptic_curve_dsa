#!/bin/bash
set -euo pipefail
root=/home/hclau/ecdsa_research/guard-tree-20261015
cd "$root"
echo $$ > run.pid
trap 's=$?;echo "$s" > "$root/run.exit"' EXIT
ulimit -v 52428800
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json
cd tool
cargo test --release --locked --offline guard_tree_ -- --nocapture > ../tests.log 2>&1
cargo build --release --locked --offline > ../build.log 2>&1
cd "$root"
mkdir -p wide
base=/home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin
tool=./tool/target/release/product_paired_diagnostic
"$tool" "$base" 1 wide/one.bin > wide/one.log 2>&1
"$tool" verify "$base" wide/one.bin /home/hclau/ecdsa_research/arithmetic-repair-20261015/packets/independent.tsv 4 guard-tree-paired-v1 > wide/paired.log 2>&1
sha256sum wide/one.bin > wide/one.sha256

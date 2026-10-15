#!/bin/bash
set -euo pipefail
root=/home/hclau/ecdsa_research/guard-tree-20261015
cd "$root"
echo $$ > phase.pid
trap 's=$?;echo "$s" > "$root/phase.exit"' EXIT
ulimit -v 52428800
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > phase-preflight.json
cd tool
cargo test --release --locked --offline phase_expand_ -- --nocapture > ../phase-tests.log 2>&1
cargo build --release --locked --offline > ../phase-build.log 2>&1
cd "$root"
mkdir -p phase
base=/home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin
tool=./tool/target/release/product_paired_diagnostic
"$tool" phase "$base" phase/wide.bin > phase/wide.log 2>&1
"$tool" verify "$base" phase/wide.bin /home/hclau/ecdsa_research/arithmetic-repair-20261015/packets/independent.tsv 4 guard-tree-phase-v1 > phase/wide-paired.log 2>&1
sha256sum phase/wide.bin > phase/wide.sha256

#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/overnight-20261014/product-zero-diagnostic
evidence=/home/hclau/ecdsa_research/overnight-20261014/product-evidence/square-zero
mkdir -p "$evidence"
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"; python3 ../research-receipt.py . "$evidence/receipt" --log "$evidence/run.log" --exit "$evidence/run.exit"; exit "$rc"' EXIT
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/overnight-20261014/product-zero-target
export G3_UT_CAP=1234 G3_UT_BATCHES=1 G3_UT_SEED=zero-representative-diagnostic-v1
ulimit -v 16777216
. /home/hclau/.cargo/env
date -u
hostname
git rev-parse HEAD
git status --short
/usr/bin/time -v cargo test --offline --locked --release --bin build_circuit research_square_zero_representative -- --nocapture --test-threads=1
date -u

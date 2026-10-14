#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014
checkout=$root/product-repair57-production-pool
evidence=$root/product-evidence/repair57-production-pool
trap 'rc=$?; echo "$rc" > "$evidence/run.exit"; args=(); if test -f "$evidence/run/ops.bin"; then args+=(--stream "$evidence/run/ops.bin"); fi; python3 "$root/research-receipt.py" "$checkout" "$evidence/receipt" --log "$evidence/run.log" --exit "$evidence/run.exit" "${args[@]}"; exit "$rc"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 CARGO_TARGET_DIR=$root/product-repair57-production-pool-target RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd "$checkout"
sha256sum src/point_add/y15_onefold.rs > "$evidence/source.sha256"
/usr/bin/time -v cargo build --offline --locked --release --bin build_circuit
sha256sum "$CARGO_TARGET_DIR/release/build_circuit" > "$evidence/native.sha256"
cd "$evidence/run"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit"
echo '49b35cf7640ebd529d76894eb8bef93ebf57e7e970fe14b3c27c8c5feb6e73e4  ops.bin' | sha256sum -c -

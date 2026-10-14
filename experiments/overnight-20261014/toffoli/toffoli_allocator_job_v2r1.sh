#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/hclau/ecdsa_research/overnight-20261014/toffoli-bank-product-v2
evidence=/home/hclau/ecdsa_research/overnight-20261014/toffoli-bank-product-evidence/allocator-v2r1
cd "$ROOT"
mkdir -p "$evidence"
printf '%s\n' "$$" > "$evidence/run.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"; python3 ../research-receipt.py . "$evidence/receipt" --log "$evidence/run.log" --exit "$evidence/run.exit"; exit "$rc"' EXIT
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/overnight-20261014/toffoli-bank-product-v2-target
ulimit -v 16777216
date -u --iso-8601=seconds
hostname
git rev-parse HEAD
git status --short
printf '%s\n' 'build_threads=4 runtime_threads=1 vmem_kib=16777216 dedicated_target=toffoli-bank-product-v2-target new_test_filter=toffoli_allocator' > "$evidence/settings.txt"
printf '%s\n' 'cargo test --offline --locked --release --bin build_circuit toffoli_allocator -- --nocapture --test-threads=1' >> "$evidence/settings.txt"
/usr/bin/time -v cargo test --offline --locked --release --bin build_circuit toffoli_allocator -- --nocapture --test-threads=1
find "$CARGO_TARGET_DIR/release/deps" -maxdepth 1 -type f -executable -name 'build_circuit-*' -exec sha256sum '{}' + > "$evidence/test-binary.sha256"
date -u --iso-8601=seconds

#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/overnight-20261014/product-candidate
evidence=/home/hclau/ecdsa_research/overnight-20261014/product-evidence/candidate-builder
mkdir -p "$evidence"
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"; python3 ../research-receipt.py . "$evidence/receipt" --log "$evidence/run.log" --exit "$evidence/run.exit" --stream "$evidence/ops.bin"; exit "$rc"' EXIT
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/overnight-20261014/product-target
ulimit -v 16777216
. /home/hclau/.cargo/env
date -u
hostname
git rev-parse HEAD
git status --short
printf '%s\n' 'build_threads=4 library_threads=1 vmem_kib=16777216 official_builder=yes official_scorer=no nonce_changed=no' > "$evidence/settings.txt"
/usr/bin/time -v cargo test --offline --locked --release --bin build_circuit classical_factors_xor -- --nocapture
/usr/bin/time -v cargo build --offline --locked --release --bin build_circuit
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit"
cp ops.bin "$evidence/ops.bin"
sha256sum ops.bin > "$evidence/ops.sha256"
python3 ../product-scan-streams.py ops.bin --out "$evidence/stream-diagnostic.json"
date -u

#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/hclau/ecdsa_research/overnight-20261014/toffoli-bank-product
evidence=/home/hclau/ecdsa_research/overnight-20261014/toffoli-bank-product-evidence/builder
cd "$ROOT"
mkdir -p "$evidence"
printf '%s\n' "$$" > "$evidence/run.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"; python3 ../research-receipt.py . "$evidence/receipt" --log "$evidence/run.log" --exit "$evidence/run.exit" --stream "$evidence/ops.bin"; exit "$rc"' EXIT
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/overnight-20261014/toffoli-target
ulimit -v 16777216
date -u --iso-8601=seconds
hostname
git rev-parse HEAD
git status --short
printf '%s\n' 'build_threads=4 runtime_threads=1 vmem_kib=16777216 official_builder=yes scorer=no nonce_changed=no bank_regeneration_ANDs=6' > "$evidence/settings.txt"
printf '%s\n' 'cargo build --offline --locked --release --bin build_circuit; target/release/build_circuit; product-scan-streams.py ops.bin' >> "$evidence/settings.txt"
/usr/bin/time -v cargo build --offline --locked --release --bin build_circuit
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit"
cp ops.bin "$evidence/ops.bin"
sha256sum ops.bin > "$evidence/ops.sha256"
python3 ../product-scan-streams.py ops.bin --out "$evidence/stream-diagnostic.json"
date -u --iso-8601=seconds

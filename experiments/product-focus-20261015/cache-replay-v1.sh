#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-focus-20261015
evidence="$root/cache-replay"
mkdir -p "$evidence"
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR="$evidence/target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$evidence/preflight.json"
python3 "$root/prepare-replay.py"
cd "$evidence/crate"
cargo generate-lockfile --offline
cargo build --release --locked --offline > "$evidence/build.log" 2>&1
for attempt in $(seq 1 120); do
 if test -f "$root/candidate-lazy-v1-evidence/benchmark.exit"; then break; fi
 if test -f "$root/candidate-lazy-v1-evidence/run.exit"; then exit 2; fi
 sleep 15
done
test -f "$root/candidate-lazy-v1-evidence/benchmark.exit"
sha256sum src/main.rs Cargo.toml Cargo.lock "$CARGO_TARGET_DIR/release/cache_paired_diagnostic" /home/hclau/ecdsa_research/product/ops.bin "$root/candidate-lazy-v1/ops.bin" > "$evidence/bindings.sha256"
for mode in independent structured candidate; do
 /usr/bin/time -v "$CARGO_TARGET_DIR/release/cache_paired_diagnostic" /home/hclau/ecdsa_research/product/ops.bin "$root/candidate-lazy-v1/ops.bin" "$root/candidate-lazy-v1-evidence/benchmark.log" "$mode" "$evidence/$mode.tsv" > "$evidence/$mode.log" 2>&1
done

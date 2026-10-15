#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/toffoli-readiness-20261015
evidence="$root/replay"
mkdir -p "$evidence"
echo $$ > "$root/replay.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR="$evidence/target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$evidence/preflight.json"
python3 "$root/prepare-replay.py" "$evidence/crate"
cd "$evidence/crate"
cargo generate-lockfile --offline
cargo build --release --locked --offline > "$evidence/build.log" 2>&1
base=/home/hclau/ecdsa_research/overnight-20261014/product-evidence/b3-baseline/run/ops.bin
candidate="$root/candidate-b3-cache-v1/ops.bin"
test -f "$root/evidence/benchmark.exit"
sha256sum src/main.rs Cargo.toml Cargo.lock "$CARGO_TARGET_DIR/release/product_paired_diagnostic" "$base" "$candidate" > "$evidence/bindings.sha256"
for mode in independent structured candidate; do
 /usr/bin/time -v "$CARGO_TARGET_DIR/release/product_paired_diagnostic" "$base" "$candidate" "$root/evidence/benchmark.log" "$mode" "$evidence/$mode.tsv" > "$evidence/$mode.log" 2>&1
done
sha256sum "$evidence"/*.tsv > "$evidence/packets.sha256"

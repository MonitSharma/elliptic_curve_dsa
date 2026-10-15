#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/toffoli-readiness-20261015
evidence="$root/wide-replay"
mkdir -p "$evidence"
echo $$ > "$root/wide-replay.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR="$root/replay/target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$evidence/preflight.json"
python3 "$root/prepare-wide-replay.py" "$evidence/crate"
cd "$evidence/crate"
cargo generate-lockfile --offline
cargo build --release --locked --offline > "$evidence/build.log" 2>&1
cp "$CARGO_TARGET_DIR/release/product_paired_diagnostic" "$evidence/paired_diagnostic"
base=/home/hclau/ecdsa_research/overnight-20261014/product-evidence/b3-baseline/run/ops.bin
candidate="$root/candidate-wide-v1/ops.bin"
test "$(cat "$root/wide-evidence/run.exit")" = 0
sha256sum src/main.rs Cargo.toml Cargo.lock "$evidence/paired_diagnostic" "$base" "$candidate" > "$evidence/bindings.sha256"
for mode in independent structured; do
 /usr/bin/time -v "$evidence/paired_diagnostic" "$base" "$candidate" "$root/wide-evidence/generation.log" "$mode" "$evidence/$mode.tsv" > "$evidence/$mode.log" 2>&1
done
sha256sum "$evidence"/*.tsv > "$evidence/packets.sha256"

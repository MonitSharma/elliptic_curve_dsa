#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/rail-control-20261015
echo $$ > "$root/phase-v3.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/phase-v3.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR="$root/phase-target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/phase-v3-preflight.json"
python3 "$root/prepare-phase-v3.py" > "$root/phase-v3-prepare.log" 2>&1
cd "$root/phase-audit-v3"
cargo test --release --locked --offline -- --nocapture --test-threads=1 > "$root/phase-v3-tests.log" 2>&1
cargo build --release --locked --offline > "$root/phase-v3-build.log" 2>&1
sha256sum "$CARGO_TARGET_DIR/release/product_paired_diagnostic" "$root/square-room-b3/ops.bin" > "$root/phase-v3-inputs.sha256"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/product_paired_diagnostic" "$root/square-room-b3/ops.bin" "$root/packets/structured.tsv" > "$root/phase-v3.log" 2>&1

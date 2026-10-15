#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/repair-integration-20261015
old=/home/hclau/ecdsa_research/rail-control-20261015
echo $$ > "$root/phase2.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/phase2.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR="$root/phase-target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/phase2-preflight.json"
python3 "$root/prepare-phase2.py" > "$root/phase2-prepare.log" 2>&1
for name in phase-context-v2 phase-bdd; do
 cd "$root/$name"
 cargo test --release --locked --offline -- --nocapture --test-threads=1 > "$root/$name-tests.log" 2>&1
 cargo build --release --locked --offline > "$root/$name-build.log" 2>&1
 sha256sum "$CARGO_TARGET_DIR/release/product_paired_diagnostic" "$old/square-room-b3/ops.bin" > "$root/$name-inputs.sha256"
 /usr/bin/time -v "$CARGO_TARGET_DIR/release/product_paired_diagnostic" "$old/square-room-b3/ops.bin" "$old/packets/structured.tsv" > "$root/$name.log" 2>&1
done

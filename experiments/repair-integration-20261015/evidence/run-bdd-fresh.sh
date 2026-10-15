#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/repair-integration-20261015
old=/home/hclau/ecdsa_research/rail-control-20261015
echo $$ > "$root/bdd-fresh.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/bdd-fresh.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR="$root/bdd-fresh-target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
test ! -e "$CARGO_TARGET_DIR"
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/bdd-fresh-preflight.json"
cd "$root/phase-bdd"
cargo test --release --locked --offline -- --nocapture --test-threads=1 > "$root/bdd-fresh-tests.log" 2>&1
grep -q 'graph_truth_tables_and_collection_are_exact ... ok' "$root/bdd-fresh-tests.log"
grep -q '5 passed' "$root/bdd-fresh-tests.log"
cargo build --release --locked --offline > "$root/bdd-fresh-build.log" 2>&1
sha256sum "$CARGO_TARGET_DIR/release/product_paired_diagnostic" "$old/square-room-b3/ops.bin" > "$root/bdd-fresh-inputs.sha256"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/product_paired_diagnostic" "$old/square-room-b3/ops.bin" "$old/packets/structured.tsv" > "$root/bdd-fresh.log" 2>&1

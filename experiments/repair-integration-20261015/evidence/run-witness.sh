#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/repair-integration-20261015
old=/home/hclau/ecdsa_research/rail-control-20261015
echo $$ > "$root/witness.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/witness.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR="$root/witness-target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
test ! -e "$CARGO_TARGET_DIR"
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/witness-preflight.json"
python3 "$root/prepare-witness.py" > "$root/witness-prepare.log" 2>&1
cd "$root/phase-bdd-witness"
cargo test --release --locked --offline -- --nocapture --test-threads=1 > "$root/witness-tests.log" 2>&1
grep -q 'witness_paths_match_exact_truth_tables_and_gc ... ok' "$root/witness-tests.log"
grep -q '6 passed' "$root/witness-tests.log"
cargo build --release --locked --offline > "$root/witness-build.log" 2>&1
sha256sum "$CARGO_TARGET_DIR/release/product_paired_diagnostic" "$old/square-room-b3/ops.bin" > "$root/witness-inputs.sha256"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/product_paired_diagnostic" "$old/square-room-b3/ops.bin" "$old/packets/structured.tsv" > "$root/witness.log" 2>&1

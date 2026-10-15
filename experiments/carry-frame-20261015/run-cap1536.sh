#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/carry-frame-20261015
prior=/home/hclau/ecdsa_research/repair-integration-20261015
old=/home/hclau/ecdsa_research/arithmetic-repair-20261015
echo $$ > "$root/cap1536.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/cap1536.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0 CARGO_TARGET_DIR="$root/cap1536-target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
test ! -e "$CARGO_TARGET_DIR"
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/cap1536-preflight.json"
python3 "$root/prepare-cap.py" > "$root/cap1536-prepare.log" 2>&1
cd "$root/cap1536-b3"
cargo build --release --locked --offline --bin build_circuit > "$root/cap1536-build.log" 2>&1
sha256sum "$CARGO_TARGET_DIR/release/build_circuit" > "$root/cap1536-binary.sha256"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" > "$root/cap1536-generation.log" 2>&1
sha256sum ops.bin > "$root/cap1536-stream.sha256"
for family in independent structured candidate; do
 /usr/bin/time -v "$old/fixed-target/release/product_paired_diagnostic" ops.bin "$old/packets/$family.tsv" > "$root/cap1536-$family.log" 2>&1
done
sha256sum "$prior/witness-target/release/product_paired_diagnostic" > "$root/cap1536-phase-binary.sha256"
/usr/bin/time -v "$prior/witness-target/release/product_paired_diagnostic" ops.bin "$prior/packets/structured.tsv" > "$root/cap1536-phase.log" 2>&1

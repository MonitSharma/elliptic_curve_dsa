#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/carry-frame-20261015
prior=/home/hclau/ecdsa_research/repair-integration-20261015
old=/home/hclau/ecdsa_research/arithmetic-repair-20261015
echo $$ > "$root/unseeded.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/unseeded.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0 CARGO_TARGET_DIR="$root/unseeded-target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
test ! -e "$CARGO_TARGET_DIR"
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/unseeded-preflight.json"
python3 "$root/prepare-unseeded.py" > "$root/unseeded-prepare.log" 2>&1
cd "$root/unseeded-b3"
cargo build --release --locked --offline --bin build_circuit > "$root/unseeded-build.log" 2>&1
sha256sum "$CARGO_TARGET_DIR/release/build_circuit" > "$root/unseeded-binary.sha256"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" > "$root/unseeded-generation.log" 2>&1
sha256sum ops.bin > "$root/unseeded-stream.sha256"
for family in independent structured candidate; do
 /usr/bin/time -v "$old/fixed-target/release/product_paired_diagnostic" ops.bin "$old/packets/$family.tsv" > "$root/unseeded-$family.log" 2>&1
done
sha256sum "$prior/witness-target/release/product_paired_diagnostic" > "$root/unseeded-phase-binary.sha256"
/usr/bin/time -v "$prior/witness-target/release/product_paired_diagnostic" ops.bin "$prior/packets/structured.tsv" > "$root/unseeded-phase.log" 2>&1

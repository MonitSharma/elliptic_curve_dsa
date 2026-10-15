#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/arithmetic-repair-20261015
echo $$ > "$root/unbound.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/unbound.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR="$root/target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/unbound-preflight.json"
python3 "$root/prepare-unbound.py" > "$root/unbound-prepare.log" 2>&1
cd "$root/candidate-fold104-unbound-b3"
cargo build --release --locked --offline --bin build_circuit > "$root/unbound-build.log" 2>&1
sha256sum "$CARGO_TARGET_DIR/release/build_circuit" > "$root/unbound-binary.sha256"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" > "$root/unbound-generation.log" 2>&1
sha256sum ops.bin "$root/unbound-generation.log" > "$root/unbound-bindings.sha256"
for family in independent structured candidate; do
  /usr/bin/time -v "$root/fixed-target/release/product_paired_diagnostic" ops.bin "$root/packets/$family.tsv" > "$root/unbound-$family.log" 2>&1
done
sha256sum "$root"/unbound-*.log > "$root/unbound-logs.sha256"

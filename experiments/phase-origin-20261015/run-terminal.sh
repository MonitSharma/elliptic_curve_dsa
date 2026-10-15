#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/phase-origin-20261015
prior=/home/hclau/ecdsa_research/repair-integration-20261015
old=/home/hclau/ecdsa_research/arithmetic-repair-20261015
echo $$ > "$root/terminal.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/terminal.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR="$root/terminal-target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
test ! -e "$CARGO_TARGET_DIR"
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/terminal-preflight.json"
python3 "$root/prepare-terminal.py" > "$root/terminal-prepare.log" 2>&1
cd "$root/terminal-b3"
cargo build --release --locked --offline --bin build_circuit > "$root/terminal-build.log" 2>&1
sha256sum "$CARGO_TARGET_DIR/release/build_circuit" > "$root/terminal-binary.sha256"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" > "$root/terminal-generation.log" 2>&1
sha256sum ops.bin > "$root/terminal-stream.sha256"
for family in independent structured candidate; do
 /usr/bin/time -v "$old/fixed-target/release/product_paired_diagnostic" ops.bin "$old/packets/$family.tsv" > "$root/terminal-$family.log" 2>&1
done
sha256sum "$prior/witness-target/release/product_paired_diagnostic" > "$root/terminal-phase-binary.sha256"
/usr/bin/time -v "$prior/witness-target/release/product_paired_diagnostic" ops.bin "$prior/packets/structured.tsv" > "$root/terminal-phase.log" 2>&1

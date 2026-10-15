#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/rail-margin-20261015
old=/home/hclau/ecdsa_research/arithmetic-repair-20261015
echo $$ > "$root/run.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/run.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR="$root/target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/preflight.json"
python3 "$root/prepare.py" > "$root/prepare.log" 2>&1
cd "$root/margin-one-b3"
cargo build --release --locked --offline --bin build_circuit > "$root/build.log" 2>&1
sha256sum "$CARGO_TARGET_DIR/release/build_circuit" > "$root/binary.sha256"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" > "$root/generation.log" 2>&1
sha256sum ops.bin > "$root/stream.sha256"
/usr/bin/time -v "$old/fixed-target/release/product_paired_diagnostic" ops.bin /home/hclau/ecdsa_research/rail-repair-20261015/known15.tsv > "$root/known15.log" 2>&1
for family in independent structured candidate; do
  /usr/bin/time -v "$old/fixed-target/release/product_paired_diagnostic" ops.bin "$old/packets/$family.tsv" > "$root/$family.log" 2>&1
done
sha256sum "$root"/*.log > "$root/logs.sha256"

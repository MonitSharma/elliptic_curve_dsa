#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/rail-control-20261015
old=/home/hclau/ecdsa_research/arithmetic-repair-20261015
echo $$ > "$root/square.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/square.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR="$root/square-target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/square-preflight.json"
python3 "$root/prepare-square.py" > "$root/square-prepare.log" 2>&1
cd "$root/square-room-b3"
cargo test --release --locked --offline --bin build_circuit uniform_positive_large -- --nocapture --test-threads=1 > "$root/square-tests.log" 2>&1
find "$CARGO_TARGET_DIR/release/deps" -maxdepth 1 -type f -name 'build_circuit-*' -executable -exec sha256sum {} \; > "$root/square-test-binaries.sha256"
cargo build --release --locked --offline --bin build_circuit > "$root/square-build.log" 2>&1
sha256sum "$CARGO_TARGET_DIR/release/build_circuit" > "$root/square-binary.sha256"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" > "$root/square-generation.log" 2>&1
sha256sum ops.bin > "$root/square-stream.sha256"
/usr/bin/time -v "$old/fixed-target/release/product_paired_diagnostic" ops.bin /home/hclau/ecdsa_research/rail-repair-20261015/known15.tsv > "$root/square-known15.log" 2>&1
for family in independent structured candidate; do
  /usr/bin/time -v "$old/fixed-target/release/product_paired_diagnostic" ops.bin "$old/packets/$family.tsv" > "$root/square-$family.log" 2>&1
done
sha256sum "$root"/square-*.log > "$root/square-logs.sha256"

#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/rail-repair-20261015
old=/home/hclau/ecdsa_research/arithmetic-repair-20261015
echo $$ > "$root/flex.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/flex.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR="$root/candidate-target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/flex-preflight.json"
for mode in baseline repair; do
  python3 "$root/prepare-flex.py" "$mode" > "$root/flex-$mode-prepare.log" 2>&1
  cd "$root/flex-$mode-b3"
  cargo build --release --locked --offline --bin build_circuit > "$root/flex-$mode-build.log" 2>&1
  sha256sum "$CARGO_TARGET_DIR/release/build_circuit" > "$root/flex-$mode-binary.sha256"
  /usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" > "$root/flex-$mode-generation.log" 2>&1
  sha256sum ops.bin > "$root/flex-$mode-stream.sha256"
  for family in independent structured candidate; do
    /usr/bin/time -v "$old/fixed-target/release/product_paired_diagnostic" ops.bin "$old/packets/$family.tsv" > "$root/flex-$mode-$family.log" 2>&1
  done
done
sha256sum "$root"/flex-*.log > "$root/flex-logs.sha256"

#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/rail-control-20261015
old=/home/hclau/ecdsa_research/arithmetic-repair-20261015
echo $$ > "$root/expand.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/expand.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR="$root/expand-target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/expand-preflight.json"
for mode in margin3 margin3-tail2; do
  python3 "$root/prepare-expand.py" "$mode" > "$root/$mode-prepare.log" 2>&1
  cd "$root/$mode-b3"
  cargo build --release --locked --offline --bin build_circuit > "$root/$mode-build.log" 2>&1
  sha256sum "$CARGO_TARGET_DIR/release/build_circuit" > "$root/$mode-binary.sha256"
  set +e
  /usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" > "$root/$mode-generation.log" 2>&1
  rc=$?
  set -e
  printf '%s\n' "$rc" > "$root/$mode-generation.exit"
  if test "$rc" != 0; then continue; fi
  sha256sum ops.bin > "$root/$mode-stream.sha256"
  /usr/bin/time -v "$old/fixed-target/release/product_paired_diagnostic" ops.bin /home/hclau/ecdsa_research/rail-repair-20261015/known15.tsv > "$root/$mode-known15.log" 2>&1
  for family in independent structured candidate; do
    /usr/bin/time -v "$old/fixed-target/release/product_paired_diagnostic" ops.bin "$old/packets/$family.tsv" > "$root/$mode-$family.log" 2>&1
  done
done
sha256sum "$root"/margin3*.log > "$root/expand-logs.sha256"

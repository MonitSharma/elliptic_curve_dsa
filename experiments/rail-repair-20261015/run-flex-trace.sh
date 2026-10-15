#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/rail-repair-20261015
echo $$ > "$root/flex-trace.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/flex-trace.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR="$root/target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/flex-trace-preflight.json"
for mode in baseline repair; do
  python3 "$root/prepare-flex-trace.py" "$mode" > "$root/flex-trace-$mode-prepare.log" 2>&1
  cd "$root/flex-trace-$mode-b3"
  cargo build --release --locked --offline --bin build_circuit > "$root/flex-trace-$mode-build.log" 2>&1
  sha256sum "$CARGO_TARGET_DIR/release/build_circuit" > "$root/flex-trace-$mode-binary.sha256"
  /usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" > "$root/flex-trace-$mode.log" 2>&1
  sha256sum ops.bin > "$root/flex-trace-$mode-stream.sha256"
done
sha256sum "$root"/flex-trace-*.log > "$root/flex-trace-logs.sha256"

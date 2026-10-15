#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/rail-repair-20261015
echo $$ > "$root/trace.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/trace.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR="$root/target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/trace-preflight.json"
python3 "$root/prepare-trace.py" > "$root/trace-prepare.log" 2>&1
cd "$root/diagnostic-rails-b3"
cargo build --release --locked --offline --bin build_circuit > "$root/trace-build.log" 2>&1
sha256sum "$CARGO_TARGET_DIR/release/build_circuit" > "$root/trace-binary.sha256"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" > "$root/trace.log" 2>&1
sha256sum ops.bin "$root/trace.log" > "$root/trace-bindings.sha256"
cmp ops.bin /home/hclau/ecdsa_research/arithmetic-repair-20261015/diagnostic-b3/ops.bin

#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/arithmetic-repair-20261015
echo $$ > "$root/pool.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/pool.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR="$root/target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/pool-preflight.json"
python3 "$root/prepare-pool.py" > "$root/pool-prepare.log" 2>&1
cd "$root/pool-observer-b3"
cargo build --release --locked --offline --bin build_circuit > "$root/pool-build.log" 2>&1
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" > "$root/pool-trace.log" 2>&1
cmp ops.bin "$root/diagnostic-b3/ops.bin"
sha256sum ops.bin "$root/pool104.json" "$root/pool-trace.log" > "$root/pool-bindings.sha256"

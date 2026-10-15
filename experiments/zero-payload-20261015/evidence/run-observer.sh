#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/zero-payload-20261015
echo $$ > "$root/observer.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/observer.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0 CARGO_TARGET_DIR="$root/observer-target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
test ! -e "$CARGO_TARGET_DIR"
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/observer-preflight.json"
python3 "$root/prepare-observer.py" > "$root/observer-prepare.log" 2>&1
cd "$root/observer-b3"
cargo build --release --locked --offline --bin build_circuit > "$root/observer-build.log" 2>&1
sha256sum "$CARGO_TARGET_DIR/release/build_circuit" > "$root/observer-binary.sha256"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" > "$root/observer.log" 2>&1
sha256sum ops.bin > "$root/observer-stream.sha256"

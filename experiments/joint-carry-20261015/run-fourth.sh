#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/joint-carry-20261015
echo $$ > "$root/state4.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/state4.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0 CARGO_TARGET_DIR="$root/state4-target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
test ! -e "$CARGO_TARGET_DIR"
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/state4-preflight.json"
python3 "$root/prepare-fourth.py" > "$root/state4-prepare.log" 2>&1
cd "$root/state4-b3"
cargo build --release --locked --offline --bin build_circuit > "$root/state4-build.log" 2>&1
sha256sum "$CARGO_TARGET_DIR/release/build_circuit" > "$root/state4-binary.sha256"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" > "$root/state4.log" 2>&1
sha256sum ops.bin > "$root/state4-stream.sha256"

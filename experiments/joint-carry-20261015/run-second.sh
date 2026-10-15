#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/joint-carry-20261015
echo $$ > "$root/state2.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/state2.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0 CARGO_TARGET_DIR="$root/state2-target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
test ! -e "$CARGO_TARGET_DIR"
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/state2-preflight.json"
python3 "$root/prepare-second.py" > "$root/state2-prepare.log" 2>&1
cd "$root/state2-b3"
cargo build --release --locked --offline --bin build_circuit > "$root/state2-build.log" 2>&1
sha256sum "$CARGO_TARGET_DIR/release/build_circuit" > "$root/state2-binary.sha256"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" > "$root/state2.log" 2>&1
sha256sum ops.bin > "$root/state2-stream.sha256"

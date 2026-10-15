#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/phase-origin-20261015
echo $$ > "$root/run.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/run.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR="$root/target" CARGO_PROFILE_RELEASE_DEBUG=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
test ! -e "$CARGO_TARGET_DIR"
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/preflight.json"
python3 "$root/prepare.py" > "$root/prepare.log" 2>&1
cd "$root/origin-b3"
cargo build --release --locked --offline --bin build_circuit > "$root/build.log" 2>&1
sha256sum "$CARGO_TARGET_DIR/release/build_circuit" > "$root/binary.sha256"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" > "$root/generation.log" 2>&1
sha256sum ops.bin > "$root/stream.sha256"
cmp ops.bin /home/hclau/ecdsa_research/rail-control-20261015/square-room-b3/ops.bin
echo BYTE_IDENTICAL_STREAM=true > "$root/equality.log"

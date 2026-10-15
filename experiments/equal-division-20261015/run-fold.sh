#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/equal-division-20261015
echo $$ > "$root/fold.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/fold.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0 CARGO_TARGET_DIR="$root/fold-target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
test ! -e "$CARGO_TARGET_DIR"
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/fold-preflight.json"
python3 "$root/prepare-fold.py" > "$root/fold-prepare.log" 2>&1
cd "$root/fold-b3"
cargo build --release --locked --offline --bin build_circuit > "$root/fold-build.log" 2>&1
sha256sum "$CARGO_TARGET_DIR/release/build_circuit" > "$root/fold-binary.sha256"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" > "$root/fold.log" 2>&1
sha256sum ops.bin > "$root/fold-stream.sha256"

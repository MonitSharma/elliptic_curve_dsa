#!/usr/bin/env bash
# Build and run the gate-inert value-failure observer on the wide circuit. Diagnostic; score=NONE.
set -euo pipefail
root=/home/hclau/ecdsa_research/trace-value-20261015
echo $$ > "$root/run.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/run.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0 CARGO_TARGET_DIR="$root/target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/preflight.json"
python3 "$root/prepare.py" > "$root/prepare.log" 2>&1
cd "$root/observer-b3"
cargo build --release --locked --offline --bin build_circuit > "$root/build.log" 2>&1
sha256sum "$CARGO_TARGET_DIR/release/build_circuit" > "$root/binary.sha256"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" > "$root/trace.log" 2>&1
sha256sum ops.bin > "$root/stream.sha256"
if grep -q 95e771bae57bd96e75c11b569faf2f87cd7dfa52b227b40dd16e40a301d8e122 "$root/stream.sha256"; then echo BYTE_IDENTICAL_STREAM=true; else echo BYTE_IDENTICAL_STREAM=false; fi > "$root/equality.log"

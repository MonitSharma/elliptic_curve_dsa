#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/wide-cache-20261015
echo $$ > "$root/replay.pid"
trap 'rc=$?; echo "$rc" > "$root/replay.exit"' EXIT
ulimit -v 33554432
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export CARGO_TARGET_DIR="$root/replay-target"
python3 /home/hclau/ecdsa_research/toffoli-readiness-20261015/prepare-wide-replay.py "$root/replay"
cd "$root/replay"
cargo generate-lockfile --offline
cargo build --release --locked --offline > "$root/evidence/replay-build.log" 2>&1
while test ! -f "$root/run.exit"; do sleep 5; done
test "$(cat "$root/run.exit")" = 0
base=/home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin
for mode in independent structured; do
 /usr/bin/time -v "$CARGO_TARGET_DIR/release/product_paired_diagnostic" "$base" "$root/candidate/ops.bin" "$root/evidence/generation.log" "$mode" "$root/evidence/replay-$mode.tsv" > "$root/evidence/replay-$mode.log" 2>&1
done
sha256sum "$root/replay/src/main.rs" "$root/replay/Cargo.lock" "$root/evidence/"*.tsv > "$root/evidence/replay-bindings.sha256"

#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/arithmetic-repair-20261015
echo $$ > "$root/fixed.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/fixed.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR="$root/fixed-target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/fixed-preflight.json"
python3 "$root/prepare-fixed.py" > "$root/fixed-prepare.log" 2>&1
cd "$root/fixed-replay"
cargo generate-lockfile --offline
cargo build --release --locked --offline > "$root/fixed-build.log" 2>&1
while ! test -f "$root/candidate.exit"; do sleep 5; done
test "$(cat "$root/candidate.exit")" = 0
sha256sum src/main.rs Cargo.toml Cargo.lock "$CARGO_TARGET_DIR/release/product_paired_diagnostic" > "$root/fixed-source.sha256"
for family in independent structured candidate; do
  /usr/bin/time -v "$CARGO_TARGET_DIR/release/product_paired_diagnostic" "$root/candidate-fold104-b3/ops.bin" "$root/packets/$family.tsv" > "$root/fixed-$family.log" 2>&1
done
sha256sum "$root"/fixed-*.log > "$root/fixed-logs.sha256"

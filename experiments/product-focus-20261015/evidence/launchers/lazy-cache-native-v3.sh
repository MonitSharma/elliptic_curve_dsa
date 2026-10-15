#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-focus-20261015
evidence="$root/lazy-cache-native-v3"
mkdir -p "$evidence"
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR="$root/erase-audit/target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$evidence/preflight.json"
python3 "$root/prepare-lazy-cache-audit.py" /home/hclau/ecdsa_research/product "$evidence/crate" /home/hclau/ecdsa_research/overnight-20261014/prepare-wire-zero-audit.py
cd "$evidence/crate"
sha256sum src/*.rs Cargo.toml > "$evidence/source.sha256"
cargo generate-lockfile --offline
cargo build --release --locked --offline > "$evidence/build.log" 2>&1
cargo test --release --locked --offline lazy_cache_ -- --nocapture --test-threads=1 > "$evidence/tests.log" 2>&1
/usr/bin/time -v "$CARGO_TARGET_DIR/release/cache_audit" /home/hclau/ecdsa_research/product/ops.bin 0 > "$evidence/analysis.log" 2>&1

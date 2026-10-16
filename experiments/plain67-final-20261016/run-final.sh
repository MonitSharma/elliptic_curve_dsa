#!/usr/bin/env bash
# PLAIN67 finalization after a complete terminal audit (queue mode; never submits).
set -euo pipefail
r=/home/hclau/ecdsa_research/plain67-final-20261016
echo $$ > "$r/final.pid"
trap 's=$?; echo "$s" > "$r/final.exit"' EXIT
ulimit -v 50331648
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export RUSTFLAGS='-C linker=/usr/bin/gcc'
unset RUSTUP_TOOLCHAIN CARGO_TARGET_DIR
python3 "$r/finalize.py" prepare > "$r/prepare.log" 2>&1
cd "$r/candidate"
cargo test --release --locked --offline --bin build_circuit frozen_cache_product67 -- --test-threads=1 > "$r/native-tests.log" 2>&1
grep -q '4 passed; 0 failed' "$r/native-tests.log"
cargo build --release --locked --offline --bin build_circuit > "$r/build.log" 2>&1
/usr/bin/time -v ./target/release/build_circuit > "$r/generate.log" 2>&1
python3 "$r/finalize.py" native > "$r/native-verification.log" 2>&1
cp ops.bin "$r/native-selected.ops.bin"
python3 "$r/finalize.py" tailcheck > "$r/tailcheck.log" 2>&1
nonce=$(python3 -c "import json;print(json.load(open('$r/SOURCE_FREEZE.json'))['nonce'])")
./benchmark.sh --note "queue-only PLAIN67 (4b2ec52f + exact 67-stage cache); lowest-pass nonce $nonce" > "$r/benchmark.log" 2>&1
python3 "$r/finalize.py" benchmark > "$r/benchmark-verification.log" 2>&1

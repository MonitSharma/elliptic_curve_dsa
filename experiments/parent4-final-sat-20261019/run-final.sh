#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/parent4-final-sat-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/parent4-final-sat-20261019/final.exit' EXIT
python3 preflight.py > final-preflight.json
ulimit -v 50331648
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export RUSTFLAGS='-C linker=/usr/bin/gcc'
unset RUSTUP_TOOLCHAIN CARGO_TARGET_DIR
python3 finalize.py prepare > prepare.log 2>&1
cd "$r/candidate"
cargo test --release --locked --offline --bin build_circuit frozen_cache_product67 -- --test-threads=1 > "$r/native-tests.log" 2>&1
grep -q '4 passed; 0 failed' "$r/native-tests.log"
cargo build --release --locked --offline --bin build_circuit > "$r/build.log" 2>&1
/usr/bin/time -v ./target/release/build_circuit > "$r/generate.log" 2>&1
python3 "$r/finalize.py" native > "$r/native-verification.log" 2>&1
cp ops.bin "$r/native-selected.ops.bin"
python3 "$r/finalize.py" tailcheck > "$r/tailcheck.log" 2>&1
nonce=$(python3 -c "import json;print(json.load(open('$r/SOURCE_FREEZE.json'))['nonce'])")
./benchmark.sh --note "queue-only parent4 exact source-bound optimization; lowest-pass nonce $nonce" > "$r/benchmark.log" 2>&1
python3 "$r/finalize.py" benchmark > "$r/benchmark-verification.log" 2>&1

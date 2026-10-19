#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-captured-factors-native-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-captured-factors-native-20261019/run.exit' EXIT
while [ ! -f ../product-captured-factors-20261019/control.exit ]; do sleep 15; done
test "$(cat ../product-captured-factors-20261019/control.exit)" = 0
python3 ../autonomous-20261019/preflight_v2.py > preflight.json
sha256sum classical_capture.rs prepare_native.py verify_native.py run.sh ../autonomous-20261019/preflight_v2.py > PREPARATION_SOURCE.sha256
ulimit -v 33554432
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export RUSTFLAGS='-C linker=/usr/bin/gcc'
unset RUSTUP_TOOLCHAIN CARGO_TARGET_DIR
python3 prepare_native.py > prepare.log 2>&1
cd "$r/candidate"
cargo test --release --locked --offline --bin build_circuit frozen_cache_product67 -- --test-threads=1 > "$r/retained-tests.log" 2>&1
cargo test --release --locked --offline --bin build_circuit classical_capture -- --test-threads=1 > "$r/capture-tests.log" 2>&1
cargo test --release --locked --offline --bin build_circuit classical_factors_xor -- --test-threads=1 > "$r/factor-tests.log" 2>&1
cargo build --release --locked --offline --bin build_circuit > "$r/build.log" 2>&1
/usr/bin/time -v ./target/release/build_circuit > "$r/generate.log" 2>&1
python3 "$r/verify_native.py" > "$r/native-verification.log" 2>&1

#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-classical-factors-native-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-classical-factors-native-20261019/run.exit' EXIT
test "$(cat ../product-classical-factors-refresh-20261019/control.exit)" = 0
python3 ../autonomous-20261019/preflight_v4.py > preflight.json
sha256sum prepare_native.py verify_native.py run.sh ../autonomous-20261019/preflight_v4.py > PREPARATION_SOURCE.sha256
ulimit -v 33554432
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export RUSTFLAGS='-C linker=/usr/bin/gcc'
unset RUSTUP_TOOLCHAIN CARGO_TARGET_DIR
python3 prepare_native.py > prepare.log 2>&1
cd "$r/candidate"
cargo test --release --locked --offline --bin build_circuit frozen_cache_product67 -- --test-threads=1 > "$r/retained-tests.log" 2>&1
cargo test --release --locked --offline --bin build_circuit classical_factors_xor -- --test-threads=1 > "$r/factor-tests.log" 2>&1
cargo build --release --locked --offline --bin build_circuit > "$r/build.log" 2>&1
sha256sum ./target/release/build_circuit > "$r/NATIVE_BINARY.sha256"
cp ./target/release/build_circuit "$r/native_build_circuit.bin"
/usr/bin/time -v ./target/release/build_circuit > "$r/generate.log" 2>&1
python3 "$r/verify_native.py" > "$r/native-verification.log" 2>&1

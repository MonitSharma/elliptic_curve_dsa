#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-classical-nine-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-classical-nine-20261019/run.exit' EXIT
python3 ../autonomous-20261019/preflight_v6.py > preflight.json
sha256sum *.py *.rs Cargo.toml run.sh ../autonomous-20261019/preflight_v6.py > PREPARATION_SOURCE.sha256
ulimit -v 33554432
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export RUSTUP_TOOLCHAIN=stable CARGO_TARGET_DIR=/home/hclau/ecdsa_research/product-order-20261019/target
cargo test --release --offline --bin classical_nine_research -- --test-threads=1 > primitive-tests.log 2>&1
cargo build --release --offline --bins > research-build.log 2>&1
sha256sum "$CARGO_TARGET_DIR/release/classical_nine_research" "$CARGO_TARGET_DIR/release/classical_nine_trace" > RESEARCH_BINARY.sha256
/usr/bin/time -v "$CARGO_TARGET_DIR/release/classical_nine_research" "$r" > rewrite.log 2>&1
/usr/bin/time -v "$CARGO_TARGET_DIR/release/classical_nine_trace" ../product-classical-factors-refresh-20261019/parent4.ops.bin research.ops.bin CONTROL-nine.json > control.log 2>&1
printf '0\n' > control.exit
python3 refresh_record.py > refresh.log 2>&1
unset RUSTUP_TOOLCHAIN CARGO_TARGET_DIR
export RUSTFLAGS='-C linker=/usr/bin/gcc'
python3 prepare_native.py > prepare.log 2>&1
cd "$r/candidate"
cargo test --release --locked --offline --bin build_circuit frozen_cache_product67 -- --test-threads=1 > "$r/retained-tests.log" 2>&1
cargo test --release --locked --offline --bin build_circuit classical_factors_xor -- --test-threads=1 > "$r/factor-tests.log" 2>&1
cargo test --release --locked --offline --bin build_circuit classical_xor_control -- --test-threads=1 > "$r/xor-tests.log" 2>&1
cargo build --release --locked --offline --bin build_circuit > "$r/build.log" 2>&1
sha256sum ./target/release/build_circuit > "$r/NATIVE_BINARY.sha256"
cp ./target/release/build_circuit "$r/native_build_circuit.bin"
/usr/bin/time -v ./target/release/build_circuit > "$r/generate.log" 2>&1
python3 "$r/verify_native.py" > "$r/native-verification.log" 2>&1

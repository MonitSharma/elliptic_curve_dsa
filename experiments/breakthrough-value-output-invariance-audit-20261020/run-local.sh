#!/bin/sh
set -eu
cd /mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments/breakthrough-value-output-invariance-audit-20261020
export RUSTC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustc
export RUSTDOC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustdoc
export RUSTUP_AUTO_INSTALL=0
export CARGO_HOME=/root/.cargo
export CARGO_BUILD_JOBS=2
export OMP_NUM_THREADS=1
export CARGO_TARGET_DIR=/mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments/breakthrough-value-guard-fusion-audit-20261020/local-tool/target
trap 's=$?; printf "%s\n" "$s" > run.exit' EXIT
/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo test --release --locked --manifest-path local-tool/Cargo.toml --bin value_output_invariance_audit -- --nocapture > tests.log 2>&1
grep -q 'test result: ok. 21 passed; 0 failed;' tests.log
/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo build --release --locked --manifest-path local-tool/Cargo.toml --bin value_output_invariance_audit > build.log 2>&1
python3 verify-input.py
timeout 2400 "$CARGO_TARGET_DIR/release/value_output_invariance_audit" /mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments/breakthrough-local-product-filter-replay-20261020/candidate/ops.bin full-audit.json > full-audit.log 2>&1

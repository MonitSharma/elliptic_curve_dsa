#!/bin/sh
set -eu
cd /mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments/breakthrough-recycle-finished-v2-20261021
export RUSTC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustc
export RUSTDOC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustdoc
export RUSTUP_AUTO_INSTALL=0
export CARGO_HOME=/root/.cargo
export CARGO_BUILD_JOBS=2
export OMP_NUM_THREADS=1
export CARGO_TARGET_DIR=/mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments/breakthrough-value-guard-fusion-audit-20261020/local-tool/target
ulimit -v 10485760
trap 's=$?; printf "%s\n" "$s" > local-v2.exit' EXIT
/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo test --release --locked --manifest-path candidate/Cargo.toml --bin build_circuit point_add::recycle_measurements:: -- --nocapture --test-threads=1 > local-v2-tests.log 2>&1
grep -q 'test result: ok. 14 passed; 0 failed;' local-v2-tests.log
/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo build --release --locked --manifest-path candidate/Cargo.toml --bin build_circuit > local-v2-build.log 2>&1
cd candidate
timeout 1800 "$CARGO_TARGET_DIR/release/build_circuit" > ../local-v2-generate.log 2>&1
cd ..
python3 verify.py

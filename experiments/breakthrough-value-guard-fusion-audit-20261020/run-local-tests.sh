#!/bin/sh
set -eu
cd /mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments/breakthrough-value-guard-fusion-audit-20261020/local-tool
export RUSTC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustc
export RUSTDOC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustdoc
export RUSTUP_AUTO_INSTALL=0
export CARGO_HOME=/root/.cargo
export CARGO_BUILD_JOBS=2
export OMP_NUM_THREADS=1
set +e
/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo test --offline --release --locked --bin value_ir_audit -- --nocapture > ../local-native.log 2>&1
status=$?
set -e
printf '%s\n' "$status" > ../local-native.exit
exit "$status"

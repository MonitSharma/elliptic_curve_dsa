#!/bin/sh
set -eu
cd /mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments/breakthrough-semantic-source-value-proof-20261021
export RUSTC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustc
export RUSTDOC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustdoc
export RUSTUP_AUTO_INSTALL=0
export CARGO_HOME=/root/.cargo
export CARGO_BUILD_JOBS=2
export OMP_NUM_THREADS=1
export CARGO_TARGET_DIR=/mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments/breakthrough-value-guard-fusion-audit-20261020/local-tool/target
trap 's=$?; printf "%s\n" "$s" > run.exit' EXIT
python3 verify-input.py
timeout 2400 "$CARGO_TARGET_DIR/release/value_normalized_aig_audit" /mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments/breakthrough-public-semantic-finished-20261021/candidate/ops.bin full-audit.json > full-audit.log 2>&1

#!/bin/sh
set -eu
cd /mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments/breakthrough-local-product-filter-replay-20261020
export RUSTC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustc
export RUSTDOC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustdoc
export RUSTUP_AUTO_INSTALL=0
export CARGO_HOME=/root/.cargo
export CARGO_BUILD_JOBS=2
export OMP_NUM_THREADS=1
export CARGO_TARGET_DIR=/mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments/breakthrough-value-guard-fusion-audit-20261020/local-tool/target
trap 's=$?; printf "%s\n" "$s" > run.exit' EXIT
cd candidate
set +e
/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo build --release --locked --bin build_circuit > ../build.log 2>&1
s=$?
printf '%s\n' "$s" > ../build.exit
set -e
test "$s" = 0
timeout 1800 "$CARGO_TARGET_DIR/release/build_circuit" > ../generate.log 2>&1
cd ..
python3 verify-and-audit.py

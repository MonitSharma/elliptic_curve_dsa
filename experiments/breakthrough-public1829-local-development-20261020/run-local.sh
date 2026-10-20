#!/bin/sh
set -eu
cd /mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments/breakthrough-public1829-local-development-20261020
export RUSTC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustc
export RUSTDOC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustdoc
export RUSTUP_AUTO_INSTALL=0
export CARGO_HOME=/root/.cargo
export CARGO_BUILD_JOBS=2
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export RAYON_NUM_THREADS=1
ulimit -v 8388608
trap 's=$?; printf "%s\n" "$s" > controller.exit' EXIT
/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo build --release --locked --manifest-path local-tool/Cargo.toml > build.log 2>&1
python3 diagnostic.py

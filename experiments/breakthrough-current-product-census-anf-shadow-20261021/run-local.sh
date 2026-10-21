#!/bin/sh
set -eu
cd /mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments/breakthrough-current-product-census-anf-shadow-20261021
export RUSTC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustc
export RUSTDOC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustdoc
export RUSTUP_AUTO_INSTALL=0
export CARGO_HOME=/root/.cargo
export CARGO_BUILD_JOBS=2
export OMP_NUM_THREADS=1
export CARGO_TARGET_DIR=/mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments/breakthrough-value-guard-fusion-audit-20261020/local-tool/target
ulimit -v 8388608
trap 's=$?; printf "%s\n" "$s" > run.exit' EXIT
/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo test --release --locked --manifest-path local-tool/Cargo.toml --bin census_anf_shadow -- --nocapture > tests.log 2>&1
grep -q 'test result: ok. 39 passed; 0 failed;' tests.log
/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo build --release --locked --manifest-path local-tool/Cargo.toml --bin census_anf_shadow > build.log 2>&1
python3 verify.py
timeout 1200 "$CARGO_TARGET_DIR/release/census_anf_shadow" /mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments/breakthrough-public1829-width-port-local-v4-20261020/public/ops.bin /mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments/breakthrough-current-product-normalized-aig-20261020/normalized-value-ir.bin.zst /mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments/breakthrough-public1829-local-development-v2-20261020/public1829.jsonl public1829-workspace-cache-local-avx2-development-20261020-v1 RESULT.json > full-audit.log 2>&1

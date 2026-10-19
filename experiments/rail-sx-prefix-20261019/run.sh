#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/rail-sx-prefix-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/rail-sx-prefix-20261019/run.exit' EXIT
python3 ../autonomous-20261019/preflight_v12.py > preflight.json
sha256sum prepare.py compare.py run.sh ../autonomous-20261019/preflight_v12.py > SOURCE.sha256
ulimit -v 33554432
export CARGO_BUILD_JOBS=1 OMP_NUM_THREADS=1 RAYON_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 RUSTUP_TOOLCHAIN=stable
. /home/hclau/.cargo/env
unset CARGO_TARGET_DIR
python3 prepare.py > prepare.log 2>&1
cd "$r/tool"
cargo build --release --locked --offline --bin value_prefilter > "$r/build.log" 2>&1
sha256sum ./target/release/value_prefilter > "$r/BINARY.sha256"
cd "$r"
python3 compare.py > compare.log 2>&1

#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/scalar-fast-20261015
echo $$ > rails.pid
trap 'rc=$?; echo "$rc" > rails.exit' EXIT
ulimit -v 8388608
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
uptime
free -g
python3 prepare-rails.py
cd rail-tool
cargo test --release --locked --offline -- --nocapture > ../rail-tests.log 2>&1
cargo build --release --locked --offline > ../rail-build.log 2>&1
cd ..
sha256sum rail-tool/src/main.rs rail-tool/src/walk_native.rs original-walk-native.rs > rail-source.sha256

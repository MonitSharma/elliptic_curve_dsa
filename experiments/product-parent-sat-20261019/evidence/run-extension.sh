#!/bin/bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product-parent-sat-20261019
trap 'rc=$?; printf "%s\n" "$rc" > extension.exit' EXIT
date -Is > extension-started.txt
uptime > extension-resources.txt
free -g >> extension-resources.txt
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 67108864
source /home/hclau/.cargo/env
sha256sum Cargo.toml verify_extension.rs validate_zero.py prove_zero.py io.rs run-extension.sh > EXTENSION-SOURCE.sha256
cargo build --release --offline --bin verify_extension > extension-build.log 2>&1
ulimit -Sv 16777216
python3 validate_zero.py > zero-proof-replay.log 2>&1
ulimit -Sv 67108864
target/release/verify_extension /home/hclau/ecdsa_research/product-exact-20261015/product-to67-rank-20261016/product-67-retained-1024-proxy.bin /home/hclau/ecdsa_research/product-pareto-20261019/parent/ops.bin /home/hclau/ecdsa_research/product-pareto-20261019/parent4-transfer/leases.json PUBLIC-PARENT-TRANSFER.json VERIFIED-EXTENSION-PROOFS.json > extension-verify.log 2>&1
sha256sum PUBLIC-PARENT-TRANSFER.json VERIFIED-EXTENSION-PROOFS.json > EXTENSION-CERTIFICATES.sha256

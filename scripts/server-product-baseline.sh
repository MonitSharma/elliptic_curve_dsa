#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product
mkdir -p ../logs
trap 'rc=$?; printf "%s\n" "$rc" > ../logs/product-baseline.exit' EXIT
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
unset LOWQ_EXACT_STREAM_PATH
ulimit -v 16777216
. /home/hclau/.cargo/env
git rev-parse HEAD
git status --short
/usr/bin/time -v bash ./benchmark.sh --note 'Unmodified public Q1234 baseline replay on smu_server, 14 October 2026; reproduction only.'
sha256sum ops.bin > ../logs/product-baseline-ops.sha256
cp score.json ../logs/product-baseline-score.json

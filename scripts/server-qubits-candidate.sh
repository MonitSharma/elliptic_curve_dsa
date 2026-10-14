#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/qubits
mkdir -p ../logs
trap 'rc=$?; printf "%s\n" "$rc" > ../logs/qubits-compact-candidate.exit' EXIT
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
unset LOWQ_EXACT_STREAM_PATH
ulimit -v 134217728
. /home/hclau/.cargo/env
git rev-parse HEAD
git diff --stat
cargo +1.93.0 test --release --locked --offline --bin build_circuit tests_midg_k24 -- --nocapture
/usr/bin/time -v bash ./benchmark.sh --note 'Compact 24-lane reciprocal on public Q693 baseline; unchanged K24, TC26, QB23 and map envelope; no nonce search.'
sha256sum ops.bin > ../logs/qubits-compact-candidate-ops.sha256
cp score.json ../logs/qubits-compact-candidate-score.json

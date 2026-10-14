#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014/qubits
cd "$root"
echo "$$" > evidence/diag2379-base.pid
trap 'code=$?; echo "$code" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/diag2379-base.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
. /home/hclau/.cargo/env
date -u
hostname
python3 /home/hclau/ecdsa_research/server-preflight.py > evidence/diag2379-base-preflight.json
git clone --quiet --no-hardlinks base diag2379-base
python3 qubit-prepare-2379-base-regression.py base diag2379v2-n274-v4 diag2379-base evidence > evidence/diag2379-base-preparation.log
export CARGO_TARGET_DIR="$root/diag2379-base/target"
/usr/bin/time -v cargo +1.93.0 test --release --locked --offline --manifest-path diag2379-base/Cargo.toml --bin build_circuit qubit_diag2379_full_column_negative_control -- --nocapture --test-threads=1 > evidence/diag2379-base-native.log 2>&1
grep -q 'test result: ok. 1 passed; 0 failed' evidence/diag2379-base-native.log
grep -q 'FIXED2379_NEGATIVE forward_bad=' evidence/diag2379-base-native.log
sha256sum "$CARGO_TARGET_DIR"/release/deps/build_circuit-* > evidence/diag2379-base-binary.sha256
date -u

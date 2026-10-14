#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014/qubits
cd "$root"
echo "$$" > evidence/diag2379-cycle.pid
trap 'code=$?; echo "$code" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/diag2379-cycle.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
. /home/hclau/.cargo/env
for variant in n275-v2 headflag-v1 n274-v4; do
  date -u
  hostname
  python3 /home/hclau/ecdsa_research/server-preflight.py > "evidence/diag2379-$variant-preflight.json"
  git clone --quiet --no-hardlinks base "diag2379-$variant"
  python3 qubit-prepare-2379-regression.py "candidate-$variant" "diag2379-$variant" evidence > "evidence/diag2379-$variant-preparation.log"
  export CARGO_TARGET_DIR="$root/diag2379-$variant/target"
  set +e
  /usr/bin/time -v cargo +1.93.0 test --release --locked --offline --manifest-path "diag2379-$variant/Cargo.toml" --bin build_circuit qubit_diag2379_full_column_negative_control -- --nocapture --test-threads=1 > "evidence/diag2379-$variant.log" 2>&1
  code=$?
  set -e
  echo "$code" > "evidence/diag2379-$variant.exit"
  sha256sum "$CARGO_TARGET_DIR"/release/deps/build_circuit-* > "evidence/diag2379-$variant-binary.sha256"
  test "$code" = 0
done
date -u

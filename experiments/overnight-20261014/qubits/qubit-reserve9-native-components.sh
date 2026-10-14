#!/usr/bin/env bash
set -eu
cd /home/hclau/ecdsa_research/overnight-20261014/qubits
echo "$$" > evidence/reserve9-native-components.pid
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/reserve9-native-components.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
. /home/hclau/.cargo/env
for variant in component-reserve7-negative candidate-reserve9; do
  date -u
  hostname
  python3 /home/hclau/ecdsa_research/server-preflight.py > "evidence/reserve9-${variant}-preflight.json"
  git -C "$variant" rev-parse HEAD
  sha256sum "$variant/src/point_add/frogdrop.rs" "$variant/src/point_add/midg.rs" "$variant/src/point_add/tests_midg_k24.rs" "evidence/${variant}.patch"
  if test "$variant" = component-reserve7-negative; then filter=reserve7_crossing_3713; else filter=reserve9_columns_crossing_3713; fi
  /usr/bin/time -v cargo +1.93.0 test --release --locked --offline --manifest-path "$variant/Cargo.toml" --bin build_circuit "$filter" -- --nocapture --test-threads=1 > "evidence/reserve9-${variant}.log" 2>&1
done
date -u

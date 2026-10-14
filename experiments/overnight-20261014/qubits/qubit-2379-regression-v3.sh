#!/usr/bin/env bash
# Reuse unchanged source-bound diagnostic binaries; v2 ran the wrong filter.
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014/qubits
cd "$root"
echo "$$" > evidence/diag2379v3-cycle.pid
trap 'code=$?; echo "$code" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/diag2379v3-cycle.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
. /home/hclau/.cargo/env
while ! test -s evidence/diag2379v2-cycle.exit; do sleep 10; done
for variant in n275-v2 headflag-v1 n274-v4; do
  date -u
  python3 /home/hclau/ecdsa_research/server-preflight.py > "evidence/diag2379v3-$variant-preflight.json"
  python3 - "$variant" <<'PY'
import hashlib,json,sys
from pathlib import Path
r=Path('/home/hclau/ecdsa_research/overnight-20261014/qubits');v=sys.argv[1]
m=json.loads((r/f'evidence/diag2379v2-{v}-manifest.json').read_text())
for name,h in m['diagnostic_source_sha256'].items():
    assert hashlib.sha256((r/f'diag2379v2-{v}'/name).read_bytes()).hexdigest()==h,name
print(json.dumps(m,sort_keys=True))
PY
  export CARGO_TARGET_DIR="$root/diag2379v2-$variant/target"
  set +e
  /usr/bin/time -v cargo +1.93.0 test --release --locked --offline --manifest-path "diag2379v2-$variant/Cargo.toml" --bin build_circuit qubit_diag2379_full_column_negative_control -- --nocapture --test-threads=1 > "evidence/diag2379v3-$variant.log" 2>&1
  code=$?
  set -e
  echo "$code" > "evidence/diag2379v3-$variant.native.exit"
  test "$code" = 0
  grep -q 'test result: ok. 1 passed; 0 failed' "evidence/diag2379v3-$variant.log"
  grep -q 'FIXED2379_NEGATIVE forward_bad=' "evidence/diag2379v3-$variant.log"
  sha256sum "$CARGO_TARGET_DIR"/release/deps/build_circuit-* > "evidence/diag2379v3-$variant-binary.sha256"
  echo 0 > "evidence/diag2379v3-$variant.exit"
done
date -u

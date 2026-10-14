#!/usr/bin/env bash
set -eu
root=/home/hclau/ecdsa_research/overnight-20261014/qubits
cd "$root"
echo "$$" > evidence/ht25-v9-harness-build-v2.pid
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/ht25-v9-harness-build-v2.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1 CARGO_TARGET_DIR="$root/harness-ht25-v9/target"
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
. /home/hclau/.cargo/env
date -u
python3 /home/hclau/ecdsa_research/server-preflight.py > evidence/ht25-v9-harness-build-v2-preflight.json
python3 qubit-prepare-trusted-harness.py base harness-ht25-v9 evidence/ht25-v9-protected-harness-manifest.json
/usr/bin/time -v cargo +1.93.0 build --release --offline --locked --manifest-path harness-ht25-v9/Cargo.toml --bin eval_circuit
sha256sum harness-ht25-v9/target/release/eval_circuit
python3 - <<'PY'
from pathlib import Path
import hashlib,json
r=Path('/home/hclau/ecdsa_research/overnight-20261014/qubits')
p=r/'evidence/ht25-v9-protected-harness-manifest.json'
m=json.loads(p.read_text())
m['protected_binary_sha256']=hashlib.sha256((r/'harness-ht25-v9/target/release/eval_circuit').read_bytes()).hexdigest()
assert len(m['protected_binary_sha256'])==64
p.write_text(json.dumps(m,indent=2)+'\n')
PY
date -u


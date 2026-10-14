#!/usr/bin/env bash
# Prepared only. Coordinator reviews this external proof wrapper before launch.
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014/qubits
evidence="$root/evidence/n274-v4-decision"
mkdir -p "$evidence"
echo "$$" > "$evidence/run.pid"
trap 'code=$?; printf "%s\n" "$code" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/n274-v4-decision/run.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
. /home/hclau/.cargo/env
date -u
hostname
python3 /home/hclau/ecdsa_research/server-preflight.py > "$evidence/preflight.json"
python3 - <<'PY'
import hashlib,json
from pathlib import Path
r=Path('/home/hclau/ecdsa_research/overnight-20261014/qubits')
p=r/'evidence/n274-v4-decision/crate';m=json.loads((p/'complete-source-binding.json').read_text())
assert m['frozen_kernel_sha256']=='72ab93a2fa1fd20bb3aad370aca9f6016ea9069013eaaa34d6b02d911d859622'
assert hashlib.sha256((p/'phase-audit-kernel.rs').read_bytes()).hexdigest()==m['frozen_kernel_sha256']
original=r/'candidate-n274-v4'
assert (r/'evidence/n274-v4-components.exit').read_text().strip()=='0'
for name,h in m['source_sha256'].items():
    assert hashlib.sha256((original/'src/point_add'/name).read_bytes()).hexdigest()==h,name
    if name not in m['research_test_sha256']:
        assert hashlib.sha256((p/'source/point_add'/name).read_bytes()).hexdigest()==h,('private-copy',name)
for name,h in m['research_test_sha256'].items():assert hashlib.sha256((p/'source/point_add'/name).read_bytes()).hexdigest()==h,name
assert m['point_add_patch_sha256']==json.loads((r/'evidence/candidate-n274-v4-manifest.json').read_text())['patch_sha256']
print(json.dumps(m,sort_keys=True))
PY
cd "$evidence/crate"
export CARGO_TARGET_DIR="$evidence/target"
sha256sum "$root/qubit-prepare-n274-v4-decision-proof.py" "$root/qubit-n274-v4-decision-proof.sh" phase-audit-kernel.rs src/main.rs Cargo.toml source/point_add/tests_midg_k24.rs source/point_add/tests_frogdrop.rs > "$evidence/proof-source.sha256"
cargo generate-lockfile --offline
sha256sum Cargo.lock >> "$evidence/proof-source.sha256"
/usr/bin/time -v cargo +1.93.0 test --release --locked --offline coordinator_ -- --nocapture --test-threads=1
sha256sum "$CARGO_TARGET_DIR"/release/deps/qubit_n274_v4_fixed_decision_proof-*
date -u

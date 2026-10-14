#!/usr/bin/env bash
set -eu
cd /home/hclau/ecdsa_research/overnight-20261014/qubits
echo "$$" > evidence/headflag-v1-components.pid
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/headflag-v1-components.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/overnight-20261014/qubits/candidate-headflag-v1/target
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
. /home/hclau/.cargo/env
date -u
hostname
python3 /home/hclau/ecdsa_research/server-preflight.py > evidence/headflag-v1-preflight.json
python3 - <<'PY'
import hashlib,json,subprocess
from pathlib import Path
root=Path('/home/hclau/ecdsa_research/overnight-20261014/qubits')
manifest=json.loads((root/'evidence/candidate-headflag-v1-manifest.json').read_text())
checkout=root/'candidate-headflag-v1'
assert subprocess.check_output(['git','-C',str(checkout),'rev-parse','HEAD'],text=True).strip()==manifest['base_revision']
changed=set(subprocess.check_output(['git','-C',str(checkout),'diff','HEAD','--name-only'],text=True).splitlines())
assert changed==set(manifest['candidate_changed_paths'])
for relative,expected in manifest['source_sha256'].items():
    actual=hashlib.sha256((checkout/relative).read_bytes()).hexdigest()
    assert actual==expected,(relative,actual,expected)
assert hashlib.sha256((root/'evidence/candidate-headflag-v1.patch').read_bytes()).hexdigest()==manifest['patch_sha256']
print(json.dumps(manifest,sort_keys=True))
PY
for filter in headflag_ n275_ ph_owner_ cap24_counterexample8048 reserve9_; do
  /usr/bin/time -v cargo +1.93.0 test --release --locked --offline --manifest-path candidate-headflag-v1/Cargo.toml --bin build_circuit "$filter" -- --nocapture --test-threads=1
done
sha256sum candidate-headflag-v1/target/release/deps/build_circuit-*
date -u

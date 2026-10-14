#!/usr/bin/env bash
# Prepared launcher. Coordinator must explicitly authorize launching it.
set -eu
root=/home/hclau/ecdsa_research/overnight-20261014/qubits
cd "$root"
echo "$$" > evidence/n275-v2-full-build.pid
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/n275-v2-full-build.exit' EXIT
ulimit -v 134217728
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export CARGO_TARGET_DIR="$root/candidate-n275-v2/target"
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL FD_POOL MIDG_RES FD_OLDPROBE FD_NOMAPANDC D3_NOMAPBOOTH
. /home/hclau/.cargo/env
date -u
hostname
python3 /home/hclau/ecdsa_research/server-preflight.py > evidence/n275-v2-full-build-preflight.json
python3 - <<'PY'
from pathlib import Path
import hashlib,json,subprocess
r=Path('/home/hclau/ecdsa_research/overnight-20261014/qubits');m=json.loads((r/'evidence/candidate-n275-v2-manifest.json').read_text());s=r/'candidate-n275-v2'
assert subprocess.check_output(['git','-C',str(s),'rev-parse','HEAD'],text=True).strip()==m['base_revision']
changed=subprocess.check_output(['git','-C',str(s),'diff','HEAD','--name-only'],text=True).splitlines()
assert sorted(changed)==sorted(m['candidate_changed_paths'])
assert all(p.startswith('src/point_add/')for p in changed)
assert not subprocess.check_output(['git','-C',str(s),'ls-files','--others','--exclude-standard'],text=True).strip()
for p,h in m['source_sha256'].items():assert hashlib.sha256((s/p).read_bytes()).hexdigest()==h,p
assert hashlib.sha256((r/'evidence/candidate-n275-v2.patch').read_bytes()).hexdigest()==m['patch_sha256']
print(json.dumps(m,sort_keys=True))
PY
cargo +1.93.0 build --release --locked --offline --manifest-path candidate-n275-v2/Cargo.toml --bin build_circuit
sha256sum "$CARGO_TARGET_DIR/release/build_circuit"
cd candidate-n275-v2
export LOWQ_EXACT_STREAM_PATH="$root/evidence/n275-v2-ops.bin"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit"
sha256sum "$LOWQ_EXACT_STREAM_PATH"
stat -c 'compressed_bytes=%s' "$LOWQ_EXACT_STREAM_PATH"
unset LOWQ_EXACT_STREAM_PATH
cd "$root"
export CARGO_TARGET_DIR="$root/stream-resource-meta/target"
python3 qubit-create-stream-meta.py base stream-resource-meta
cargo +1.93.0 build --release --offline --manifest-path stream-resource-meta/Cargo.toml
/usr/bin/time -v "$CARGO_TARGET_DIR/release/qubit_stream_resource_meta" "$root/evidence/n275-v2-ops.bin" > evidence/n275-v2-stream-metadata.json
sha256sum stream-resource-meta/src/main.rs stream-resource-meta/Cargo.toml stream-resource-meta/Cargo.lock "$CARGO_TARGET_DIR/release/qubit_stream_resource_meta"
date -u

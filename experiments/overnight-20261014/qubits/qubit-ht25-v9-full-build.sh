#!/usr/bin/env bash
# Prepared launcher. Coordinator must explicitly authorize launching it.
set -eu
root=/home/hclau/ecdsa_research/overnight-20261014/qubits
cd "$root"
echo "$$" > evidence/ht25-v9-full-build.pid
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/ht25-v9-full-build.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
export CARGO_TARGET_DIR="$root/candidate-ht25-v9/target"
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL FD_POOL MIDG_RES FD_OLDPROBE FD_NOMAPANDC D3_NOMAPBOOTH
. /home/hclau/.cargo/env
date -u
hostname
python3 /home/hclau/ecdsa_research/server-preflight.py > evidence/ht25-v9-full-build-preflight.json
python3 - <<'PY'
from pathlib import Path
import hashlib,json,subprocess,re
r=Path('/home/hclau/ecdsa_research/overnight-20261014/qubits');m=json.loads((r/'evidence/candidate-ht25-v9-manifest.json').read_text());s=r/'candidate-ht25-v9'
assert subprocess.check_output(['git','-C',str(s),'rev-parse','HEAD'],text=True).strip()==m['base_revision']
assert (r/'evidence/ht25-v9-components.exit').read_text().strip()=='0'
assert (r/'evidence/ht25-v9-decision-v3/run.exit').read_text().strip()=='0'
native=(r/'evidence/ht25-v9-components.log').read_text();assert list(map(int,re.findall(r'test result: ok\. (\d+) passed; 0 failed',native)))==[6,5,2,1,2]
proof=(r/'evidence/ht25-v9-decision-v3/native-proof.log').read_text();assert 'test result: ok. 16 passed; 0 failed' in proof and proof.count('DECISION_DIAGRAM_PHASE_PROOF')==576
changed=subprocess.check_output(['git','-C',str(s),'diff','HEAD','--name-only'],text=True).splitlines()
assert sorted(changed)==sorted(m['candidate_changed_paths'])
assert all(p.startswith('src/point_add/')for p in changed)
assert not subprocess.check_output(['git','-C',str(s),'ls-files','--others','--exclude-standard'],text=True).strip()
for p,h in m['source_sha256'].items():assert hashlib.sha256((s/p).read_bytes()).hexdigest()==h,p
assert hashlib.sha256((r/'evidence/candidate-ht25-v9.patch').read_bytes()).hexdigest()==m['patch_sha256']
protected={}
for p in subprocess.check_output(['git','-C',str(s),'ls-files'],text=True).splitlines():
    if p.startswith('src/point_add/'):continue
    original=subprocess.check_output(['git','-C',str(s),'show','HEAD:'+p]);actual=(s/p).read_bytes()
    assert actual==original,('protected',p)
    protected[p]=hashlib.sha256(actual).hexdigest()
(r/'evidence/ht25-v9-full-build-protected-source.json').write_text(json.dumps(protected,indent=2)+'\n')
print(json.dumps(m,sort_keys=True))
PY
cargo +1.93.0 test --release --locked --offline --manifest-path candidate-ht25-v9/Cargo.toml --bin build_circuit serializer_matches_unchanged_harness_bytes -- --nocapture --test-threads=1 > evidence/ht25-v9-serializer.log 2>&1
grep -q 'test result: ok. 1 passed; 0 failed' evidence/ht25-v9-serializer.log
grep -q 'EXACT_STREAM_SERIALIZER_PASS physical_ops=462 all_fields=true trusted_write_ops=true' evidence/ht25-v9-serializer.log
cargo +1.93.0 build --release --locked --offline --manifest-path candidate-ht25-v9/Cargo.toml --bin build_circuit
sha256sum "$CARGO_TARGET_DIR/release/build_circuit"
cd candidate-ht25-v9
export LOWQ_EXACT_STREAM_PATH="$root/evidence/ht25-v9-ops.bin"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit"
sha256sum "$LOWQ_EXACT_STREAM_PATH"
stat -c 'compressed_bytes=%s' "$LOWQ_EXACT_STREAM_PATH"
unset LOWQ_EXACT_STREAM_PATH
cd "$root"
export CARGO_TARGET_DIR="$root/stream-resource-meta/target"
test -x "$CARGO_TARGET_DIR/release/qubit_stream_resource_meta"
# Existing unchanged external bounded metadata binary reused.
/usr/bin/time -v "$CARGO_TARGET_DIR/release/qubit_stream_resource_meta" "$root/evidence/ht25-v9-ops.bin" > evidence/ht25-v9-stream-metadata.json
python3 - <<'PY'
from pathlib import Path
import json
r=Path('/home/hclau/ecdsa_research/overnight-20261014/qubits');m=json.loads((r/'evidence/ht25-v9-stream-metadata.json').read_text());print(m)
# Metadata is bounded: never load a Vec or invoke a scorer here.
counts=[v for k,v in m.items()if k in ('ops','ops_count','n','N','physical_ops','header_n','decoded_ops','ops_total')]
assert counts,('unrecognized metadata count fields',m.keys())
n=max(counts);admission=dict(scope='Parser count admission only; no full evaluation or score',MAX_OPS=4000000000,observed_N=n,within_MAX_OPS=n<=4000000000,constructor_source='candidate-ht25-v9',placeholder_scored=False)
(r/'evidence/ht25-v9-parser-admission.json').write_text(json.dumps(admission,indent=2)+'\n');print(admission)
PY
sha256sum stream-resource-meta/src/main.rs stream-resource-meta/Cargo.toml stream-resource-meta/Cargo.lock "$CARGO_TARGET_DIR/release/qubit_stream_resource_meta"
date -u


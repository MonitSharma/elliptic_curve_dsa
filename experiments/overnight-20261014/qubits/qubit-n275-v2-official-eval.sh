#!/usr/bin/env bash
# Coordinator must authorize evaluation and specify virtual-memory KiB.
set -eu
root=/home/hclau/ecdsa_research/overnight-20261014/qubits
cd "$root"
limit_kib=${1:?explicit coordinator-approved memory KiB required}
case "$limit_kib" in *[!0-9]*|'') exit 2;; esac
echo "$$" > evidence/n275-v2-official-eval.pid
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/n275-v2-official-eval.exit' EXIT
ulimit -v "$limit_kib"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
date -u
hostname
python3 /home/hclau/ecdsa_research/server-preflight.py > evidence/n275-v2-official-eval-preflight.json
ps -eo pid,ppid,pcpu,rss,args --sort=-rss | head -12
python3 - "$limit_kib" <<'PY'
from pathlib import Path
import hashlib,json,subprocess,sys
r=Path('/home/hclau/ecdsa_research/overnight-20261014/qubits');limit=int(sys.argv[1])*1024
assert (r/'evidence/n275-v2-full-build.exit').read_text().strip()=='0'
assert (r/'evidence/n275-v2-harness-build.exit').read_text().strip()=='0'
assert (r/'evidence/n275-v2-serializer.exit').read_text().strip()=='0'
m=json.loads((r/'evidence/n275-v2-stream-metadata.json').read_text());need=m['op_vec_bytes']+16*2**30
pre=json.loads((r/'evidence/n275-v2-official-eval-preflight.json').read_text())
assert need<limit and need<pre['memory']['MemAvailable_bytes'],(need,limit,pre['memory']['MemAvailable_bytes'])
assert m['ops']>1_000_000 and m['sizeof_op']==56
stream=r/'evidence/n275-v2-ops.bin';header=stream.open('rb').read(16);assert header[:8]==b'QECCOPSZ'and int.from_bytes(header[8:],'little')==m['ops']
for name in ['candidate-n275-v2-manifest.json','n275-v2-protected-harness-manifest.json']:
    f=json.loads((r/'evidence'/name).read_text());s=Path(f['checkout']);hashes=f.get('source_sha256',f.get('protected_source_sha256'))
    for p,h in hashes.items():assert hashlib.sha256((s/p).read_bytes()).hexdigest()==h,p
    if 'candidate_changed_paths'in f:
        changed=subprocess.check_output(['git','-C',str(s),'diff','HEAD','--name-only'],text=True).splitlines()
        assert sorted(changed)==sorted(f['candidate_changed_paths'])
        assert subprocess.check_output(['git','-C',str(s),'rev-parse','HEAD'],text=True).strip()==f['base_revision']
        assert hashlib.sha256((r/'evidence/candidate-n275-v2.patch').read_bytes()).hexdigest()==f['patch_sha256']
h=r/'harness-n275-v2';assert not (h/'score.json').exists()and not (h/'results.tsv').exists()and not(h/'ops.bin').exists()
assert not subprocess.check_output(['git','-C',str(h),'status','--porcelain'],text=True).strip()
assert hashlib.sha256((h/'target/release/eval_circuit').read_bytes()).hexdigest()=='892c6c0c8ab7546dcee4fb08deb8146d4ca250b8ea941d02ce9bc43711ccb4dc'
(h/'ops.bin').symlink_to(stream);assert (h/'ops.bin').resolve()==stream.resolve()
print(json.dumps(dict(scope='Unchanged official evaluator allocation/input attestation',metadata=m,memory_limit_bytes=limit,storage_plus_margin_bytes=need,input_symlink=str(h/'ops.bin'),resolved_stream=str(stream),placeholder_used=False,historical_outputs_absent_before=True)))
PY
sha256sum evidence/n275-v2-ops.bin harness-n275-v2/target/release/eval_circuit
cd harness-n275-v2
set +e
/usr/bin/time -v target/release/eval_circuit --note "N275-v2 frozen patch10a0d56672b4327a341eca3a88fb0aaa34f1cad0a1e68c65ce30461b286cb17f; unchanged protected harness; exact full stream; nonce34/5 unchanged"
native_status=$?
set -e
echo "$native_status" > "$root/evidence/n275-v2-official-eval-native.exit"
for artifact in score.json results.tsv; do
  if test -f "$artifact"; then cp -n "$artifact" "$root/evidence/n275-v2-official-$artifact"; fi
done
date -u
exit "$native_status"

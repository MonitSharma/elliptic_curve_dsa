"""Gate all complete generated records and protected source after native build."""
from pathlib import Path
import hashlib,json,subprocess
from ops_io import load
HERE=Path(__file__).resolve().parent;tree=HERE/'candidate';freeze=json.loads((HERE/'NATIVE_SOURCE_FREEZE.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for rel,digest in {**freeze['source_files'],**freeze['protected_files']}.items():assert sha(tree/rel)==digest,rel
actual=tree/'ops.bin';a=load(actual);b=load(HERE/'candidate.bin');assert a==b
assert hashlib.sha256(a).hexdigest()==freeze['expected_canonical_sha256']
resources=json.loads(subprocess.check_output(['python3',str(HERE.parent/'product-exact-20261015/stream_resources.py'),str(actual)]))
assert resources['ops']==freeze['expected_ops'] and resources['qubits']==1473 and resources['classical_bits']==3112
assert len(freeze['protected_files'])==17
out=dict(status='FULL_NORMAL_NATIVE_ALL_OP_BYTES_AND_PROTECTED_SOURCE_PASS',canonical_sha256=hashlib.sha256(a).hexdigest(),
         native_stream_sha256=sha(actual),external_stream_sha256=sha(HERE/'candidate.bin'),resources=resources,
         all_source_files=len(freeze['source_files']),all_protected_files=17,freeze_sha256=sha(HERE/'NATIVE_SOURCE_FREEZE.json'),
         no_census_nonce_or_benchmark_claim=True)
(HERE/'NATIVE_RESULT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))

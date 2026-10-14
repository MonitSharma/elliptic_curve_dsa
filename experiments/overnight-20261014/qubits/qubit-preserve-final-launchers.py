"""Preserve exact server launcher bytes, including CRLF failures."""
from pathlib import Path
import hashlib,gzip,json,datetime
r=Path('/home/hclau/ecdsa_research/overnight-20261014/qubits');e=r/'evidence';files=[]
for name in ['qubit-ht25-v9-harness-build.sh','qubit-ht25-v9-harness-build-v2.sh','qubit-ht25-v9-full-build.sh','qubit-ht25-v9-decision-v2-proof.sh','qubit-ht25-v9-decision-v3-proof.sh','qubit-ht25-bankswap-v2-full-build.sh']:
 p=r/name
 if not p.exists():continue
 raw=p.read_bytes();archive=e/(name+'.raw.gz');archive.write_bytes(gzip.compress(raw,mtime=0))
 files.append(dict(source=name,source_sha256=hashlib.sha256(raw).hexdigest(),archive=archive.name,archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),CRLF_pairs=raw.count(b'\r\n'),lone_CR=raw.count(b'\r')-raw.count(b'\r\n')))
receipt=dict(collected_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=files,harness_v1=dict(wrapper_exit=127,native_compile_exit=0,protected_binary_sha256='88b6fd33dfcd85b317ed6694c10715dbb6b4d5926838400ec7c4e23cdda77e3a',failure='Trailing carriage-return shell command after completed native build; preserved exact bytes/log'),harness_v2=dict(wrapper_exit=0,new_LF_wrapper=True,reused_Cargo_build_artifact=True),V9_generation=dict(wrapper_exit=0,CRLF_failure=False,scope='Actual server launcher completed; local export line endings are separately archived'))
(e/'ht25-final-raw-launcher-index.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))

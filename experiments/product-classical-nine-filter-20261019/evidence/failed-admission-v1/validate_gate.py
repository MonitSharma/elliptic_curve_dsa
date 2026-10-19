"""One qualification only, and only after the declared source gate passes."""
import hashlib,json,os,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;n=r.parent/'product-classical-nine-20261019'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
assert (r/'build.exit').read_text().strip()=='0' and (n/'gate-v2.exit').read_text().strip()=='0'
gate=json.loads((n/'qualification/RESULT.json').read_text());assert gate['status']=='FAILURE_GATE_PASS' and all(gate['rules'].values())
assert not (r/'QUALIFICATION-START.json').exists()
prep=json.loads((r/'PREPARATION.json').read_text())
assert sha(n/'candidate/ops.bin')==prep['candidate_stream_sha256']==gate['stream_sha256']['candidate']
assert all(sha(Path(p))==h for p,h in prep['additional_proof_artifacts'].items())
assert all(sha(r/'tool'/p)==v['sha256'] for p,v in prep['files'].items())
receipt={'status':'NEW_SOURCE_DISABLED_RUNTIME_QUALIFICATION_STARTED_AFTER_FINAL_GATE_PASS','gate_sha256':sha(n/'qualification/RESULT.json'),'candidate_sha256':prep['candidate_stream_sha256'],'binary_sha256':sha(r/'tool/target/release/value_prefilter'),'authoritative_rejection':False,'nonce_selection_enabled':False,'controls':'Own Fiat-Shamir seeds; generic/threaded full9024 state/phase/physical-RNG; zero-MR128+partial; six4096-row prefix/timing trials.'}
(r/'QUALIFICATION-START.json').write_text(json.dumps(receipt,indent=2)+'\n')
subprocess.run(['python3',str(r/'validate.py')],check=True)
assert sha(r/'tool/target/release/value_prefilter')==receipt['binary_sha256']

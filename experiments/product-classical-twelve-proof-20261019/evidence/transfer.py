import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;n=ws/'product-classical-twelve-native-20261019';old=ws/'product-classical-nine-proof-20261019'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
read=lambda p:json.loads(Path(p).read_text())
assert (r/'run.exit').read_text().strip()==(n/'run.exit').read_text().strip()=='0'
assert read(r/'PROOF.json')['status']=='THREE_ADDITIONAL_SOURCE_BOUND_CLASSICAL_IDENTITIES_UNSAT_REPLAY_PASS'
assert read(r/'EDIT-AUDIT.json')['status']=='THREE_ADDITIONAL_REPLACEMENTS_AND_ALL_OTHER_OPS_VERIFIED'
native=read(n/'NATIVE-RECEIPT.json');assert native['raw_sha3_256']=='2ef31475f03b40a72d5522d830717aef4c1675d0e1a061bf0bfed78ab7d2f265'
assert native['compressed_sha256']=='17c767f514ca98ad02d4da9e5b1dbedf67189e5c70b7b15916adc0f0c2f0a7f7'==sha(n/'candidate/ops.bin')
freeze=read(n/'SOURCE_FREEZE.json');assert len(freeze['source_files'])==180 and len(freeze['protected_files'])==17
assert all(sha(n/'candidate'/p)==h for p,h in {**freeze['source_files'],**freeze['protected_files']}.items())
parent=read(old/'TRANSFER.json');assert parent['status']=='CLASSICAL_NINE_VALUE_PHASE_AND_RNG_TRANSFER_AUDIT_PASS'
assert all(sha(Path(p))==h for p,h in parent['required_artifacts'].items())
required=set(Path(p) for p in parent['required_artifacts'])
required.update([old/'TRANSFER.json',r/'PROOF.json',r/'EDIT-AUDIT.json',r/'AUDIT.json',r/'INSTRUMENTATION.json',r/'SEMANTICS.md',r/'prove.py',r/'verify_edits.rs',r/'transfer.py',r/'proof/wide/mod.rs',r/'proof/wide/table.rs',
 n/'SOURCE_FREEZE.json',n/'NATIVE-RECEIPT.json',n/'candidate/ops.bin',ws/'product-classical-factors-wide-20261019/CONTROL.json',ws/'product-classical-factors-wide-20261019/compat7.json',ws/'product-classical-factors-wide-20261019/tests-v2.log'])
required.update(r.glob('*.smt2.gz'));assert len(list(r.glob('factor-*.smt2.gz')))==3
result={'status':'CLASSICAL_TWELVE_VALUE_PHASE_AND_RNG_TRANSFER_AUDIT_PASS','candidate_stream_sha256':native['compressed_sha256'],'parent_classical9_stream_sha256':parent['candidate_stream_sha256'],'parent4_mask_sha256':parent['parent4_mask_sha256'],
 'additional_exact_identities':3,'source_files':180,'protected_files_unchanged':17,'required_artifacts':{str(p):sha(p) for p in sorted(required)},'authoritative_rejection_enabled':False,'nonce_selected':None,
 'scope':'Universal source extension only. No statistical gate, runtime acceptance or scored benchmark is claimed; no old gate reused.'}
(r/'TRANSFER.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='required_artifacts'},indent=2))

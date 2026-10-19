"""Bind exact source/equivalence evidence; never accepts a search runtime."""
import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;n=ws/'product-classical-nine-20261019'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
read=lambda p:json.loads(Path(p).read_text())
assert (r/'run.exit').read_text().strip()==(r/'edits.exit').read_text().strip()==(n/'run.exit').read_text().strip()=='0'
assert read(r/'PROOF.json')['status']=='EIGHT_SOURCE_BOUND_FACTOR_IDENTITIES_AND_NINTH_XOR_UNSAT_REPLAY_PASS'
assert read(r/'EDIT-AUDIT.json')['status']=='NINE_SOURCE_BOUND_REPLACEMENTS_AND_ALL_OTHER_OPS_VERIFIED'
native=read(n/'NATIVE-RECEIPT.json');assert native['raw_sha3_256']=='4b81cbc1e247e791ab11ff56c5f84b4da5edc8618d7c19fe590305390fa6f93f'
assert native['compressed_sha256']==sha(n/'candidate/ops.bin')
freeze=read(n/'SOURCE_FREEZE.json')
assert all(sha(n/'candidate'/p)==h for p,h in {**freeze['source_files'],**freeze['protected_files']}.items())
old=ws/'parent4-operational-sat-20261019/ACCEPTANCE.json';accepted=read(old)
assert accepted['status']=='SOURCE_BOUND_MASK_TRANSFER_AND_RUNTIME_ACCEPTED_FOR_ASCENDING_SEARCH'
assert all(sha(Path(p))==h for p,h in accepted['runtime_artifacts'].items())
required=[old,r/'PROOF.json',r/'EDIT-AUDIT.json',r/'AUDIT.json',r/'INSTRUMENTATION.json',r/'SEMANTICS.md',r/'prove.py',r/'verify_edits.rs',r/'transfer.py',r/'proof/classical_factors_xor.rs',
 ws/'product-classical-control-expression-20261019/EXPRESSION.json',ws/'product-classical-control-expression-20261019/expression.rs',ws/'product-classical-control-expression-20261019/guard_prefix.rs',
 ws/'product-classical-type-probe-20261019/RESULT.json',n/'SOURCE_FREEZE.json',n/'NATIVE-RECEIPT.json',n/'CONTROL-nine.json',n/'classical_xor_control.rs',
 ws/'product-classical-factors-refresh-20261019/CONTROL-parent4.json',ws/'product-classical-factors-native-20261019/NATIVE-RECEIPT.json',n/'candidate/ops.bin']
required.extend(sorted(r.glob('*.smt2.gz')))
assert len(list(r.glob('factor-*.smt2.gz')))==8
result={'status':'CLASSICAL_NINE_VALUE_PHASE_AND_RNG_TRANSFER_AUDIT_PASS','candidate_stream_sha256':native['compressed_sha256'],
 'parent4_stream_sha256':accepted['candidate_stream_sha256'],'parent4_mask_sha256':accepted['mask_sha256'],
 'all_17_protected_files_unchanged':True,'eight_factor_proofs':'independent UNSAT and saved SMT2 replay',
 'ninth_classical_control':'exact source-bound prefix induction and independent dirty-target XOR UNSAT',
 'old_accepted_runtime_artifacts_unchanged':len(accepted['runtime_artifacts']),
 'required_artifacts':{str(p):sha(p) for p in required},'authoritative_rejection_enabled':False,'nonce_selected':None,
 'scope':'Universal source transfer evidence only. Fresh gate and new-source runtime qualification remain mandatory before nonce search.'}
(r/'TRANSFER.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='required_artifacts'},indent=2))

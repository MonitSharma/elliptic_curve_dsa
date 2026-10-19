"""Bind independent local proof, exact frame audit and pinned native source."""
import gzip,hashlib,json,sys
from pathlib import Path
ws=Path(__file__).resolve().parent.parent;r=ws/'product-copy-cache-proof-20261020';n=ws/'product-copy-cache-native-20261020';parent=ws/'product-classical-twelve-native-20261019';oldproof=ws/'product-classical-twelve-proof-20261019'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
read=lambda p:json.loads(Path(p).read_text())
assert not (r/'TRANSFER.json').exists()
assert (n/'run.exit').read_text().strip()=='0';native=read(n/'NATIVE-RECEIPT.json');freeze=read(n/'SOURCE_FREEZE.json')
assert native['raw_sha3_256']=='d343ca717c726c9136505edb1ba3602a58f7bfe063151d8a9e82b4f39d71a6a5' and native['ops']==17889637
assert len(freeze['source_files'])==182 and len(freeze['protected_files'])==17
assert all(sha(n/'candidate'/p)==h for p,h in {**freeze['source_files'],**freeze['protected_files']}.items())
assert sha(n/'candidate/ops.bin')==native['compressed_sha256']=='26dc60ee329a6cf448143eebc9f1f218efd73ffeaaef92213a75e7d31f3e7cc1'
audit=read(r/'EDIT-AUDIT.json');result=read(r/'LOCAL-WINDOW-RESULT.json')
assert audit['predicted_full_output_raw_sha3_256']==native['raw_sha3_256'] and audit['storage_not_abi_and_no_original_touch_in_closed_hold']
assert sha(r/'WINDOW.json')==audit['window_sha256'];assert result['verdict']=='unsat' and result['saved_smt2_replayed'] and result['physical_draw_count_each']==770 and result['phase_compared']
assert 'Ran 6 tests' in (r/'proof.log').read_text() and '\nOK\n' in (r/'proof.log').read_text()
sys.path.insert(0,str(ws/'product-parent-sat-20261019/libraries'));import z3
s=z3.Solver();s.from_string(gzip.open(r/'local-window.smt2.gz','rt').read());assert s.check()==z3.unsat
replay={'status':'INDEPENDENT_SERVER_SMT2_REPLAY_UNSAT','z3_version':z3.get_version_string(),'smt2_sha256':sha(r/'local-window.smt2.gz'),'local_solver_version':result['solver_version'],'scope':'Same saved theorem; no new test input, census or verdict.'};(r/'SERVER-REPLAY.json').write_text(json.dumps(replay,indent=2)+'\n')
old=read(oldproof/'TRANSFER.json');assert old['status']=='CLASSICAL_TWELVE_VALUE_PHASE_AND_RNG_TRANSFER_AUDIT_PASS'
required={str(Path(p)):h for p,h in old['required_artifacts'].items()}
paths=[oldproof/'TRANSFER.json',parent/'NATIVE-RECEIPT.json',parent/'SOURCE_FREEZE.json',parent/'point-add-source.tar.gz',parent/'candidate/ops.bin',n/'NATIVE-RECEIPT.json',n/'SOURCE_FREEZE.json',n/'point-add-source.tar.gz',n/'candidate/ops.bin',n/'candidate/src/sim.rs',n/'candidate/src/point_add/copy_cache_one.rs',n/'candidate/src/point_add/tests_copy_cache_one.rs',n/'prototype-RESULT.json',r/'WINDOW.json',r/'EDIT-AUDIT.json',r/'LOCAL-WINDOW-RESULT.json',r/'local-window.smt2.gz',r/'local-window.proof.gz',r/'prove_window.py',r/'extract.py',r/'METHOD.md',r/'proof.log',r/'SERVER-REPLAY.json']
required.update({str(p):sha(p) for p in paths});assert all(sha(Path(p))==h for p,h in required.items())
prototype=read(n/'prototype-RESULT.json');assert prototype['cache_pairs']==1 and prototype['control']['saved_executed_Toffolis_total_on_512_control_shots']==512
component={'status':'UNIVERSAL_ONE_EXECUTED_TOFFOLI_PER_SHOT_SAVING_CERTIFIED','additional_executed_toffoli_saving_per_shot':1,'every_quantum_classical_phase_and_physical_rng_value_equal':True,'finite_control_shots':512,'finite_control_total_saving':512,'scope':'Unconditional structural cost theorem plus finite protected control. No valid-point mean estimate, statistical gate, nonce selection or full resource record.'};(r/'COMPONENT.json').write_text(json.dumps(component,indent=2)+'\n')
required[str(r/'COMPONENT.json')]=sha(r/'COMPONENT.json')
transfer={'status':'COPY_CACHE_VALUE_PHASE_AND_PHYSICAL_RNG_TRANSFER_AUDIT_PASS','candidate_stream_sha256':native['compressed_sha256'],'parent_stream_sha256':read(parent/'NATIVE-RECEIPT.json')['compressed_sha256'],'source_archive_sha256':native['source_archive_sha256'],'source_files':182,'protected_files_unchanged':17,'independent_all_state_phase_and_rng_theorem':result,'server_saved_theorem_replay':replay,'extra_measurements_or_resets':0,'required_artifacts':required,'new_statistical_gate_still_required':True,'no_nonce_selected':True,'score':None}
(r/'TRANSFER.json').write_text(json.dumps(transfer,indent=2)+'\n');print(json.dumps({'status':transfer['status'],'bound_artifacts':len(required),'native_source_files':182,'scope':'No new gate or nonce, no record.'}))

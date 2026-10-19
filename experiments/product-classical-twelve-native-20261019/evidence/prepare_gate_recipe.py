from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'product-classical-nine-20261019'
s=(old/'qualify.py').read_text().replace('pareto-parent4-classical9-gate-20261019-v1','pareto-parent4-classical12-gate-20261019-v1')
needle='assert len(freeze[\'protected_files\'])==17';assert s.count(needle)==1
proof='''assert len(freeze['source_files'])==180
proof=r.parent/'product-classical-twelve-proof-20261019'
assert (proof/'run.exit').read_text().strip()=='0'
transfer=json.loads((proof/'TRANSFER.json').read_text())
assert transfer['status']=='CLASSICAL_TWELVE_VALUE_PHASE_AND_RNG_TRANSFER_AUDIT_PASS'
assert transfer['candidate_stream_sha256']==native['compressed_sha256']
assert all(sha(Path(p))==h for p,h in transfer['required_artifacts'].items())
component=json.loads((proof/'COMPONENT.json').read_text())
assert component['status']=='FRESH_VALID_POINT_COMPONENT_SAVING_VERIFIED'
assert component['additional_mean_executed_Toffolis_saved']>0 and component['every_paired_value_phase_and_dirty_diagnostic_identical']
'''
s=s.replace(needle,needle+'\n'+proof)
s=s.replace("'scope':'Fresh failure-rate qualification only; no benchmark, score or nonce search.',","'scope':'Independent final classical12 gate planned before the classical9 verdict. Fresh failure-rate qualification only; no benchmark, score or nonce search.',\n      'universal_transfer_sha256':sha(proof/'TRANSFER.json'),'valid_point_component_sha256':sha(proof/'COMPONENT.json'),'predeclared_plan_sha256':sha(r/'GATE-PLAN.md'),")
(r/'qualify.py').write_text(s,newline='\n')
(r/'refresh_record.py').write_bytes((old/'refresh_record.py').read_bytes())
for p in r.glob('*.py'):compile(p.read_text(),str(p),'exec')
print('Prepared fixed262144-batch classical12 gate recipe; no declaration or census started')

import hashlib,importlib.util,json,struct,subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prefix='zero-8192';d=json.loads((r/(prefix+'-result.json')).read_text());m=d['input']
assert d['status']=='UNIVERSAL_ZERO_EFFECT_PASS' and d['verdict']=='unsat'
assert d['driver_sha256']==sha(r/'prove_zero.py')
assert m['initial_depth']==0 and m['first']==m['last']==17876252
assert m['base_pre_tail_sha3_256']=='468e86dd1628976643d42b4bb50bdb8c43211f4d29bfbc3df60b11f7342ac619'
raw=(r/m['raw_file']).read_bytes();assert sha(r/m['raw_file'])==m['raw_sha256']
assert hashlib.sha3_256(raw).hexdigest()==m['raw_sha3_256']
assert hashlib.sha3_256(raw[-56:]).hexdigest()==m['row_sha3_256']=='167c7dad3201c7b11743b8d6bdd1949fa61952ac7201f71692a3a369be305823'
with (r/(prefix+'-replay.log')).open('wb') as log:
    subprocess.run([sys.executable,str(r/'replay_one.py'),str(r/(prefix+'.smt2.gz')),str(r/(prefix+'-replay.json'))],stdout=log,stderr=subprocess.STDOUT,check=True)
replay=json.loads((r/(prefix+'-replay.json')).read_text());assert replay['verdict']=='unsat'
spec=importlib.util.spec_from_file_location('zero_proof',r/'prove_zero.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
ops=list(struct.iter_unpack('<7Q',raw));NO=(1<<64)-1;a,b=ops[-1][2],ops[-1][1]
faults=[]
for wires in ([a],[b],[a,b]):
    mutation=ops[:-1]+[(6,NO,NO,q,NO,NO,NO) for q in wires]+ops[-1:]
    name='zero-fault-'+('-'.join(map(str,wires)))
    proof=mod.prove(mutation,timeout=30000,save=r/name,first_index=len(mutation)-1,zero_goal=True)
    faults.append({'flipped_controls':wires,'verdict':proof['verdict'],'seconds':proof['seconds']})
assert any(f['verdict']=='sat' for f in faults),'The actual source mutation control did not expose an error'
(r/'ZERO-MUTATION-CONTROLS.json').write_text(json.dumps(faults,indent=2)+'\n')
out=json.loads((r/'VERIFIED-PROOFS.json').read_text());assert out['status']=='SOURCE_BOUND_UNIVERSAL_PROOFS_VERIFIED'
out['status']='SOURCE_BOUND_EXTENSION_PROOFS_VERIFIED'
out['zero_row']={'input':m,'fresh_replay':replay,'mutation_controls':faults,
    'meaningful_source_fault_detected':True,'result_sha256':sha(r/(prefix+'-result.json')),
    'source_driver_sha256':sha(r/'prove_zero.py'),'formula_sha256':sha(r/(prefix+'.smt2.gz'))}
(r/'VERIFIED-EXTENSION-PROOFS.json').write_text(json.dumps(out,indent=2)+'\n')
print('Zero row replayed UNSAT; actual source-control mutation detected; extension proofs ready',flush=True)

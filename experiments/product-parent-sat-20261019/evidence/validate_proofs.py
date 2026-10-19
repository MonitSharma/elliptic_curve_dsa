import concurrent.futures,hashlib,json,subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
properties=json.loads((r/'GLOBAL-PROPERTIES.json').read_text())
assert len(properties)==27 and all(all(p[k] is True for k in ('start_guard_true','end_guard_true','donor_clean','donor_untouched')) for p in properties)
def one(j):
    prefix='wide-02-1024' if j==2 else f'seeded-lease-{j:02}'
    d=json.loads((r/(prefix+'-result.json')).read_text())
    assert d['status']=='UNIVERSAL_PRODUCT_EQUALITY_PASS' and d['verdict']=='unsat'
    driver=r/('prove_wide.py' if j==2 else 'prove.py')
    assert d['driver_sha256']==sha(driver)
    m=d['input'];assert m['lease']==j
    assert m['base_pre_tail_sha3_256']=='c143e90580bb0c6f6a12996a50147c179c4fdfe3a50d8af85350bf9e6d755e04'
    assert m['raw_sha256']==sha(r/m['raw_file'])
    if j!=2:assert d['boundary_sha256']==sha(r/f'boundary-{j:02}.json')
    else:assert m['initial_depth']==0 and m['start']<=m['first']
    formula=r/(prefix+'.smt2.gz');output=r/(prefix+'-replay.json')
    with (r/(prefix+'-replay.log')).open('wb') as log:
        subprocess.run([sys.executable,str(r/'replay_one.py'),str(formula),str(output)],stdout=log,stderr=subprocess.STDOUT,check=True)
    v=json.loads(output.read_text());assert v['verdict']=='unsat'
    return {'lease':j,'first':m['first'],'last':m['last'],'raw_sha256':m['raw_sha256'],
        'boundary_file':str(r/f'boundary-{j:02}.json'),'boundary_sha256':sha(r/f'boundary-{j:02}.json'),
        'proof_result_sha256':sha(r/(prefix+'-result.json')),'source_driver_sha256':sha(driver),
        'formula':formula.name,'formula_sha256':sha(formula),'fresh_replay':v}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:proofs=list(pool.map(one,range(1,28)))
out={'status':'SOURCE_BOUND_UNIVERSAL_PROOFS_VERIFIED','base_pre_tail_sha3_256':'c143e90580bb0c6f6a12996a50147c179c4fdfe3a50d8af85350bf9e6d755e04',
    'global_properties_sha256':sha(r/'GLOBAL-PROPERTIES.json'),'boundary_export_source_sha256':sha(r/'export.rs'),
    'replay_driver_sha256':sha(r/'replay_one.py'),'proofs':proofs,'nonce_rejection_enabled':False,'candidate_changed':False}
(r/'VERIFIED-PROOFS.json').write_text(json.dumps(out,indent=2)+'\n')
print('27 source-bound universal proofs replayed UNSAT',flush=True)

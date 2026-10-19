import concurrent.futures,hashlib,json,subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parent
properties=json.loads((r/'GLOBAL-PROPERTIES.json').read_text())
def one(j):
    with (r/f'seeded-lease-{j:02}.log').open('wb') as f:
        subprocess.run([sys.executable,str(r/'prove.py'),str(j),'seeded'],stdout=f,stderr=subprocess.STDOUT,check=True)
    return json.loads((r/f'seeded-lease-{j:02}-result.json').read_text())
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(one,range(1,28)))
good=lambda p:all(p[k] is True for k in ('start_guard_true','end_guard_true','donor_clean','donor_untouched'))
summary={'status':'SEEDED_LOCAL_PROOF_SCREEN_COMPLETE','proved':[j+1 for j,d in enumerate(results) if d['verdict']=='unsat'],
    'inconclusive':[j+1 for j,d in enumerate(results) if d['verdict']!='unsat'],
    'global_donor_guard_properties_pass':all(map(good,properties)),
    'global_properties':properties,'verdicts':[d['verdict'] for d in results],
    'candidate_changed':False,'gate_rerun':False,'nonce_rejection_enabled':False}
(r/'SEEDED-RESULT.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:summary[k] for k in ('status','proved','inconclusive','global_donor_guard_properties_pass')}),flush=True)

import hashlib,json,subprocess,tarfile
from pathlib import Path
from datetime import datetime,timezone
r=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for cut in (1232,1230):
    b=json.loads((r/f'borrow-{cut}.json').read_text())
    m=json.loads((r/f'combined-{cut}.json').read_text())
    s=json.loads((r/f'refined-{cut}.json').read_text())
    t=json.loads((r/f'last-carry-{cut}.json').read_text())
    w=json.loads((r/f'last-carry-width-{cut}.json').read_text())
    extra=sum(x['added_unconditional_Toffolis'] for x in (b,s,t))+m['predicted_additional_toffoli']
    q=w['peak_simultaneous_lifetimes']
    rows.append(dict(cut=cut,converted_carries=sum(x['replaced_carries'] for x in (b,s,t)),
        recomputed_caches=len(m['unwrappings']),conservative_Q=q,added_T=extra,
        budgeted_product=q*(761096+extra),product_delta=q*(761096+extra)-939192464,
        status='NEGATIVE_DIAGNOSTIC_NOT_A_SCORED_RESULT'))
(r/'FINAL-CARRY-RESULT.json').write_text(json.dumps(rows,indent=2)+'\n')
parent=r.parent/'product-pareto-20261019/parent'
state={'at_utc':datetime.now(timezone.utc).isoformat(),
    'parent_revision':subprocess.check_output(['git','-C',str(parent),'rev-parse','HEAD'],text=True).strip(),
    'parent_status':subprocess.check_output(['git','-C',str(parent),'status','--short'],text=True),
    'parent_stream_sha256':sha(parent/'ops.bin'),
    'terminal_exits':{p.name:p.read_text().strip() for p in r.glob('*.exit')},
    'census_gate_started':False,'nonce_search_started':False,'submission_created':False}
(r/'TERMINAL.json').write_text(json.dumps(state,indent=2)+'\n')
files=sorted(p for p in r.iterdir() if p.is_file() and p.suffix in ('.rs','.py','.sh','.toml','.lock','.json','.log','.sha256','.pid','.exit','.txt','.md'))
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({p.name:sha(p) for p in files if p.name!='EVIDENCE-MANIFEST.json'},indent=2)+'\n')
files.append(r/'EVIDENCE-MANIFEST.json')
with tarfile.open(r/'evidence.tar.gz','w:gz') as tar:
    for p in sorted(set(files)):tar.add(p,arcname=p.name)
(r/'EVIDENCE.sha256').write_text(sha(r/'evidence.tar.gz')+'  evidence.tar.gz\n')
print(json.dumps({'carry_results':rows,'terminal':state,'archive_sha256':sha(r/'evidence.tar.gz')}))

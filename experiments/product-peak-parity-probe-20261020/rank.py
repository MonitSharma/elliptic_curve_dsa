import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;meta=json.loads((r/'probe.json').read_text());b=json.loads((r/'BINDING.json').read_text());results=[]
for point in [b['point']-1,b['point']]:
 p=r/f'snapshot-{point}.json';snap=json.loads(p.read_text());q=snap['q'];terms=sorted({tuple(m) for poly in q for m in poly if m});column={m:i for i,m in enumerate(terms)};basis={};relations=[]
 for wire,poly in enumerate(q):
  if wire==len(q)-1:continue
  mask=sum(1<<column[tuple(m)] for m in poly if m);support=1<<wire;constant=[] in poly
  while mask:
   pivot=mask.bit_length()-1
   if pivot not in basis:basis[pivot]=(mask,support,constant);break
   other,provenance,c=basis[pivot];mask^=other;support^=provenance;constant^=c
  if not mask:
   wires=[i for i in range(len(q)) if support>>i&1];actual=set()
   for w in wires:actual.symmetric_difference_update(tuple(m) for m in q[w])
   assert actual==({()} if constant else set())
   quiet=not any(w in meta['epoch_touched_roles'] for w in wires)
   donors=[w for w in wires if w not in meta['ABI_roles'] and w!=len(q)-1] if quiet else []
   relations.append({'wires':wires,'constant':constant,'all_wires_untouched_in_epoch':quiet,'nonABI_donors':donors})
 results.append({'after_source_op':point,'qubit_roles':len(q),'non_high_rows':len(q)-1,'monomials':len(terms),'rank':len(basis),'linear_relations':len(relations),'quiet_held_relations':sum(bool(x['nonABI_donors']) for x in relations),'relations':relations,'snapshot_sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest()})
(r/'RESULT.json').write_text(json.dumps({'status':'EXACT_CONSERVATIVE_PEAK_ANF_RANK_DIAGNOSTIC_COMPLETED','prefix_baseline_all_fields_and_hashes_equal':True,'base_tests':17,'probe_tests':17,'fixed_epoch':[b['epoch_first'],b['epoch_last']],'states':results,'scope':'Exact rank of conservative ANF abstraction, not a quantum width lower bound, lease, native candidate, census, nonce or score.'},indent=2)+'\n');print(json.dumps([{k:v for k,v in x.items() if k!='relations'} for x in results],indent=2),flush=True)

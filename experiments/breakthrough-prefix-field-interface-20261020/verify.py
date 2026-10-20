"""Exact old/new field-map interface on the full14-bit domain."""
import hashlib,json,re
from pathlib import Path
r=Path(__file__).resolve().parent;s=(r/'runtime-source.rs').read_text();one=(1<<16384)-1;inputs=[sum(1<<v for v in range(16384)if v>>i&1)for i in range(14)]
def combine(mask,columns):
 out=0
 for i,x in enumerate(columns):
  if mask>>i&1:out^=x
 return out
def form(q,mask):return combine(mask,[one]+q)
def pairs(text):return[(int(a),int(b))for a,b in re.findall(r'\((\d+),(\d+)\)',text)]
q=inputs.copy();draws=0;gates=0
for line in s[s.index('const STAGES:'):s.index('fn form(')].splitlines():
 if not line.startswith('Stage{'):continue
 if gate:=re.search(r'gate:Some\(\((\d+),(\d+)\)\)',line):a,b=map(int,gate.groups());q.append(form(q,a)&form(q,b));gates+=1
 for a,b in pairs(re.search(r'cx:&\[(.*?)\],x:',line)[1]):q[b]^=q[a]
 mask=int(re.search(r'],x:(\d+),erase:',line)[1])
 for i in range(len(q)):
  if mask>>i&1:q[i]^=one
 for at,terms in re.findall(r'Erase\{at:(\d+),terms:&\[(.*?)\]\}',line):
  at=int(at);phase=0
  for a,b in pairs(terms):phase^=(one if a==0 else q[a-1])&(one if b==0 else q[b-1])
  assert phase==q[at];q.pop(at);draws+=1
assert gates==31 and draws==11 and len(q)==34
dag=json.loads((r/'PREFIX-DAG.json').read_text());old=[one]+inputs
for _,a,b in dag['gates']:old.append(combine(a,old)&combine(b,old))
new_masks=list(map(int,re.search(r'const FULL_FIELDS:&\[u64\]=&\[([\d,]+)\]',s)[1].split(',')));assert len(new_masks)==len(dag['field_masks'])==21
truth_hash=lambda x:hashlib.sha256(x.to_bytes(2048,'little')).hexdigest();fields=[]
for i,(new,previous)in enumerate(zip(new_masks,dag['field_masks'])):
 a=form(q,new);b=combine(previous,old);assert a==b;fields.append({'field':i,'new_mask':new,'old_mask':previous,'common_truth_sha256':truth_hash(a)})
for i,mask in enumerate(dag['low_sum_masks']):assert q[i]==combine(mask,old)
assert q[6:14]==inputs[6:14]and q[33]==combine(dag['c6_mask'],old)
result={'status':'ALL14_INPUT_FIELD_INTERFACES_EXACTLY_EQUAL','primary_input_assignments':16384,'field_forms_equal':21,'low_sum_outputs_equal':6,'other_primary_inputs_restored':8,'carry_in_held19_equals_original_c6':True,'forward_measurement_phase_identities_equal':11,'fields':fields,'source_hashes':{p:hashlib.sha256((r/p).read_bytes()).hexdigest()for p in ['verify.py','runtime-source.rs','PREFIX-DAG.json']},'scope':'Exact truth-function interface of unretained prefix27/cleanup11, the mask0 setting selected for two whole ticks. New FULL_FIELDS match all21 original field functions,6 low-sum outputs and c6 carry on all16384 primary inputs; forward phase-repair predicates also exact. This supports compositional use of unchanged field_map/ladder_d arithmetic and existing native phase/upper-word controls. It is NOT a proof of arbitrary source-bound postpass transport, a full curve correctness proof, a benchmark or resource record.'};(r/'INTERFACE-VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'])

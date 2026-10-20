"""Compile exact linear basis schedules and Clifford phase witnesses to Rust."""
import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;d=json.loads((r/'PREFIX-DAG.json').read_bytes());modelpath=r/'PROTECTED-v3-c1+c2+c3+c4+tt.json';m=json.loads(modelpath.read_bytes());assert m['quadratic_only_final_helpers']==20 and m['greedy_quadratic_erasure_helper_peak']==27 and m['finishing_cubic_terms']==0
f={k:int(v,16)for k,v in json.loads((r.parent/'breakthrough-live-core-rank-20261020/FUNCTIONS.json').read_bytes()).items()};values=[f['one']]+[f['input'+str(i)]for i in range(14)]
def truth(mask):
 v=0
 while mask:
  bit=mask&-mask;v^=values[bit.bit_length()-1];mask^=bit
 return v
for _,a,b in d['gates']:values.append(truth(a)&truth(b))
def coordinate(v,source):
 basis={}
 for i,x in enumerate(source):
  coef=1<<i
  while x:
   h=x.bit_length()-1
   if h not in basis:basis[h]=(x,coef);break
   w,c=basis[h];x^=w;coef^=c
  assert x
 coef=0
 while v:
  h=v.bit_length()-1;w,c=basis[h];v^=w;coef^=c
 return coef
def transform(source,target):
 assert len(source)==len(target)and source[0]==target[0]==1;coeff=[coordinate(v,source)for v in target[1:]];rows=[v>>1 for v in coeff];n=len(rows);gates=[]
 def cx(a,b):rows[b]^=rows[a];gates.append((a,b))
 for i in range(n):
  pivot=next(j for j in range(i,n)if rows[j]>>i&1)
  if pivot!=i:cx(i,pivot);cx(pivot,i);cx(i,pivot)
  for j in range(n):
   if i!=j and rows[j]>>i&1:cx(i,j)
 assert rows==[1<<i for i in range(n)];ops=list(reversed(gates));offset=sum((v&1)<<i for i,v in enumerate(coeff));check=source[1:].copy()
 for a,b in ops:check[b]^=check[a]
 for i in range(n):check[i]^=offset>>i&1
 assert [1]+check==target
 return ops,offset
current=[1]+[1<<(i+1)for i in range(14)];rust=[];totalcx=0;erasures=0
for stage in m['stages']:
 gate='None'
 if not stage.get('cleanup_only'):
  i=stage['born']-1;_,a,b=d['gates'][i];gate=f'Some(({coordinate(a,current)},{coordinate(b,current)}))';current=current+[1<<(15+i)]
 full=stage['full_masks'];cx,offset=transform(current,full);totalcx+=len(cx);current=full.copy();er=[]
 for item in stage['erasures']:
  g=item['function_mask'];at=current.index(g)-1;assert at>=14;terms=[]
  for term in item['phase_terms']:
   ids=[current.index(v)for v in term];assert 0<=len(ids)<=2 and current.index(g)not in ids;terms.append((ids[0],ids[1]if len(ids)==2 else 0))
  er.append('Erase{at:'+str(at)+',terms:&['+','.join(f'({a},{b})'for a,b in terms)+']}');current.pop(at+1);erasures+=1
 assert current==stage['retained_masks'];rust.append('Stage{gate:'+gate+',cx:&['+','.join(f'({a},{b})'for a,b in cx)+'],x:'+str(offset)+',erase:&['+','.join(er)+']}')
selected=json.loads((r.parent/'breakthrough-live-core-rank-20261020/QUADRATIC-LOAN-REVERSE-MODEL.json').read_bytes())['selected_output_basis'];output=[d['c6_mask']if n=='c6'else d['field_masks'][int(n[5:])]for n in selected];target=[1]+d['low_sum_masks']+[1<<(i+1)for i in range(6,14)]+output;assert len(target)==35;cx,offset=transform(current,target);totalcx+=len(cx);rust.append('Stage{gate:None,cx:&['+','.join(f'({a},{b})'for a,b in cx)+'],x:'+str(offset)+',erase:&[]}');assert erasures==11
source='''struct Erase{at:usize,terms:&'static[(usize,usize)]}
struct Stage{gate:Option<(u64,u64)>,cx:&'static[(usize,usize)],x:u64,erase:&'static[Erase]}
const STAGES:&[Stage]=&[
'''+',\n'.join(rust)+'''
];
fn form(q:&[QubitId],mask:u64)->Lin{let mut f=Lin::k(mask&1!=0);for(i,&w)in q.iter().enumerate(){if mask>>(i+1)&1!=0{f=f.x(&l(w));}}f}
pub(super)fn build(c:&mut Builder,input:&[QubitId])->Vec<QubitId>{assert_eq!(input.len(),14);let mut q=input.to_vec();
 for stage in STAGES{if let Some((a,b))=stage.gate{let a=form(&q,a);let b=form(&q,b);q.push(lin_and(c,&a,&b));}for &(a,b)in stage.cx{c.cx(q[a],q[b]);}for i in 0..q.len(){if stage.x>>i&1!=0{c.x(q[i]);}}
  for erase in stage.erase{let bit=c.alloc_bit();c.hmr(q[erase.at],bit);c.push_condition(bit);for &(a,b)in erase.terms{match(a,b){(0,0)=>{c.cz(q[0],q[0]);c.x(q[0]);c.cz(q[0],q[0]);c.x(q[0]);},(a,0)|(0,a)=>c.cz(q[a-1],q[a-1]),(a,b)=>c.cz(q[a-1],q[b-1]),}}c.pop_condition();c.free_bit(bit);c.release_clean(q[erase.at]);q.remove(erase.at);}
 }assert_eq!(&q[..14],input);assert_eq!(q.len(),34);q[14..].to_vec()
}
''';(r/'native-schedule.rs').write_bytes(source.encode())
expected=[truth(v)for v in target[1:]];lines=['34 256']
for value in expected:lines.append(' '.join(str(value>>(64*i)&((1<<64)-1))for i in range(256)))
(r/'native-schedule-expected.dat').write_bytes(('\n'.join(lines)+'\n').encode());(r/'NATIVE-GENERATION.json').write_bytes((json.dumps({'status':'GENERATED_NATIVE_COMPONENT_PENDING','model_sha256':hashlib.sha256(modelpath.read_bytes()).hexdigest(),'runtime_sha256':hashlib.sha256((r/'native-schedule.rs').read_bytes()).hexdigest(),'expected_sha256':hashlib.sha256((r/'native-schedule-expected.dat').read_bytes()).hexdigest(),'ANDs':31,'HMRs':erasures,'basis_CNOTs':totalcx,'predicted_helper_peak':27,'final_helpers':20,'phase_repairs':'Clifford only','scope':'Generated component source and all linear transforms checked; no native pass or full-circuit gain yet.'},indent=2)+'\n').encode());print('Generated',totalcx,'basis CNOTs,31ANDs,11HMRs; native tests pending')

"""Invert late prefix scheduling, then close the six low-bit carries in place."""
import ast,hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;tree=ast.parse((r/'generate-native-schedule.py').read_text());ns={};exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name in ['coordinate','transform']],type_ignores=[]),'<exact-linear-functions>','exec'),ns);coordinate=ns['coordinate'];transform=ns['transform'];d=json.loads((r/'PREFIX-DAG.json').read_bytes());m=json.loads((r/'PROTECTED-v3-c1+c2+c3+c4+tt.json').read_bytes());f={k:int(v,16)for k,v in json.loads((r.parent/'breakthrough-live-core-rank-20261020/FUNCTIONS.json').read_bytes()).items()};values=[f['one']]+[f['input'+str(i)]for i in range(14)]
def truth(mask):
 v=0
 while mask:
  bit=mask&-mask;v^=values[bit.bit_length()-1];mask^=bit
 return v
for _,a,b in d['gates']:values.append(truth(a)&truth(b))
def mul(a,b):
 linear=0;edges=set()
 for i in range(a.bit_length()):
  if not a>>i&1:continue
  for j in range(b.bit_length()):
   if not b>>j&1:continue
   if i==0 or j==0 or i==j:linear^=1<<max(i,j)
   else:
    edge=tuple(sorted([i,j]));edges.symmetric_difference_update([edge])
 return linear,edges
def factor(linear,edges):
 edges=edges.copy();products=[]
 while edges:
  a,b=min(edges);aa=(1<<a);bb=(1<<b)
  for x,y in edges:
   if b in(x,y)and a not in(x,y):aa^=1<<(y if x==b else x)
   if a in(x,y)and b not in(x,y):bb^=1<<(y if x==a else x)
  li,ee=mul(aa,bb);linear^=li;edges.symmetric_difference_update(ee);assert not any(a in e or b in e for e in edges);products.append((aa,bb))
 return linear,products
def phase_terms(linear,edges):return [(i,0)for i in range(linear.bit_length())if linear>>i&1]+sorted(edges)
def value_of(mask,state):
 value=0
 for i,v in enumerate(state):
  if mask>>i&1:value^=v
 return truth(value)
records=[];current=[1]+[1<<(i+1)for i in range(14)]
for stage in m['stages']:
 old=current.copy();gate=None
 if not stage.get('cleanup_only'):
  j=stage['born']-1;_,a,b=d['gates'][j];gate=(coordinate(a,old),coordinate(b,old));current=current+[1<<(15+j)]
 birth=current.copy();cx,offset=transform(birth,stage['full_masks']);current=stage['full_masks'].copy();erasures=[]
 for item in stage['erasures']:
  at=current.index(item['function_mask'])-1;current.pop(at+1);linear=0;edges=set()
  for term in item['phase_terms']:
   ids=[current.index(v)for v in term]
   if len(ids)==1:linear^=1<<ids[0]
   else:
    li,ee=mul(1<<ids[0],1<<ids[1]);linear^=li;edges.symmetric_difference_update(ee)
  li,products=factor(linear,edges);check=value_of(li,current)
  for a,b in products:check^=value_of(a,current)&value_of(b,current)
  assert check==truth(item['function_mask']);erasures.append({'at':at,'function':item['function_mask'],'linear':li,'products':products,'after':current.copy()})
 assert current==stage['retained_masks'];records.append({'stage':stage,'old':old,'birth':birth,'gate':gate,'cx':cx,'offset':offset,'erasures':erasures,'after':current.copy()})
selected=json.loads((r.parent/'breakthrough-live-core-rank-20261020/QUADRATIC-LOAN-REVERSE-MODEL.json').read_bytes())['selected_output_basis'];outputs=[d['c6_mask']if n=='c6'else d['field_masks'][int(n[5:])]for n in selected];target=[1]+d['low_sum_masks']+[1<<(i+1)for i in range(6,14)]+outputs
ops=[];rebuilds=[]
def emit_xform(source,dest):
 global current
 assert current==source;cx,offset=transform(source,dest)
 for a,b in cx:ops.append(f'CleanupStep::Cx({a},{b})')
 for i in range(len(source)-1):
  if offset>>i&1:ops.append(f'CleanupStep::X({i})')
 current=dest.copy()
current=target.copy();emit_xform(current,records[-1]['after'])
def emit_erase(at,linear,edges):
 global current
 assert at>=14 and not(linear>>(at+1)&1)and all(at+1 not in e for e in edges);terms=phase_terms(linear,edges);ops.append('CleanupStep::Erase{at:'+str(at)+',terms:&['+','.join(f'({a},{b})'for a,b in terms)+']}');current.pop(at+1)
for rec in reversed(records):
 stage=rec['stage']
 if not stage.get('cleanup_only')and stage['born']==11:break
 assert current==rec['after']
 for item in reversed(rec['erasures']):
  assert current==item['after'];products=item['products'];ops.append('CleanupStep::Rebuild{at:'+str(item['at'])+',linear:'+str(item['linear'])+',products:&['+','.join(f'({a},{b})'for a,b in products)+']}');rebuilds.append({'function_mask':item['function'],'ANDs':len(products)});current.insert(item['at']+1,item['function'])
 emit_xform(current,rec['birth'])
 if rec['gate']:
  a,b=rec['gate'];linear,edges=mul(a,b);assert value_of(a,current)&value_of(b,current)==truth(current[-1]);emit_erase(len(current)-2,linear,edges)
 assert current==rec['old']
canonical=[1]+[1<<(i+1)for i in range(14)]+d['helper_masks'][:11];assert len(current)==26;emit_xform(current,canonical)
def erase_original(j):
 _,a,b=d['gates'][j];off=d['helper_masks'][j]^(1<<(15+j));at=current.index(d['helper_masks'][j])-1;aa=coordinate(a,current);bb=coordinate(b,current);linear,edges=mul(aa,bb);linear^=coordinate(off,current);assert value_of(aa,current)&value_of(bb,current)^value_of(coordinate(off,current),current)==truth(d['helper_masks'][j]);emit_erase(at,linear,edges)
for j in [9,8,7,6,4]:erase_original(j)
new=[1]+d['low_sum_masks']+[1<<(i+1)for i in range(6,14)]+current[15:];emit_xform(current,new)
for j in [10,3,2,1,0,5]:erase_original(j)
assert current==[1]+d['low_sum_masks']+[1<<(i+1)for i in range(6,14)]
runtime='''enum CleanupStep{Cx(usize,usize),X(usize),Rebuild{at:usize,linear:u64,products:&'static[(u64,u64)]},Erase{at:usize,terms:&'static[(usize,usize)]}}
const CLEANUP:&[CleanupStep]=&[
'''+',\n'.join(ops)+'''
];
pub(super)fn finish(c:&mut Builder,input:&[QubitId],held:&[QubitId]){assert_eq!(input.len(),14);assert_eq!(held.len(),20);let mut q=input.to_vec();q.extend_from_slice(held);
 for step in CLEANUP{match step{CleanupStep::Cx(a,b)=>c.cx(q[*a],q[*b]),CleanupStep::X(a)=>c.x(q[*a]),CleanupStep::Rebuild{at,linear,products}=>{let target=c.alloc_qubit();for &(a,b)in *products{lin_and_into(c,target,&form(&q,a),&form(&q,b));}lin_xor_into(c,&form(&q,*linear),target);q.insert(*at,target);},CleanupStep::Erase{at,terms}=>{let bit=c.alloc_bit();c.hmr(q[*at],bit);c.push_condition(bit);for &(a,b)in *terms{match(a,b){(0,0)=>{c.cz(q[0],q[0]);c.x(q[0]);c.cz(q[0],q[0]);c.x(q[0]);},(a,0)|(0,a)=>c.cz(q[a-1],q[a-1]),(a,b)=>c.cz(q[a-1],q[b-1]),}}c.pop_condition();c.free_bit(bit);c.release_clean(q[*at]);q.remove(*at);}}}
 assert_eq!(q,input);
}
''';(r/'native-cleanup.rs').write_bytes(runtime.encode());total=sum(x['ANDs']for x in rebuilds);(r/'CLEANUP-GENERATION.json').write_bytes((json.dumps({'status':'GENERATED_LOW_SUM_PRESERVING_CLEANUP_PENDING_NATIVE','runtime_sha256':hashlib.sha256((r/'native-cleanup.rs').read_bytes()).hexdigest(),'rebuilds':rebuilds,'cleanup_ANDs':total,'cleanup_HMRs':sum('::Erase{'in x for x in ops),'stops_inverse_after_birth':11,'low_sum_map_uses_existing_carries':True,'scope':'All regenerated function identities checked on16384 assignments; every linear transform checked. Native prefix-plus-upper-ladder/cleanup tests pending; no full-circuit resource result.'},indent=2)+'\n').encode());print('Generated cleanup',total,'ANDs;',sum('::Erase{'in x for x in ops),'HMRs; native verification pending')

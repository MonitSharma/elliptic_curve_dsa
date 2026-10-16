from pathlib import Path
from collections import Counter
import ctypes,ctypes.util,hashlib,json,struct,time
from algebra import product,factor
from cones import analyze

R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d=json.loads((R/'DECLARATION.json').read_text());source=Path(d['source']);N=2**64-1
names=['DECLARATION.json',*d['code_pins']];before={name:sha(R/name)for name in names}
for name,h in d['code_pins'].items():assert before[name]==h,name
assert sha(source)==d['source_sha256']
(R/'SOURCE-PINS-BEFORE.json').write_text(json.dumps(before,indent=2)+'\n')
start=time.monotonic();blob=source.read_bytes();assert blob[:8]==b'QECCOPSZ'
n=struct.unpack_from('<Q',blob,8)[0];assert n==10522755
z=ctypes.CDLL(ctypes.util.find_library('zstd'));z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
raw=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(raw,len(raw),blob[16:],len(blob)-16)==len(raw);del blob
op=lambda i:struct.unpack_from('<7Q',raw,i*56)
counts=Counter();cones=[];input_bits=set()
for i in range(n):
 kind,a,b,t,bt,guard,rt=op(i)
 if kind==2 and bt!=N:input_bits.add(bt)
 if kind!=13:continue
 counts['CCX_seeds']+=1
 cone=analyze(op,i,n,counts)
 if cone is not None:
  end=cone['end_exclusive'];cone['span_sha256']=hashlib.sha256(ctypes.string_at(ctypes.addressof(raw)+i*56,(end-i)*56)).hexdigest()
  cones.append(cone)

# Exact conservative classical constants; arbitrary declared input bits and
# every HMR bit are UNKNOWN. Scopes snapshot their actual incoming base.
state={b:2 for b in input_bits};base=1;stack=[];at={c['begin']:c for c in cones}
AND=lambda x,y:0 if x==0 or y==0 else 1 if x==y==1 else 2
for i in range(n):
 k,a,b,t,bt,g,rt=op(i);cond=AND(base,1 if g==N else state.get(g,0));old=state.get(bt,0)
 if i in at:at[i].update(entry_depth=len(stack),provable_enable=['false','true','unknown'][cond])
 if k==3:state[bt]=old if cond==0 else 1-old if cond==1 and old!=2 else 2
 elif k==4:state[bt]=0 if cond==1 or old==0 else old if cond==0 else 2
 elif k==5:state[bt]=1 if cond==1 or old==1 else old if cond==0 else 2
 elif k==12:state[bt]=old if cond==0 else 2
 elif k==15:stack.append(base);base=AND(base,state.get(g,0))
 elif k==16:assert stack;base=stack.pop()
assert not stack
eligible=[c for c in cones if c['rank']<4];selected=[];last=0
for cone in sorted(eligible,key=lambda c:(c['end_exclusive'],c['begin'])):
 if cone['begin']>=last:selected.append(cone);last=cone['end_exclusive']
known=sum(c['syntactic_T_saving']for c in selected if c['provable_enable']=='true')
upper=sum(c['syntactic_T_saving']for c in selected if c['provable_enable']!='false')
after={name:sha(R/name)for name in names};assert before==after and sha(source)==d['source_sha256']
(R/'SOURCE-PINS-AFTER.json').write_text(json.dumps(after,indent=2)+'\n')
report={'status':'SOURCE_ONLY_BOUNDED_TWO_CCX_AFFINE_INVENTORY_COMPLETE','source_sha256':d['source_sha256'],
 'ops':n,'scan_counters':dict(counts),'all_cones':cones,'selected_beneficial_indices':[[c['begin'],c['end_exclusive']]for c in selected],
 'selected_nonoverlap_cones':len(selected),'selected_rank_counts':dict(Counter(c['rank']for c in selected)),
 'selected_provable_enable_counts':dict(Counter(c['provable_enable']for c in selected)),
 'guaranteed_executed_T_saving_per_shot':known,'maximum_selected_syntactic_T_saving_per_shot':upper,
 'selection':'Maximum-cardinality beneficial disjoint intervals by earliest finish, then earliest start; not a maximum-weight T optimization.',
 'elapsed_seconds':time.monotonic()-start,'candidate_created':False,'census_or_nonce_search':False,'mean_T_claim':False}
(R/'INVENTORY.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items()if k not in('all_cones','selected_beneficial_indices')}),flush=True)
